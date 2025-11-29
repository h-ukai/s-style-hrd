#!/usr/local/bin/python
# -*- coding: utf-8 -*-
#
"""Another login utility sample on Google App Engine : Regist

Author    : OKAZAKI Hiroki (okaz@teshigoto.net, https://www.teshigoto.net/)
Version   : $Id: regist.py,v 1.7 2009/02/05 02:11:48 okaz Exp $
Copyright : Copyright (c) 2009 OKAZAKI Hiroki
License   : Python
https://teshigoto.net/junklogs/?p=382
"""


import os
import urllib
import types

#from google.appengine.ext import webapp
import webapp2
from google.appengine.ext.webapp import template
from google.appengine.ext import db
from google.appengine.api import mail
import logging
import sys

import config
from SecurePageBase import SecurePageBase

ADMIN_EMAIL = config.ADMIN_EMAIL

class Sendmsg(SecurePageBase):

    def __init__(self,request, response):
        self.initialize(request, response)
        self.tmpl_val = {}
        self.tmpl_val['error_msg'] = ''
        self.tmpl_val['completed_msg'] = ''

    def get(self,**kwargs):
        self.post(**kwargs)

    def post(self,**kwargs):
        self.Secure_init(**kwargs)

        try:
            referer = self.response.headers['Referer']
        except:
            referer = ''

        try:
            origin = self.response.headers['Origin']
        except:
            origin = ''
        # この方法でOriginやRefererが取れるので
        # 必要に応じてチェック処理などを入れるといいのでは。
        # ちなみにtry〜exceptを使わないと、存在しない場合Key Errorが発生しますよ

        # これはあちこちのサイトでよく言われている処理
        self.response.headers['Access-Control-Allow-Origin'] = '*'
        # IE8は、これがないとうまく動きませんでした。
        self.response.headers['Access-Control-Allow-Headers'] = '*'
        # GET/POSTなど、必要に応じて許可するメソッドを指定します。
        # POSTの場合はOPTIONSも指定する必要があります。
        self.response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        #self.response.headers['Content-Type'] = 'text/plain;charset=UTF-8'

        self.tmpl_val['reqnum'] = self.request.get('reqnum')
        self.tmpl_val['reqtext'] = self.request.get('reqtext')
        self.tmpl_val['ref'] = self.request.get('ref')
        self.tmpl_val['togo'] = self.request.get('togo')
#        self.tmpl_val['userpagebase'] = self.request.get('userpagebase','userpagebase.html')
        if self.auth:
            self.tmpl_val['sid'] = self.request.get('sid')
            new_regist = self.request.get('new_regist')
            if new_regist:
                self.postmsg("ＨＰ問い合わせ",self.tmpl_val['reqnum']+" 内容:"+self.tmpl_val['reqtext'],False,"問い合わせ",'each',self.tmpl_val['reqnum'])
                user_email = config.EMAIL_RECEIVER
                self._send_mail(user_email,u"物件のお問い合わせをいただきました")
                self.tmpl_val['completed_msg'] = u'送信しました'
        else:
            urlstr = "corp_name=" + self.corp_name
            urlstr = urlstr + "&branch_name=" + self.branch_name
            urlstr = urlstr + "&sitename=" + self.Sitename
            if self.tmpl_val['ref']:
                urlstr += "&ref=" + self.tmpl_val['ref']
            if self.tmpl_val['userpagebase']:
                urlstr += "&userpagebase=" + self.tmpl_val['userpagebase']

            if self.tmpl_val['togo']:
                try:
                    togo = urllib.unquote_plus(self.tmpl_val['togo'])
                    if type(togo) is types.UnicodeType:
                        self.tmpl_val['togo'] =  urllib.quote_plus(togo.encode("utf-8"))
                    else:
                        self.tmpl_val['togo'] = urllib.quote_plus(togo)
                except:
                    logging.error('regist_urllib_plusError:' + sys.exc_info()[0] + ' togo:' + togo)
                urlstr += "&togo=" + self.tmpl_val['togo']

            if self.tmpl_val['reqnum']:
                try:
                    reqnum = urllib.unquote_plus(self.tmpl_val['reqnum'])
                    if type(reqnum) is types.UnicodeType:
                        self.tmpl_val['reqnum'] =  urllib.quote_plus(reqnum.encode("utf-8"))
                    else:
                        self.tmpl_val['reqnum'] = urllib.quote_plus(reqnum)
                except:
                    logging.error('regist_urllib_plusError:' + sys.exc_info()[0] + ' reqnum:' + reqnum)
                urlstr += "&reqnum=" + self.tmpl_val['reqnum']

            if self.tmpl_val['reqtext']:
                try:
                    reqtext = urllib.unquote_plus(self.tmpl_val['reqtext'])
                    if type(reqtext) is types.UnicodeType:
                        self.tmpl_val['reqtext'] =  urllib.quote_plus(reqtext.encode("utf-8"))
                    else:
                        self.tmpl_val['reqtext'] = urllib.quote_plus(reqtext)
                except:
                    logging.error('regist_urllib_plusError:' + sys.exc_info()[0] + ' reqnum:' + reqnum)
                urlstr += "&reqtext=" + self.tmpl_val['reqtext']
#           ssn.set_ssn_data("togo", urllib.quote_plus(self.request.path))
            self.redirect(str('/regist?' + urlstr))

        self.tmpl_val["applicationpagebase"] = self.corp_name + u"/" + self.branch_name + u"/" + self.Sitename + u"/" + self.tmpl_val['userpagebase']
        path = os.path.join( os.getcwd(),'templates','sendmsg.html')
        #path = os.path.dirname(__file__) + '/templates/regist.html'
        self.response.out.write(template.render(path, self.tmpl_val))

    def options(self):
        # 何らかの処理を行う
        # POSTの場合は、このoptionsも指定して下さい。
        self.response.headers['Access-Control-Allow-Origin'] = '*'
        self.response.headers['Access-Control-Allow-Headers'] = '*'
        self.response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'

    def _send_mail(self, email,subject):
        msgbody = ''
        for n,v in self.request.POST.multi._items:
            msgbody += n + " : " + v + "\n"
        """
        for key in self.request.arguments():
            msgbody += key + " : " + self.request.get(key) + "\n"
        """
        message = mail.EmailMessage()
        message.sender = '"登録報告" <' + config.ADMIN_EMAIL + '>'
        message.to = email
        message.subject = subject
        message.body = msgbody + "\n" + self.dumpdata()
        message.send()


