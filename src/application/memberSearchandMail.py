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
import sys
import config
import messageManager
from models.message import Message
from models.member import member
from SecurePage import SecurePage
from wordstocker import wordstocker
from bklistutl import bklistutl
from GqlEncoder import GqlJsonEncoder
import timemanager
import datetime
import re
from google.appengine.api import taskqueue
from application.mailvalidation import mailvalidation

BASE_URL = config.BASE_URL #'http.//s-style-hrd.appspot.com'
ADMIN_EMAIL = config.ADMIN_EMAIL
ADMIN_SYSTEM_ID = config.TANTOID

class memberSearchandMailbase(SecurePage):
    corp_name = ""
    branch_name = ""

    def get(self,**kwargs):
        self.post()

    def memberSearchandMailbase_init(self):
        if not self.corp_name:
            self.corp_name = self.request.get("corp_name")
        if not self.branch_name:
            self.branch_name = self.request.get("branch_name")

        self.bkID = self.request.get("bkID")
        self.tmpl_val["bkID"] = self.bkID
        self.followsubject = self.request.get("followsubject")
        self.tmpl_val["followsubject"] = self.followsubject
        self.rireki = self.request.get("rireki")
        if self.rireki:
            self.rireki = int(self.rireki)
        self.tmpl_val["rireki"] = self.rireki
        self.service = self.request.get("service")
        self.tmpl_val["service"] = self.service
        self.status = self.request.get("status")
        self.tmpl_val["status"] = self.status
        self.seiyaku = self.request.get("seiyaku")
        self.tmpl_val["seiyaku"] = self.seiyaku
        self.tmpl_val["tourokunengappiL"] = self.request.get("tourokunengappiL")
        self.tourokunengappiL = self.gettime(self.request.get("tourokunengappiL"))
        self.tmpl_val["tourokunengappiU"] = self.request.get("tourokunengappiU")
        self.tourokunengappiU = self.gettime(self.request.get("tourokunengappiU"),1)
        self.filter = self.request.get("filter")
        self.tmpl_val["filter"] = self.filter
        self.filtervalue = self.request.get("filtervalue")
        self.tmpl_val["filtervalue"] = self.filtervalue
        self.htmlmail = self.request.get("htmlmail")
        self.tmpl_val["htmlmail"] = self.htmlmail
        #重複のチェックが外れてしまう

        self.msgkey = self.request.get("msgkey")
        #return
        self.memsitename = self.request.get("memsitename")
        self.submit = self.request.get("com")
        self.msg = self.request.get("msg")
        if self.msg:
            self.msg = int(self.msg)
        self.tmpl_val['msg'] = self.msg
        self.tmpl_val['subject'] = self.request.get("subject")
        self.tmpl_val['body'] = self.request.get("body")
        self.msID = self.request.get("msID")
        self.tmpl_val['msID'] = self.msID
        self.mailbody = ""
        self.media = self.request.get("media")
        if not self.media:
            self.media = "web"
        self.tmpl_val["media"] = self.media

    def gettime(self,timestr,add=None):
        res = None
        if timestr:
            if re.compile(".*/.*/.* .*:.*:.*").match(timestr, 1):
                res = timemanager.jst2utc_date(datetime.datetime.strptime(timestr, "%Y/%m/%d %H:%M:%S"))
            elif re.compile(".*/.*/.*").match(timestr, 1):
                res = timemanager.jst2utc_date(datetime.datetime.strptime(timestr, "%Y/%m/%d"))
            elif re.compile(".*/.*").match(timestr, 1):
                res = timemanager.jst2utc_date(datetime.datetime.strptime(timestr, "%Y/%m"))
            if add:
                res += datetime.timedelta(days=add)
        return res

    def makedata(self,bkd,media):
        """
        query_str = u"SELECT * FROM Blob WHERE CorpOrg_key = '" + bkd.nyrykkisyID + u"' AND Branch_Key = '" + bkd.nyrykstnID + u"' AND bkID = '" + bkd.bkID + u"' AND media = '" + media + u"' ORDER BY pos ASC"
        blobs = db.GqlQuery (query_str)
        b2 = []
        heimenzu = None
        for c in blobs:
            if c.pos != "平面図":
                b2.append(c)
            else :
                heimenzu = c
        kakakuM = None
        if bkd.kkkuCnryu:
            kakakuM = GqlJsonEncoder.floatfmt(float(int(bkd.kkkuCnryu/100))/100)
        tknngt = None
        if bkd.cknngtSirk:
            tknngt = bkd.cknngtSirk.year
            if int(tknngt) < 1989:
                tknngt = u"昭和" + str(tknngt-1925) + u"年"
            elif int(tknngt) >= 1989:
                tknngt = u"平成" + str(tknngt-1988) + u"年"
            else:
                tknngt = tknngt + u"年"
        data = GqlJsonEncoder.GQLmoneyfmt(bkd)
        entitys = {"bkdata":data,"picdata":b2,"kakakuM":kakakuM,"tknngtG":tknngt,"heimenzu":heimenzu}
        """
        entitys = bkd.makedata(media)
        return entitys

    def makebody(self,site,msID,media,tmpl_val,filename = 'bklistml.html'):
        entitys = {}
        entitys["media"] = media
        if msID:
            bkdb = bklistutl.getlistbyID(self.corp_name, msID)
            #bkdb.filter("mtngflg",True)
            #bkdb.filter("webknskflg",True)
            #bkdb.filter("nyrykkisyID", self.corp_name)
            #bkdb.filter("nyrykstnID", self.branch_name)
            bklist=bkdb.fetch(1000, 0)
            list = []
            for bkl in bklist:
                list.append(self.makedata(bkl.refbk,media))
            entitys["bkdatalist"] = list
            """
            https://s-style-hrd.appspot.com/show/s-style/hon/www.chikusaku-mansion.com/bkdata/article.html?id=59&media=web
            """
            entitys["bkdataurl"] = BASE_URL + u"/show/" + self.corp_name + u"/" + self.branch_name + u"/" + site + u"/bkdata/article.html?media=" + media + u"&id="
            entitys["listKey"] = msID
            tmpl_val["data"]=entitys
        templ = os.path.join( os.getcwd(),'templates',self.corp_name,self.branch_name,site,filename)
        temp2 = os.path.join( os.getcwd(),'templates',self.corp_name,self.branch_name,filename)
        if os.path.isfile(templ):
            path = templ
        elif os.path.isfile(temp2):
            path = temp2
        else:
            path = os.path.join( os.getcwd(),'templates','bklistml.html')
        return template.render(path,tmpl_val)

