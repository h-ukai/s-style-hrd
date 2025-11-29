# -*- coding: utf-8 -*-

# Copyright 2008 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Utility classes and methods for use with simplejson and appengine.

Provides both a specialized simplejson encoder, GqlEncoder, designed to simplify
encoding directly from GQL results to JSON. A helper function, encode, is also
provided to further simplify usage.

  GqlEncoder: Adds support for GQL results and properties to simplejson.
  encode(input): Direct method to encode GQL objects as JSON.


このページから呼び出されるデータは基本的にFloatが整形される ***,***,***.*****ので注意

"""
#from google.appengine.dist import use_library
#use_library('django', '1.2')

#from google.appengine.ext import webapp
import webapp2
import timemanager
import re
from google.appengine.ext import db
import datetime
import sys, traceback
from google.appengine.api import mail
from google.appengine.api import memcache
import urllib
import logging

"""
GQLから検索するmodelkindはすべてインポートすること
"""
from models.bkdata import BKdata
from models.bksearchaddress import bksearchaddresslist
from models.member import member
from models.message import Message
from models.address import address1
from models.address import address2
from models.address import address3
from models.ziplist import ziplist
from models.blob import Blob
from models.station import Station
from models.member import member

from models.bksearchaddress import getname

from copy import deepcopy
import messageManager
from GqlEncoder import GqlJsonEncoder
from bklistutl import bklistutl
import calendar
from calendar import monthrange
from qreki import Kyureki
import config
from dataProvider.bkdataSearchProvider import bkdataSearchProbider

class jsonservice(webapp2.RequestHandler):


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

    def bklistGenerator(self,list):
        res = ""
        #list_key=MesThread.bbs_key.get_value_for_datastore(thread)
        for i in range(0,list.count(1000000),50):
            if not res == "":
                s = GqlJsonEncoder(ensure_ascii=False).encode(db.get(list[i:i+50]))
                res = res[0:-1] + ", " + s[1:]
            else:
                res += GqlJsonEncoder(ensure_ascii=False).encode(db.get(list[i:i+50]))
        return res

    def _send_mail(self, email):
        msgbody = ''
        for key in self.request.arguments():
            msgbody += key + " : " + self.request.get(key) + "\n"
        message = mail.EmailMessage()
        message.sender = '"Another login utility" <' + config.ADMIN_EMAIL + '>'
        message.to = email
        message.subject = 'regist confirmation'
        message.body = msgbody
        message.send()

    def makedata(self,bkd,media):
        query_str = u"SELECT * FROM Blob WHERE CorpOrg_key = '" + bkd.nyrykkisyID + u"' AND Branch_Key = '" + bkd.nyrykstnID + u"' AND bkID = '" + bkd.bkID + u"' AND media = '" + media + u"' ORDER BY pos ASC"
        blobs = db.GqlQuery (query_str)
        b2 = []
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
            tknngt = timemanager.utc2jst_date(bkd.cknngtSirk).year
            if int(tknngt) < 1989:
                tknngt = u"昭和" + str(tknngt-1925) + u"年"
            elif int(tknngt) >= 1989:
                tknngt = u"平成" + str(tknngt-1988) + u"年"
            else:
                tknngt = tknngt + u"年"
        #getname(cls,co,br,div,tod,ad1,ad2):
        gakkuS = getname(bkd.nyrykkisyID,bkd.nyrykstnID,u"小学校区",bkd.tdufknmi,bkd.shzicmi1,bkd.shzicmi2)
        #data = GqlJsonEncoder.GQLmoneyfmt(bkd) #2014/02/02　comment out
        data = bkd
        entitys = {"bkdatakey":bkd.key(),"bkdata":data,"picdata":b2,"kakakuM":kakakuM,"totitubo":totitubo,"tatemonotubo":tatemonotubo,"tknngtG":tknngt,"heimenzu":heimenzu,"gakkuS":gakkuS}
        return entitys

    def senddata(self,bklist,media):
        if self.callback:
            self.response.headers['Content-Type'] = "text/javascript"
            self.response.out.write( self.callback + "(")
    #                            (self.callback, self.listGenerator(entitys)))
        else:
            self.response.headers['Content-Type'] = "application/json"

        self.response.out.write("[")
        resdata = ""
        gqljson = GqlJsonEncoder(ensure_ascii=False)
        field = self.request.get("field")
        for bke in bklist:
            bk = bke.refbk
            #sumple jQuery17109012071304023266_1327365113283([{"情報": {"null":
            if resdata <> "":
                self.response.out.write(", ")
            if field == "normal":
                gqljson.fieldname = "normal"
                resdata = u'{"info":%s,"bk":%s,"key":"%s"}' %( gqljson.encode(bke) ,gqljson.encode(self.makedata(bk,media)),str(bke.key()))
            else:
                resdata = u'{"情報":%s,"物件":%s,"key":"%s"}' %( gqljson.encode(bke) ,gqljson.encode(self.makedata(bk,media)),str(bke.key()))
            self.response.out.write(resdata)
        self.response.out.write("]")
        if self.callback:
            self.response.out.write(");")
    #                            (self.callback, self.listGenerator(entitys)))
        return


    def get(self,**kwargs):
        self.post()

    def post(self,**kwargs):

        self.source = self.request.get("source")
        self.com = self.request.get("com")
        self.search_key = self.request.get("search_key")
        self.callback = self.request.get("callback")
        GqlJsonEncoder.fieldname = self.request.get("fieldname")
        GqlJsonEncoder.floatformat = self.request.get("floatformat")
        gqlstr = u""
        where = u""
        entitys = []

        self.corp_name = "s-style" #本来はあり得ない企業名で初期化することそうすればmemberを得られない
        self.branch_name = "hon"

        """
        #セッションチェック
        ssn = session.Session(self.request, self.response)
        if ssn.chk_ssn():
            user = ssn.get_ssn_data('user')
            corp = user.CorpOrg_key_name
        """

        try:
            if self.com == u"address1":
                todofukenmei = self.request.get("todofukenmei")
                gqlstr = u"SELECT * FROM address1"
                if todofukenmei:
                    where += u" WHERE" if where == u"" else u" AND"
                    where += u" todofukenmei = '" + todofukenmei + u"'"
                if self.search_key:
                    where += u" WHERE" if where == u"" else u" AND"
                    where += u" shikutyosonmei >= '" + self.search_key + u"' and shikutyosonmei < '" + self.search_key + u"\uFFFD'"
                    where += u" ORDER BY shikutyosonmei"
                if gqlstr!= '':
                    gqlstr += where
                    entitys = db.GqlQuery(gqlstr)

    #https://s-style-hrd.appspot.com/jsonservice?com=address2&todofukenmei=%E6%84%9B%E7%9F%A5%E7%9C%8C&shikutyosonmei=%E5%90%8D%E5%8F%A4%E5%B1%8B%E5%B8%82%E5%8D%83%E7%A8%AE%E5%8C%BA&search_key=
            elif self.com == u"address2":
                todofukenmei = self.request.get("todofukenmei")
                shikutyosonmei = self.request.get("shikutyosonmei")
                gqlstr = u"SELECT * FROM address2"
                if todofukenmei:
                    where += u" WHERE" if where == u"" else u" AND"
                    where += u" todofukenmei = '" + todofukenmei + u"'"
                if shikutyosonmei:
                    where += u" WHERE" if where == u"" else u" AND"
                    where += u" shikutyosonmei = '" + shikutyosonmei + u"'"
                if self.search_key:
                    where += u" WHERE" if where == u"" else u" AND"
                    where += u" ooazatyotyome >= '" + self.search_key + u"' and ooazatyotyome < '" + self.search_key + u"\uFFFD'"
                    where += u" ORDER BY ooazatyotyome"
                if gqlstr!= '':
                    gqlstr += where
                    entitys = db.GqlQuery(gqlstr)

            elif self.com == u"address12":
                todofukenmei = self.request.get("todofukenmei")
                gqlstr = u"SELECT * FROM ziplist"
                if todofukenmei:
                    where += u" WHERE" if where == u"" else u" AND"
                    where += u" todofukenmei = '" + todofukenmei + u"'"
                if self.search_key:
                    where += u" WHERE" if where == u"" else u" AND"
                    where += u" shikutyosonmei >= '" + self.search_key + u"' and shikutyosonmei < '" + self.search_key + u"\uFFFD'"
                if gqlstr!= '':
                    gqlstr += where
                    entitys = db.GqlQuery(gqlstr)

    #https://s-style-hrd.appspot.com/jsonservice?com=address2&todofukenmei=%E6%84%9B%E7%9F%A5%E7%9C%8C&shikutyosonmei=%E5%90%8D%E5%8F%A4%E5%B1%8B%E5%B8%82%E5%8D%83%E7%A8%AE%E5%8C%BA&search_key=
            elif self.com == u"address22":
                todofukenmei = self.request.get("todofukenmei")
                shikutyosonmei = self.request.get("shikutyosonmei")
                gqlstr = u"SELECT * FROM address2"
                if todofukenmei:
                    where += u" WHERE" if where == u"" else u" AND"
                    where += u" todofukenmei = '" + todofukenmei + u"'"
                if shikutyosonmei:
                    where += u" WHERE" if where == u"" else u" AND"
                    where += u" shikutyosonmei = '" + shikutyosonmei + u"'"
                if self.search_key:
                    where += u" WHERE" if where == u"" else u" AND"
                    where += u" ooazatyotyome >= '" + self.search_key + u"' and ooazatyotyome < '" + self.search_key + u"\uFFFD'"
                if gqlstr!= '':
                    gqlstr += where
                    entitys = db.GqlQuery(gqlstr)

    #https://s-style-hrd.appspot.com/jsonservice?com=zip2address&todofukenmei=愛知県&shikutyosonmei=名古屋市千種区&search_key=4
            elif self.com == u"zip2address":
                todofukenmei = self.request.get("todofukenmei")
                shikutyosonmei = self.request.get("shikutyosonmei")
                gqlstr = u"SELECT * FROM ziplist"
                if todofukenmei:
                    where += u" WHERE" if where == u"" else u" AND"
                    where += u" pref = '" + todofukenmei + u"'"
                if shikutyosonmei:
                    where += u" WHERE" if where == u"" else u" AND"
                    where += u" city = '" + shikutyosonmei + u"'"
                if self.search_key:
                    where += u" WHERE" if where == u"" else u" AND"
                    where += u" zipcode >= '" + self.search_key + u"' and zipcode < '" + self.search_key + u"\uFFFD'"
                if gqlstr!= '':
                    gqlstr += where
                    entitys = db.GqlQuery(gqlstr)

    #https://s-style-hrd.appspot.com/jsonservice?com=address2zip&&search_key=
            elif self.com == u"address2zip":
                gqlstr = u"SELECT * FROM ziplist"
                if self.search_key:
                    where += u" WHERE" if where == u"" else u" AND"
                    where += u" fulladdress >= '" + self.search_key + u"' and fulladdress < '" + self.search_key + u"\uFFFD'"
                if gqlstr!= '':
                    gqlstr += where
                    entitys = db.GqlQuery(gqlstr)

    #https://s-style-hrd.appspot.com/jsonservice?com=BKdata&sksijky=請求チェック
            elif self.com == u"BKdata2":
                query = db.Query(BKdata, keys_only=True)
                bbchntikbn = self.request.get("bbchntikbn")
                if bbchntikbn:
                    query.filter("bbchntikbn =", bbchntikbn)
                dtsyuri = self.request.get("dtsyuri")
                if dtsyuri:
                    query.filter("dtsyuri =",dtsyuri )
                todofukenmei = self.request.get("todofukenmei")
                if todofukenmei:
                    query.filter("tdufknmi =",todofukenmei )
                sksijky = self.request.get("sksijky")
                if sksijky:
                    query.filter("sksijky =",sksijky )
                entitys = self.listGenerator(query.fetch(limit=100))
                    #entitys = self.formatBKdata(entitys)

        #https://s-style-hrd.appspot.com/jsonservice?com=BKdata&sksijky=請求チェック
            elif self.com == u"BKdata":
                sksijky = self.request.get("sksijky")
                gqlstr = u"SELECT * FROM BKdata"
                bbchntikbn = self.request.get("bbchntikbn")
                if bbchntikbn:
                    where += u" WHERE" if where == u"" else u" AND"
                    where += u" bbchntikbn = '" + bbchntikbn + u"'"
                dtsyuri = self.request.get("dtsyuri")
                if dtsyuri:
                    where += u" WHERE" if where == u"" else u" AND"
                    where += u" dtsyuri = '" + dtsyuri + u"'"
                todofukenmei = self.request.get("todofukenmei")
                if todofukenmei:
                    where += u" WHERE" if where == u"" else u" AND"
                    where += u" tdufknmi = '" + todofukenmei + u"'"
                if sksijky:
                    where += u" WHERE" if where == u"" else u" AND"
                    where += u" sksijky = '" + sksijky +"'"
                where += u" ORDER BY kknnngp DESC"
                where += u" LIMIT 500"
                if gqlstr!= '':
                    gqlstr += where
                    #entitys = self.listGenerator(db.GqlQuery(gqlstr))
                    entitys = db.GqlQuery(gqlstr)

        #https://s-style-hrd.appspot.com/jsonservice?com=BKdataicon&icon=トップ&media=web
        #https://localhost:8080/jsonservice?com=BKdataicon&icon=トップ&media=web
            elif self.com == u"BKdataicon":
                listnam = 50
                Domain = "s-style-hrd.appspot.com"
                corp = "s-style" #本来はあり得ない企業名で初期化することそうすればmemberを得られない
                branch = "hon"
                sitename = "www.chikusaku-mansion.com"
                """
                #セッションチェック
                ssn = session.Session(self.request, self.response)
                if ssn.chk_ssn():
                    user = ssn.get_ssn_data('user')
                    corp = user.CorpOrg_key_name
                """

                icon = self.request.get("icon")
                offset = self.request.get("offset")
                media = self.request.get("media")
                if icon:
                    bkdb = BKdata.all()
                    bkdb.filter("mtngflg",True)
                    bkdb.filter("webknskflg",True)
                    bkdb.filter("nyrykkisyID", corp)
                    bkdb.filter("nyrykstnID", branch)
                    if icon == u"全て":
                        bkdb.filter("icons != ","null")
                    else:
                        bkdb.filter("icons", icon)
                    bkdb.order("icons")
                    bkdb.order("hykpint")
                    if offset:
                        bklist=bkdb.fetch(listnam, offset=int(offset))
                    else:
                        bklist=bkdb.fetch(listnam, 0)
                    list = []
                    for bkd in bklist:
                        list.append(self.makedata(bkd,media))
                    entitys = {}
                    entitys["bkdatalist"] = list
                    if offset:
                        entitys["offsetnext"] = self.request.url.split(u'?')[0] + u"?offset=" + str(int(offset) + listnam) + u"&icon=" + icon + u"&media=" + media
                        pre = int(offset)-listnam if int(offset) >= listnam else 0
                        entitys["offsetpre"] = self.request.url.split(u'?')[0] + u"?offset=" + str(pre) + u"&icon=" + icon + u"&media=" + media
                    """
                    https://s-style-hrd.appspot.com/show/s-style/hon/www.chikusaku-mansion.com/bkdata/article.html?id=59&media=web
                    """
                    entitys["bkdataurl"] = u"https://" + Domain + u"/show/" + corp + u"/" + branch + u"/" + sitename + u"/bkdata/article.html?media=" + media + u"&id="
                    entitys["icon"] = icon
                    entitys["media"] = media

        #https://s-style-hrd.appspot.com/jsonservice?com=BKalldata
        #https://localhost:8080/jsonservice?com=BKalldata
            elif self.com == u"BKalldata":
                Domain = "s-style-hrd.appspot.com"
                corp = "s-style" #本来はあり得ない企業名で初期化することそうすればmemberを得られない
                branch = "hon"
                sitename = "www.chikusaku-mansion.com"
                """
                #セッションチェック
                ssn = session.Session(self.request, self.response)
                if ssn.chk_ssn():
                    user = ssn.get_ssn_data('user')
                    corp = user.CorpOrg_key_name
                """
                icon = self.request.get("icon")
                offset = self.request.get("offset")
                media = self.request.get("media")
                bkdb = BKdata.all()
                bkdb.filter("mtngflg",True)
                bkdb.filter("webknskflg",True)
                bkdb.filter("nyrykkisyID", corp)
                bkdb.filter("nyrykstnID", branch)
                bkdb.filter("bbchntikbn",u"売買")
                bkdb.filter("bkknShbt",u"マンション等")
                bkdb.filter("dtsyuri",u"サンプル")
                bklist=bkdb.fetch(1000, 0)
                list1 = []
                for bkd in bklist:
                    list1.append(self.makedata(bkd,media))
                bkdb = None
                bkdb = BKdata.all()
                bkdb.filter("mtngflg",True)
                bkdb.filter("webknskflg",True)
                bkdb.filter("nyrykkisyID", corp)
                bkdb.filter("nyrykstnID", branch)
                bkdb.filter("bbchntikbn",u"売買")
                bkdb.filter("bkknShbt",u"マンション等")
                bkdb.filter("dtsyuri",u"物件")
                bkdb.filter("idkd !=",None)
                bklist=bkdb.fetch(1000, 0)
                bklist.sort(key=lambda obj: obj.kkkuCnryu)
                list2 = []
                for bkd in bklist:
                    list2.append(self.makedata(bkd,media))
                entitys = {}
                entitys["bksumple"] = list1
                entitys["bkdatalist"] = list2

    #https://s-style-hrd.appspot.com/jsonservice?com=bkdchk
            elif self.com == u"bkdchk":
                gqlstr = u"SELECT * FROM BKdata"
                bbchntikbn = self.request.get("bbchntikbn")
                if bbchntikbn:
                    where += u" WHERE" if where == u"" else u" AND"
                    where += u" bbchntikbn = '" + bbchntikbn + u"'"
                dtsyuri = self.request.get("dtsyuri")
                if dtsyuri:
                    where += u" WHERE" if where == u"" else u" AND"
                    where += u" dtsyuri = '" + dtsyuri + u"'"
                todofukenmei = self.request.get("todofukenmei")
                if todofukenmei:
                    where += u" WHERE" if where == u"" else u" AND"
                    where += u" tdufknmi = '" + todofukenmei + u"'"
                shzicmi1 = self.request.get("shzicmi1")
                if shzicmi1:
                    where += u" WHERE" if where == u"" else u" AND"
                    where += u" shzicmi1 = '" + shzicmi1 +"'"
                tcMnsk2 = self.request.get("tcMnsk2")
                ttmnMnsk1 = self.request.get("ttmnMnsk1")
                snyuMnskSyuBbnMnsk2 = self.request.get("snyuMnskSyuBbnMnsk2")
                if tcMnsk2:
                    where += u" WHERE" if where == u"" else u" AND"
                    where += u" tcMnsk2 > " + str(float(tcMnsk2) * 0.8) + u" AND tcMnsk2 < " + str(float(tcMnsk2) * 1.2)
                elif ttmnMnsk1:
                    where += u" WHERE" if where == u"" else u" AND"
                    where += u" ttmnMnsk1 > " + str(float(ttmnMnsk1) * 0.8) + u" AND  ttmnMnsk1 < " + str(float(ttmnMnsk1) * 1.2)
                elif snyuMnskSyuBbnMnsk2:
                    where += u" WHERE" if where == u"" else u" AND"
                    where += u" snyuMnskSyuBbnMnsk2 > " + str(float(snyuMnskSyuBbnMnsk2) * 0.8) + u" AND snyuMnskSyuBbnMnsk2 < " + str(float(snyuMnskSyuBbnMnsk2) * 1.2)
                if self.search_key:
                    where += u" WHERE" if where == u"" else u" AND"
                    where += u" shzicmi2 = '" + self.search_key + u"'"
                where += u" LIMIT 100"
                if gqlstr!= '':
                    gqlstr += where
                    entitys = db.GqlQuery(gqlstr)
                    #entitys = self.formatBKdata(entitys)

    #https://s-style-hrd.appspot.com/jsonservice?com=line
            elif self.com == u"line":
                gqlstr = u"SELECT * FROM Station"
                pref = self.request.get("pref")
                if pref:
                    where += u" WHERE" if where == u"" else u" AND"
                    where += u" pref_cd = '" + self.code[pref] + u"'"
                if self.search_key:
                    where += u" WHERE" if where == u"" else u" AND"
                    where += u" line_name >= '" + self.search_key + u"' and line_name < '" + self.search_key + u"\uFFFD'"
                if gqlstr!= '':
                    gqlstr += where + "ORDER BY line_name,line_sort"
                    entitys = db.GqlQuery(gqlstr)
                    entitysb = []
                    for b in entitys:
                        for t in entitysb:
                            if t.line_cd == b.line_cd:
                                break
                        else:
                            entitysb.append(b)
                    entitys = deepcopy(entitysb)

    #https://s-style-hrd.appspot.com/jsonservice?com=station&pref=愛知県&line=名鉄本線
    #https://localhost:8080/jsonservice?com=station&pref=23&line=東海道線
            elif self.com == u"station":
                gqlstr = u"SELECT * FROM Station"
                pref = self.request.get("pref")
                if pref:
                    where += u" WHERE" if where == u"" else u" AND"
                    where += u" pref_cd = '" + self.code[pref] + u"'"
                line = self.request.get("line")
                if line:
                    where += u" WHERE" if where == u"" else u" AND"
                    where += u" line_name = '" + line + u"'"
                if self.search_key:
                    where += u" WHERE" if where == u"" else u" AND"
                    where += u" station_name >= '" + self.search_key + u"' and station_name < '" + self.search_key + u"\uFFFD'"  + "ORDER BY station_name"
                else:
                    where += "ORDER BY station_sort"
                if gqlstr!= '':
                    gqlstr += where
                    entitys = db.GqlQuery(gqlstr)


    #https://s-style-hrd.appspot.com/jsonservice?com=member&memberID=
            elif self.com == u"member":
                gqlstr = u"SELECT * FROM member"
                memberID = self.request.get("memberID")
                if memberID:
                    where += u" WHERE" if where == u"" else u" AND"
                    where += u" memberID = '" + memberID + u"'"
                corp = "s-style" #本来はあり得ない企業名で初期化することそうすればmemberを得られない

                """
                #セッションチェック
                ssn = session.Session(self.request, self.response)
                if ssn.chk_ssn():
                    user = ssn.get_ssn_data('user')
                    corp = user.CorpOrg_key_name
                """

                where += u" WHERE" if where == u"" else u" AND"
                where += u" CorpOrg_key_name = '" + corp + u"'"
                if gqlstr!= '':
                    gqlstr += where
                    entitys = db.GqlQuery(gqlstr)


    #https://s-style-hrd.appspot.com/jsonservice?com=getmemName&search_key=
    #https://localhost:8080/jsonservice?com=getmemName&search_key=
    #com：getmemName
    #よみがなから顧客情報を取得します
    #パラメータ：search_key(jQuery-autocomplete:request.termオブジェクト)



            elif self.com == u"getmemName":
                gql = member.all()
                if self.search_key:
                    gql.filter(" yomi >= " ,self.search_key)
                    gql.filter(" yomi < " ,self.search_key + u"\uFFFD'" )
                corp = self.request.get("corp")
                corp = "s-style" #本来はあり得ない企業名で初期化することそうすればmemberを得られない
                #セッションチェック
                #ssn = session.Session(self.request, self.response)
                #if ssn.chk_ssn():
                #    user = ssn.get_ssn_data('user')
                #    corp = user.CorpOrg_key_name

                gql.filter(" CorpOrg_key_name = " ,corp)
                gql.order("yomi")
                gql.order("phone")
                gql.order("sitename")
                entitys = gql.fetch(1000)


    #https://s-style-hrd.appspot.com/jsonservice?com=getmemID&memID=
    #com：getmemID
    #顧客IDから顧客情報を取得します
    #パラメータ：memID
    #戻り値
    #　　　　上記と同じです

            elif self.com == u"getmemID":
                gql = member.all()
                memberID = self.request.get("memID")
                if memberID:
                    gql.filter(" memberID >= " ,memberID)
                    gql.filter(" memberID < " ,memberID + u"\uFFFD'" )
                corp = self.request.get("corp")
                corp = "s-style" #本来はあり得ない企業名で初期化することそうすればmemberを得られない

                """
                #セッションチェック
                ssn = session.Session(self.request, self.response)
                if ssn.chk_ssn():
                    user = ssn.get_ssn_data('user')
                    corp = user.CorpOrg_key_name
                """

                gql.filter(" CorpOrg_key_name = " ,corp)
                gql.order("memberID")
                gql.order("sitename")
                entitys = gql.fetch(1000)


    #https://s-style-hrd.appspot.com/jsonservice?com=getmemTel&memTel=
    #com：getmemTel
    #顧客電話番号から顧客情報を取得します
    #パラメータ：memTel
    #戻り値

            elif self.com == u"getmemTel":
                gql = member.all()
    #            gql.filter(" co = " ,corp)
                memTel = self.request.get("memTel")
                if memTel:
                    gql.filter(" phone >= " ,memTel)
                    gql.filter(" phone < " ,memTel + u"\uFFFD'" )
                corp = self.request.get("corp")
                corp = "s-style" #本来はあり得ない企業名で初期化することそうすればmemberを得られない

                """
                #セッションチェック
                ssn = session.Session(self.request, self.response)
                if ssn.chk_ssn():
                    user = ssn.get_ssn_data('user')
                    corp = user.CorpOrg_key_name
                """

                gql.filter(" CorpOrg_key_name = " ,corp)
                gql.order("phone")
                gql.order("sitename")
                if not gql.count(1):

                    gql = member.all()
        #            gql.filter(" co = " ,corp)
                    memTel = self.request.get("memTel")
                    if memTel:
                        gql.filter(" mobilephone >= " ,memTel)
                        gql.filter(" mobilephone < " ,memTel + u"\uFFFD'" )
                    corp = self.request.get("corp")
                    corp = "s-style" #本来はあり得ない企業名で初期化することそうすればmemberを得られない

                    """
                    #セッションチェック
                    ssn = session.Session(self.request, self.response)
                    if ssn.chk_ssn():
                        user = ssn.get_ssn_data('user')
                        corp = user.CorpOrg_key_name
                    """

                    gql.filter("CorpOrg_key_name = " ,corp)
                    gql.order("mobilephone")
                    gql.order("sitename")
                entitys = gql.fetch(1000)

    #https://s-style-hrd.appspot.com/jsonservice?com=getmemTel&mail=
    #com：getmemmail
    #顧客メールアドレスから顧客情報を取得します
    #パラメータ：memTel
    #戻り値

            elif self.com == u"getmemmail":
                gql = member.all()
    #            gql.filter(" co = " ,corp)
                memmail = self.request.get("mail")
                if memmail:
                    gql.filter(" mail >= " ,memmail)
                    gql.filter(" mail < " ,memmail + u"\uFFFD'" )
                corp = self.request.get("corp")
                corp = "s-style" #本来はあり得ない企業名で初期化することそうすればmemberを得られない

                """
                #セッションチェック
                ssn = session.Session(self.request, self.response)
                if ssn.chk_ssn():
                    user = ssn.get_ssn_data('user')
                    corp = user.CorpOrg_key_name
                """

                gql.filter(" CorpOrg_key_name = " ,corp)
                gql.order("mail")
                gql.order("sitename")
                entitys = gql.fetch(1000)

    #https://s-style-hrd.appspot.com/jsonservice?com=chkAuthbymail&corp=s-style&site=www.chikusaku-mansion.com&mail=
    #com：chkAuthbymail
    #顧客メールアドレスから認証のあるなしを応答します
    #パラメータ：corp,site,mail
    #戻り値：{"Auth":"True","False"

            elif self.com == u"chkAuthbymail":
                gql = member.all()
    #            gql.filter(" co = " ,corp)
                memmail = self.request.get("mail")
                corp = self.request.get("corp")
                site = self.request.get("site")
                data = None
                if memmail and corp and site:
                    gql.filter(" mail = " ,memmail)
                    gql.filter(" sitename = " ,site)
                    gql.filter(" CorpOrg_key_name = " ,corp)
                    gql.filter(" seiyaku = ",u"未成約")
                    data = gql.fetch(1)
                if data:
                    entitys = {"Auth":"True"}
                else :
                    entitys = {"Auth":"False"}

    #https://s-style-hrd.appspot.com/jsonservice?com=chkAuthbymail&corp=s-style&site=www.chikusaku-mansion.com&sid=
    #com：chkAuthbysid
    #sidから認証のあるなしを応答します
    #パラメータ：corp,site,sid
    #戻り値：{"Auth":"True","False"}

            elif self.com == u"chkAuthbysid":
                gql = member.all()
    #            gql.filter(" co = " ,corp)
                sid = self.request.get("sid")
                corp = self.request.get("corp")
                site = self.request.get("site")
                data = None
                if sid and corp and site:
                    gql.filter(" sid = " ,sid)
                    gql.filter(" sitename = " ,site)
                    gql.filter(" CorpOrg_key_name = " ,corp)
                    gql.filter(" seiyaku = ",u"未成約")
                    data = gql.fetch(1)
                if data:
                    entitys = {"Auth":"True"}
                else :
                    entitys = {"Auth":"False"}

                """
    #hhttps://s-style-hrd.appspot.com/jsonservice?com=getcal&yearmonth=2011/12&tantoID=test222
    #https://localhost:8080/jsonservice?com=getcal&yearmonth=2011/12&tantoID=10
    #com：getmcal
    #指定年月一ヶ月分のカレンダーを返します。
    #パラメータ：yearmonth(yyyy/mm)
    #　　　　　　tantoID (担当のmemberID)
    #戻り値  {"日付":"yyyy/mm/dd","曜日":"火曜日","六曜":"大安","予定":[{フォロー履歴}]}

            elif self.com == u"getcal":
                yearmonth = self.request.get("yearmonth")
                memID =  self.request.get("tantoID")
                corp = self.request.get("corp")
                corp = "s-style" #本来はあり得ない企業名で初期化することそうすればmemberを得られない
                #セッションチェック
                #ssn = session.Session(self.request, self.response)
                #if ssn.chk_ssn():
                #    user = ssn.get_ssn_data('user')
                #    corp = user.CorpOrg_key_name
                if memID:
                    list = []
                    gql = member.all()
                    gql.filter(" memberID = " ,memID)
                    gql.filter(" CorpOrg_key_name = " ,corp)
                    reservationLower = datetime.datetime.strptime(yearmonth + "/1", "%Y/%m/%d")
                    #https://jinim.jp/archives/510
                    year, month = divmod(reservationLower.month + 1, 12)
                    year = year + reservationLower.year
                    #ちょうど割り切れたら12月で、マイナス1年。
                    if month == 0:
                        month = 12
                        year = year - 1
                    #入力日付がその月の月末なら、加算後月の日数を。
                    #そうじゃなければ入力日付の日。
                    day = reservationLower.day
                    if reservationLower.day > monthrange(year, month)[1]:
                        day = monthrange(year, month)[1]
                    reservationUpper = datetime.datetime(year=year, month=month, day=day)

                    for m in gql.fetch(1)[0].mytanto:
                        l = messageManager.messageManager.getmeslist(corp, m, done = False,reservationLower=reservationLower,reservationUpper=reservationUpper)
                        list = list + l
                    list.sort(key=lambda obj: obj.reservation)
                    c = calendar.Calendar()
                    l2 = []
                    for i in c.itermonthdates(reservationLower.year, reservationLower.month):
                        k = Kyureki.from_date(i)
                        d = {}
                        d[u"日付"]=datetime.datetime.strftime(i,"%Y/%m/%d")
                        d[u"曜日"]=WD[i.weekday()]
                        d[u"六曜"]=k.rokuyou()
                        l4 = []
                        for l3 in list:
                            if not l3.done and not l3.kill and l3.reservation.year == i.year and l3.reservation.month == i.month and l3.reservation.day == i.day :
                                l4.append(l3)
                        d[u"予定"]=l4
                        l2.append(d)
                entitys = l2
            """
    #hhttps://s-style-hrd.appspot.com/jsonservice?com=getcal&yearmonth=2011/12&tantoID=test222
    #https://localhost:8080/jsonservice?com=getcal&yearmonth=2011/12&tantoID=10
    #com：getmcal
    #指定年月一ヶ月分のカレンダーを返します。
    #パラメータ：yearmonth(yyyy/mm)
    #　　　　　　tantoID (担当のmemberID)
    #戻り値  {"日付":"yyyy/mm/dd","曜日":"火曜日","六曜":"大安","予定":[{フォロー履歴}]}

            elif self.com == u"getcal":
                yearmonth = self.request.get("yearmonth")
                memID =  self.request.get("tantoID")
                corp = self.request.get("corp")
                corp = "s-style" #本来はあり得ない企業名で初期化することそうすればmemberを得られない
                """
                #セッションチェック
                ssn = session.Session(self.request, self.response)
                if ssn.chk_ssn():
                    user = ssn.get_ssn_data('user')
                    corp = user.CorpOrg_key_name
                """
                if memID:
                    gql = member.all()
                    gql.filter(" memberID = " ,memID)
                    gql.filter(" CorpOrg_key_name = " ,corp)
                    reservationLower = datetime.datetime.strptime(yearmonth + "/1", "%Y/%m/%d")
                    #https://jinim.jp/archives/510
                    year, month = divmod(reservationLower.month + 1, 12)
                    year = year + reservationLower.year
                    #ちょうど割り切れたら12月で、マイナス1年。
                    if month == 0:
                        month = 12
                        year = year - 1
                    #入力日付がその月の月末なら、加算後月の日数を。
                    #そうじゃなければ入力日付の日。
                    day = reservationLower.day
                    if reservationLower.day > monthrange(year, month)[1]:
                        day = monthrange(year, month)[1]
                    reservationUpper = datetime.datetime(year=year, month=month, day=day)
                    mlist  = messageManager.messageManager.getmeslist(corp, gql.fetch(1)[0], done = False,reservationLower=reservationLower,reservationUpper=reservationUpper,order='reservation')
                    c = calendar.Calendar()
                    l2 = []
                    for i in c.itermonthdates(reservationLower.year, reservationLower.month):
                        k = Kyureki.from_date(i)
                        d = {}
                        d[u"日付"]=datetime.datetime.strftime(i,"%Y/%m/%d")
                        d[u"曜日"]=WD[i.weekday()]
                        d[u"六曜"]=k.rokuyou()
                        l4 = []
                        for l3 in mlist:
                            if not l3.done and not l3.kill and l3.reservation.year == i.year and l3.reservation.month == i.month and l3.reservation.day == i.day :
                                l4.append(l3)
                        d[u"予定"]=l4
                        l2.append(d)
                entitys = l2

    #https://s-style-hrd.appspot.com/jsonservice?com=getfol&memberID=
    #https://localhost:8080/jsonservice?com=getfol&memberID=1
    #com：getfol
    #フォロー履歴の一覧を取得します
    #パラメータ：memberID(hiddenフィールドmemberIDのvalue)
    #　　　　　　　 year(省略可能)
    #　　　　　　　 mon(省略可能)
    #        day(省略可能)

            elif self.com == u"getfol":
                memberID = self.request.get("memberID")
                year = self.request.get("yeaar")
                mon = self.request.get("mon")
                day = self.request.get("day")
                if memberID:
                    corp = "s-style" #本来はあり得ない企業名で初期化することそうすればmemberを得られない
                    """
                    #セッションチェック
                    ssn = session.Session(self.request, self.response)
                    if ssn.chk_ssn():
                        user = ssn.get_ssn_data('user')
                        corp = user.CorpOrg_key_name
                    """
                    meslist = messageManager.messageManager.getmeslistbyID(corp,memberID,order = "reservation",combkind=u"所有")

                    e2 = []
                    """
                        body = db.StringProperty(verbose_name=u"本文",multiline=True)
                        subject = db.StringProperty(verbose_name=u"表題")
                        kindname = db.StringProperty(verbose_name=u"アクション")
                        done = db.BooleanProperty(verbose_name=u"済",default=False)
                        kill = db.BooleanProperty(verbose_name=u"消",default=False)
                        timestamp = db.DateTimeProperty(auto_now_add = True,verbose_name=u"タイムスタンプ")
                        reservation = db.DateTimeProperty(auto_now_add = True,verbose_name=u"予定日")
                        reservationend = db.DateTimeProperty(auto_now_add = True,verbose_name=u"予定終了日")
                        commentTo = db.SelfReference(collection_name=u"refmes",verbose_name=u"コメント先")
                    """
                    for mes in meslist:
                        d2={}
                        d2[u"本文"] = mes.body
                        d2[u"表題"] = mes.subject
                        d2[u"アクション"] = mes.kindname
                        d2[u"済"] = mes.done
                        d2[u"予定日"] = mes.reservation
                        #比較はJSTで行うので変換は不要
                        if year:
                            year = int(year)
                            if mon:
                                mon = int(mon)
                                if day:
                                    day = int(day)
                                    b = datetime.date(year,mon,day)
                                    a = datetime.date(year,mon,day+1)
                                else:
                                    b = datetime.date(year,mon,1)
                                    a = datetime.date(year,mon+1,1)
                            else:
                                b = datetime.date(year,1,1)
                                a = datetime.date(year+1,1,1)
                            if mes.reservation < b or mes.reservation >= a:
                                continue
                        d2[u"予定終了日"] = mes.reservationend
                        d2[u"タイムスタンプ"] = mes.timestamp
                        try:
                            d2[u"コメント先"] = str(mes.commentTo.key())
                        except:
                            mes.commentTo = None
                            d2[u"コメント先"] = None
                        d2[u"key"] = mes.key().id()
                        e2.append(d2)
                    entitys = e2


    #https://s-style-hrd.appspot.com/jsonservice?com=addeditfol&body=てすとてすと&subject=表題&memfrom=test111&kindname=電話ありまくり
    #https://localhost:8080/jsonservice?com=addeditfol&body=てすとてすと&subject=表題&memfrom=7&key=2327&kindname=電話ありまくり
    #com：addeditfol
    #POST推奨
    #keyに対応するフォロー履歴を更新します。
    #keyが省略された場合フォロー履歴に一行追加します。
    #パラメータ：
    #   key(省略可能)
    #   body (本文)
    #   subject (表題)
    #   memfrom (メンバーID)
    #   kindname (アクション{メール,Tel,来店...etc})
    #   combkind (メッセージ種類[u"送信",u"受信",u"所有",u"参照"])
    #   done (省略可能:済)
    #   reservation (省略可能:予定日)(yyyy/mm/dd tt:mm:ss)
    #   reservationend (省略可能:予定終了日)(yyyy/mm/dd tt:mm:ss)
    #   memto　(省略可能:メッセージ宛先メンバーID)
    #   commentTo  (省略可能:コメント)
    #   mailto (省略可能：メール送信　member tanto)
    #戻り値：
    #   {key:}

            elif self.com == u"addeditfol":
                msgkey = self.request.get("key")
                body = self.request.get("body")
                sub = self.request.get("subject")
                kindname = self.request.get("kindname")
                combkind = self.request.get("combkind")
                done =  self.request.get("done")
                memfrom = self.request.get("memfrom")
                reservation = self.request.get("reservation")
                reservationend = self.request.get("reservationend")
                memto = self.request.get("memto")
                commentto = self.request.get("commentTo")
                mailto = self.request.get("mailto") #tanto member


                corp = self.request.get("corp")
                corp = "s-style" #本来はあり得ない企業名で初期化することそうすればmemberを得られない

                """
                #セッションチェック
                ssn = session.Session(self.request, self.response)
                if ssn.chk_ssn():
                    user = ssn.get_ssn_data('user')
                    corp = user.CorpOrg_key_name
                """

                meskey = messageManager.messageManager.post(corp, sub, body, done, memfrom, kindname, combkind, msgkey,reservation ,reservationend,memto, commentto,mailto)
                entitys = {"key":str(meskey.id())}

    #https://localhost:8080/jsonservice?com=removefol&key=
    #com：removefol
    #keyに対応するフォロー履歴を削除します。
    #パラメータ：
    #   key()
    #戻り値：
    #   {result:}

            elif self.com == u"removefol":
                msgkey = self.request.get("key")

                corp = "s-style" #本来はあり得ない企業名で初期化することそうすればmemberを得られない

                """
                #セッションチェック
                ssn = session.Session(self.request, self.response)
                if ssn.chk_ssn():
                    user = ssn.get_ssn_data('user')
                    corp = user.CorpOrg_key_name
                """
                messageManager.messageManager.killmesbyID(corp,msgkey)
                entitys = {"result":"OK"}

    #https://localhost:8080/jsonservice?com=getfolbyID&id=
    #com：getfolbyID
    #idに対応するフォロー履歴を取得します。
    #パラメータ：
    #   id
    #戻り値：
    #   メッセージ

            elif self.com == u"getfolbyID":
                id = self.request.get("id")

                corp = "s-style" #本来はあり得ない企業名で初期化することそうすればmemberを得られない

                """
                #セッションチェック
                ssn = session.Session(self.request, self.response)
                if ssn.chk_ssn():
                    user = ssn.get_ssn_data('user')
                    corp = user.CorpOrg_key_name
                """
                entitys = messageManager.messageManager.getmesbyID(corp,id)

    #https://localhost:8080/jsonservice?com=getfolbykey&key=
    #com：getfolbykey
    #keyに対応するフォロー履歴を取得します。
    #パラメータ：
    #   key
    #戻り値：
    #   メッセージ

            elif self.com == u"getfolbykey":
                key = self.request.get("key")

                corp = "s-style" #本来はあり得ない企業名で初期化することそうすればmemberを得られない

                """
                #セッションチェック
                ssn = session.Session(self.request, self.response)
                if ssn.chk_ssn():
                    user = ssn.get_ssn_data('user')
                    corp = user.CorpOrg_key_name
                """
                entitys = messageManager.messageManager.getmesbykey(corp,key)



            elif self.com == u"getmemlistbymesID":
                id = self.request.get("id")
                entitys = messageManager.messageManager.getmembymesID(id)

    #https://s-style-hrd.appspot.com/jsonservice?com=searchbkdata
    #サンプル取得用リクエスト
    #https://s-style-hrd.appspot.com/jsonservice?com=searchbkdata&dtsyuri=サンプル&submit=新規ページへ保存して検索
    #com：searchbkdata
    #物件検索を行い指定のmemberIDのフォローリストに結果を挿入しフォローリスト番号を返します。
    #パラメータ：
    #戻り値：{"bklistkey":}
            elif self.com == "searchbkdata":
                self.corp_name = "s-style" #本来はあり得ない企業名で初期化することそうすればmemberを得られない
                self.branch_name = "hon"
                """
                #セッションチェック
                ssn = session.Session(self.request, self.response)
                if ssn.chk_ssn():
                    user = ssn.get_ssn_data('user')
                    corp = user.CorpOrg_key_name
                """

                """
                reqlist = self.request.query_string.split("&")
                req={}
                for arg in reqlist:
                    req[urllib.unquote_plus(arg.split("=")[0])]=urllib.unquote_plus(arg.split("=")[1])
                req["mtngflg"] = "1"
                req["webknskflg"] = "1"
                req["nyrykkisyID"] = self.corp_name
                req["nyrykstnID"] = self.branch_name
                req["POST"] = {"multi":self.request.GET.multi}
                req["bbchntikbn"] =u"売買"
                req["bkknShbt"] = u"マンション等"
                req["dtsyuri"] = u"物件"
                """
                self.memberID = self.request.get("memID")
                if not self.memberID:
                    #self.memberID = "systemID0023232@memberlist" #取り扱いに注意
                    #self.userID = "systemID0023232@memberlist" #取り扱いに注意
                    self.memberID = "test111" #取り扱いに注意
                    self.userID = "test111" #取り扱いに注意
                    #self.memberID = "1" #取り扱いに注意
                    #self.userID = "1" #取り扱いに注意
                    self.userkey = None
                    self.memdb = None
                    self.tmpl_val = []
                bksp = bkdataSearchProbider(self.corp_name,self.branch_name,self.memberID,self.userID,self.userkey,self.memdb,self.tmpl_val,self.request)
                bklistkey = bksp.post(**kwargs)
                entitys = {"bklistkey":bklistkey}



    #https://s-style-hrd.appspot.com/jsonservice?com=getcache&key=
    #com：getcache
    #memcacheからデータを取得します
    #パラメータ：
    #戻り値：{"bklistkey":}
            elif self.com == "getcache":
                key = self.request.get("key")
                """
                #セッションチェック
                ssn = session.Session(self.request, self.response)
                if ssn.chk_ssn():
                    user = ssn.get_ssn_data('user')
                    corp = user.CorpOrg_key_name
                """
                cacheddata = memcache.get(key)
                entitys = {"data":cacheddata}



    #https://localhost:8080/jsonservice?com=getBKlistKey&key=2327
    #https://localhost:8080/jsonservice?com=getBKlistKey&key=2327&field=normal
    #com：getBKlistKey
    #フォロー履歴のkeyに対応した物件の一覧を取得します field=normalで正式なエンティティ名を取得できます
    #パラメータ：key(コマンドgetfolのkey)
    #戻り値：[{情報:{メモ,送信済,送信日時},物件:{物件情報},key:str] listGenerator(self,list):

            elif self.com == u"getBKlistKey":
                msgID = self.request.get("key")

                corp = "s-style" #本来はあり得ない企業名で初期化することそうすればmemberを得られない

                """
                #セッションチェック
                ssn = session.Session(self.request, self.response)
                if ssn.chk_ssn():
                    user = ssn.get_ssn_data('user')
                    corp = user.CorpOrg_key_name
                """


                bklist = bklistutl.getlistbyID(corp,msgID)
                logging.info('json.getBKlistKey lenbklist:' + str(bklist.count()))
                reslist = ""
                for bke in bklist:
                    bk = bke.refbk
                    #sumple jQuery17109012071304023266_1327365113283([{"情報": {"null":
                    gqljson = GqlJsonEncoder(ensure_ascii=False)
                    field = self.request.get("field")
                    if field == "normal":
                        gqljson.fieldname = "normal"
                        resbklist = u'{"info":%s,"bk":%s,"key":"%s"}' %( gqljson.encode(bke) ,gqljson.encode(bk),str(bke.key()))
                    else:
                        resbklist = u'{"情報":%s,"物件":%s,"key":"%s"}' %( gqljson.encode(bke) ,gqljson.encode(bk),str(bke.key()))
                    if reslist:
                        reslist+=", "
                    reslist+=resbklist
                reslist = "[" +reslist + "]"

                if self.callback:
                    self.response.headers['Content-Type'] = "text/javascript"
                    self.response.out.write("%s(%s);" %
                                (self.callback, reslist))
    #                            (self.callback, self.listGenerator(entitys)))
                else:
                    self.response.headers['Content-Type'] = "application/json"
                    self.response.out.write(reslist)
                return


            elif self.com == u"getBKlistKey2":
                listkey = self.request.get("key")

                corp = "s-style" #本来はあり得ない企業名で初期化することそうすればmemberを得られない

                """
                #セッションチェック
                ssn = session.Session(self.request, self.response)
                if ssn.chk_ssn():
                    user = ssn.get_ssn_data('user')
                    corp = user.CorpOrg_key_name
                """


                bklist = bklistutl.getlistbyID(corp,listkey)
                reslist = []
                for bke in bklist:
                    bk = bke.refbk
                    resbklist = {u"情報":bke,u"物件":bk,"key":str(bke.key())}
                    reslist.append(resbklist)
                entitys = reslist



    #https://localhost:8080/jsonservice?com=getBKlistKeyonly&key=2327
    #com：getBKlistKeyonly
    #フォロー履歴のkeyに対応した物件リストの一覧を取得します
    #パラメータ：key(コマンドgetfolのkey)
    #戻り値：[bklistkey,]

            elif self.com == u"getBKlistKeyonly":
                msgID = self.request.get("key")
                corp = "s-style" #本来はあり得ない企業名で初期化することそうすればmemberを得られない
                """
                #セッションチェック
                ssn = session.Session(self.request, self.response)
                if ssn.chk_ssn():
                    user = ssn.get_ssn_data('user')
                    corp = user.CorpOrg_key_name
                """
                bklist = bklistutl.getreflistkeysbymesID(corp,msgID)
                li = []
                for e in bklist:
                    li.append(e)
                entitys = li


    #https://localhost:8080/jsonservice?com=getBKlistbykeylist&keylist=
    #com：getBKlistbykeylist
    #フォロー履歴のkeyに対応した物件リストの一覧を取得します
    #パラメータ：keylist(コマンドgetBKlistKeyonlyのkeylist)
    #戻り値：[{情報:{メモ,送信済,送信日時},物件:{物件情報},key:str] listGenerator(self,list):

            elif self.com == u"getBKlistbykeylist":

                corp = "s-style" #本来はあり得ない企業名で初期化することそうすればmemberを得られない

                """
                #セッションチェック
                ssn = session.Session(self.request, self.response)
                if ssn.chk_ssn():
                    user = ssn.get_ssn_data('user')
                    corp = user.CorpOrg_key_name
                """
                media = self.request.get("media")
                refliststr = self.request.get("keylist")
                reflist = refliststr.split(",")
                bklist = bklistutl.getreflistbyreflistkeys(reflist)
                reslist = ""
                for bke in bklist:
                    bk = bke.refbk
                    #sumple jQuery17109012071304023266_1327365113283([{"情報": {"null":
                    gqljson = GqlJsonEncoder(ensure_ascii=False)
                    field = self.request.get("field")
                    if field == "normal":
                        gqljson.fieldname = "normal"
                        resbklist = u'{"info":%s,"bk":%s,"key":"%s"}' %( gqljson.encode(bke) ,gqljson.encode(self.makedata(bk,media)),str(bke.key()))
                    else:
                        resbklist = u'{"情報":%s,"物件":%s,"key":"%s"}' %( gqljson.encode(bke) ,gqljson.encode(self.makedata(bk,media)),str(bke.key()))
                    if reslist:
                        reslist+=", "
                    reslist+=resbklist
                reslist = "[" +reslist + "]"
                if self.callback:
                    self.response.headers['Content-Type'] = "text/javascript"
                    self.response.out.write("%s(%s);" %
                                (self.callback, reslist))
    #                            (self.callback, self.listGenerator(entitys)))
                else:
                    self.response.headers['Content-Type'] = "application/json"
                    self.response.out.write(reslist)
                return


            elif self.com == u"getBKlistbykeylist2":
                #getBKlistbykeylistの逐次出力板　テストしてない

                corp = "s-style" #本来はあり得ない企業名で初期化することそうすればmemberを得られない

                """
                #セッションチェック
                ssn = session.Session(self.request, self.response)
                if ssn.chk_ssn():
                    user = ssn.get_ssn_data('user')
                    corp = user.CorpOrg_key_name
                """
                media = self.request.get("media")
                refliststr = self.request.get("keylist")
                reflist = refliststr.split(",")
                bklist = bklistutl.getreflistbyreflistkeys(reflist)

                self.senddata(bklist,media)
                return


    #https://localhost:8080/jsonservice?com=getBKlistbymesID&field=normal&media=web&mesID=
    #com：getBKlistbykeylist
    #フォロー履歴のkeyに対応した物件リストの一覧を取得します
    #パラメータ：mesID
    #戻り値：[{情報:{メモ,送信済,送信日時},物件:{物件情報},key:str] listGenerator(self,list):
            elif self.com == u"getBKlistbymesID":

                corp = "s-style" #本来はあり得ない企業名で初期化することそうすればmemberを得られない

                """
                #セッションチェック
                ssn = session.Session(self.request, self.response)
                if ssn.chk_ssn():
                    user = ssn.get_ssn_data('user')
                    corp = user.CorpOrg_key_name
                """
                media = self.request.get("media")
                refliststr = self.request.get("mesID")
                field = self.request.get("field")
                #reflist = refliststr.split(",")
                bklist = bklistutl.getreflistbymesID(corp,refliststr)
                reslist = ""
                for bke in bklist:
                    bk = bke.refbk
                    #sumple jQuery17109012071304023266_1327365113283([{"情報": {"null":
                    gqljson = GqlJsonEncoder(ensure_ascii=False)
                    if field == "normal":
                        gqljson.fieldname = "normal"
                        resbklist = u'{"info":%s,"bk":%s,"key":"%s"}' %( gqljson.encode(bke) ,gqljson.encode(self.makedata(bk,media)),str(bke.key()))
                    else:
                        resbklist = u'{"情報":%s,"物件":%s,"key":"%s"}' %( gqljson.encode(bke) ,gqljson.encode(self.makedata(bk,media)),str(bke.key()))
                    if reslist:
                        reslist+=", "
                    reslist+=resbklist
                reslist = "[" +reslist + "]"
                if self.callback:
                    self.response.headers['Content-Type'] = "text/javascript"
                    self.response.out.write("%s(%s);" %
                                (self.callback, reslist))
    #                            (self.callback, self.listGenerator(entitys)))
                else:
                    self.response.headers['Content-Type'] = "application/json"
                    self.response.out.write(reslist)
                return

            elif self.com == u"getBKlistbymesID2":
                """
                #作ってみたけど逐次送信はできんみたいで意味なし
                """

                corp = "s-style" #本来はあり得ない企業名で初期化することそうすればmemberを得られない

                """
                #セッションチェック
                ssn = session.Session(self.request, self.response)
                if ssn.chk_ssn():
                    user = ssn.get_ssn_data('user')
                    corp = user.CorpOrg_key_name
                """
                media = self.request.get("media")
                refliststr = self.request.get("mesID")
                #reflist = refliststr.split(",")
                bklist = bklistutl.getreflistbymesID(corp,refliststr)
                self.senddata(bklist,media)
                return

    #https://localhost:8080/jsonservice?com=getBKlistLenbymesID&field=normal&media=web&mesID=
    #com：getBKlistbykeylist
    #フォロー履歴のkeyに対応した物件リストの物件数を取得します
    #パラメータ：mesID
    #戻り値：{物件数:物件数）:
            elif self.com == u"getBKlistLenbymesID":
                corp = "s-style" #本来はあり得ない企業名で初期化することそうすればmemberを得られない
                """
                #セッションチェック
                ssn = session.Session(self.request, self.response)
                if ssn.chk_ssn():
                    user = ssn.get_ssn_data('user')
                    corp = user.CorpOrg_key_name
                """
                media = self.request.get("media")
                refliststr = self.request.get("mesID")
                field = self.request.get("field")
                #reflist = refliststr.split(",")
                bklist = bklistutl.getreflistbymesID(corp,refliststr)
                count = bklist.count()
                if field == "normal":
                    entitys = {u"count":str(count)}
                else:
                    entitys = {u"物件数":str(count)}


    #https://localhost:8080/jsonservice?com=addBKlist&bkID=10&memo=メモです&send=true&key=2327&senddate=2011/12/24 00:00:01
    #com：addBKlist
    #フォロー履歴に対応した物件のリストを一行挿入します
    #POST推奨
    #パラメータ：key(follistのkey)
    #        bkID(物件番号)
    #　　　　　　　memo (省略可能:text)
    #        send (省略可能:bool)
    #　　　　　　　senddate(省略可能:yyyy/mm/dd tt:mm:ss)
    #戻り値：
    #   {result:}

            elif self.com == u"addBKlist":
                refmes = self.request.get("key")
                bkID = self.request.get("bkID")
                memo = self.request.get("memo")
                sended = self.request.get("send")
                senddate = self.request.get("senddate")

                corp = self.request.get("corp")
                corp = u"s-style" #本来はあり得ない企業名で初期化することそうすればmemberを得られない
                branch = u"hon"

                """
                #セッションチェック
                ssn = session.Session(self.request, self.response)
                if ssn.chk_ssn():
                    user = ssn.get_ssn_data('user')
                    corp = user.CorpOrg_key_name
                """

                bklistutl.addlistbyID(corp,branch,bkID,refmes,None,None,senddate,sended,memo)
                entitys = {u"result":u"OK"}

    #https://localhost:8080/jsonservice?com=addeditBKlist&bkID=10&memo=%E3%83%A1%E3%83%A2%E3%81%A7%E3%81%99&send=true&meskey=2327&senddate=2011/12/24%2000:00:01&bklistkey=agtkZXZ-YW1hbmVkYnINCxIGQktsaXN0GIUbDA
    #com：addeditBKlist
    #フォロー履歴に対応した物件のリストを一行挿入しますリストがある場合は上書きします
    #POST推奨
    #パラメータ：meskey(follistのkey)
    #        bkID(物件番号)
    #        bklistkey (省略可能：bklistのkey)
    #　　　　　　　memo (省略可能:text)
    #        send (省略可能:"true"or"on")
    #　　　　　　　senddate(省略可能:yyyy/mm/dd tt:mm:ss)
    #戻り値：
    #   {bklistkey:}

            elif self.com == u"addeditBKlist":
                refmes = self.request.get("meskey")
                bkID = self.request.get("bkID")
                memo = self.request.get("memo")
                sended = self.request.get("send")
                if bkID:
                        if sended == "true" or sended == "True" or sended == "on":
                            sended = True
                        senddate = self.request.get("senddate")
                        key = self.request.get("bklistkey")

                        corp = self.request.get("corp")
                        corp = u"s-style" #本来はあり得ない企業名で初期化することそうすればmemberを得られない
                        branch = u"hon"

                        """
                        #セッションチェック
                        ssn = session.Session(self.request, self.response)
                        if ssn.chk_ssn():
                            user = ssn.get_ssn_data('user')
                            corp = user.CorpOrg_key_name
                        """
                        key = bklistutl.addlistbyID(corp,branch,bkID,refmes,None,key,senddate,sended,memo)
                        entitys = {u"bklistkey":key}
                entitys = {u"bklistkey":None}
    #https://localhost:8080/jsonservice?com=removeBK&key=2327&bkID=10
    #com：removeBK
    #フォロー履歴に対応した物件のリストを削除します
    #パラメータ：key(follistのkey)
    #                bkID(物件番号,・・・・・)
    #戻り値：
    #   {result:}
            elif self.com == u"removeBK":
                refmes = self.request.get("key")
                bkID = self.request.get("bkID")

                corp = self.request.get("corp")
                corp = "s-style" #本来はあり得ない企業名で初期化することそうすればmemberを得られない
                branch = "hon"

                """
                #セッションチェック
                ssn = session.Session(self.request, self.response)
                if ssn.chk_ssn():
                    user = ssn.get_ssn_data('user')
                    corp = user.CorpOrg_key_name
                """
                for i in bkID.split(","):
                    bklistutl.remlistbyID(corp,branch,i,refmes)
                entitys = {"result":"OK"}


    #https://s-style-hrd.appspot.com/jsonservice?com=getmemAction&tantoID=test222&action=
    #https://localhost:8080/jsonservice?com=getmemAction&memberID=1&action=
    #com：getmemAction
    #フォロー履歴の未処理アクションから顧客のリストを取得します。
    #パラメータ：action
    #　　　　　　　 datetime(省略可能:yyyy/mm/dd)
    #        　　　　tantoID
    #戻り値：上記顧客情報(array)

            elif self.com == "getmemAction":
                action = self.request.get("action")
                memberID = self.request.get("tantoID")
                corp = self.request.get("corp")
                dt = self.gettime(self.request.get("datetime"))
                #dtはgettimeで整形されてUSTになっているmessegeManagerのリストはJST変換されているので比較のためdtをJSTに復元する
                if dt:
                    dt = timemanager.utc2jst_date(dt).replace(tzinfo=None)
                corp = "s-style" #本来はあり得ない企業名で初期化することそうすればmemberを得られない
                """
                #セッションチェック
                ssn = session.Session(self.request, self.response)
                if ssn.chk_ssn():
                    user = ssn.get_ssn_data('user')
                    corp = user.CorpOrg_key_name
                """
                if memberID:
                    tan = member.get_by_key_name(corp + "/" + memberID)
                    #gql = member.all()
                    #gql.filter(" memberID = " ,memberID)
                    #gql.filter(" CorpOrg_key_name = " ,corp)
                    d2=[]
                    #for mem in gql.fetch(1)[0].mytanto:
                    for mem in tan.mytanto:
                        meslist = messageManager.messageManager.getmeslistbyID(corp,mem.memberID,done = False ,kill = False, order = "-reservation",combkind=u"所有")
                        """
                            body = db.StringProperty(verbose_name=u"本文",multiline=True)
                            subject = db.StringProperty(verbose_name=u"表題")
                            kindname = db.StringProperty(verbose_name=u"アクション")
                            done = db.BooleanProperty(verbose_name=u"済",default=False)
                            kill = db.BooleanProperty(verbose_name=u"消",default=False)
                            timestamp = db.DateTimeProperty(auto_now_add = True,verbose_name=u"タイムスタンプ")
                            reservation = db.DateTimeProperty(auto_now_add = True,verbose_name=u"予定日")
                            reservationend = db.DateTimeProperty(auto_now_add = True,verbose_name=u"予定終了日")
                            commentTo = db.SelfReference(collection_name=u"refmes",verbose_name=u"コメント先")
                        """
                        for mes in meslist:
                            if not mes.done and not mes.kill and mes.kindname == action :
                                if dt:
                                    if mes.reservation.year == dt.year and mes.reservation.month == dt.month and mes.reservation.day == dt.day :
                                        d2.append(mem)
                                else:
                                    d2.append(mem)
                    entitys = d2

    #https://s-style-hrd.appspot.com/jsonservice?com=getaction&tantoID=test222
    #com：getaction
    #フォロー履歴の未処理アクションの統計リストを取得します
    #パラメータ：tantoID
    #　　　　　　　 date(省略可能:yyyy/mm/dd)
    #戻り値：(array)
    #   [{アクション:},{件数:}]
            elif self.com == u"getaction":
                memberID = self.request.get("tantoID")
                corp = self.request.get("corp")
                dt = self.gettime(self.request.get("datetime"))
                corp = "s-style" #本来はあり得ない企業名で初期化することそうすればmemberを得られない

                """
                #セッションチェック
                ssn = session.Session(self.request, self.response)
                if ssn.chk_ssn():
                    user = ssn.get_ssn_data('user')
                    corp = user.CorpOrg_key_name
                """
                if memberID:
                    tan = member.get_by_key_name(corp + "/" + memberID)
                    #gql = member.all()
                    #gql.filter(" memberID = " ,memberID)
                    #gql.filter(" CorpOrg_key_name = " ,corp)

                    d2={}
                    #for mem in gql.fetch(1)[0].mytanto:
                    ml = []
                    meslist = messageManager.messageManager.getmeslistbyID(corp,memberID,done = False ,kill = False, order = "-reservation",combkind=u"参照")
                    """
                            body = db.StringProperty(verbose_name=u"本文",multiline=True)
                            subject = db.StringProperty(verbose_name=u"表題")
                            kindname = db.StringProperty(verbose_name=u"アクション")
                            done = db.BooleanProperty(verbose_name=u"済",default=False)
                            kill = db.BooleanProperty(verbose_name=u"消",default=False)
                            timestamp = db.DateTimeProperty(auto_now_add = True,verbose_name=u"タイムスタンプ")
                            reservation = db.DateTimeProperty(auto_now_add = True,verbose_name=u"予定日")
                            reservationend = db.DateTimeProperty(auto_now_add = True,verbose_name=u"予定終了日")
                            commentTo = db.SelfReference(collection_name=u"refmes",verbose_name=u"コメント先")
                        for mes in meslist:
                            if not mes.done:
                                ml.append(mes)
                    ml.sort(key=lambda obj: obj.reservation)
                    ml.reverse()
                    for mes in ml:
                        if dt:
                            if mes.reservation.year == dt.year and mes.reservation.month == dt.month and mes.reservation.day == dt.day :
                                if d2.has_key(mes.kindname):
                                    d2[mes.kindname] = d2[mes.kindname] + 1
                                else:
                                    d2[mes.kindname] = 1
                        else:
                            if d2.has_key(mes.kindname):
                                d2[mes.kindname] = d2[mes.kindname] + 1
                            else:
                                d2[mes.kindname] = 1
                    #d2がdictなので順番が保証されない　更新すること
                    ↓短くしてみたけど効果なし
                    """
                    for mes in meslist:
                        if not mes.done:
                            if dt:
                                if mes.reservation.year == dt.year and mes.reservation.month == dt.month and mes.reservation.day == dt.day :
                                    if d2.has_key(mes.kindname):
                                        d2[mes.kindname] = d2[mes.kindname] + 1
                                    else:
                                        d2[mes.kindname] = 1
                            else:
                                if d2.has_key(mes.kindname):
                                    d2[mes.kindname] = d2[mes.kindname] + 1
                                else:
                                    d2[mes.kindname] = 1

                    entitys = d2



    #戻り値result仕様
    #{result:OK}
    #{result:{error:エラーメッセージ}}

    #https://s-style-hrd.appspot.com/jsonservice?com=memberservice&service=
            elif self.com == u"memberservice":

                logging.info('json memberservice strat')
                corp = "s-style" #本来はあり得ない企業名で初期化することそうすればmemberを得られない
                branch = "hon"
                """
                #セッションチェック
                ssn = session.Session(self.request, self.response)
                if ssn.chk_ssn():
                    user = ssn.get_ssn_data('user')
                    corp = user.CorpOrg_key_name
                """
                bkID = self.request.get("bkID")
                followsubject = self.request.get("followsubject")
                rireki = self.request.get("rireki")
                service = self.request.get("service")
                status = self.request.get("status")
                seiyaku = self.request.get("seiyaku")
                jufuku = self.request.get("jufuku",None)
                if jufuku == '1' or jufuku == None or jufuku == "True":
                    jufuku = True
                else:
                    jufuku = False
                tourokunengappiL = self.gettime(self.request.get("tourokunengappiL"))
                tourokunengappiU = self.gettime(self.request.get("tourokunengappiU"),1)
                filter = self.request.get("filter")
                filtervalue = self.request.get("filtervalue")
                memlist = []
                if followsubject:
                    meslist = Message.all()
                    meslist.filter("subject >= " ,followsubject)
                    meslist.filter("subject < ",followsubject + u"\uFFFD'")
                    meslist.filter("corp = ",self.corp_name)
                    meslist.filter("kill = ",False)
                    for mes in meslist:
                        comblist = mes.refmemlist
                        for e in comblist.filter("combkind = ",u"所有"):
                            e2 = e.refmem.key()
                            if not e2 in memlist :
                                memlist.append(e2)
                if bkID:
                    meslist = bklistutl.getmeslistbybkID(self.corp_name, self.branch_name, bkID)
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
                if rireki:
                    mes = messageManager.messageManager.getmesbyID(corp,rireki)
                    meslist = mes.refmes
                    if len(memlist):
                        reslist = []
                        for mes in meslist:
                            m = messageManager.messageManager.getmemlist(mes,u"所有")
                            for e in m:
                                e2 = e.refmem.key()
                                if e2 in memlist:
                                    if not e2 in reslist :
                                        reslist.append(e2)
                        meslist = reslist
                    else:
                        for mes in meslist:
                            m = messageManager.messageManager.getmemlist(mes)
                            for e in m:
                                e2 = e.refmem.key()
                                if not e2 in memlist :
                                    memlist.append(e2)
                if (service or status or seiyaku or tourokunengappiL or tourokunengappiU or (filter and filtervalue)):
                    logging.info('json memberservice query strat')
                    query = member.all(keys_only=True)
                    if service:
                        query.filter("service = ",service)
                    if status:
                        query.filter("status = ",status)
                    if seiyaku:
                        query.filter("seiyaku = " ,seiyaku)
                    if tourokunengappiL:
                        query.filter("tourokunengappi >= " ,tourokunengappiL)
                    if tourokunengappiU:
                        query.filter("tourokunengappi <= " ,tourokunengappiU)
                    if filter and filtervalue:
                        if filtervalue == "true":
                            filtervalue1 = True
                        elif filtervalue == "false":
                            filtervalue1 = False
                        elif filtervalue == "none":
                            filtervalue1 = None
                        elif filtervalue.isdigit():
                            filtervalue1 = float(filtervalue)
                        elif self.gettime(filtervalue):
                            filtervalue1 = self.gettime(filtervalue)
                        else:
                            filtervalue1 = filtervalue
                        query.filter(filter + " = " ,filtervalue1)
                    query.filter("CorpOrg_key_name = ",self.corp_name )
                    logging.info('json memberservice loop strat : memlist:' + str(len(memlist)) + " query:" + str(query.count()))
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
                entitys = member.get(memlist)


    #https://s-style-hrd.appspot.com/jsonservice?com=area&division=小学校区&corp=s-style&search_key=a
            elif self.com == u"area":
                gql = bksearchaddresslist.all()
                corp = self.request.get("corp")
    #            gql.filter(" co = " ,corp)
                division = self.request.get("division")
                if division:
                    gql.filter(" division = " ,division)
                    pass
                if self.search_key:
                    gql.filter(" name >= " ,self.search_key)
                    gql.filter(" name < " ,self.search_key + u"\uFFFD'" )
                es = gql.fetch(1000)
                e2=[]
                for e in es:
                    d2={}
                    d2[u"区分"] = e.division
                    d2[u"名前"] = e.name
                    d2[u"会社"] = e.co
                    d2[u"支店"] = e.br
                    d2[u"key"] = str(e.key())
                    e2.append(d2)
                entitys = e2

    #https://s-style-hrd.appspot.com/jsonservice?com=addresslist&area=千種　田代小&corp=s-style
            elif self.com == u"addresslist":
                gql = bksearchaddresslist.all()
                corp = self.request.get("corp")
    #            gql.filter(" co = " ,corp)
                area = self.request.get("area")
                if division:
                    gql.filter(" division = " ,division)
                    pass
                if self.search_key:
                    gql.filter(" name >= " ,self.search_key)
                    gql.filter(" name < " ,self.search_key + u"\uFFFD'" )
                entitys = gql.fetch(1000)


    #https://s-style-hrd.appspot.com/jsonservice?com=addressset&key=agtkZXZ-YW1hbmVkYnIZCxITYmtzZWFyY2hhZGRyZXNzbGlzdBgVDA
            elif self.com == u"addressset":
                key_name = self.request.get('key')
                obj = None
                if key_name:
                    obj = db.get(db.Key(key_name))
                if obj:
                    e2=[]
                    for e in obj.adset:
                        d2={}
                        d2[u"都道府県名"] = e.tdufknmi
                        d2[u"所在地名1"] = e.shzicmi1
                        d2[u"会社"] = e.co
                        d2[u"支店"] = e.br
                        d2[u"key"] = str(e.key())
                        e2.append(d2)
                    entitys = e2

    #https://s-style-hrd.appspot.com/jsonservice?com=address2data&key=agtkZXZ-YW1hbmVkYnIZCxITYmtzZWFyY2hhZGRyZXNzbGlzdBgVDA
            elif self.com == u"address2data":
                key_name = self.request.get('key')
                obj = None
                if key_name:
                    obj = db.get(db.Key(key_name))
                    e2=[]
                    for e in obj.address2list:
                        d2={}
                        d2[u"大字・町丁目"] = e.shzicmi2
                        e2.append(d2)
                    entitys = e2


    #https://s-style-hrd.appspot.com/jsonservice?com=addresslistname&key=agtkZXZ-YW1hbmVkYnIaCxITYmtzZWFyY2hhZGRyZXNzbGlzdBi-BQw
            elif self.com == u"addresslistname":
                key_name = self.request.get('key')
                obj = None
                if key_name:
                    obj = db.get(db.Key(key_name))
                    entitys = obj

    #https://s-style-hrd.appspot.com/jsonservice?com=GetautomaticSearch?sub=
            elif self.com == u"GetautomaticSearch":

                key_name = self.request.get('sub')
                gql = Message.all()
                gql.filter("corp = ",self.corp_name)
                gql.filter("subject = ",sub)
                list = []
                for mes in gql:
                    mem = None
                    for comb in mes.refmemlist:
                        if comb.combkind == u"所有":
                            list.append({u"メンバーID":mem.memberID,u"氏名":mem.name,u"メールアドレス":mem.mail,u"サイト名":mem.sitename,u"マッチ数":comb.refmes.refbklist.count()})
                            break
                entitys = list


    #https://s-style-hrd.appspot.com/jsonservice?com=bkdataopenshow
            elif self.com == u"bkdataopenshow":
                gqlstr = u"SELECT * FROM BKdata"
                corp = self.request.get("corp")
                self.media = self.request.get("media")
                if corp:
                    where += u" WHERE" if where == u"" else u" AND"
                    where += u" nyrykkisyID = '" + corp + u"'"
                bkID = self.request.get("bkID")
                if bkID:
                    where += u" WHERE" if where == u"" else u" AND"
                    where += u" bkID = '" + bkID + u"'"
                if gqlstr!= '':
                    gqlstr += where
                    entitys = db.GqlQuery(gqlstr)
                    if entitys.count():
                        b = entitys[0]
                        query_str = u"SELECT * FROM Blob WHERE CorpOrg_key = '" + b.nyrykkisyID + u"' AND Branch_Key = '" + b.nyrykstnID + u"' AND bkID = '" + b.bkID + u"' AND media = '" + self.media + u"' ORDER BY pos ASC"
                        #query_str = u"SELECT * FROM Blob WHERE CorpOrg_key = '" + b.nyrykkisyID + u"' AND Branch_Key = '" + b.nyrykstnID+ u"' AND bkID = '59' ORDER BY  media, pos ASC"
                        blobs = db.GqlQuery (query_str)
                        b2 = []
                        heimenzu = None
                        for c in blobs:
                            if c.pos.isdigit():
                                b2.append(c)
                            elif c.pos == "平面図":
                                heimenzu = c
                        kakakuM = None
                        kakakuB = None
                        if b.kkkuCnryu:
                            kakakuM = GqlJsonEncoder.floatfmt(float(int(b.kkkuCnryu/100))/100)
                            #kakakuB = self.moneyfmt(b.kkkuCnryu)
                        tknngt = None
                        if b.cknngtSirk:
                            tknngt = b.cknngtSirk.year
                            if int(tknngt) < 1989:
                                tknngt = u"昭和" + str(tknngt-1925) + u"年"
                            elif int(tknngt) >= 1989:
                                tknngt = u"平成" + str(tknngt-1988) + u"年"
                            else:
                                tknngt = tknngt + u"年"
                        #entitys = self.formatfloatdata(entitys)
                        #b = entitys[0]
                    entitys = {"bkdatakey":b.key(),"bkdata":b,"picdata":b2,"kakakuM":kakakuM,"kakakuB":kakakuB,"tknngtG":tknngt,"heimenzu":heimenzu}
            else:
                entitys = {"result":"error","error_msg":"Undefined Commande"}
            #データを得る
            #"SELECT * FROM Greeting where content >= :1 and content < :2 ", search_key, search_key + u"\uFFFD"
            #プロパティのトリミングはクライアント側でやってもらう
            self.response.content_type='application/json'
            if self.callback:
                self.response.headers['Content-Type'] = "text/javascript; charset=utf-8"
                self.response.out.write("%s(%s);" %
                            (self.callback, GqlJsonEncoder(ensure_ascii=False).encode(entitys)))
#                            (self.callback, self.listGenerator(entitys)))
            else:
                self.response.headers['Content-Type'] = "application/json; charset=utf-8"
                self.response.out.write(GqlJsonEncoder(ensure_ascii=False).encode(entitys))
#                self.response.out.write(self.listGenerator(entitys))
            #GqlEncoder(ensure_ascii=False).encode(mymodel)

        except:
            entitys = {"result":"error","error_msg":traceback.format_exc()}
            self.response.content_type='application/json; charset=utf-8'
            if self.callback:
                self.response.headers['Content-Type'] = "text/javascript; charset=utf-8"
                self.response.out.write("%s(%s);" %
                            (self.callback, GqlJsonEncoder(ensure_ascii=False).encode(entitys)))
            else:
                self.response.headers['Content-Type'] = "application/json; charset=utf-8"
                self.response.out.write(GqlJsonEncoder(ensure_ascii=False).encode(entitys))


    code = {

u"北海道":u"1",
u"青森県":u"2",
u"岩手県":u"3",
u"宮城県":u"4",
u"秋田県":u"5",
u"山形県":u"6",
u"福島県":u"7",
u"茨城県":u"8",
u"栃木県":u"9",
u"群馬県":u"10",
u"埼玉県":u"11",
u"千葉県":u"12",
u"東京都":u"13",
u"神奈川県":u"14",
u"新潟県":u"15",
u"富山県":u"16",
u"石川県":u"17",
u"福井県":u"18",
u"山梨県":u"19",
u"長野県":u"20",
u"岐阜県":u"21",
u"静岡県":u"22",
u"愛知県":u"23",
u"三重県":u"24",
u"滋賀県":u"25",
u"京都府":u"26",
u"大阪府":u"27",
u"兵庫県":u"28",
u"奈良県":u"29",
u"和歌山県":u"30",
u"鳥取県":u"31",
u"島根県":u"32",
u"岡山県":u"33",
u"広島県":u"34",
u"山口県":u"35",
u"徳島県":u"36",
u"香川県":u"37",
u"愛媛県":u"38",
u"高知県":u"39",
u"福岡県":u"40",
u"佐賀県":u"41",
u"長崎県":u"42",
u"熊本県":u"43",
u"大分県":u"44",
u"宮崎県":u"45",
u"鹿児島県":u"46",
u"沖縄県":u"47"
    }
    ken = {
u"1":u"北海道",
u"2":u"青森県",
u"3":u"岩手県",
u"4":u"宮城県",
u"5":u"秋田県",
u"6":u"山形県",
u"7":u"福島県",
u"8":u"茨城県",
u"9":u"栃木県",
u"10":u"群馬県",
u"11":u"埼玉県",
u"12":u"千葉県",
u"13":u"東京都",
u"14":u"神奈川県",
u"15":u"新潟県",
u"16":u"富山県",
u"17":u"石川県",
u"18":u"福井県",
u"19":u"山梨県",
u"20":u"長野県",
u"21":u"岐阜県",
u"22":u"静岡県",
u"23":u"愛知県",
u"24":u"三重県",
u"25":u"滋賀県",
u"26":u"京都府",
u"27":u"大阪府",
u"28":u"兵庫県",
u"29":u"奈良県",
u"30":u"和歌山県",
u"31":u"鳥取県",
u"32":u"島根県",
u"33":u"岡山県",
u"34":u"広島県",
u"35":u"山口県",
u"36":u"徳島県",
u"37":u"香川県",
u"38":u"愛媛県",
u"39":u"高知県",
u"40":u"福岡県",
u"41":u"佐賀県",
u"42":u"長崎県",
u"43":u"熊本県",
u"44":u"大分県",
u"45":u"宮崎県",
u"46":u"鹿児島県",
u"47":u"沖縄県"
   }
WD = ("月","火","水","木","金","土","日")


