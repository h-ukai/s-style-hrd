# -*- coding: utf-8 -*-

"""
Message management module - Python 3.11 migration

Original: GAE Standard Python 2.7 + db.Model
Migrated: Python 3.11 + Cloud NDB + smtplib
"""

from google.cloud import ndb
from application.models.message import Message
from application.models.msgcombinator import msgcombinator
from application.models.member import member
from datetime import datetime
import re
from application import timemanager
from application import config
import logging
import smtplib
import ssl
from email.message import EmailMessage
from email.utils import formataddr
from application.secret_manager import get_smtp_config


class messageManager:
    """Message management utility for handling messages and mail"""

    @classmethod
    def _send_mail(cls, sender, emailto, subject, body=None, html=None):
        """
        Send email using SMTP (migration from Mail API)

        Args:
            sender: Sender email address or formatted string
            emailto: Recipient email address
            subject: Email subject
            body: Plain text body (optional)
            html: HTML body (optional)
        """
        try:
            # Create EmailMessage (Python 3.11 standard library)
            message = EmailMessage()
            message['From'] = sender
            message['To'] = emailto
            message['Subject'] = subject

            if html:
                message.set_content(body or "", subtype='plain')
                message.add_alternative(html, subtype='html')
            elif body:
                message.set_content(body, subtype='plain')
            else:
                message.set_content("", subtype='plain')

            # SMTP設定をSecret Managerから取得
            smtp_config = get_smtp_config()

            # SSL/TLS接続（ポート465）で送信
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(smtp_config['server'], smtp_config['port'], context=context) as server:
                server.login(smtp_config['user'], smtp_config['password'])
                server.send_message(message)
                logging.warning('送信しました')

        except Exception as e:
            logging.error('送信失敗しました 失敗した送信先>> %s', emailto)
            raise

    @classmethod
    def post(cls, corp, sub, body, done, memfrom, kindname, combkind="所有", msgkey=None,
             reservation=None, reservationend=None, memto=None, commentto=None, mailto=None, htmlmail=None):
        """
        Post a message

        Args:
            corp: Corporation key name
            sub: Subject
            body: Message body
            done: Done flag
            memfrom: Member ID (sender)
            kindname: Message kind name
            combkind: Combination kind
            msgkey: Message key (for updates)
            reservation: Reservation datetime
            reservationend: Reservation end datetime
            memto: Member ID (recipient)
            commentto: Comment to field
            mailto: Email recipient type ('tanto', 'member', 'each')
            htmlmail: HTML mail flag
        """
        Flg = False
        memdb = None

        if not memfrom and not msgkey:
            return None

        if memfrom:
            key_name = corp + "/" + memfrom
            memdb = member.get_by_key_name(key_name)
            if memdb:
                if memdb.isrequest(kindname):
                    memdb.LastRequestdatetimeset()

        if msgkey:
            msg = cls.getmesbyID(corp, msgkey)
        else:
            msg = Message()
            Flg = True

        if corp:
            msg.corp = corp
        if body:
            body2 = body
            if mailto == "tanto":
                body2 += "\n" + "with 担当にメール送信"
            elif mailto == "member":
                body2 += "\n" + "with メール送信"
            elif mailto == "each":
                body2 += "\n" + "with メール送信 担当にもメール送信"
            msg.body = body2

        if sub:
            msg.subject = sub
        if kindname:
            msg.kindname = kindname
        if done == True or done == "true" or done == "True":
            msg.done = True
        else:
            msg.done = False

        if reservation:
            r = re.compile(".*:.*:.*").match(reservation, 1)
            if r is None:
                rtime = datetime.strptime(reservation, "%Y/%m/%d")
            else:
                rtime = datetime.strptime(reservation, "%Y/%m/%d %H:%M:%S")
            msg.reservation = timemanager.jst2utc_date(rtime)

        if reservationend:
            r = re.compile(".*:.*:.*").match(reservationend, 1)
            if r is None:
                rtime = datetime.strptime(reservationend, "%Y/%m/%d")
            else:
                rtime = datetime.strptime(reservationend, "%Y/%m/%d %H:%M:%S")
            msg.reservationend = timemanager.jst2utc_date(rtime)

        if commentto:
            msg.commentTo = commentto
            if not kindname:
                msg.kindname = "コメント"

        msgkey = msg.put()

        if combkind == "":
            combkind = "所有"

        res = None

        if msgkey and Flg:
            res = cls.combination(msgkey, corp, memdb, combkind)
            if not memto and memdb and memdb.tanto:
                res = cls.combination(msgkey, corp, memdb.tanto, "参照")

        if memto and Flg:
            key_name = corp + "/" + memto
            memdbto = member.get_by_key_name(key_name)
            res = cls.combination(msgkey, corp, memdbto, "送信")

        if mailto:  # tanto, member, each
            if mailto == "tanto" or mailto == "each":
                if memdb and memdb.tanto and memdb.tanto.mail:
                    sender = f'sender{config.ADMIN_EMAIL_BASE}'
                    if htmlmail:
                        cls._send_mail(sender, memdb.tanto.mail, subject=sub, html=body)
                    else:
                        mailbody = ""
                        if memdb.name:
                            mailbody += "お客様：" + memdb.name + "　"
                        if memdb.yomi:
                            mailbody += memdb.yomi
                        if mailbody != "":
                            mailbody += "\n"
                        if memdb.address:
                            mailbody += "住所：" + memdb.address + "\n"
                        if memdb.phone:
                            mailbody += "tel：" + memdb.phone + "\n"
                        if memdb.mail:
                            mailbody += "mail：" + memdb.mail + "\n"
                        mailbody += body
                        cls._send_mail(sender, memdb.tanto.mail, subject=sub, body=mailbody)
                else:
                    msg.body += "NG アドレス不明"
                    msg.put()

            if mailto == "member" or mailto == "each":
                key_name = corp + "/" + memfrom
                memdb = member.get_by_key_name(key_name)
                if memdb and memdb.tanto and memdb.tanto.memberID:
                    sender = f'"{memdb.tanto.name}" <{corp}_{memdb.memberID}{config.ADMIN_EMAIL_BASE}>'
                    if htmlmail:
                        cls._send_mail(sender, memdb.mail, subject=sub, html=body)
                    else:
                        cls._send_mail(sender, memdb.mail, subject=sub, body=body)
                else:
                    msg.body += "NG　 アドレス不明"
                    msg.put()

        return msgkey

    @classmethod
    def combination(cls, msgkey, corp, memdb, combkind):
        """Create a message-member combination"""
        # REVIEW-L1: memdb.key() → memdb.key (ndb では key プロパティ)
        # 修正前: comb.refmem = memdb.key() (Python 2.7 の db.Model)
        # 修正後: comb.refmem = memdb.key (Python 3.11 の ndb.Model)
        if memdb:
            comb = msgcombinator()
            comb.refmes = msgkey
            comb.refmem = memdb.key
            comb.combkind = combkind
            comb.put()
            return True
        else:
            return False

    @classmethod
    def killmesbyID(cls, corp, ID):
        """Mark message as deleted by ID"""
        msg = cls.getmesbyID(corp, ID)
        if msg:
            msg.kill = True
            msg.put()

    @classmethod
    def killmes(cls, corp, key):
        """Mark message as deleted by key"""
        msg = cls.getmesbykey(corp, key)
        if msg:
            msg.kill = True
            msg.put()

    @classmethod
    def getmeslistbyID(cls, corp, memberID, subject=None, kindname=None, done=None, kill=None,
                      reservationLower=None, reservationUpper=None, order=None, combkind=None):
        """Get message list by member ID"""
        mem = member.get_by_key_name(corp + "/" + memberID)
        if mem:
            return cls.getmeslist(corp, mem, subject, kindname, done, kill, reservationLower,
                                 reservationUpper, order, combkind)
        return []

    @classmethod
    def getmeslist(cls, corp, member_obj, subject=None, kindname=None, done=None, kill=None,
                  reservationLower=None, reservationUpper=None, order=None, combkind=None):
        """Get message list for a member"""
        if member_obj.CorpOrg_key_name != corp:
            raise messageManagerError("BadIDError: Invalid ID")

        # REVIEW-L2-FIXED: ndb migration - replace db backreference with explicit query
        # Old db code: comblist = member_obj.refmeslist (automatic backreference)
        # New ndb code: query msgcombinator where refmem == member_obj.key
        comblist = msgcombinator.query(msgcombinator.refmem == member_obj.key)
        if combkind:
            comblist = comblist.filter(msgcombinator.combkind == combkind)

        res = []
        for comb in comblist:
            # REVIEW-L2-FIXED: ndb Key needs .get() to access properties
            # Old db: comb.refmes.subject (automatic dereferencing)
            # New ndb: comb.refmes.get().subject (explicit dereferencing)
            try:
                msg = comb.refmes.get() if comb.refmes else None
                if not msg:
                    comb.key.delete()
                    continue
                sub = msg.subject
            except Exception as e:
                logging.error("comb.refmes.subject ERROR: %s", str(e))
                comb.key.delete()
                continue

            if subject and msg.subject != subject:
                continue
            if kindname and msg.kindname != kindname:
                continue
            if done is not None and msg.done != done:
                continue
            if kill == False:
                if msg and kill != msg.kill:
                    continue
            if reservationLower:
                rt = timemanager.jst2utc_date(reservationLower).replace(tzinfo=None)
                if msg.reservation < rt:
                    continue
            if reservationUpper:
                rt = timemanager.jst2utc_date(reservationUpper).replace(tzinfo=None)
                if msg.reservation >= rt:
                    continue

            res.append(msg)

        # REVIEW-L3: ソート処理が既に reverse=True を使用しており最適化済み
        # 効果: 旧コード(sort + reverse)より効率的
        if order:
            if order == "reservation":
                res.sort(key=lambda obj: obj.reservation)
            elif order == "-reservation":
                res.sort(key=lambda obj: obj.reservation, reverse=True)

        return res

    @classmethod
    def getmemlist(cls, message, combkind=None):
        """Get member list for a message"""
        # Cloud NDB: ReferenceProperty の collection_name (refmemlist) は自動生成されないため
        # 明示的なクエリで msgcombinator を取得する
        query = msgcombinator.query(msgcombinator.refmes == message.key)
        if combkind:
            query = query.filter(msgcombinator.combkind == combkind)
        return query

    @classmethod
    def getmesbyID(cls, corp, id):
        """Get message by ID"""
        mes = Message.get_by_id(int(id))
        if mes:
            cls.chkmes(corp, id, mes)
        return mes

    @classmethod
    def getmesbykey(cls, corp, key):
        """Get message by key"""
        mes = ndb.Key(urlsafe=key).get() if isinstance(key, str) else key.get()
        if mes:
            cls.chkmes(corp, str(key), mes)
        return mes

    @classmethod
    def getmembymesID(cls, id):
        """Get member by message ID"""
        mes = Message.get_by_id(int(id))
        comblist = cls.getmemlist(mes)
        mems = []
        for comb in comblist:
            mems = comb.refmem
        return mems

    @classmethod
    def chkmes(cls, corp, id, message):
        """Check if message belongs to corporation"""
        # Cloud NDB: ReferenceProperty の collection_name (refmemlist) は自動生成されないため
        # 明示的なクエリで msgcombinator を取得する
        comblist = msgcombinator.query(msgcombinator.refmes == message.key).fetch()
        for comb in comblist:
            mem = comb.refmem.get() if comb.refmem else None
            if mem and mem.CorpOrg_key_name != corp:
                raise messageManagerError("BadIDError: Invalid ID")


