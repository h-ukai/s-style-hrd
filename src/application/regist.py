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
import re
import gettext
import hashlib
import base64
import urllib
import types

import cs   # https://pythonscripts.net/ciphersaber-in-python-download-610.html

import config
import users
import view

#from google.appengine.ext import webapp
import webapp2
from google.appengine.ext.webapp import template
from google.appengine.ext import db
from google.appengine.api import mail

from models.member import member
from models.CorpOrg import CorpOrg
from models.Branch import Branch
from messageManager import messageManager
from bklistutl import bklistutl
import session
import logging
import sys


from google.appengine.api import urlfetch
from application.lib import json

CIPHER_KEY = 'pHa5UO3c1SvyL46' # for _key_encode, _key_decode
PASSWORD_MAX_LENGTH = 3

#BASE_URL = config.BASE_URL
ADMIN_EMAIL = config.ADMIN_EMAIL

class Regist(webapp2.RequestHandler):

    def __init__(self,request, response):
        self.initialize(request, response)
        self.tmpl_val = {}
        self.tmpl_val['error_msg'] = ''
        self.tmpl_val['completed_msg'] = ''

    def get(self):
        self.post()

    def post(self):

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

        #
        # get data from <form> stream
        #
        get_new_regist = self.request.get('new_regist')
        #logging.error('new_regist：：' + get_new_regist)
        get_new_login_id = self.request.get('new_login_id')
        get_new_login_pwd = self.request.get('new_login_pwd')
        get_new_user_email = self.request.get('new_user_email')

        get_new_recaptcha_response = self.request.get('g-recaptcha-response')

        self.tmpl_val['corp_name'] = self.request.get('corp_name')
        self.tmpl_val['branch_name'] = self.request.get('branch_name')
        self.tmpl_val['sitename'] = self.request.get('sitename')
        self.tmpl_val['sid'] = self.request.get('sid')
        self.tmpl_val['ref'] = self.request.get('ref')
        self.tmpl_val['togo'] = ''
        self.tmpl_val['userpagebase'] = self.request.get('userpagebase','userpagebase.html')

        self.tmpl_val['sitekey'] = '6LfRxU4aAAAAAD6BDE23lHzfDy3OX2h8qqV-bH2Q'
        
        togo = self.request.get('togo')
        if togo:
            try:
                togo = urllib.unquote_plus(togo)
                if type(togo) is types.UnicodeType:
                    togo = urllib.quote_plus(togo.encode("utf-8"))
                else:
                    togo = urllib.quote_plus(togo)
                self.tmpl_val['togo'] = togo
            except:
                logging.error('regist_urllib_plusError:' + sys.exc_info()[0] + ' togo:' + togo)
        reqnum = self.request.get('reqnum')
        if reqnum:
            try:
                reqnum = urllib.unquote_plus(reqnum)
                self.tmpl_val['reqnum'] = reqnum
                if type(reqnum) is types.UnicodeType:
                    reqnum = urllib.quote_plus(reqnum.encode("utf-8"))
                else:
                    reqnum = urllib.quote_plus(reqnum)
            except:
                logging.error('regist_urllib_plusError:' + sys.exc_info()[0] + ' reqnum:' + self.tmpl_val['reqnum'])
        reqtext = self.request.get('reqtext')
        if reqtext:
            try:
                reqtext = urllib.unquote_plus(reqtext)
                self.tmpl_val['reqtext'] = reqtext
                if type(reqtext) is types.UnicodeType:
                    reqtext = urllib.quote_plus(reqtext.encode("utf-8"))
                else:
                    reqtext = urllib.quote_plus(reqtext)
            except:
                logging.error('regist_urllib_plusError:' + sys.exc_info()[0] + ' reqtext:' + self.tmpl_val['reqtext'])

        self.tmpl_val["applicationpagebase"]= self.tmpl_val['corp_name'] + u"/" + self.tmpl_val['branch_name'] + u"/" + self.tmpl_val['sitename'] + u"/" + self.tmpl_val['userpagebase']

        regx = re.compile(r'^[\s]*(.*?)[\s]*$') #スペースを含んでいないことをチェック
        get_new_login_id = regx.match(get_new_login_id).group(1)
        get_new_user_email = regx.match(get_new_user_email).group(1)

        #
        # command processing
        #
        if get_new_regist:
            """
            意味不明コード 2021/02/11置換
            if not get_new_login_pwd:
                get_new_login_pwd = get_new_user_email
            """
            if not get_new_login_id:
                self.tmpl_val['error_msg'] = 'ご希望のIDが無効です'
            elif len(get_new_login_pwd) < PASSWORD_MAX_LENGTH and len(get_new_login_pwd) > 0:
                # password length check
                self.tmpl_val['error_msg'] = 'パスワードが短かすぎます（４文字以上）'
            elif not mail.is_email_valid(get_new_user_email):
                # email valid check
                self.tmpl_val['error_msg'] = 'メールアドレスに間違いがあります'

            elif get_new_recaptcha_response:
                recaptcha_secret_key = '6LfRxU4aAAAAAB-Dk4Hj0knERSxCPDmStgE24xyD'
                # reCAPTCHA認証
                """
                {
                    "success": true,
                    "challenge_ts": "2020-03-21T04:53:48Z",
                    "hostname": "webdesignleaves.localhost",
                    "score": 0.9,  //スコア
                    "action": "contact"  // アクション名
                    }
                """
                recaptcha_url = 'https://www.google.com/recaptcha/api/siteverify'
                form_fields = {
                    'secret': recaptcha_secret_key,  # app.yaml に記述した環境変数から取得
                    'response': get_new_recaptcha_response,
                    'remoteip': self.request.remote_addr,
                }
        
                form_data = urllib.urlencode(form_fields)
                response = urlfetch.fetch(
                    url=recaptcha_url,
                    payload=form_data,
                    method=urlfetch.POST,
                )
                if response.status_code == 200:
                    json_data = response.content
                    decode_json_data = json.loads(json_data)
                    if decode_json_data['success']:
                        if decode_json_data['score']>0.5:
                            msg1 = 'reCAPTCHA成功::' + ' success::' + str(decode_json_data['success']) + ' challenge_ts::' + str(decode_json_data['challenge_ts']) + ' hostname::' + str(decode_json_data['hostname']) + ' score::' + str(decode_json_data['score']) + ' action::' + str(decode_json_data['action'])
                            logging.error('regist_reCAPTCHA_success:' + msg1)
                        else:
                            self.tmpl_val['error_msg'] = '機械操作が検出されました::' + ' success::' + str(decode_json_data['success']) + ' challenge_ts::' + str(decode_json_data['challenge_ts']) + ' hostname::' + str(decode_json_data['hostname']) + ' score::' + str(decode_json_data['score']) + ' action::' + str(decode_json_data['action'])
                            logging.error('regist_reCAPTCHA_Error:' + self.tmpl_val['error_msg'])
                    else:
                        self.tmpl_val['error_msg'] = '機械操作が検出されました::not reCAPTCHA sucsess'
                        logging.error('regist_reCAPTCHA_Error:' + self.tmpl_val['error_msg'])
                else:
                    self.tmpl_val['error_msg'] = '機械操作の検出に失敗しました:：status_code error'
                    logging.error('regist_reCAPTCHA_Error:' + self.tmpl_val['error_msg'])
            elif not get_new_recaptcha_response:
                self.tmpl_val['error_msg'] = '機械操作が検出されました::No reCAPTCHA ' 
                logging.error('No_reCAPTCHA_Error:' + self.tmpl_val['error_msg'])

            if self.tmpl_val['error_msg']:
                pass
            else:
                # anyway, new data puts in DataStore once
                #hashed_pwd = hashlib.sha256(get_new_login_pwd).hexdigest()
                co = CorpOrg.get_or_insert(self.tmpl_val['corp_name'])
                memberID = str(co.getNextIDNum())
                key_name = self.tmpl_val['corp_name'] + "/" + memberID
                memdb = member.get_or_insert(key_name)
                memdb.memberID = memberID
                memdb.status = u"顧客"
                memdb.netID = get_new_login_id
                memdb.CorpOrg_key_name = self.tmpl_val['corp_name']
                memdb.Branch_Key_name = self.tmpl_val['branch_name']
                memdb.sitename = self.tmpl_val['sitename']
                memdb.netPass = get_new_login_pwd  #hached_pwdとりあえず使わない
                memdb.mail = get_new_user_email
                memdb.seiyaku = u"仮"
                # テキストベースの担当KEYを使わないバージョン
                # tanto = member.get_or_insert(self.tmpl_val['corp_name'] + "/" + config.TANTOID)
                # memdb.tanto = tanto
                memdb.tanto = db.Key(config.TANTO)
                memdb.sid = self.tmpl_val['sid']
                memdb.put()

                # It gives it up when there are the same tow id or more.
                query = member.all()
                query.filter('netID =', get_new_login_id)  #hached_pwdとりあえず使わない
                query.filter('CorpOrg_key_name =', self.tmpl_val['corp_name'])
                query.filter('sitename =', self.tmpl_val['sitename'])
                count = 0
                for user in query:
                    count += 1

                if count == 1:
                    res = self._send_confirm(get_new_login_id,
                                       get_new_user_email,
                                       memdb.key(),
                                       self.tmpl_val['corp_name'],
                                       self.tmpl_val['branch_name'],
                                       self.tmpl_val['sitename'],
                                       self.tmpl_val['togo'],
                                       reqnum,
                                       reqtext,
                                       self.tmpl_val['userpagebase']
                                       )
                    ###デバッグ用
                    #self.response.out.write(res)
                    ###
                    self.tmpl_val['completed_msg'] = 'ご登録のメールアドレスに登録用メールが送信されました　ご確認ください \n届かない場合、迷惑メールフォルダをご確認の上、送信アドレスの迷惑メール設定を解除してください'
                    logging.error('completed_msg::' + self.tmpl_val['completed_msg'])
                    #
                    #仮登録を知らせるメールは一時オミットする
                    #  2019/04/08
                    #
                    #user_email = 's-style.s8@nifty.com;warao.shikyo@gmail.com;fuminori.yokoyama@gmail.com'
                    #self._send_mail(user_email,u"仮登録されました")
                    body =  u"物件番号 : " + reqnum + u"  リクエスト: " + self.request.get('reqtext')
                    meskey = messageManager.post(self.tmpl_val['corp_name'],u"新規登録リクエスト",body,False,memberID,u"問い合わせ",combkind=u"所有")
                    if reqnum:
                        bklistutl.addlistbyID(self.tmpl_val['corp_name'],self.tmpl_val['branch_name'],reqnum,str(meskey.id()))
                else:
                    memdb.delete()
                    self.tmpl_val['error_msg'] = 'ご希望のIDがすでに使われています'
                    logging.error('regist_Error_msg::' + self.tmpl_val['error_msg'])
        else:
            logging.error('get_new_regist_error::' + get_new_regist)

        if self.tmpl_val['error_msg']:
            self.tmpl_val['new_login_id_value'] = get_new_login_id
            self.tmpl_val['new_user_email_value'] = get_new_user_email

        path = os.path.join( os.getcwd(),'templates','regist.html')
        #path = os.path.dirname(__file__) + '/templates/regist.html'
        self.response.out.write(template.render(path, self.tmpl_val))

    def _send_confirm(self, id, email, key, corp, branch, site, togo, reqnum, reqtext,userpagebase='userpagebase.html'):
        #accept_lang = os.environ['HTTP_ACCEPT_LANGUAGE']
        #lang = re.compile('^.{2}').match(accept_lang).group()

        BASE_URL = self.request.url.partition(u'://')[0] + self.request.url.partition(u'://')[1] + self.request.url.partition(u'://')[2].partition(u'/')[0]
        """
        lang = 'en'
        locale_path = os.path.dirname(__file__) + '/locale'
        rs = gettext.translation('resource', locale_path, languages=[lang])
        rs.install()
        _ = rs.gettext
        """
        confirm_key = self._key_encode(key)
        confirm_key = urllib.quote_plus(confirm_key)
        confirm_url = BASE_URL + '/confirm?ck=' + confirm_key + '&corp_name=' + corp + '&branch_name=' + branch + '&sitename=' + site
        if togo:
            confirm_url += '&togo=' + togo
        if reqnum:
            confirm_url += '&reqnum=' + reqnum
        if reqtext:
            confirm_url += '&reqtext=' + reqtext
        if userpagebase:
            confirm_url += '&userpagebase=' + userpagebase


        message = mail.EmailMessage()

        message.sender = '"' + site + ' 登録情報送信用" <' + ADMIN_EMAIL + '>'
        message.to = email
        message.subject = u'ご登録のリクエストを受付ました'
        message.body = u'このたびは' + site + u'にお申し込みいただきありがとうございます。' + "\n"
        message.body = u'このアドレスにアクセスしてユーザー登録を完了させてください。' + "\n\n"
        message.body += confirm_url
        message.send()
        logging.error('message.send::' + message.body)


        return confirm_url

    def _key_encode(self, p_text):
        #
        # encoder for data object
        #
        cipher_text = cs.cipher(str(p_text), CIPHER_KEY, True)
        cipher_text = base64.urlsafe_b64encode(cipher_text)
        return cipher_text

    def options(self):
        # 何らかの処理を行う
        # POSTの場合は、このoptionsも指定して下さい。
        self.response.headers['Access-Control-Allow-Origin'] = '*'
        self.response.headers['Access-Control-Allow-Headers'] = '*'
        self.response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'

    def _send_mail(self, email,subject):
        msgbody = ''
        if self.request.POST.multi._items:
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
        message.body = msgbody
        message.send()


