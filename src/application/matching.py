#!/usr/local/bin/python
# -*- coding: utf-8 -*-

#from google.appengine.ext import webapp
import webapp2
from google.appengine.ext.webapp import template
from google.appengine.ext import db
from google.appengine.api import mail
import config
import os
import sys
from datetime import date, datetime, timedelta
from SecurePage import SecurePage
from google.appengine.api import taskqueue
from models.matchingdate import matchingdate
from models.matchingparam import matchingparam
from models.bklist import BKlist
from models.member import member
import timemanager
import logging
from application.bksearchutl import bksearchutl
from application.messageManager import messageManager
from wordstocker import wordstocker
from application.mailvalidation import mailvalidation


BASE_URL = config.BASE_URL #'http.//s-style-hrd.appspot.com'
ADMIN_EMAIL = config.ADMIN_EMAIL
ADMIN_SYSTEM_ID = config.TNTOID

class matching(SecurePage):
    corp_name = ""
    branch_name = ""

    def get(self,**kwargs):
        self.post()

    def post(self,**kwargs):
        if self.Secure_init(*[u"管理者",u"担当"]):
            mpr = {}
            com = self.request.get("com")
            sitename = self.request.get("sitename")
            matchingtarget = self.request.get("sksijky")
            service = self.request.get("service")
            seikyu =  self.request.get("seikyu")
            lev1noreactiondays= self.request.get("lev1noreactiondays")
            lev1maxsended = self.request.get("lev1maxsended")
            lev2noreactiondays= self.request.get("lev2noreactiondays")
            lev2maxsended = self.request.get("lev2maxsended")
            limitdistance  = self.request.get("limitdistance")
            sousinsyurui = self.request.get("sousinsyurui")
            media  = self.request.get("media")
            subject  = self.request.get("subject")
            body  = self.request.get("body")

            key_name = self.corp_name + "/" + self.branch_name + "/" + sitename
            if com:
                mpr = matchingparam.get_or_insert(key_name,CorpOrg_key_name=self.corp_name)
                mpr.CorpOrg_key_name = self.corp_name
                mpr.Branch_Key_name = self.branch_name
                mpr.sitename = sitename
                mpr.service = service
                mpr.seikyu = seikyu
                mpr.matchingtarget = matchingtarget
                if lev1noreactiondays:
                    mpr.lev1noreactiondays = int(lev1noreactiondays)
                if lev1maxsended:
                    mpr.lev1maxsended = int(lev1maxsended)
                if lev2noreactiondays:
                    mpr.lev2noreactiondays = int(lev2noreactiondays)
                if lev2maxsended:
                    mpr.lev2maxsended = int(lev2maxsended)
                if limitdistance:
                    mpr.limitdistance = int(limitdistance)
                mpr.sousinsyurui = sousinsyurui
                mpr.media = media
                mpr.subject = subject
                mpr.body = body
                mpr.put()

            self.tmpl_val['param'] = mpr

            mchigdatelist = matchingdate.all()
            mchigdatelist.filter("CorpOrg_key_name", self.corp_name)
            mchigdatelist.filter("Branch_Key_name", self.branch_name)
            if sitename:
                mchigdatelist.filter("sitename", sitename)
            mchigdatelist.order("-matchingdate")
            mdl = mchigdatelist.fetch(1000,0)
            lastdate = None
            if  len(mdl):
                lastdate = mdl[0].matchingdate
            if com == u"履歴削除" and len(mdl):
                mdl[0].delete()
                mdl = mchigdatelist.fetch(1000,0)
                if len(mdl):
                    lastdate = mdl[0].matchingdate #utc
                else:
                    lastdate = None
            datelist = []
            for e in mdl:
                datelist.append( timemanager.utc2jst_date(e.matchingdate)) #jst

            self.tmpl_val['servicelist'] = wordstocker.get(self.corp_name, u"サービス")

            if com == u"マッチング開始":
                if service:
                    mytask = taskqueue.Queue('mintask')
                    task = taskqueue.Task(url='/matching/tasks/matchingworker', params={
                                                                                        'lastdate':str(lastdate),
                                                                                        'corp_name':self.corp_name,
                                                                                        'branch_name':self.branch_name,
                                                                                        'service':service,
                                                                                        'matchingtarget':matchingtarget,
                                                                                        'sitename': sitename,
                                                                                        'seikyu':seikyu
                                                                                        },target="memdb2")
                    mytask.add(task)
                    #https://localhost:8080/matching/tasks/matchingworker?lastdate=2014-10-26%2009:43:40.157000&corp_name=s-style&branch_name=hon&service=マッチング&target=請求チェック
                    datelist.append( timemanager.utc2jst_date( self.matchingdate()))
                    self.tmpl_val["message"] = u"マッチングが開始されました"
                else:
                    self.tmpl_val["message"] = u"マッチング対象サービスを設定してください　マッチングはキャンセルされました"

            self.tmpl_val["dateentitys"] = datelist

            if com == u"メール送信":
                if not service :
                    self.tmpl_val["message"] = u"対象サービスを設定してください　送信はキャンセルされました"
                elif not lev1noreactiondays:
                    self.tmpl_val["message"] = u"レベル１無言日数を設定してください　送信はキャンセルされました"
                elif not lev1maxsended:
                    self.tmpl_val["message"] = u"レベル１最多送信物件数を設定してください　送信はキャンセルされました"
                elif not lev2noreactiondays:
                    self.tmpl_val["message"] = u"レベル２無言日数を設定してください　送信はキャンセルされました"
                elif not lev2maxsended:
                    self.tmpl_val["message"] = u"レベル２最多送信物件数を設定してください　送信はキャンセルされました"
                elif not limitdistance:
                    self.tmpl_val["message"] = u"最低レベルを設定してください　送信はキャンセルされました"
                else:
                #              msgkey = messageManager.post(corp = self.corp_name,sub = self.tmpl_val['subject'], body = self.tmpl_val['body'],done = True, memfrom = ADMIN_SYSTEM_ID,kindname = u"送信したメール", combkind = u"所有", msgkey = self.msg)
                #              if msgkey:
                    mytask = taskqueue.Queue('oneshotmintask')
                    task = taskqueue.Task(url='/matching/tasks/sendmailworker', params={
                                                                            "corp_name" : self.corp_name,
                                                                            "branch_name" : self.branch_name,
                                                                            "sitename":sitename,
                                                                            "subject" : self.tmpl_val['subject'],
                                                                            "body" : self.tmpl_val['body'],
                                                                            "media" : media,
                                                                            "service": service,
                                                                            "lev1noreactiondays":lev1noreactiondays,
                                                                            "lev1maxsended":lev1maxsended,
                                                                            "lev2noreactiondays":lev2noreactiondays,
                                                                            "lev2maxsended":lev2maxsended,
                                                                            "limitdistance":limitdistance
                                                                          },target="memdb2")
                    mytask.add(task)
                    self.tmpl_val["message"] = u"送信が開始されました"
                    #localhost:8080/matching/tasks/sendmailworker?body=%E9%96%8B%E6%A5%AD%0D%0A%E6%94%B9%E8%89%AF%0D%0A%E9%96%8B%E6%A5%AD%E3%81%97%E3%81%A6%E3%81%BE%E3%81%99%E3%82%88&service=&sitename=&media=web&lev1noreactiondays=35&branch_name=hon&lev2noreactiondays=65&corp_name=s-style&limitdistance=100&lev1maxsended=105&lev2maxsended=155&subject=%E3%82%BF%E3%82%A4%E3%83%88%E3%83%AB

            filename = 'matching.html'
            temp1 = os.path.join( os.getcwd(),'templates',self.corp_name,self.branch_name,self.Sitename,filename)
            temp2 = os.path.join( os.getcwd(),'templates',self.corp_name,self.branch_name,filename)
            if os.path.isfile(temp1):
                path = temp1
            elif os.path.isfile(temp2):
                path = temp2
            else:
                path = os.path.join( os.getcwd(),'templates',filename)
            self.response.out.write(template.render(path, self.tmpl_val))

    def matchingdate(self):
        newent = matchingdate(CorpOrg_key_name=self.corp_name,Branch_Key_name= self.branch_name)
        newent.put()
        return newent.matchingdate