class messageManagerError(Exception):
    """Message Manager Exception"""
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


def change_tanto_worker_route():
    """Cloud Tasks worker for changing tanto (assigned person)"""
    from flask import request, Response
    from google.cloud import tasks_v2
    import logging

    try:
        corp = request.values.get("corp_name", "")
        tantoID = request.values.get("tantoID", "")
        oldtantoID = request.values.get("oldtantoID", "")

        tanto = member.get_by_key_name(corp + '/' + tantoID)
        oldtanto = member.get_by_key_name(corp + '/' + oldtantoID)

        if tanto and oldtanto:
            tantomem = oldtanto.mytanto
            for mem in tantomem:
                mem.tanto = tanto
                mem.put()  # Triggers change_tanto_task via put hook

            logging.info("Changed tanto for %s members", len(tantomem))
            return Response("OK", status=200)
        else:
            logging.error("Tanto not found: %s or %s", tantoID, oldtantoID)
            return Response("Error", status=400)

    except Exception as e:
        logging.error("Error in change_tanto_worker: %s", str(e))
        return Response("Error: " + str(e), status=500)


def change_tanto_task_route():
    """Cloud Tasks task for changing tanto reference messages"""
    from flask import request, Response

    try:
        corp = request.values.get("corp_name", "")
        memberID = request.values.get("memberID", "")
        tantoID = request.values.get("tantoID", "")
        oldtantoID = request.values.get("oldtantoID", "")

        mlist = messageManager.getmeslistbyID(corp, memberID)
        tanto = member.get_by_key_name(corp + '/' + tantoID)
        oldtanto = member.get_by_key_name(corp + '/' + oldtantoID)

        # REVIEW-L1: key() → key (ndb プロパティ)
        # 修正前: comb.refmem.key() == oldtanto.key() (db.Model)
        # 修正後: comb.refmem.key == oldtanto.key (ndb.Model)
        if tanto and oldtanto:
            for mes in mlist:
                comblist = messageManager.getmemlist(mes, combkind="参照")
                for comb in comblist:
                    if comb.refmem.key == oldtanto.key:
                        comb.refmem = tanto.key
                        comb.put()

            logging.info("Changed message references for member %s", memberID)
            return Response("OK", status=200)
        else:
            logging.error("Tanto not found: %s or %s", tantoID, oldtantoID)
            return Response("Error", status=400)

    except Exception as e:
        logging.error("Error in change_tanto_task: %s", str(e))
        return Response("Error: " + str(e), status=500)