class memberSearchandMail(memberSearchandMailbase):
    def get(self,**kwargs):
        self.post()

    def post(self,**kwargs):
        if self.Secure_init(*[u"管理者",u"担当"]):
            self.memberSearchandMailbase_init()
            if self.submit == u"プレビュー":
                if self.htmlmail == "1":
                    self.tmpl_val["htmlmail"] = self.htmlmail
                    self.mailbody = self.makebody(self.Sitename,self.msID,self.media,self.tmpl_val)
                else:
                    self.mailbody = self.tmpl_val['body']
                self.tmpl_val['preview'] = self.mailbody
            if self.submit == u"メール送信" or self.submit == u"リスト保存" or self.submit == u"メール保存":
                if not self.tmpl_val['subject'] and (self.submit == u"メール送信" or self.submit == u"メール保存"):
                    self.tmpl_val['error_msg'] += u"表題がありません　　"
                if not self.tmpl_val['body'] and (self.submit == u"メール送信" or self.submit == u"メール保存"):
                    self.tmpl_val['error_msg'] += u"本文がありません　"
                if (self.tmpl_val['error_msg']=="" and self.submit == u"メール保存"):
                #post(cls,corp,sub,body,done,memfrom,kindname,combkind=u"所有",msgkey=None,reservation=None,reservationend=None,memto=None,commentto=None,mailto=None)
                    msgkey = messageManager.messageManager.post(corp = self.corp_name,sub = self.tmpl_val['subject'], body = self.tmpl_val['body'],done = False, memfrom = ADMIN_SYSTEM_ID,kindname = u"保存したメール", combkind = u"所有", msgkey = self.msg)