#localhost:8080/matching/tasks/sendmailworker?body=%E9%96%8B%E6%A5%AD%0D%0A%E6%94%B9%E8%89%AF%0D%0A%E9%96%8B%E6%A5%AD%E3%81%97%E3%81%A6%E3%81%BE%E3%81%99%E3%82%88&service=&sitename=&media=web&lev1noreactiondays=35&branch_name=hon&lev2noreactiondays=65&corp_name=s-style&limitdistance=100&lev1maxsended=105&lev2maxsended=155&subject=%E3%82%BF%E3%82%A4%E3%83%88%E3%83%AB
class matchingworker(webapp2.RequestHandler):
    def get(self,**kwargs):
        self.post()

    def post(self,**kwargs):
        logging.info('matchingworker strat')
        self.corp_name =  self.request.get("corp_name")
        self.branch_name = self.request.get("branch_name")
        self.sitename = self.request.get("sitename")
        self.service = self.request.get("service")
        self.lastdate = self.request.get("lastdate")
        self.seikyu = self.seikyu.get("seikyu")
        if self.service and self.corp_name and self.branch_name:
            memberkeylist = member.all(keys_only=True)
            memberkeylist.filter("CorpOrg_key_name", self.corp_name)
            memberkeylist.filter("Branch_Key_name", self.branch_name)
            memberkeylist.filter("seiyaku",u"未成約")
            if self.service:
                memberkeylist.filter("service",self.service)
            if self.sitename:
                memberkeylist.filter("sitename",self.sitename)
            for m in memberkeylist.run():
                mytask = taskqueue.Queue('mintask')
                task = taskqueue.Task(url='/matching/tasks/matchingtask', params={'key':str(m),'lastdate':self.lastdate,'seikyu':self.seikyu},target="memdb2")
                mytask.add(task)
                #https://localhost:8080/matching/tasks/matchingtask?key=agtkZXZ-YW1hbmVkYnIVCxIGbWVtYmVyIglzLXN0eWxlLzIM&lastdate=2014-10-26%2009:43:40.157000
                self.response.out.write(str(m))
                self.response.out.write('<br>')

