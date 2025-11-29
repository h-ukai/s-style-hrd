#!/usr/local/bin/python
# -*- coding: utf-8 -*-

"""
message = mail.EmailMessage(sender="support@example.com",
                            subject="Your account has been approved")

message.to = "Albert Johnson <Albert.Johnson@example.com>"
message.body = ""

Dear Albert:

Your example.com account has been approved.  You can now visit
https://www.example.com/ and sign in using your Google Account to
access new features.

Please let us know if you have any questions.

The example.com Team
""

message.send()
"""
#from google.appengine.ext import webapp
import webapp2
from google.appengine.ext.webapp import template
from google.appengine.ext import db
from google.appengine.api import mail
import session
import os
import config
import messageManager
from models.member import member
from wordstocker import wordstocker

ADMIN_EMAIL = config.ADMIN_EMAIL


class mailinglist(webapp2.RequestHandler):

    def get(self,**kwargs):
        self.post()

    def post(self,**kwargs):
        self.tmpl_val = {}
        ssn = session.Session(self.request, self.response,"s-style")
        self.tmpl_val['error_msg'] = ''
        if not ssn.chk_ssn():
            query = member.all()
            query.filter('CorpOrg_key_name = ', 's-style')
            query.filter('memberID = ', 'president')
            user = query.fetch(1)[0]
            self.auth = True
            ssn = session.Session(self.request, self.response,"s-style")
            sid = ssn.new_ssn()
            """                       
            regex = re.compile('^.{2}')
            lang = regex.match(os.environ['HTTP_ACCEPT_LANGUAGE']).group()
            """  
            ssn.set_ssn_data('CorpOrg_key_name', user.CorpOrg_key_name)
            ssn.set_ssn_data('Branch_Key_name', user.Branch_Key_name)
            ssn.set_ssn_data('sitename',user.sitename)
            ssn.set_ssn_data('memberID',user.memberID)
            ssn.set_ssn_data('name', user.name)
            ssn.set_ssn_data('status',user.status)
            ssn.set_ssn_data('phone',user.phone)
            ssn.set_ssn_data('mobilephone',user.mobilephone)
            ssn.set_ssn_data('mail',user.mail)
            ssn.set_ssn_data('userkey',str(user.key()))
            #ssn.set_ssn_data('user',user)
            
            #self.redirect('/login?togo=' + self.request.path)
            #return
        CorpOrg_key_name=ssn.get_ssn_data('CorpOrg_key_name')
        Branch_Key_name=ssn.get_ssn_data('Branch_Key_name')
        sitename=ssn.get_ssn_data('sitename')
        memberID=ssn.get_ssn_data('memberID')
        name=ssn.get_ssn_data('name')
        status=ssn.get_ssn_data('status')
        phone=ssn.get_ssn_data('phone')
        mobilephone=ssn.get_ssn_data('mobilephone')
        usermail=ssn.get_ssn_data('mail')
        userkey=ssn.get_ssn_data('userkey')
        """
        status
        u"管理者",u"業者",u"建築業者",u"紹介者",u"顧客",u"担当",u"その他"
        seiyaku
        u"未成約",u"成約",u"契予",u"決予",u"辞退",u"休止",u"ブラック",u"仮",u"その他"
        """
        msg=None
        if self.request.get("msgkey"):
            self.tmpl_val['msgkey']=self.request.get("msgkey")
            msg = db.get(self.tmpl_val['msgkey'])
            self.tmpl_val['subject'] = msg.subject
            self.tmpl_val['body'] = msg.body
        if self.request.get("subject"):
            self.tmpl_val['subject'] = self.request.get("subject")
        if self.request.get("body"):
            self.tmpl_val['body'] = self.request.get("body")
            
        self.tmpl_val['status'] = self.request.get("status")
        self.tmpl_val['seiyaku'] = self.request.get("seiyaku")
        self.tmpl_val['service'] = self.request.get("service")

        self.tmpl_val['servicelist'] = wordstocker.get(CorpOrg_key_name, u"サービス")

        submit = self.request.get("com")
        if submit == u"メール保存":
            msgkey = messageManager.messageManager.post(self.tmpl_val['subject'], self.tmpl_val['body'], db.Key(userkey), "メーリングリスト", "所有", msg)
        if submit == u"メール送信":
            if not self.tmpl_val['subject']:
                self.tmpl_val['error_msg'] += u"表題がありません　　"
            if not self.tmpl_val['body']:
                self.tmpl_val['error_msg'] += u"本文がありません"
            if self.tmpl_val['error_msg']=="":
                msgkey = messageManager.messageManager.post(self.tmpl_val['subject'], u"送信済み：\n" + self.tmpl_val['body'], db.Key(userkey), u"メーリングリスト", u"送信")
                self.tmpl_val['msgkey'] = msgkey
                """
                sender
                                送信者（From アドレス）のメール アドレス。これはアプリケーションに登録された管理者のメール アドレス、またはログイン中のユーザーのアドレスです。アプリケーションに管理者を追加するには管理コンソールを使用します。現在のユーザーのメール アドレスは、Users API を使用して指定します。
                to
                                メッセージ ヘッダーの To: 行に表示される、受信者のメール アドレス（文字列）。
                cc
                                メッセージ ヘッダーの Cc: 行に表示される、受信者のメール アドレス（文字列）。
                bcc
                                メッセージ ヘッダーに表示されない（「ブラインド カーボン コピー」）、メッセージ受信者のメール アドレス（文字列）。
                reply_to
                                受信者が返信する宛先のメール アドレス（sender アドレスではない）、Reply-To: フィールド。
                subject
                                メッセージの件名、Subject: 行。
                body
                                プレーンテキスト形式によるメッセージの本文。
                html
                HTML メールを好む受信者に対応した、HTML 形式の本文。
                attachments
                                メ ッセージの添付ファイル（2 値のタプルのリスト、1 つの添付ファイルに 1 つのタプル）。各タプルの最初の要素はファイル名、もう 1 つの要素はファイル コンテンツです。
                                添付ファイルは使用できるファイル形式とし、ファイル名の末尾にはファイル形式に対応した拡張子を付けます。使用できるファイル形式とファイル名の拡張子については、概要: 添付ファイルをご覧ください。
                """
                gqlstr = u"SELECT * FROM member"
                where = ""
                service = self.request.get("service")
                if service:
                    where += u" WHERE" if where == u"" else u" AND"
                    where += u" service = '" + service + u"'"
                status = self.request.get("status")
                if status:
                    where += u" WHERE" if where == u"" else u" AND"
                    where += u" status = '" + status + u"'"
                seiyaku = self.request.get("seiyaku")
                if seiyaku:
                    where += u" WHERE" if where == u"" else u" AND"
                    where += u" seiyaku = '" + seiyaku + u"'"
                where += u" WHERE" if where == u"" else u" AND"
                where += u" CorpOrg_key_name = '" + CorpOrg_key_name + u"'"
                if gqlstr!= '':
                    gqlstr += where
                    entitys = db.GqlQuery(gqlstr)
                    if entitys:
                        message = mail.EmailMessage()
                        message.sender = '"' + name + '" <' + ADMIN_EMAIL + '>'
                        message.reply_to = usermail
                        message.subject = self.tmpl_val['subject']
                        message.body = self.tmpl_val['body']
                        for mem in entitys:
                            if mem.mail:
                                message.to = mem.mail
                                message.send()
                                messageManager.messageManager.combination(msgkey ,CorpOrg_key_name, mem.key(), u"受信")

        msglist = messageManager.messageManager.getmeslist(corp = CorpOrg_key_name,member = member.get(userkey), kindname = u"メーリングリスト",order='-reservation')
        self.tmpl_val['msglist'] = msglist
        path = os.path.dirname(__file__) + '/../templates/mailinglist.html'
        self.response.out.write(template.render(path, self.tmpl_val))
        