class Confirm(webapp2.RequestHandler):
    def __init__(self,request, response):
        self.initialize(request, response)
        self.tmpl_val = {}
        self.tmpl_val['error_msg'] = ''
        self.tmpl_val['completed_msg'] = ''

    def get(self):
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

        ck = urllib.unquote_plus(self.request.get('ck'))
        key = self._key_decode(ck)
        togo = self.request.get('togo')
        if togo:
            try:
                togo = urllib.unquote_plus(togo)
                if type(togo) is types.UnicodeType:
                    self.tmpl_val['togo'] =  urllib.quote_plus(togo.encode("utf-8"))
                else:
                    self.tmpl_val['togo'] = urllib.quote_plus(togo)
            except:
                logging.error('regist_urllib_plusError:' + sys.exc_info()[0] + ' togo:' + togo)
        reqnum = self.request.get('reqnum')
        if reqnum:
            try:
                reqnum = urllib.unquote_plus(reqnum)
                self.tmpl_val['reqnum'] = reqnum
            except:
                logging.error('regist_urllib_plusError:' + sys.exc_info()[0] + ' reqnum:' + reqnum)
        self.tmpl_val['reqtext'] = ''
        reqtext = self.request.get('reqtext')
        if reqtext:
            try:
                reqtext = urllib.unquote_plus(reqtext)
                self.tmpl_val['reqtext'] = reqtext
            except:
                logging.error('regist_urllib_plusError:' + sys.exc_info()[0] + ' reqtext:' + reqtext)
        #self.tmpl_val['togo'] = urllib.quote_plus(urllib.unquote_plus(self.request.get('togo')))
        self.tmpl_val['corp_name'] = self.request.get('corp_name')
        self.tmpl_val['branch_name'] = self.request.get('branch_name')
        self.tmpl_val['sitename'] = self.request.get('sitename')
        self.tmpl_val['sid'] = self.request.get('sid')
        self.tmpl_val['ref'] = self.request.get('ref')
        self.tmpl_val['userpagebase'] = self.request.get('userpagebase','userpagebase.html')
        self.tmpl_val["applicationpagebase"]= self.tmpl_val['corp_name'] + u"/" + self.tmpl_val['branch_name'] + u"/" + self.tmpl_val['sitename'] + u"/" + self.tmpl_val['userpagebase']

        try:
            account = db.get(key)
        except:
            path = os.path.dirname(__file__) + '/../templates/regist.html'
            self.tmpl_val['error_msg'] = u'仮登録が無効です　登録をやりなおしてください'
        else:
            self.tmpl_val['mail'] = account.mail
            path = os.path.dirname(__file__) + '/../templates/form.html'
            self.tmpl_val['completed_msg'] = u''
            #path = path + "?ck=" + self.request.get('ck')

        #
        # view rendering
        #
        self.response.out.write(template.render(path, self.tmpl_val))

    def post(self):
        ck = urllib.unquote_plus(self.request.get('ck'))
        key = self._key_decode(ck)
        self.tmpl_val['mail'] = self.request.get('mail')
        self.tmpl_val['corp_name'] = self.request.get('corp_name')
        self.tmpl_val['branch_name'] = self.request.get('branch_name')
        self.tmpl_val['sitename'] = self.request.get('sitename')
        self.tmpl_val['userpagebase'] = self.request.get('userpagebase','userpagebase.html')
        togo = self.request.get('togo')
        if togo:
            try:
                togo = urllib.unquote_plus(togo)
                if type(togo) is types.UnicodeType:
                    self.tmpl_val['togo'] =  urllib.quote_plus(togo.encode("utf-8"))
                else:
                    self.tmpl_val['togo'] = urllib.quote_plus(togo)
            except:
                logging.error('regist_urllib_plusError:' + sys.exc_info()[0] + ' togo:' + togo)
        reqnum = self.request.get('reqnum')
        if reqnum:
            try:
                reqnum = urllib.unquote_plus(reqnum)
                self.tmpl_val['reqnum'] = reqnum
            except:
                logging.error('regist_urllib_plusError:' + sys.exc_info()[0] + ' reqnum:' + reqnum)
        self.tmpl_val['reqtext'] = ''
        reqtext = self.request.get('reqtext')
        if reqtext:
            try:
                reqtext = urllib.unquote_plus(reqtext)
                self.tmpl_val['reqtext'] = reqtext
            except:
                logging.error('regist_urllib_plusError:' + sys.exc_info()[0] + ' reqtext:' + reqtext)
        self.tmpl_val['sid'] = self.request.get('sid')
        self.tmpl_val['ref'] = self.request.get('ref')
        self.tmpl_val["applicationpagebase"]= self.tmpl_val['corp_name'] + u"/" + self.tmpl_val['branch_name'] + u"/" + self.tmpl_val['sitename'] + u"/" + self.tmpl_val['userpagebase']

        try:
            account = db.get(key)
        except:
            path = os.path.dirname(__file__) + '/../templates/regist.html'
            self.tmpl_val['error_msg'] = u'仮登録が無効です　登録をやりなおしてください'
        else:
            self.tmpl_val['error_msg'] = ""
            if self.request.get('lastname') and self.request.get('fastname'):
                account.name = self.request.get('lastname') + self.request.get('fastname')
            else:
                path = os.path.dirname(__file__) + '/../templates/form.html'
                if not self.request.get('lastname'):
                    self.tmpl_val['error_msg'] = self.tmpl_val['error_msg'] + u'　"姓"を記入してください'
                if not self.request.get('fastname'):
                    self.tmpl_val['error_msg'] = self.tmpl_val['error_msg'] + u'　"名"を記入してください'

            if self.request.get('yomi1') and self.request.get('yomi2'):
                account.yomi = self.request.get('yomi1') + self.request.get('yomi2')
            else:
                path = os.path.dirname(__file__) + '/../templates/form.html'
                if not self.request.get('yomi1'):
                    self.tmpl_val['error_msg'] = self.tmpl_val['error_msg'] + u'　"姓よみがな"を記入してください'
                if not self.request.get('yomi2'):
                    self.tmpl_val['error_msg'] = self.tmpl_val['error_msg'] + u'　"名よみがな"を記入してください'

            if self.request.get('zip1') and self.request.get('zip2'):
                account.zip = self.request.get('zip1') + self.request.get('zip2')
            else:
                path = os.path.dirname(__file__) + '/../templates/form.html'
                self.tmpl_val['error_msg'] = self.tmpl_val['error_msg'] + u'　"郵便番号"を記入してください'

            if self.request.get('ken') and self.request.get('address1') and self.request.get('address2') and self.request.get('address3'):
                account.address = self.request.get('ken') + self.request.get('address1') + self.request.get('address2') + self.request.get('address3')
                account.address1 = self.request.get('address1')
                account.address2 = self.request.get('address2')
            else:
                path = os.path.dirname(__file__) + '/../templates/form.html'
                if not self.request.get('ken'):
                    self.tmpl_val['error_msg'] = self.tmpl_val['error_msg'] + u'　"都道府県"を記入してください'
                if not self.request.get('address1'):
                    self.tmpl_val['error_msg'] = self.tmpl_val['error_msg'] + u'　"市区町村"を記入してください'
                if not self.request.get('address2'):
                    self.tmpl_val['error_msg'] = self.tmpl_val['error_msg'] + u'　"町字丁目"を記入してください'
                if not self.request.get('address3'):
                    self.tmpl_val['error_msg'] = self.tmpl_val['error_msg'] + u'　"番地、マンション名"を記入してください'
                if not self.request.get('phone'):
                    self.tmpl_val['error_msg'] = self.tmpl_val['error_msg'] + u'　"電話番号"を記入してください'
            if self.request.get('phone'):
                account.phone = self.request.get('phone')

            if self.tmpl_val['error_msg'] == "":
                path = os.path.dirname(__file__) + '/../templates/form.html'
                self.tmpl_val['completed_msg'] = u'登録が完了しました'
                account.seiyaku = u"未成約"
                account.put()
                corp = CorpOrg.get_by_key_name(account.CorpOrg_key_name)
                #branch = Branch.get_by_key_name(account.Branch_key_name)
                branch = account.Branch_Key_name
                user_email = config.EMAIL_RECEIVER
                self._send_mail(user_email,u"本登録が終わりました")
                body =  u"物件番号 : " + reqnum + u"  リクエスト: " + reqtext
                meskey = messageManager.post(self.tmpl_val['corp_name'],u"登録完了",body,False,account.memberID,u"問い合わせ",combkind=u"所有")
                if reqnum:
                    bklistutl.addlistbyID(self.tmpl_val['corp_name'],self.tmpl_val['branch_name'],reqnum,str(meskey.id()))


                if corp.active :
                    self.auth = True
                    ssn = session.Session(self.request, self.response,self.tmpl_val['corp_name'] + "_" + self.tmpl_val['branch_name'] + "_" + self.tmpl_val['sitename'])
                    account.sid = ssn.new_ssn()
                    account.put()
                    ssn.set_ssn_data('CorpOrg_key_name', account.CorpOrg_key_name)
                    ssn.set_ssn_data('Branch_Key_name', account.Branch_Key_name)
                    ssn.set_ssn_data('sitename',account.sitename)
                    ssn.set_ssn_data('memberkey',str(account.key()))
                    ssn.set_ssn_data('memberID',account.memberID)
                    ssn.set_ssn_data('name', account.name)
                    ssn.set_ssn_data('status',account.status)
                    ssn.set_ssn_data('phone',account.phone)
                    ssn.set_ssn_data('mobilephone',account.mobilephone)
                    ssn.set_ssn_data('mail',account.mail)
                    ssn.set_ssn_data('userkey',str(account.key()))
                    message = mail.EmailMessage()
                    message.sender = '"' + account.sitename + ' regist utility" <' + ADMIN_EMAIL + '>'
                    message.to = account.mail
                    message.subject = u'ご登録が完了いたしました'
                    message.body = u'この度はご登録ありがとうございました。' + "\n"
                    message.body = account.name + u'様の夢が早くかないますように' + "\n"
                    message.body = u'スタッフ一同心を込めてお手伝いさせていただきます。' + "\n"
                    message.send()

                    if togo:
                        self.tmpl_val['onloadsclipt'] = u"location.replace('"+ togo + u"')"
                        self.tmpl_val['completed_msg'] = u'本登録が完了しました。このまま自動ログインします。　<br /> <a href="'  + togo + '"> しばらく待って移動しない場合はココをクリックしてください。</a>'

                        #self.redirect(urllib.unquote_plus(togo))
                        #return
                    else:
                        self.tmpl_val['onloadsclipt'] = u"location.replace('https://" + account.sitename + "/')"
                        self.tmpl_val['completed_msg'] = u'本登録が完了しました。このまま自動ログインします。　<br /> <a href=https://"'  + account.sitename + '"> しばらく待って移動しない場合はココをクリックしてください。</a>'
                        #self.redirect('https://' + account.sitename + '/')
                        #return
                else:
                    self.tmpl_val['error_msg'] = u'サービスが無効となっています　管理者におたずねください'
            else:
                self.tmpl_val['lastname'] = self.request.get('lastname')
                self.tmpl_val['fastname'] = self.request.get('fastname')
                self.tmpl_val['yomi1'] = self.request.get('yomi1')
                self.tmpl_val['yomi2'] = self.request.get('yomi2')
                self.tmpl_val['zip1'] = self.request.get('zip1')
                self.tmpl_val['zip2'] = self.request.get('zip2')
                self.tmpl_val['ken'] = self.request.get('ken')
                self.tmpl_val['address1'] = self.request.get('address1')
                self.tmpl_val['address2'] = self.request.get('address2')
                self.tmpl_val['address3'] = self.request.get('address3')
                self.tmpl_val['phone'] = self.request.get('phone')

                #self.tmpl_val['togo'] = urllib.quote_plus(urllib.unquote_plus(self.request.get('togo')))

        #
        # view rendering
        #
        # 何らかの処理を行う
        self.response.headers['Access-Control-Allow-Origin'] = '*'
        self.response.headers['Access-Control-Allow-Headers'] = '*'
        self.response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'

        #self.response.headers['Content-Type'] = 'text/plain;charset=UTF-8'
        self.response.out.write(template.render(path, self.tmpl_val))

    def _key_decode(self, p_text):
        #
        # decoder for data object
        #
        p_text = base64.urlsafe_b64decode(p_text.encode('utf-8'))
        cipher_text = cs.cipher(p_text, CIPHER_KEY, False)
        return cipher_text


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
        message.body = msgbody
        message.send()