#                    msgkey = messageManager.messageManager.post(corp = self.corp_name,sub = self.tmpl_val['subject'], body = self.tmpl_val['body'],done = False, memfrom = ADMIN_SYSTEM_ID,kindname = u"保存したメール", combkind = u"所有")
                elif (self.tmpl_val['error_msg']=="" and self.submit == u"メール送信") or self.submit == u"リスト保存":
                    if self.submit == u"メール送信":
                        msgkey = messageManager.messageManager.post(corp = self.corp_name,sub = self.tmpl_val['subject'], body = self.tmpl_val['body'],done = True, memfrom = ADMIN_SYSTEM_ID,kindname = u"送信したメール", combkind = u"所有", msgkey = self.msg)
                    elif self.submit == u"リスト保存":
                        msgkey = messageManager.messageManager.post(corp = self.corp_name,sub = self.tmpl_val['subject'], body = self.tmpl_val['body'],done = False, memfrom = ADMIN_SYSTEM_ID,kindname = u"保存したリスト", combkind = u"所有", msgkey = self.msg)
                    if msgkey:
                        mytask = taskqueue.Queue('oneshotmintask')
                        task = taskqueue.Task(url='/tasks/mailinglistsend', params={
                                                                                "corp_name" : self.corp_name,
                                                                                "branch_name" : self.branch_name,
                                                                                "bkID" : self.bkID,
                                                                                "followsubject" : self.followsubject,
                                                                                "rireki" : str(self.rireki),
                                                                                "service" : self.service,
                                                                                "status" : self.status,
                                                                                "seiyaku" : self.seiyaku,
                                                                                "tourokunengappiL" : self.tmpl_val["tourokunengappiL"],
                                                                                "tourokunengappiU" : self.tmpl_val["tourokunengappiU"],
                                                                                "filter" : self.filter,
                                                                                "filtervalue" : self.filtervalue ,
                                                                                "htmlmail": self.htmlmail,
                                                                                "com" : self.submit,
                                                                                "msg" : self.msg,
                                                                                "subject" : self.tmpl_val['subject'],
                                                                                "body" : self.tmpl_val['body'],
                                                                                "msID" : self.msID,
                                                                                "media" : self.media,
                                                                                "msgkey": str(msgkey),
                                                                                "memsitename":self.memsitename
                                                                              })
                        mytask.add(task)
                else:
                    self.tmpl_val['error_msg'] += u"\nキャンセルされました"

            #    def getmeslistbyID(cls,corp,memberID,subject=None,kindname=None,done=None,kill=None,reservationLower=None,reservationUpper=None,order=None,combkind=None):
            msglist = messageManager.messageManager.getmeslistbyID(corp = self.corp_name,memberID = ADMIN_SYSTEM_ID,order='-reservation',combkind=U'所有')
            self.tmpl_val['msglist'] = msglist
            self.tmpl_val['servicelist'] = wordstocker.get(self.corp_name, u"サービス")
            path = 'templates/memberSearchandMail.html'
            self.response.out.write(template.render(path, self.tmpl_val))

class mailsendback(memberSearchandMailbase):

    def get(self,**kwargs):
        self.post()

    def post(self,**kwargs):
        self.memberSearchandMailbase_init()
        memberID = self.request.get("memberID")
        mailbody = ""

        """
                    メールの送信者はメンバーの担当のIDが送信元になる
        """
        if self.submit == u"メール送信":
            if self.htmlmail == "1":
                htmlml = True
                try:
                    mailbody = self.makebody(self.memsitename , self.msID , self.media , self.tmpl_val)
                except IOError:
                    mailbody = u'適切なテンプレートファイルが存在しません。顧客データのサイト名等をチェックしてください。'
                    self.tmpl_val['subject'] += u'送信時エラー 　テンプレートエラー'
                    msgkey2 = messageManager.messageManager.post(corp = self.corp_name,sub = self.tmpl_val['subject'],body = mailbody,done = False,  memfrom = memberID, kindname = u"顧客リストエラー", combkind = u"所有",msgkey = None , commentto=Message.get(self.msgkey),mailto=None)
                    return
                except :
                    mailbody = u"未確認のエラーが発生したため送信できませんでした\n%s\n%s" %(sys.exc_info()[0],sys.exc_info()[1])
                    self.tmpl_val['subject'] += u'送信時エラー　未確認システムエラー'
                    msgkey2 = messageManager.messageManager.post(corp = self.corp_name,sub = self.tmpl_val['subject'],body = mailbody,done = False,  memfrom = memberID, kindname = u"顧客リストエラー", combkind = u"所有",msgkey = None , commentto=Message.get(self.msgkey),mailto=None)
                    return

            else:
                #mailbody = self.tmpl_val['body']
                htmlml = False
                try:
                    mailbody = self.makebody(self.memsitename , self.msID , self.media , self.tmpl_val,'bklistml.txt')
                except IOError:
                    mailbody = u'適切なテンプレートファイルが存在しません。顧客データのサイト名等をチェックしてください。'
                    self.tmpl_val['subject'] += u'送信時エラー 　テンプレートエラー'
                    msgkey2 = messageManager.messageManager.post(corp = self.corp_name,sub = self.tmpl_val['subject'],body = mailbody,done = False,  memfrom = memberID, kindname = u"顧客リストエラー", combkind = u"所有",msgkey = None , commentto=Message.get(self.msgkey),mailto=None)
                    return
                except :
                    mailbody = u"未確認のエラーが発生したため送信できませんでした\n%s\n%s" %(sys.exc_info()[0],sys.exc_info()[1])
                    self.tmpl_val['subject'] += u'送信時エラー　未確認システムエラー'
                    msgkey2 = messageManager.messageManager.post(corp = self.corp_name,sub = self.tmpl_val['subject'],body = mailbody,done = False,  memfrom = memberID, kindname = u"顧客リストエラー", combkind = u"所有",msgkey = None , commentto=Message.get(self.msgkey),mailto=None)
                    return
            msgkey2 = messageManager.messageManager.post(corp = self.corp_name,sub = self.tmpl_val['subject'],body = mailbody,done = True,  memfrom = memberID, kindname = u"メーリングリスト", combkind = u"所有",msgkey = None,commentto=Message.get(self.msgkey),mailto="member",htmlmail=htmlml)
        elif self.submit == u"リスト保存":
            msgkey2 = messageManager.messageManager.post(corp = self.corp_name,sub = self.tmpl_val['subject'],body = mailbody,done = False,  memfrom = memberID, kindname = u"顧客リスト", combkind = u"所有",msgkey = None , commentto=Message.get(self.msgkey),mailto=None)


