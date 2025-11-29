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
#from google.appengine.dist import use_library
#use_library('django', '1.2')
from django.utils import simplejson
import datetime
import time
from google.appengine.api import users
from google.appengine.ext import db
from models.bkdata import BKdata
from models.address import address1
from models.member2 import member2
from models.bksearchaddress import bksearchaddresslist
#from models.ziplist import Ziplist
from copy import deepcopy
from decimal import *
import session
import messageManager
from GqlEncoder import GqlJsonEncoder
from bklistutl import bklistutl

class jsonservice(webapp2.RequestHandler):


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
                
#https://s-style-hrd.appspot.com/jsonservice?com=BKdata
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
            where += u" LIMIT 100"
            if gqlstr!= '':
                gqlstr += where
                entitys = db.GqlQuery(gqlstr)
                #entitys = self.formatBKdata(entitys)

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
            if self.search_key:
                where += u" WHERE" if where == u"" else u" AND"
                where += u" shzicmi2 >= '" + self.search_key + u"' and shzicmi2 < '" + self.search_key + u"\uFFFD'"
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
                gqlstr += where
                entitys = db.GqlQuery(gqlstr)
                entitysb = []
                for b in entitys:
                    for t in entitysb:
                        if t.line_cd == b.line_cd:
                            break
                    else:
                        entitysb.append(b)
                entitys = deepcopy(entitysb)

#https://s-style-hrd.appspot.com/jsonservice?com=station
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
                where += u" station_name >= '" + self.search_key + u"' and station_name < '" + self.search_key + u"\uFFFD'"
            if gqlstr!= '':
                gqlstr += where
                entitys = db.GqlQuery(gqlstr)


#https://s-style-hrd.appspot.com/jsonservice?com=member&memberID=
        elif self.com == u"member":
            gqlstr = u"SELECT * FROM member"
            memberID = self.request.get("mamberID")
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
            """            
            gql = member.all()
            if self.search_key:
                gql.filter(" yomi >= " ,self.search_key)
                gql.filter(" yomi < " ,self.search_key + u"\uFFFD'" )
            """
            corp = self.request.get("corp")
            corp = "s-style" #本来はあり得ない企業名で初期化することそうすればmemberを得られない
            """
            #セッションチェック
            #ssn = session.Session(self.request, self.response)
            #if ssn.chk_ssn():
            #    user = ssn.get_ssn_data('user')
            #    corp = user.CorpOrg_key_name

            gql.filter(" CorpOrg_key_name = " ,corp)
            entitys = gql.fetch(1000)
            """
            gqlstr = u"SELECT * FROM member"
            if self.search_key:
                where += u" WHERE" if where == u"" else u" AND"
                where += u"  yomi >=  '" + self.search_key + u"'"
                where += u"  yomi <  '" + self.search_key + u"\uFFFD'"
            where += u" WHERE" if where == u"" else u" AND"
            where += u" CorpOrg_key_name = '" + corp + u"'"
            if gqlstr!= '':
                gqlstr += where
                entitys = db.GqlQuery(gqlstr)

#https://s-style-hrd.appspot.com/jsonservice?com=getmemName&search_key=
#https://localhost:8080/jsonservice?com=getmemName2&search_key=
#com：getmemName
#よみがなから顧客情報を取得します
#パラメータ：search_key(jQuery-autocomplete:request.termオブジェクト)


        
        elif self.com == u"getmemName2":
            gql = member2.all()
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

            #gql.filter(" CorpOrg_key_name = " ,corp)
            entitys = gql.fetch(1000)


#https://s-style-hrd.appspot.com/jsonservice?com=getmemID&memID=
#com：getmemID
#顧客IDから顧客情報を取得します
#パラメータ：memID
#戻り値
#　　　　上記と同じです

        elif self.com == u"getmemID":
            gql = member2.all()
            memberID = self.request.get("memID")
            if memberID:
                gql.filter(" memberID = " ,memberID)
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
            entitys = gql.fetch(1000)


#https://s-style-hrd.appspot.com/jsonservice?com=getmemTel&memTel=
#com：getmemTel
#顧客電話番号から顧客情報を取得します
#パラメータ：memTel
#戻り値

        elif self.com == u"getmemTel":
            gql = member2.all()
#            gql.filter(" co = " ,corp)
            memTel = self.request.get("memTel")
            if memTel:
                gql.filter(" phone = " ,memTel)
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
            entitys = gql.fetch(1000)




#https://s-style-hrd.appspot.com/jsonservice?com=getfol&memberID=
#com：getfol
#フォロー履歴の一覧を取得します
#パラメータ：memberID(hiddenフィールドmemberIDのvalue)
#　　　　　　　 year(省略可能)
#　　　　　　　 mon(省略可能)
#        day(省略可能)

        elif self.com == u"getfol":
            memberID = self.request.get("memberID")
            if memberID:
                corp = "s-style" #本来はあり得ない企業名で初期化することそうすればmemberを得られない
                """
                #セッションチェック
                ssn = session.Session(self.request, self.response)
                if ssn.chk_ssn():
                    user = ssn.get_ssn_data('user')
                    corp = user.CorpOrg_key_name
                """
                meslist = messageManager.messageManager.getmeslistbyID(corp,memberID)
    
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
                    d2[u"予定終了日"] = mes.reservationend
                    d2[u"タイムスタンプ"] = mes.timestamp
                    if mes.commentTo:
                        d2[u"コメント先"] = str(mes.commentTo.key())
                    if mes.key():
                        d2[u"key"] = str(mes.key())
                    e2.append(d2)
                entitys = e2
    



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
                if entitys:
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
                        kakakuM = GqlJsonEncoder.moneyfmt(int(b.kkkuCnryu/100)/100,0)
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
                entitys = {"bkdata":b,"picdata":b2,"kakakuM":kakakuM,"kakakuB":kakakuB,"tknngtG":tknngt,"heimenzu":heimenzu}
        
        else:
            entitys = {"error":"Undefined Commande"}
        #データを得る
        #"SELECT * FROM Greeting where content >= :1 and content < :2 ", search_key, search_key + u"\uFFFD"
        #プロパティのトリミングはクライアント側でやってもらう
        self.response.content_type='application/json'
        if self.callback:
                self.response.out.write("%s(%s);" %
                        (self.callback, GqlJsonEncoder(ensure_ascii=False).encode(entitys)))
        else:
            self.response.out.write(GqlJsonEncoder(ensure_ascii=False).encode(entitys))
         
        #GqlEncoder(ensure_ascii=False).encode(mymodel)




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
