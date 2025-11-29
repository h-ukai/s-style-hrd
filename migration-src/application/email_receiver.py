# -*- coding: utf-8 -*-

"""Email receiver handler - IMAP polling migration from GAE Mail API

Original: InboundMailHandler + Mail API (GAE Python 2.7)
Migrated: IMAP polling + Flask + Cloud NDB (Python 3.11)

Migration notes:
- GAE Mail API (/_ah/mail/*) is deprecated in Python 3.11
- Replaced with IMAP polling (10 minute intervals via Cron)
- Runs in Cron job: /tasks/check-incoming-mail (see cron.yaml)
- Uses imaplib for Python 3 compatible IMAP access
"""

import logging
import imaplib
import email
from email import policy
from email.header import decode_header
from email.utils import parseaddr, getaddresses
from flask import request, Response
from google.cloud import ndb
import config
from application.email_decoder import email_decoder
from application.messageManager import messageManager
from application.models.member import member

# IMAP server configuration (should be in Cloud Secret Manager)
IMAP_SERVER = config.get('IMAP_SERVER', 'imap.example.com')
IMAP_PORT = config.get('IMAP_PORT', 993)
IMAP_USER = config.get('IMAP_USER', 'mailbox@example.com')
IMAP_PASSWORD = config.get('IMAP_PASSWORD', '')


def mail_handler_route():
    """
    Email receiver handler - IMAP polling version

    Replaces GAE Mail API InboundMailHandler
    Called by Cron job every 10 minutes
    """
    try:
        return check_incoming_mail()
    except Exception as e:
        logging.error("Email handler error: %s", str(e))
        return Response("Error: " + str(e), status=500)


def check_incoming_mail():
    """Check IMAP mailbox for new messages and process them"""
    # REVIEW-L2: IMAP接続情報が平文で設定されている
    # 推奨: Cloud Secret Manager から認証情報を取得するようにセキュリティを強化
    try:
        # Connect to IMAP server (SSL)
        imap = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)
        imap.login(IMAP_USER, IMAP_PASSWORD)

        # Select INBOX
        status, mailbox_data = imap.select('INBOX')
        if status != 'OK':
            logging.error("Failed to select INBOX: %s", status)
            return Response("Failed to select INBOX", status=400)

        # Get unseen messages
        status, messages = imap.search(None, 'UNSEEN')
        if status != 'OK':
            logging.warning("No unseen messages found")
            imap.close()
            imap.logout()
            return Response("No new messages", status=200)

        message_ids = messages[0].split()
        processed_count = 0

        for msg_id in message_ids:
            try:
                # Fetch message
                status, msg_data = imap.fetch(msg_id, '(RFC822)')
                if status != 'OK':
                    logging.warning("Failed to fetch message %s", msg_id)
                    continue

                # Parse message
                msg_bytes = msg_data[0][1]
                msg = email.message_from_bytes(msg_bytes, policy=policy.default)

                # Process message
                process_incoming_message(msg)

                # REVIEW-L3: \Seen フラグを立てているが、マイグレーション仕様では「既読フラグ付与せず」
                # 提案: GAE_MIGRATION_STATE.md の仕様(Line 190)と一致させるため、このフラグ付与を削除するか確認
                # Mark as seen (keep in mailbox)
                imap.store(msg_id, '+FLAGS', '\\Seen')
                processed_count += 1

            except Exception as e:
                logging.error("Error processing message %s: %s", msg_id, str(e))
                continue

        imap.close()
        imap.logout()

        logging.info("Processed %d messages", processed_count)
        return Response(f"Processed {processed_count} messages", status=200)

    except Exception as e:
        logging.error("IMAP connection error: %s", str(e))
        return Response("Error: " + str(e), status=500)


def process_incoming_message(msg):
    """
    Process a single incoming email message

    Args:
        msg: email.message.Message object
    """
    try:
        # Decode message content
        mail = email_decoder(msg.as_string())

        subject = mail.subject
        plaintext = mail.get_body_plain()

        # Extract to list
        to_list = mail.listaddr('to', address_only=False)
        to = 'To: %s' % (', '.join(['%s <%s>' % (_n if _n else _a, _a) for (_n, _a) in to_list]))

        # Extract from list
        from_list = mail.listaddr('from', address_only=False)
        mailfrom = 'From: %s' % (', '.join(['%s <%s>' % (_n if _n else _a, _a) for (_n, _a) in from_list]))

        body = plaintext + '\n' + mailfrom + '\n' + to

        # Extract member ID from email address
        # Format: corp_memberID@domain
        userstr = mail.to.split('@')[0]
        user = userstr.split('_')

        if len(user) > 1:
            corp = user[0]
            userID = user[1]
        else:
            # Default to system member
            corp = 's-style'
            userID = 'test222'

        logging.info('mail receiver Subject: %s', mail.subject)
        logging.info('mail receiver to: %s and %s', corp, userID)

        # Get member key
        key_name = corp + "/" + userID
        memdb = member.get_by_key_name(key_name)
        memto = None
        # REVIEW-L1: tanto の None チェックを追加
        # 修正前: memto = memdb.tanto.memberID if memdb.tanto else None (memdb が None の場合エラー)
        # 修正後: memdb と memdb.tanto の両方をチェック
        if memdb and memdb.tanto:
            memto = memdb.tanto.memberID
        else:
            memto = None

        # Post message to messageManager
        mes = messageManager.post(
            corp=corp,
            sub=subject,
            body=body,
            done=False,
            memfrom=userID,
            kindname="メール受信",
            combkind="所有",
            msgkey=None,
            reservation=None,
            reservationend=None,
            memto=memto,
            commentto=None,
            mailto="tanto",
            htmlmail=None
        )

        logging.info("Message processed: %s", str(mes))

    except Exception as e:
        logging.error("Error processing incoming message: %s", str(e))
        raise


# Legacy InboundMailHandler class (for reference, deprecated)
# In Python 3.11, this handler type is no longer available in GAE
# All email reception is now done via IMAP polling

class MailHandler:
    """Legacy InboundMailHandler - deprecated, kept for reference only"""
    def post(self):
        """Deprecated: use check_incoming_mail() instead"""
        raise NotImplementedError("InboundMailHandler is deprecated in Python 3.11. Use IMAP polling instead.")
