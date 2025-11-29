# -*- coding: utf-8 -*-

#from google.appengine.dist import use_library
#use_library('django', '1.2')


import os
import re
#from google.appengine.ext import webapp
import webapp2
from google.appengine.ext.webapp import template
from google.appengine.ext import db
from application.GqlEncoder import GqlJsonEncoder
from application.bklistutl import bklistutl
from models import bkdata
import session
from SecurePageBase import SecurePageBase
from chkauth import dbsession
import urllib
from models.bksearchaddress import getname
#os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
#from google.appengine.dist import use_library
#use_library('django', '1.2')

class Show(SecurePageBase):

    def get(self,**kwargs):

        """
                  テンプレート名はアドレスのファイル名から自動取得
        pathParts = path.split(u'/')
        request.path [u'', u'show', u's-style', u'hon', u'sitename',u'command',u'bkdata.html?id=59]
        request.url [u'https:', u'', u's-style-hrd.appspot.com', u'show', u's-style', u'hon', u'sitename',u'command',u'bkdata.html?id=59]
        """
        self.Secure_init(**kwargs)
        path = self.request.path
        pathParts = path.split(u'/')
        Domain = self.request.url.split(u'/')[2]
        CorpOrg_key  = pathParts[2]
        Branch_Key = pathParts[3]
        Sitename = pathParts[4]
        Command = pathParts[5]
        user_agent = self.request.user_agent
        templ = CorpOrg_key + "/" + Branch_Key + "/" + Sitename + "/" + pathParts[6].split(u'?')[0]
        entitys = {}
        #self.tmpl_val["applicationpagebase"] = u"userpagebase.html"
        """
        selecl searvice
        """
        self.tmpl_val['corp_name'] = CorpOrg_key
        self.tmpl_val['branch_name'] = Branch_Key
        self.tmpl_val['sitename'] = Sitename
        media = self.request.get("media")

        if Command == "bkdata" or Command == "bkdatam" or Command == "bkdatash":
            """
            https://s-style-hrd.appspot.com/show/s-style/hon/www.chikusaku-mansion.com/bkdata/article.html?id=59&media=web
            https://localhost:8080/show/s-style/hon/www.chikusaku-mansion.com/bkdata/article.html?id=59&media=web
            """
            bkID = self.request.get("id")
            if bkID:
                key_name =  CorpOrg_key + u"/" + Branch_Key + u"/" + bkID
                bkdb = bkdata.BKdata.get_by_key_name(key_name)
                if bkdb:
                    if (bkdb.mtngflg and bkdb.webknskflg) or True :
                        entitys = self.makedata(bkdb,media)
                        """
                                                        以下の判定はテンプレート側でやるように改造する
                        """
                        """
                        if not(bkdb.kukkTnsiKbn == u"広告可" or bkdb.kukkTnsiKbn == u"一部可（インターネット）" or bkdb.kukkTnsiKbn == u"広告可（但し要連絡）"):
                                                                 ここでセッションチェック表示してよいデータか確認する
                            if not self.auth:
                                urlstr = "corp_name=" + CorpOrg_key
                                urlstr = urlstr + "&branch_name=" + Branch_Key
                                urlstr = urlstr + "&style=show"
                                urlstr = urlstr + "&sitename=" + Sitename
                                urlstr = urlstr + "&togo=" + urllib.quote_plus(self.request.path + "?" + self.request.query_string)
    #                           ssn.set_ssn_data("togo", urllib.quote_plus(self.request.path))
                                self.redirect(str('/login?' + urlstr))
                                return
                        """
                        if bkdb.kukkTnsiKbn == u"広告可" or bkdb.kukkTnsiKbn == u"一部可（インターネット）" or bkdb.kukkTnsiKbn == u"広告可（但し要連絡）":
                            entitys["webkkkk"]=True
                        else :
                            entitys["webkkkk"]=False
                    else:
                        self.tmpl_val['error_msg'] = u'物件の表示が許可されませんでした。'
                        templ = CorpOrg_key + "/" + Branch_Key + "/" + Sitename + "/" + "sorry.html"
                else:
                    self.tmpl_val['error_msg'] = u'物件の情報が取得できませんでした。No data'
                    templ = CorpOrg_key + "/" + Branch_Key + "/" + Sitename + "/" + "sorry.html"
            else:
                self.tmpl_val['error_msg'] = u'物件の情報が取得できませんでした。bkID missing'
                templ = CorpOrg_key + "/" + Branch_Key + "/" + Sitename + "/" + "sorry.html"


        elif Command == "bklist" or Command == "bklistm" or Command == "bklistsp":
            """
            https://s-style-hrd.appspot.com/show/s-style/hon/www.chikusaku-mansion.com/bklist/bklist.html?listkey=トップ&offset=0&media=web
            https://localhost:8080/show/s-style/hon/www.chikusaku-mansion.com/bklist/bklist.html?listkey=トップ&offset=0&media=web
                            【listkey】
            ●トップページに「おすすめ物件」として表示させる場合
            →　トップ

            ●物件ページ内での「リノベーション」「リフォーム」「アウトレット」の区分
                            例）リノベーションの場合は　→　リノベーション

            ●トップページのマンションMap上でのアイコン表示
                            「人気のマンション（オレンジのアイコン）」→　人気
                            「購入希望者がいるマンション（青のアイコン）」→　　購入
                            「現在売却物件があるマンション（赤のア イコン）」→　売り
                            「現在売却物件がないマンション（白のア イコン）」→　その他
            """
            listKey = self.request.get("listkey")
            offset = self.request.get("offset")
            if listKey:
                bkdb = bkdata.BKdata.all()
                bkdb.filter("mtngflg",True)
                bkdb.filter("webknskflg",True)
                bkdb.filter("nyrykkisyID", CorpOrg_key)
                bkdb.filter("nyrykstnID", Branch_Key)
                if listKey==u"全ての販売情報":
                    bkdb.filter("bkknShbt =", u"マンション等")
                    bkdb.filter("icons !=", None)
                    bkdb.order("icons")
                else:
                    bkdb.filter("icons", listKey)
                bkdb.order("-hykpint")
                bklist = bkdb.fetch(1000, 0)
                bklistlen = len(bklist)
                if bklist != None and bklistlen:
                    bklist.sort(key=lambda x:x.hykpint, reverse=True)
                if offset:
                    bklist=bklist[int(offset):int(offset) + 9]
                    #bklist=bkdb.fetch(10, offset=int(offset))
                else:
                    bklist=bklist[0:9]
                    #bklist=bkdb.fetch(10, 0)
                list = []
                for bkd in bklist:
                    list.append(self.makedata(bkd,media))
                entitys["bkdatalist"] = list
                if offset:
                    offsetnext = int(offset)+10 if int(offset)+10 <= bklistlen else 0
                    if offsetnext:
                        entitys["offsetnext"] = self.request.url.split(u'?')[0] + u"?offset=" + str(offsetnext) + u"&listkey=" + listKey + u"&media=" + media
                    pre = int(offset)-10 if int(offset) >=10 and int(offset) -10 <= bklistlen else 0
                    if pre:
                        entitys["offsetpre"] = self.request.url.split(u'?')[0] + u"?offset=" + str(pre) + u"&listkey=" + listKey + u"&media=" + media
                """
                https://s-style-hrd.appspot.com/show/s-style/hon/www.chikusaku-mansion.com/bkdata/article.html?id=59&media=web
                """
                if Command == "bklist":
                    entitys["bkdataurl"] = u"https://" + Domain + u"/show/" + CorpOrg_key + u"/" + Branch_Key + u"/" + Sitename + u"/bkdata/article.html?media=" + media + u"&id="
                elif Command == "bklistm":
                    entitys["bkdataurl"] = u"https://" + Domain + u"/show/" + CorpOrg_key + u"/" + Branch_Key + u"/" + Sitename + u"/bkdatam/articlem.html?media=" + media + u"&id="
                elif Command == "bklistsp":
                    entitys["bkdataurl"] = u"https://" + Domain + u"/show/" + CorpOrg_key + u"/" + Branch_Key + u"/" + Sitename + u"/bkdata/article-sp.html?media=" + media + u"&id="
                entitys["listKey"] = listKey
                entitys["media"] = media
                entitys["Command"] = Command
                entitys["pcsite"] =  u"https://" + Domain + u"/show/" + CorpOrg_key + u"/" + Branch_Key + u"/" + Sitename + u"/bklist/bklist.html?media=" + media + u"&listkey=" + listKey
                entitys["spsite"] =  u"https://" + Domain + u"/show/" + CorpOrg_key + u"/" + Branch_Key + u"/" + Sitename + u"/bklistsp/bklist-sp.html?media=" + media + u"&listkey=" + listKey
            else:
                self.tmpl_val['error_msg'] = u'リストの情報が取得できませんでした。'
                templ = CorpOrg_key + u"/" + Branch_Key + u"/" + Sitename + u"/" + u"sorry.html"

        elif Command == "bklistmesID" or  Command == "bklistmesIDm" or Command == "bklistmesIDsp":
            """
            https://s-style-hrd.appspot.com/show/s-style/hon/www.chikusaku-mansion.com/bklistmesID/bklist.html?offset=0&media=web&mesID=537763
            https://s-style-hrd.appspot.com/show/s-style/hon/www.chikusaku-mansion.com/bklistmesID/bklist.html?offset=0&media=web&mesID=
            https://localhost:8080/show/s-style/hon/www.chikusaku-mansion.com/bklistmesID/bklist.html?offset=0&media=web&mesID=
            """
            mesid = self.request.get("mesID")
            title = self.request.get("title")
            offset = self.request.get("offset")
            if mesid:
                bkdb = bklistutl.getlistbyID(CorpOrg_key,mesid)
                bklist = bkdb.fetch(1000, 0)
                bklistlen = len(bklist)
                if bklist != None and bklistlen:
                    bklist.sort(key=lambda x:x.refbk.hykpint, reverse=True)
                if offset:
                    bklist=bklist[int(offset):int(offset) + 10]
                    #bklist=bkdb.fetch(10, offset=int(offset))
                else:
                    bklist=bklist[0:10]
                    #bklist=bkdb.fetch(10, 0)
                list = []
                for bkl in bklist:
                    list.append(self.makedata(bkl.refbk,media))
                entitys["bkdatalist"] = list
                if offset:
                    offsetnext = int(offset)+10 if int(offset)+10 <= bklistlen else 0
                    if offsetnext:
                        entitys["offsetnext"] = self.request.url.split(u'?')[0] + u"?offset=" + str(offsetnext) + u"&mesID=" + mesid + "&title=" + title + u"&media=" + media
                    pre = int(offset)-10 if int(offset) -10 >= 0 else -1
                    if pre >= 0:
                        entitys["offsetpre"] = self.request.url.split(u'?')[0] + u"?offset=" + str(pre) + u"&mesID=" +  mesid + "&title=" + title +  u"&media=" + media
                """
                https://s-style-hrd.appspot.com/show/s-style/hon/www.chikusaku-mansion.com/bkdata/article.html?id=59&media=web
                """
                if Command == "bklistmesID":
                    entitys["bkdataurl"] = u"https://" + Domain + u"/show/" + CorpOrg_key + u"/" + Branch_Key + u"/" + Sitename + u"/bkdata/article.html?media=" + media + u"&id="
                elif Command == "bklistmesIDm":
                    entitys["bkdataurl"] = u"https://" + Domain + u"/show/" + CorpOrg_key + u"/" + Branch_Key + u"/" + Sitename + u"/bkdatam/articlem.html?media=" + media + u"&id="
                elif Command == "bklistmesIDsp":
                    entitys["bkdataurl"] = u"https://" + Domain + u"/show/" + CorpOrg_key + u"/" + Branch_Key + u"/" + Sitename + u"/bkdata/article-sp.html?media=" + media + u"&id="
                entitys["listKey"] = title
                entitys["media"] = media
                entitys["mesID"] = mesid
                entitys["Command"] = Command
                entitys["pcsite"] =  u"https://" + Domain + u"/show/" + CorpOrg_key + u"/" + Branch_Key + u"/" + Sitename + u"/bklistmesID/bklist.html?media=" + media + u"&title=" + title + u"&mesID=" +  mesid
                entitys["spsite"] =  u"https://" + Domain + u"/show/" + CorpOrg_key + u"/" + Branch_Key + u"/" + Sitename + u"/bklistmesIDsp/bklist-sp.html?media=" + media + u"&title=" + title + u"&mesID=" +  mesid
            else:
                self.tmpl_val['error_msg'] = u'リストの情報が取得できませんでした。'
                templ = CorpOrg_key + u"/" + Branch_Key + u"/" + Sitename + u"/" + u"sorry.html"

        else:
            self.tmpl_val['error_msg'] = u'不正なアドレスへのアクセスです。'
            templ = CorpOrg_key + "/" + Branch_Key + "/" + Sitename + "/" + "sorry.html"

        self.tmpl_val["data"] = entitys
        path = os.path.dirname(__file__) + '/../templates/' + templ
        self.response.out.write(template.render(path, self.tmpl_val))

    def post(self,**kwargs):

        self.get(**kwargs)


    def urlencode2(self,value, encoding):
        return urllib.quote_plus(value.encode(encoding))

    def makedata(self,bkd,media):
        """
        query_str = u"SELECT * FROM Blob WHERE CorpOrg_key = '" + bkd.nyrykkisyID + u"' AND Branch_Key = '" + bkd.nyrykstnID + u"' AND bkID = '" + bkd.bkID + u"' AND media = '" + media + u"' ORDER BY pos ASC"
        blobs = db.GqlQuery (query_str)
        b2 = []
        webkkkk = False
        if bkd.kukkTnsiKbn in [u"広告可",u"一部可（インターネット）",u"広告可（但し要連絡）"]:
            webkkkk = True
        heimenzu = None
        for c in blobs:
            if c.pos != u"平面図":
                b2.append(c)
            else :
                heimenzu = c
        totitubo = None
        if bkd.tcMnsk2:
            totitubo = float(int(bkd.tcMnsk2 * 0.3025 * 100))/100
        tatemonotubo = None
        if bkd.ttmnMnsk1:
            tatemonotubo = float(int(bkd.ttmnMnsk1 * 0.3025 * 100))/100
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
        #【{{data.bkdata.bkID}}】{{data.bkdata.ttmnmi}}について
        if bkd.ttmnmi:
            mailmsg = u'【' + bkd.bkID + u'】' + bkd.bkknShmk + u" " + bkd.ttmnmi + u"について"
        else:
            mailmsg = u'【' + bkd.bkID + u'】' + bkd.bkknShmk + u"について"

        #getname(cls,co,br,div,tod,ad1,ad2):
        gakkuS = getname(bkd.nyrykkisyID,bkd.nyrykstnID,u"小学校区",bkd.tdufknmi,bkd.shzicmi1,bkd.shzicmi2)
        bkdata = GqlJsonEncoder.GQLmoneyfmt(bkd)
        entitys = {"auth":self.auth, "mailmsg":mailmsg, "bkdata":bkdata,"picdata":b2,"kakakuM":kakakuM,"totitubo":totitubo,"tatemonotubo":tatemonotubo,"tknngtG":tknngt,"heimenzu":heimenzu,"gakkuS":gakkuS,"webkkkk":webkkkk}
        """
        entitys = bkd.makedata(media)
        entitys["auth"]=self.auth
        return entitys

    def makedata_old(self,bkd,media):
        query_str = u"SELECT * FROM Blob WHERE CorpOrg_key = '" + bkd.nyrykkisyID + u"' AND Branch_Key = '" + bkd.nyrykstnID + u"' AND bkID = '" + bkd.bkID + u"' AND media = '" + media + u"' ORDER BY pos ASC"
        blobs = db.GqlQuery (query_str)
        b2 = []
        heimenzu = None
        for c in blobs:
            if c.pos != u"平面図":
                b2.append(c)
            else :
                heimenzu = c
        kakakuM = None
        if bkd.kkkuCnryu:
            kakakuM = GqlJsonEncoder.floatfmt(int(bkd.kkkuCnryu/100)/100)
        tknngt = None
        if bkd.cknngtSirk:
            tknngt = bkd.cknngtSirk.year
            if int(tknngt) < 1989:
                tknngt = u"昭和" + str(tknngt-1925) + u"年"
            elif int(tknngt) >= 1989:
                tknngt = u"平成" + str(tknngt-1988) + u"年"
            else:
                tknngt = tknngt + u"年"
        bkdata = GqlJsonEncoder.GQLmoneyfmt(bkd)
        entitys = {"bkdata":bkdata,"picdata":b2,"kakakuM":kakakuM,"tknngtG":tknngt,"heimenzu":heimenzu}
        return entitys