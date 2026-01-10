#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Send message handler for Google App Engine Python 3.11 migration

Original: GAE Standard Python 2.7
Migrated: Python 3.11 + Flask + Cloud NDB
"""

import os
import urllib.parse
import logging
import sys
import smtplib
import ssl
from email.message import EmailMessage
from flask import request, Response, render_template, redirect
from google.cloud import ndb
from application import config
from application.SecurePageBase import SecurePageBase
from application.models.member import member
from application.secret_manager import get_smtp_config

ADMIN_EMAIL = config.ADMIN_EMAIL


def sendmsg_route():
    """Send message (contact form) handler - Flask version"""
    handler = Sendmsg()
    if request.method == 'GET':
        return handler.get()
    elif request.method == 'POST':
        return handler.post()
    return Response("Method not allowed", status=405)


class Sendmsg(SecurePageBase):
    """Send message handler for contact forms"""

    def __init__(self):
        super().__init__()
        self.tmpl_val = {}
        self.tmpl_val['error_msg'] = ''
        self.tmpl_val['completed_msg'] = ''

    def get(self, **kwargs):
        return self.post(**kwargs)

    def post(self, **kwargs):
        self.Secure_init(**kwargs)

        try:
            referer = request.headers.get('Referer', '')
        except Exception:
            referer = ''

        try:
            origin = request.headers.get('Origin', '')
        except Exception:
            origin = ''

        # REVIEW-L3: CORSヘッダーのワイルドカード使用
        # 効果: 本番環境ではセキュリティリスク。許可するドメインを制限することを推奨
        # CORS headers
        response = Response()
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Headers'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'

        self.tmpl_val['reqnum'] = request.values.get('reqnum', '')
        self.tmpl_val['reqtext'] = request.values.get('reqtext', '')
        self.tmpl_val['ref'] = request.values.get('ref', '')
        self.tmpl_val['togo'] = request.values.get('togo', '')

        if self.auth:
            self.tmpl_val['sid'] = request.values.get('sid', '')
            new_regist = request.values.get('new_regist', '')
            if new_regist:
                self.postmsg("HP問い合わせ", self.tmpl_val['reqnum'] + " 内容:" + self.tmpl_val['reqtext'],
                            False, "問い合わせ", 'each', self.tmpl_val['reqnum'])
                user_email = config.EMAIL_RECEIVER
                self._send_mail(user_email, "物件のお問い合わせをいただきました")
                self.tmpl_val['completed_msg'] = '送信しました'
        else:
            # Build redirect URL
            urlstr = "corp_name=" + self.corp_name
            urlstr = urlstr + "&branch_name=" + self.branch_name
            urlstr = urlstr + "&sitename=" + self.Sitename
            if self.tmpl_val['ref']:
                urlstr += "&ref=" + self.tmpl_val['ref']
            if self.tmpl_val.get('userpagebase'):
                urlstr += "&userpagebase=" + self.tmpl_val['userpagebase']

            # URL encode parameters
            if self.tmpl_val['togo']:
                try:
                    togo = urllib.parse.unquote_plus(self.tmpl_val['togo'])
                    # Python 3: str is already unicode
                    self.tmpl_val['togo'] = urllib.parse.quote_plus(togo)
                except Exception as e:
                    logging.error('URL encode error: %s togo: %s', str(e), self.tmpl_val['togo'])
                urlstr += "&togo=" + self.tmpl_val['togo']

            if self.tmpl_val['reqnum']:
                try:
                    reqnum = urllib.parse.unquote_plus(self.tmpl_val['reqnum'])
                    self.tmpl_val['reqnum'] = urllib.parse.quote_plus(reqnum)
                except Exception as e:
                    logging.error('URL encode error: %s reqnum: %s', str(e), self.tmpl_val['reqnum'])
                urlstr += "&reqnum=" + self.tmpl_val['reqnum']

            if self.tmpl_val['reqtext']:
                try:
                    reqtext = urllib.parse.unquote_plus(self.tmpl_val['reqtext'])
                    self.tmpl_val['reqtext'] = urllib.parse.quote_plus(reqtext)
                except Exception as e:
                    logging.error('URL encode error: %s reqtext: %s', str(e), self.tmpl_val['reqtext'])
                urlstr += "&reqtext=" + self.tmpl_val['reqtext']

            return redirect('/regist?' + urlstr)

        self.tmpl_val["applicationpagebase"] = (self.corp_name + "/" + self.branch_name +
                                               "/" + self.Sitename + "/" +
                                               self.tmpl_val.get('userpagebase', 'userpagebase.html'))
        path = os.path.join(os.getcwd(), 'templates', 'sendmsg.html')
        return render_template('sendmsg.html', **self.tmpl_val)

    def options(self):
        """Handle CORS preflight requests"""
        response = Response()
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Headers'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        return response

    def _send_mail(self, email, subject):
        """Send email using SMTP (migration from Mail API)"""
        msgbody = ''
        # Build message body from request parameters
        for key, value in request.form.items():
            msgbody += key + " : " + value + "\n"

        # Create EmailMessage (Python 3.11 standard library)
        message = EmailMessage()
        message['From'] = f'登録報告 <{config.ADMIN_EMAIL}>'
        message['To'] = email
        message['Subject'] = subject
        message.set_content(msgbody + "\n" + self.dumpdata())

        # SMTP設定をSecret Managerから取得
        smtp_config = get_smtp_config()

        # SSL/TLS接続（ポート465）で送信
        try:
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(smtp_config['server'], smtp_config['port'], context=context) as server:
                server.login(smtp_config['user'], smtp_config['password'])
                server.send_message(message)
                logging.info("Email sent successfully to %s", email)
        except Exception as e:
            logging.error("Failed to send email: %s", str(e))
            raise
