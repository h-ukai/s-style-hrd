# -*- coding: utf-8 -*-

import logging
from google.appengine.ext.webapp.mail_handlers import InboundMailHandler
from application.email_decoder import email_decoder
from application.messageManager import messageManager
from application.models.member import member
"""
https://d.hatena.ne.jp/furyu-tei/20110518/1305644910

# MIMEエンコードされたメールを読み込んでデコード処理を行い、mailオブジェクトを作成
mail = email_decoder(mime_encoded_mail_text)

# タイトル(Subject)表示
print mail.subject

# 本文(text/plain)表示
print mail.get_body_plain()

# 本文(text/html)表示
print mail.get_body_html()

# To 表示(1)
print u'To: %s' % (mail.to)

# To 表示(2)
to_list = mail.listaddr('to',address_only=False)
print u'To: %s' % (u', '.join([u'%s <%s>' % (_n if _n else _a,_a) for (_n, _a) in to_list]))
""" 
 
class MailHandler(InboundMailHandler):
  def post(self):
    mail = email_decoder(self.request.body)
    subject = mail.subject
    plaintext = mail.get_body_plain()
    to_list = mail.listaddr('to',address_only=False)
    to = u'To: %s' % (u', '.join([u'%s <%s>' % (_n if _n else _a,_a) for (_n, _a) in to_list]))
    from_list = mail.listaddr('from',address_only=False)
    mailfrom = u'From: %s' % (u', '.join([u'%s <%s>' % (_n if _n else _a,_a) for (_n, _a) in from_list]))
    body = plaintext + u'\n' + mailfrom + u'\n' + to 
    userstr = mail.to.split('@')[0]
    user = userstr.split('_')
    if len(user)> 1:
        corp = user[0]
        userID = user[1]
    else:
        corp = 's-style'
        userID = 'test222'
    logging.info(u'mail receiver Subject: ' + mail.subject)
    logging.info(u'mail receiver to: ' + corp + " and " + userID)

    key_name = corp + "/" + userID
    memdb = member.get_by_key_name(key_name)
    memto = None
    if memdb:
        memto = memdb.tanto.memberID
    #post(                    corp,sub,         body,                 done,memfrom,kindname,  combkind=u"所有",msgkey=None,reservation=None,reservationend=None,memto=None,commentto=None,mailto=None,htmlmail=None)

    mes = messageManager.post(corp,subject,body,False,userID,u"メール受信",combkind=u"所有",msgkey=None,reservation=None,reservationend=None,memto=memto,commentto=None,mailto="tanto",htmlmail=None)
