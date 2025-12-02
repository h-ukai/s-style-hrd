#!/usr/local/bin/python
# -*- coding: utf-8 -*-

from flask import request, render_template_string
from google.cloud import ndb
import smtplib
from email.message import EmailMessage
from application import session
import os
from application import config
from application import messageManager
from application.models.member import member
from application.wordstocker import wordstocker
import datetime

ADMIN_EMAIL = config.ADMIN_EMAIL

def mailinglist_route(**kwargs):
    """Flask route handler for mailing list"""
    if request.method == 'GET':
        return do_post(**kwargs)
    else:
        return do_post(**kwargs)

def do_post(**kwargs):
    """POST handler for mailing list"""
    tmpl_val = {}
    ssn = session.Session(request, sid_name="s-style")
    tmpl_val['error_msg'] = ''

    if not ssn.chk_ssn():
        # Create default session for president
        query = member.query(member.CorpOrg_key_name == 's-style', member.memberID == 'president')
        users = query.fetch(1)
        if users:
            user = users[0]
            ssn = session.Session(request, sid_name="s-style")
            sid = ssn.new_ssn()

            ssn.set_ssn_data('CorpOrg_key_name', user.CorpOrg_key_name)
            ssn.set_ssn_data('Branch_Key_name', user.Branch_Key_name)
            ssn.set_ssn_data('sitename', user.sitename)
            ssn.set_ssn_data('memberID', user.memberID)
            ssn.set_ssn_data('name', user.name)
            ssn.set_ssn_data('status', user.status)
            ssn.set_ssn_data('phone', user.phone)
            ssn.set_ssn_data('mobilephone', user.mobilephone)
            ssn.set_ssn_data('mail', user.mail)
            ssn.set_ssn_data('userkey', str(user.key.urlsafe().decode()))

    CorpOrg_key_name = ssn.get_ssn_data('CorpOrg_key_name')
    Branch_Key_name = ssn.get_ssn_data('Branch_Key_name')
    sitename = ssn.get_ssn_data('sitename')
    memberID = ssn.get_ssn_data('memberID')
    name = ssn.get_ssn_data('name')
    status = ssn.get_ssn_data('status')
    phone = ssn.get_ssn_data('phone')
    mobilephone = ssn.get_ssn_data('mobilephone')
    usermail = ssn.get_ssn_data('mail')
    userkey = ssn.get_ssn_data('userkey')

    msg = None
    if request.values.get("msgkey"):
        tmpl_val['msgkey'] = request.values.get("msgkey")
        # REVIEW-L2: ndb.Key(urlsafe=...) の使用方法を確認
        # 推奨: msgkey は正しく urlsafe エンコードされていることを確認
        msg = ndb.Key(urlsafe=tmpl_val['msgkey']).get() if tmpl_val['msgkey'] else None
        if msg:
            tmpl_val['subject'] = msg.subject
            tmpl_val['body'] = msg.body

    if request.values.get("subject"):
        tmpl_val['subject'] = request.values.get("subject")
    if request.values.get("body"):
        tmpl_val['body'] = request.values.get("body")

    tmpl_val['status'] = request.values.get("status", "")
    tmpl_val['seiyaku'] = request.values.get("seiyaku", "")
    tmpl_val['service'] = request.values.get("service", "")

    tmpl_val['servicelist'] = wordstocker.get(CorpOrg_key_name, u"サービス")

    submit = request.values.get("com", "")
    if submit == u"メール保存":
        msgkey = messageManager.messageManager.post(
            tmpl_val['subject'], tmpl_val['body'],
            ndb.Key(urlsafe=userkey), "メーリングリスト", "所有", msg
        )
    if submit == u"メール送信":
        if not tmpl_val.get('subject'):
            tmpl_val['error_msg'] += u"表題がありません　　"
        if not tmpl_val.get('body'):
            tmpl_val['error_msg'] += u"本文がありません"

        if tmpl_val['error_msg'] == "":
            msgkey = messageManager.messageManager.post(
                tmpl_val['subject'],
                u"送信済み：\n" + tmpl_val['body'],
                ndb.Key(urlsafe=userkey),
                u"メーリングリスト",
                u"送信"
            )
            tmpl_val['msgkey'] = msgkey

            # Get recipients based on filters
            where_clauses = []
            service = request.values.get("service", "")
            if service:
                where_clauses.append(member.service == service)

            status = request.values.get("status", "")
            if status:
                where_clauses.append(member.status == status)

            seiyaku = request.values.get("seiyaku", "")
            if seiyaku:
                where_clauses.append(member.seiyaku == seiyaku)

            where_clauses.append(member.CorpOrg_key_name == CorpOrg_key_name)

            # Build query
            query = member.query()
            for clause in where_clauses:
                query = query.filter(clause)

            members = query.fetch()
            if members:
                for mem in members:
                    if mem.mail:
                        try:
                            # Send email via SMTP
                            msg_email = EmailMessage()
                            msg_email['Subject'] = tmpl_val['subject']
                            msg_email['From'] = f'"{name}" <{ADMIN_EMAIL}>'
                            msg_email['To'] = mem.mail
                            msg_email['Reply-To'] = usermail
                            msg_email.set_content(tmpl_val['body'])

                            # Note: SMTP server configuration should be in config.py
                            # smtp_server = smtplib.SMTP(config.SMTP_SERVER, config.SMTP_PORT)
                            # smtp_server.send_message(msg_email)
                            # smtp_server.quit()

                            messageManager.messageManager.combination(
                                msgkey, CorpOrg_key_name, mem.key, u"受信"
                            )
                        except Exception as e:
                            print(f"Error sending email: {e}")

    member_obj = ndb.Key(urlsafe=userkey).get() if userkey else None
    if member_obj:
        msglist = messageManager.messageManager.getmeslist(
            CorpOrg_key_name,
            member_obj,
            kindname=u"メーリングリスト",
            order='-reservation'
        )
    else:
        msglist = []
    tmpl_val['msglist'] = msglist

    path = os.path.dirname(__file__) + '/../templates/mailinglist.html'
    try:
        with open(path, 'r', encoding='utf-8') as f:
            template_content = f.read()
        return render_template_string(template_content, **tmpl_val)
    except FileNotFoundError:
        return f"Template not found: {path}", 404