class matchingtask(webapp2.RequestHandler):
    def get(self,**kwargs):
        self.post()

    def post(self,**kwargs):
        key = self.request.get('key')
        lastdate = self.request.get("lastdate")
        seikyu = self.request.get("seikyu")
        flg = False
        if seikyu == u"すべて資料請求する":
            flg = True
        person = db.get(db.Key(key))
        """
        検索する顧客のフィルタリングが必要ならここでやる
        """
        if person.rank == "Z":
            self.response.out.write('rank=Z')
            return
        if person.bksearchdata_set.count() > 0:
            msgkey = messageManager.post(corp=person.CorpOrg_key_name,sub=u"一括検索中",body=u"",done=False,memfrom=person.memberID,kindname="マッチング",combkind=u"所有",reservation=None,reservationend=None,memto=None,commentto=None,mailto=None,htmlmail=None)
            mlist = bksearchutl.do_allsearch(person,msgkey,lastdate,flg)
            for m in mlist:
                self.response.out.write(str(m))
                self.response.out.write('<br>')
        else:
            msgkey = messageManager.post(corp=person.CorpOrg_key_name,sub=u"マッチングエラー",body=u"検索条件がひとつも登録されていません",done=False,memfrom=person.memberID,kindname="マッチング",combkind=u"所有",reservation=None,reservationend=None,memto=None,commentto=None,mailto="tanto",htmlmail=None)
            self.response.out.write("マッチングエラー 検索条件なし")