class memberSearchandMailback(memberSearchandMailbase):

    def get(self,**kwargs):
        self.post()

    def post(self,**kwargs):
        try:
            rep = ''
            self.memberSearchandMailbase_init()
            self.tmpl_val['msgkey'] = str(self.msgkey)
            memlist = []
            if self.followsubject:
                meslist = Message.all()
                meslist.filter("subject >= " ,self.followsubject)
                meslist.filter("subject < ",self.followsubject + u"\uFFFD'")
                meslist.filter("corp = ",self.corp_name)
                meslist.filter("kill = ",False)
                for mes in meslist:
                    comblist = mes.refmemlist
                    for e in comblist.filter("combkind = ",u"所有"):
                        e2 = e.refmem.key()
                        if not e2 in memlist :
                            memlist.append(e2)
            if self.bkID:
                meslist = bklistutl.getmeslistbybkID(self.corp_name, self.branch_name, self.bkID)
                if len(memlist):
                    reslist = []
                    for mes in meslist:
                        m = messageManager.messageManager.getmemlist(mes,u"所有")
                        for e in m:
                            e2 = e.refmem.key()
                            if e2 in memlist:
                                if not e2 in reslist :
                                    reslist.append(e2)
                    memlist = reslist
                else:
                    for mes in meslist:
                        m = messageManager.messageManager.getmemlist(mes,u"所有")
                        for e in m:
                            e2 = e.refmem.key()
                            if not e2 in memlist :
                                memlist.append(e2)
            if self.rireki:
                #履歴メッセージ番号からメッセージを取得
                mes = messageManager.messageManager.getmesbyID(self.corp_name,self.rireki)
                #へっセージへのコメント参照メッセージを取得
                meslist = mes.refmes
                if len(memlist):
                    reslist = []
                    for mes in meslist:
                        #コメントメッセージから所有者メンバーを取得
                        m = messageManager.messageManager.getmemlist(mes,u"所有")
                        for e in m:
                            e2 = e.refmem.key()
                            if e2 in memlist:
                                if not e2 in reslist :
                                    reslist.append(e2)
                    meslist = reslist
                else:
                    for mes in meslist:
                        m = messageManager.messageManager.getmemlist(mes,u"所有")
                        for e in m:
                            e2 = e.refmem.key()
                            if not e2 in memlist :
                                memlist.append(e2)
            if (self.service or self.status or self.seiyaku or self.tourokunengappiL or self.tourokunengappiU or (self.filter and self.filtervalue)):
                query = member.all(keys_only=True)
                if self.service:
                    query.filter("service = ",self.service)
                if self.status:
                    query.filter("status = ",self.status)
                if self.seiyaku:
                    query.filter("seiyaku = " ,self.seiyaku)
                if self.tourokunengappiL:
                    query.filter("tourokunengappi >= " ,self.tourokunengappiL)
                if self.tourokunengappiU:
                    query.filter("tourokunengappi <= " ,self.tourokunengappiU)
                if filter and self.filtervalue:
                    if self.filtervalue == "true":
                        self.filtervalue1 = True
                    elif self.filtervalue == "false":
                        self.filtervalue1 = False
                    elif self.filtervalue == "none":
                        self.filtervalue1 = None
                    elif self.filtervalue.isdigit():
                        self.filtervalue1 = float(self.filtervalue)
                    elif self.gettime(self.filtervalue):
                        self.filtervalue1 = self.gettime(self.filtervalue)
                    else:
                        self.filtervalue1 = self.filtervalue
                    query.filter(self.filter + " = " ,self.filtervalue1)
                query.filter("CorpOrg_key_name = ",self.corp_name )
                if len(memlist):
                    reslist = []
                    for e in query:
                        if e in memlist:
                            if not e in reslist :
                                reslist.append(e)
                    memlist = reslist
                else:
                    for e in query:
                        if not e in memlist :
                            memlist.append(e)
            memlist = member.get(memlist)
            if self.submit == u"メール送信" or self.submit == u"リスト保存":
                mv = mailvalidation()
                for mem in memlist:
                    if mem.tanto:
                        if mem.mail:
                            if not mv.chk(mem.mail):
                                msgkey2 = messageManager.messageManager.post(corp = self.corp_name,sub = u"メールアドレスチェック" ,body = u"パターンがマッチしない警告を受けました。このユーザーのメールアドレスをチェックしてください。" ,done = False,  memfrom = mem.memberID, kindname = u"アドレスチェック", combkind = u"所有",msgkey = None , commentto=Message.get(self.msgkey),mailto=None)
                                rep += u"アドレス不正チェック:" + mem.memberID + " :" + mem.mail + u"\n"
                            mytask = taskqueue.Queue('oneshotmintask')
                            task = taskqueue.Task(url='/tasks/mailsendback', params={
                                                                                    "corp_name" : self.corp_name,
                                                                                    "branch_name" : self.branch_name,
                                                                                    "bkID" : self.bkID,
                                                                                    "followsubject" : self.followsubject,
                                                                                    "rireki" : self.rireki,
                                                                                    "service" : self.service,
                                                                                    "status" : self.status,
                                                                                    "seiyaku" : self.seiyaku,
                                                                                    "tourokunengappiL" : self.tmpl_val["tourokunengappiL"],
                                                                                    "tourokunengappiU" : self.tmpl_val["tourokunengappiU"],
                                                                                    "filter" : self.filter,
                                                                                    "filtervalue" : self.filtervalue ,
                                                                                    "htmlmail": self.htmlmail,
                                                                                    "com" : self.submit,
                                                                                    "msg" : self.msg,
                                                                                    "subject" : self.tmpl_val['subject'],
                                                                                    "body" : self.tmpl_val['body'],
                                                                                    "msID" : self.msID,
                                                                                    "media" : self.media,
                                                                                    "msgkey":str(self.msgkey),
                                                                                    "memberID":mem.memberID,
                                                                                    "memsitename":mem.sitename
                                                                                  })
                            mytask.add(task)
                        else:
                            rep += u"アドレス未設定チェック:" + mem.memberID + u"\n"
                    else:
                        rep += u"担当未設定チェック:" + mem.memberID + u"\n"
                if rep:
                    msgkey = messageManager.messageManager.post(corp = self.corp_name,sub = u"メールアドレスチェック結果", body = rep,done = False, memfrom = ADMIN_SYSTEM_ID,kindname = u"メールアドレスチェック", combkind = u"所有", msgkey = None,mailto=None)
            if self.submit == u"はがき" or self.submit == u"タックシール":
                self.tmpl_val["memlist"] = memlist
                if self.submit == u"はがき":
                    path = 'templates/HAGAKI.html'
                    self.response.out.write(template.render(path, self.tmpl_val))
                elif self.submit == u"タックシール":
                    path = 'templates/ATENA.html'
                    self.response.out.write(template.render(path, self.tmpl_val))
        except :
            mailbody = u"エラーが発生したため一部のメールが送信できませんでした\n%s\n%s\nその他のエラー\n%s" %(sys.exc_info()[0],sys.exc_info()[1],rep)
            sub = u'タスクキューエラー　未確認システムエラー'
            msgkey2 = messageManager.messageManager.post(corp = self.corp_name,sub = sub,body = mailbody,done = False,  memfrom = ADMIN_SYSTEM_ID, kindname = u"顧客リストエラー", combkind = u"所有",msgkey = None , mailto=None)
            raise sys.exc_info()[1]

