#!/usr/local/bin/python
# -*- coding: utf-8 -*-
#

import datetime
import hashlib
import re
import os
import urllib
import sys

from models.member import member
from models.CorpOrg import CorpOrg
from models.Branch import Branch
import session
from chkauth import dbsession
#from google.appengine.ext import webapp
import webapp2
from google.appengine.ext.webapp import template
import types
import logging

class Login(webapp2.RequestHandler):

    def __init__(self,request, response):
        self.initialize(request, response)
        self.tmpl_val = {}
        self.tmpl_val['error_msg'] = ''
        self.auth = False

    def get(self):
        self.post()

    def post(self):
        #
        # get data from <form> stream
        #
        #/login?corp_name=s-style&branch_name=hon&sitename=www.chikusaku.mansion.com
        get_login_id = self.request.get('login_id')
        get_login_pwd = self.request.get('login_pwd')
        get_login_submit = self.request.get('login_submit')
        get_logoff = self.request.get('logoff')
        get_login_togo = self.request.get('togo')
        get_login_style = self.request.get('style')
        self.tmpl_val['style'] = get_login_style
        self.tmpl_val['corp_name'] = self.request.get('corp_name')
        self.tmpl_val['branch_name'] = self.request.get('branch_name')
        self.tmpl_val['sitename'] = self.request.get('sitename')
        self.tmpl_val['togo'] = ''
        self.tmpl_val['userpagebase'] = self.request.get('userpagebase','userpagebase.html')
        if get_login_togo:
            try:
                togo = urllib.unquote_plus(get_login_togo)
                if type(togo) is types.UnicodeType:
                    self.tmpl_val['togo'] = urllib.quote_plus(togo.encode("utf-8"))
                else:
                    self.tmpl_val['togo'] = urllib.quote_plus(togo)
            except:
                logging.error('login_urllib_plusError:' + sys.exc_info()[0] + ' togo:' + togo)
        #self.tmpl_val['togo'] = urllib.unquote_plus(get_login_togo)
        self.tmpl_val["query_string"] = 'corp_name=' + self.tmpl_val['corp_name'] + '&branch_name=' + self.tmpl_val['branch_name'] + '&sitename=' + self.tmpl_val['sitename'] + '&togo=' + self.tmpl_val['togo'] + '&userpagebase=' + self.tmpl_val['userpagebase']
        self.tmpl_val["applicationpagebase"]= self.tmpl_val['corp_name'] + u"/" + self.tmpl_val['branch_name'] + u"/" + self.tmpl_val['sitename'] + u"/" + self.tmpl_val['userpagebase']
        regx = re.compile(r'^[\s]*(.*?)[\s]*$')#スペースを含んでいないことをチェック
        get_login_id = regx.match(get_login_id).group(1)
        if get_logoff=="true":
            ssn = dbsession(self.request, self.response,self.tmpl_val['corp_name'] + "_" + self.tmpl_val['branch_name'] + "_" + self.tmpl_val['sitename'])
            #ssn = session.Session(self.request, self.response,self.tmpl_val['corp_name'] + "_" + self.tmpl_val['branch_name'] + "_" + self.tmpl_val['sitename'])
            ssn.destroy_ssn()
            self.tmpl_val['completed_msg'] = u'ログアウトしました'

        #
        # command processing
        #
        if get_login_submit:
            hashed_pwd = hashlib.sha256(get_login_pwd).hexdigest()
            query = member.all()
            query.filter('CorpOrg_key_name = ', self.tmpl_val['corp_name'])
            query.filter('sitename = ', self.tmpl_val['sitename'])
            query.filter('netID = ', get_login_id)
            query.filter('netPass = ', get_login_pwd)
            query.filter('seiyaku = ', u"未成約")
            count = 0
            for u in query:
                count += 1
                user = u
            if count != 1:
                self.tmpl_val['error_msg'] = u'IDかパスワードが見つかりません'
            else:
                corp = CorpOrg.get_by_key_name(user.CorpOrg_key_name)
                if corp.active:
                    ssn = dbsession(self.request, self.response,self.tmpl_val['corp_name'] + "_" + self.tmpl_val['branch_name'] + "_" + self.tmpl_val['sitename'],user.sid)
                    ssn.new_ssn()
                    user.sid = ssn.getsid()
                    user.put()
                    self.auth = True
                    self.tmpl_val['auth'] = True
                    self.tmpl_val['sid'] = ssn.sid_value
                    #sid = ssn.new_ssn()
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
                    if get_login_togo:
                        self.tmpl_val['onloadsclipt'] = u"location.replace('"+ urllib.unquote_plus(get_login_togo) + u"')"
                        self.tmpl_val['completed_msg'] = u'ログインに成功しました　<br /> <a href="'  + urllib.unquote_plus(get_login_togo) + '"> しばらく待って移動しない場合はココをクリックしてください。</a>'
                    else:
                        self.tmpl_val['onloadsclipt'] = u"location.replace('https://"+ user.sitename + u"')"
                        self.tmpl_val['completed_msg'] = u'ログインに成功しました　<br /> <a href="https://'  + user.sitename + '"> しばらく待って移動しない場合はココをクリックしてください。</a>'

                else:
                    self.tmpl_val['error_msg'] = u'サービスが無効となっています　管理者におたずねください'


        #
        # view rendering
        #
        #if get_login_submit and self.auth and get_login_togo:
        #    self.redirect(urllib.unquote_plus(get_login_togo))
        #else:
        if get_login_style: #ログインテンプレートを動的に変更する場合
            path = os.path.join( os.getcwd(),'templates',get_login_style + '.html')
            self.response.out.write(template.render(path, self.tmpl_val))
        else:
            path = os.path.join( os.getcwd(),'templates','login.html')
            self.response.out.write(template.render(path, self.tmpl_val))



class Logout(webapp2.RequestHandler):
    def get(self):
        self.post()

    def post(self):
        ssn = session.Session(self.request, self.response)
        sid = ssn.destroy_ssn()
        """
        logs = users.Logs.all()
        logs.filter('sid = ', sid)
        log = logs.fetch(1)
        log[0].logout = datetime.datetime.now()
        log[0].put()
        """
        self.redirect('/')