# https://localhost:8080/matching/tasks/sendmailworker?corp_name=s-style&branch_name=hon&service=マッチング&media=web&subject=テストですよ&&lev1noreactiondays=35&lev1maxsended=105&lev2noreactiondays=65&lev2maxsended=155&limitdistance=100
class sendmailworker(webapp2.RequestHandler):
    def get(self,**kwargs):
        self.post()

    def post(self,**kwargs):
        #logging.info('sendmailworker strat')
        self.corp_name =  self.request.get("corp_name")
        self.branch_name = self.request.get("branch_name")
        self.sitename = self.request.get("sitename")
        self.service = self.request.get("service")
        self.media = self.request.get("media")
        self.subject = self.request.get("subject")
        self.body= self.request.get("body")
        lev1noreactiondays= int(self.request.get("lev1noreactiondays"))
        lev1maxsended = int(self.request.get("lev1maxsended"))
        lev2noreactiondays= int(self.request.get("lev2noreactiondays"))
        lev2maxsended = int(self.request.get("lev2maxsended"))
        limitdistance  = int(self.request.get("limitdistance"))
        if self.corp_name and self.branch_name:
            memberkeylist = member.all()
            memberkeylist.filter("CorpOrg_key_name", self.corp_name)
            memberkeylist.filter("Branch_Key_name", self.branch_name)
            memberkeylist.filter("seiyaku",u"未成約")
            if self.sitename:
                memberkeylist.filter("sitename",self.sitename)
            if self.service:
                memberkeylist.filter("service",self.service)
            mv = mailvalidation()
            rep = ""
            for m in memberkeylist.run():
                if m.tanto:
                    if m.mail:
                        if not mv.chk(m.mail):
                            msgkey2 = messageManager.post(corp = self.corp_name,sub = u"メールアドレスチェック" ,body = u"パターンがマッチしない警告を受けました。このユーザーのメールアドレスをチェックしてください。" ,done = False,  memfrom = m.memberID, kindname = u"アドレスチェック", combkind = u"所有",msgkey = None , commentto=None,mailto="tanto")
                            rep += u"アドレス不正チェック:" + m.memberID + " :" + m.mail + u"\n"
                        #前回送信日からの経過日数の取得
                        if self.spandayschk(m,lev1noreactiondays,lev1maxsended,lev2noreactiondays,lev2maxsended,limitdistance):
                            mytask = taskqueue.Queue('mintask')
                            task = taskqueue.Task(url='/matching/tasks/sendmailtask', params={
                                                                                              'memberkey':str(m.key()),
                                                                                              "corp_name":self.corp_name,
                                                                                              "branch_name":self.branch_name,
                                                                                              "media":self.media,
                                                                                              "subject":self.subject,
                                                                                              "body":self.body
                                                                                              },target="memdb2")
                            mytask.add(task)
                        #https://localhost:8080/matching/tasks/sendmailtask?body=%E9%96%8B%E6%A5%AD%0D%0A%E6%94%B9%E8%89%AF%0D%0A%E9%96%8B%E6%A5%AD%E3%81%97%E3%81%A6%E3%81%BE%E3%81%99%E3%82%88&media=web&memberkey=agtkZXZ-YW1hbmVkYnIVCxIGbWVtYmVyIglzLXN0eWxlLzIM&branch_name=hon&corp_name=s-style&subject=%E3%82%BF%E3%82%A4%E3%83%88%E3%83%AB
                            self.response.out.write(str(m))
                            self.response.out.write('<br>')
                    else:
                        rep += u"アドレス未設定チェック:" + m.memberID + u"\n"
                else:
                        rep += u"担当未設定チェック:" + m.memberID + u"\n"
                if rep:
                    msgkey = messageManager.post(corp = self.corp_name,sub = u"メールアドレスチェック結果", body = rep,done = False, memfrom = ADMIN_SYSTEM_ID,kindname = u"メールアドレスチェック", combkind = u"所有", msgkey = None,mailto=None)

    def spandayschk(self,m,lev1noreactiondays,lev1maxsended,lev2noreactiondays,lev2maxsended,limitdistance):
        return m.canSend(lev1noreactiondays,lev1maxsended,lev2noreactiondays,lev2maxsended,limitdistance)