class Resign(webapp2.RequestHandler):
    def __init__(self):
        self.tmpl_val = {}
        self.tmpl_val['error_msg'] = ''
        self.tmpl_val['completed_msg'] = ''
        self.tmpl_val['userpagebase'] = self.request.get('userpagebase','userpagebase.html')
        self.tmpl_val["applicationpagebase"]= self.tmpl_val['corp_name'] + u"/" + self.tmpl_val['branch_name'] + u"/" + self.tmpl_val['sitename'] + u"/" + self.tmpl_val['userpagebase']

    def get(self):
        self.post()

    def post(self):
        #
        # get data from <form> stream
        #
        self.response.headers['Access-Control-Allow-Origin'] = '*'
        self.response.headers['Access-Control-Allow-Headers'] = '*'
        self.response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        get_resign = self.request.get('resign')
        get_resign_login_id = self.request.get('resign_login_id')
        get_resign_login_pwd = self.request.get('resign_login_pwd')
        get_resign_user_email = self.request.get('resign_user_email')

        regx = re.compile(r'^[\s]*(.*?)[\s]*$')
        get_resign_login_id = regx.match(get_resign_login_id).group(1)
        get_resign_user_email = regx.match(get_resign_user_email).group(1)

        #
        # command processing
        #
        if get_resign:
            hashed_pwd = hashlib.sha256(get_resign_login_pwd).hexdigest()
            query = member.all()
            query.filter('netID =', get_resign_login_id)
            query.filter('netPass =', get_resign_login_pwd) #hached_pwdとりあえず使わない

            count = 0
            for user in query:
                count += 1

            if count == 1:
                user = query.fetch(1)
                user[0].seiyaku = "辞退"
                user[0].put()
                self.tmpl_val['completed_msg'] = u'登録の解除を終了しました'
            else:
                self.tmpl_val['error_msg'] = u'ログインIDかパスワードが見つかりません'

        if self.tmpl_val['error_msg']:
            self.tmpl_val['resign_login_id_value'] = get_resign_login_id
            self.tmpl_val['resign_user_email_value'] = get_resign_user_email

        #
        # view rendering
        #
        v = view.View(self.response)
        v.render('resign', self.tmpl_val)
