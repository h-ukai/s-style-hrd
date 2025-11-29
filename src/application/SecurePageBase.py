# -*- coding: utf-8 -*-

import os
#from google.appengine.ext import webapp
import webapp2
from models.member import member
from messageManager import messageManager
from bklistutl import bklistutl
import datetime
import timemanager
from chkauth import dbsession

class SecurePageBase(webapp2.RequestHandler):

    def __init__(self,request, response):
        self.initialize(request, response)
        self.tmpl_val = {}
        self.tmpl_val['error_msg'] = ''
        self.auth = False


    def dumpdata(self):
        t = 'dumpdata:\n'
        for e in self.tmpl_val.items():
            t += str(e[0]) + ' : ' + str(e[1]) + '\n'
        return t

    def postmsg(self,sub,body,done,kindname,mailto,bkid=None):
        if self.auth:
            #post(cls,corp,sub,body,done,memfrom,kindname,combkind=u"所有",msgkey=None,reservation=None,reservationend=None,memto=None,commentto=None,mailto=None,htmlmail=None)
            mes = messageManager.post(self.corp_name,sub,body,done,self.userID,kindname,combkind=u"所有",msgkey=None,reservation=None,reservationend=None,memto=None,commentto=None,mailto=mailto,htmlmail=None)
            if bkid:
                #ｂｋid物件番号 refmesIDメッセージID
                bklistutl.addlistbyID(self.corp_name,self.branch_name,bkid,mes.id(),key=None,senddate=None,sended=None,memo=None)
            return mes

    def Secure_init(self,**kwargs):

        self.path = self.request.path
        self.pathParts = self.path.split(u'/')
        self.Domain = self.request.url.split(u'/')[2]
        self.corp_name = self.pathParts[2]
        self.branch_name = self.pathParts[3]
        self.Sitename = self.pathParts[4]


        if len(self.pathParts)>5:
            self.filename = self.pathParts[5]
        else:
            self.filename = None
        self.tmpl_val['Domain']=self.Domain
        self.tmpl_val["CorpOrg_key_name"]=self.corp_name
        self.tmpl_val["Branch_Key_name"]=self.branch_name
        self.tmpl_val["sitename"]=self.Sitename

        self.now = datetime.datetime.now()  # datetime.datetime(2009, 7, 8, 22, 59, 0, 688787)
        self.tmpl_val["now"]=self.now

        self.tmpl_val['userpagebase'] = self.request.get('userpagebase','userpagebase.html')

        """
        ssn = session.Session(self.request, self.response,self.corp_name + "_" + self.branch_name + "_" + self.Sitename)
        if not ssn.chk_ssn():
        """
        ssn = dbsession(self.request, self.response,self.corp_name + "_" + self.branch_name + "_" + self.Sitename)
        if not ssn.chkauth(self.corp_name,self.branch_name,self.Sitename):
            self.auth = False
            self.tmpl_val['auth'] = False
        else:
            self.auth = True
            self.tmpl_val['auth'] = True
            self.userID = ssn.get_ssn_data('memberID')
            self.userkey = ssn.get_ssn_data('userkey')
            """
            user = None
            if self.userkey:
                user = member.get(self.userkey)
            if not user:
                urlstr = "corp_name=" + self.corp_name
                urlstr = urlstr + "&branch_name=" + self.branch_name
                urlstr = urlstr + "&sitename=" + self.Sitename
                urlstr = urlstr + "&togo=" + self.request.path
    #           ssn.set_ssn_data("togo", urllib.quote_plus(self.request.path))
                self.redirect(str('/login?' + urlstr))
                return
            if user.seiyaku != u"未成約":
                self.tmpl_val['error_msg'] = u'アカウント停止中です。お問い合わせください。'
                templ = self.corp_name + "/" + self.branch_name + "/" + self.Sitename + "/" + "sorry.html"
                path = os.path.dirname(__file__) + '/../templates/' + templ
                self.response.out.write(template.render(path, self.tmpl_val))
                return False
            """
            self.tmpl_val["userID"]=self.userID
            self.tmpl_val["name"]=ssn.get_ssn_data('name')
            self.tmpl_val["status"]=ssn.get_ssn_data('status')
            self.tmpl_val["phone"]=ssn.get_ssn_data('phone')
            self.tmpl_val["mobilephone"]=ssn.get_ssn_data('mobilephone')
            self.tmpl_val["usermail"]=ssn.get_ssn_data('mail')
            self.tmpl_val["userkey"]=ssn.get_ssn_data('userkey')
            '''
            if not self.tmpl_val["status"] in status:
                self.tmpl_val['error_msg'] = u'必要なステータスがありません'
                templ = self.corp_name + "/" + self.branch_name + "/" + self.Sitename + "/" + "sorry.html"
                path = os.path.dirname(__file__) + '/../templates/' + templ
                self.response.out.write(template.render(path, self.tmpl_val))
                return False
            '''

            if kwargs.get("memberID",None) == None:
                self.memberID = self.request.get("memberID")
            else :
                self.memberID =kwargs.get("memberID",None)



            self.memdb=None
            tankey=""
            self.tanto=None
            if self.memberID:
                key_name = self.corp_name + "/" + self.memberID
                self.memdb = member.get_by_key_name(key_name)
                if self.memdb:
                    if self.memdb.tanto:
                        self.tanto = self.memdb.tanto
                        tankey = str(self.tanto.key())

                    self.memdb = timemanager.utc2jst_gql(self.memdb)

                    self.tmpl_val["membertel"]=self.memdb.phone
                    self.tmpl_val["membermail"]=self.memdb.mail
                    self.tmpl_val["memberyomi"]=self.memdb.yomi
                    self.tmpl_val["membername"]=self.memdb.name

            self.tmpl_val["memdb"]=self.memdb
            self.tmpl_val["tankey"]=tankey
            self.tmpl_val["memberID"]= self.memberID

        self.tmpl_val["pagepath"]=self.path
        self.tmpl_val["applicationpagebase"]= os.path.dirname(__file__) + '/../templates/' + self.tmpl_val['CorpOrg_key_name'] + u"/" + self.tmpl_val['Branch_Key_name'] + u"/" + self.tmpl_val['sitename'] + u"/" + self.tmpl_val['userpagebase']
        self.dirpath = self.pathParts[-1].split(u'?')[0]
        return True

    def get(self,**kwargs):
        pass

    def post(self,**kwargs):
        self.get(**kwargs)