class sendmailtask(webapp2.RequestHandler):
    """
    https://localhost:8080/matching/tasks/sendmailtask?body=%E9%96%8B%E6%A5%AD%0D%0A%E6%94%B9%E8%89%AF%0D%0A%E9%96%8B%E6%A5%AD%E3%81%97%E3%81%A6%E3%81%BE%E3%81%99%E3%82%88&media=web&memberkey=agtkZXZ-YW1hbmVkYnIVCxIGbWVtYmVyIglzLXN0eWxlLzIM&branch_name=hon&corp_name=s-style&subject=%E3%82%BF%E3%82%A4%E3%83%88%E3%83%AB
    """
    def get(self,**kwargs):
        self.post()

    def post(self,**kwargs):
        self.tmpl_val = {}
        self.corp_name = self.request.get("corp_name")
        self.branch_name = self.request.get("branch_name")
        self.media = self.request.get("media")
        memberkey = self.request.get('memberkey')
        if not memberkey:
            return False
        self.tmpl_val = {}
        self.tmpl_val['subject'] = self.request.get("subject")
        self.tmpl_val['body'] = self.request.get("body")
        self.tmpl_val['body'] = self.request.get("body")
        self.tmpl_val["htmlmail"] = "1"
        mem = member.get(memberkey)
        if not self.tmpl_val['subject']:
            self.subject= mem.name + u"様のご希望条件にあった物件が見つかりました！！"
        if not  self.tmpl_val['body']:
            self.tmpl_val['body'] = u''
        self.tmpl_val['body']=u"こんにちは！" + self.corp_name + "です。\n" + mem.name + "様が登録した希望条件に一致する物件が見つかりましたのでお知らせいたします。\n\n" + self.tmpl_val['body']
        if not mem.tanto:
            msgkey2 = messageManager.post(corp = self.corp_name,sub = u"担当者が設定されていません",body = u"顧客ID"+mem.memberID,done = False,  memfrom = config.TNTOID, kindname = u"マッチング送信エラー", combkind = u"所有",msgkey = None,commentto=None,mailto="tanto")
            return
        bklist = mem.refbklist
        bklist.filter("issend = ",True)# if refmes.kindname in  [u"マッチング",u"自動検索",u"資料請求",u"ネット資料請求",u"送付依頼"]: in bklistutl.py
        bklist.filter("sended = ",False)
        nlist = []
        # 今
        now = datetime.now()
        # ３０日前
        s30_days_ago = now - timedelta(30)
        for bkl in bklist:
            """
            確認年月日のフィルタリング 作成状況のフィルタリングは？？？？
            """
            if bkl.refbk.kknnngp < s30_days_ago:
                if bkl.kindname == u'マッチング' and bkl.refbk.dtsyuri in [u"事例",u"重複",u"停止",u"予約"]:
                    bkl.issend = False
                    bkl.senddate = None
                    bkl.memo = bkl.refbk.dtsyuri + u"により送信キャンセル"
                    bkl.put()
                else:
                    if (bkl.refbk.sksijky == u"作成済み" or bkl.refbk.sksijky == u"ＨＰ掲載") and bkl.refbk.dtsyuri  != u"商談中":
                        bkl.senddate = now
                        bkl.sended = True
                        bkl.put()
                        nlist.append(bkl.refbk)
        if len(nlist):
            #登録年月日turknngp でソーティング
            nlist.sort(key=lambda obj: obj.kknnngp)
            try:
                body = self.makebody(mem.sitename , nlist , self.media , self.tmpl_val)
            except IOError:
                mailbody = u'適切なテンプレートファイルが存在しません。顧客データのサイト名等をチェックしてください。'
                self.tmpl_val['subject'] += u'送信時エラー 　テンプレートエラー'
                msgkey2 = messageManager.post(corp = self.corp_name,sub = self.tmpl_val['subject'],body = mailbody,done = False,  memfrom = mem.memberID, kindname = u"マッチング送信エラー", combkind = u"所有",msgkey = None,commentto=None,mailto="tanto")
                return
            except :
                mailbody = u"未確認のエラーが発生したため送信できませんでした\n%s\n%s" %(sys.exc_info()[0],sys.exc_info()[1])
                self.tmpl_val['subject'] += u'送信時エラー　未確認システムエラー'
                msgkey2 = messageManager.post(corp = self.corp_name,sub = self.tmpl_val['subject'],body = mailbody,done = False,  memfrom = mem.memberID, kindname = u"マッチング送信エラー", combkind = u"所有",msgkey = None , commentto=None,mailto="tanto")
                return
            msgkey2 = messageManager.post(corp = self.corp_name,sub = self.tmpl_val['subject'],body = body,done = True,  memfrom = mem.memberID, kindname = u"マッチング送信", combkind = u"所有",msgkey = None,commentto=None,mailto="member",htmlmail=True)
            self.response.out.write(body)
        else:
            self.response.out.write("リストにデータがありません")


    def makebody(self,site,bklist,media,tmpl_val,filename = 'bklistml.html'):
        entitys = {}
        entitys["media"] = media
        dlist = []
        if bklist:
            for bkl in bklist:
                dlist.append(bkl.makedata(media))
            entitys["bkdatalist"] = dlist
            """
            https://s-style-hrd.appspot.com/show/s-style/hon/www.chikusaku-mansion.com/bkdata/article.html?id=59&media=web
            """
            entitys["bkdataurl"] = BASE_URL + u"/show/" + self.corp_name + u"/" + self.branch_name + u"/" + site + u"/bkdata/article.html?media=" + media + u"&id="
            entitys["listKey"] = ""
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

