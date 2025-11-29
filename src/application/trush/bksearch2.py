# -*- coding: utf-8 -*-

import os
#from google.appengine.ext import webapp
import webapp2
from google.appengine.ext.webapp import template

from models.member import member
from models.bksearchdata import bksearchdata
from models.bkdata import BKdata
from models.CorpOrg import CorpOrg
from models.Branch import Branch
from models.bksearchaddress import *
from models.bksearchmadori import bksearchmadori
from bksearchensenutl import bksearchensenutl


import datetime
import re
from bksearchutl import bksearchutl
import timemanager
from SecurePage import SecurePage
from wordstocker import wordstocker
class bksearch(SecurePage):


    def get(self,**kwargs):
        
        if self.Secure_init(*[u"管理者",u"担当"],**kwargs):
            if kwargs.get("page",None) != None:
                page = int(kwargs.get("page",None))
            else:
                if self.request.get("page")!="":
                    page = int(self.request.get("page"))
                else: 
                    page = 0
            key = ''
            sddb = ""
            allpage = 0
            adlist = []
            line = []
            room = []
            if self.memberID == "" or not self.memberID:
                self.memberID = self.userID
                key_name = self.corp_name + "/" + self.memberID
                self.memdb = member.get_by_key_name(key_name)
                self.tmpl_val["membertel"]=self.memdb.phone
                self.tmpl_val["membermail"]=self.memdb.mail
                self.tmpl_val["memberyomi"]=self.memdb.yomi
                self.tmpl_val["membername"]=self.memdb.name
                self.tmpl_val["memberID"]= self.memberID

            if self.memberID:
                allpage = self.memdb.bksearchdata_set.count()
                pages = []
                for i in range(allpage):
                    opstr = ""
                    if self.memberID:
                        opstr = "?memberID=" + self.memberID + "&page=" + str(i+1)
                    else:
                        opstr = "?page=" + str(i+1)
                        
                    pages.append({"page":i+1,"path":self.request.path + opstr})
                if page and allpage > 0:
                    if  allpage < page:
                        page = allpage
                    bksearchdata_set = self.memdb.bksearchdata_set
                    bksearchdata_set.order("sortkey")
                    sddb = bksearchdata_set.fetch(page)[page-1]
                    key = str(sddb.key())
                else:
                    if allpage > 0:
                        sddb = self.memdb.bksearchdata_set.order("sortkey").fetch(1)[0]
                        key = str(sddb.key())
                        page = 1
                    else:
                        pass
                if sddb:
                    for al in sddb.adlist.order("sortkey"):
                        if al.ref_bksearchaddresslist == None:
                            al.delete()
                        else:
                            adlist.append({"name":al.ref_bksearchaddresslist.name,"division":al.ref_bksearchaddresslist.division,"key":str(al.ref_bksearchaddresslist.key())})
                    for ensen in sddb.ensen.order("sortkey"):
                        line.append({"tdufknmi":ensen.tdufknmi,"ensenmei":ensen.ensenmei,"thHnU":ensen.thHnU,"thMU":ensen.thMU,"station":[eki.ekimei for eki in ensen.eki]})
                    for madori in sddb.madori.order("sortkey"):
                        room.append({"mdrHysu":str(madori.mdrHysu),"mdrTyp":madori.mdrTyp})
    
                    sddb = timemanager.utc2jst_gql(sddb)
            self.tmpl_val['iconlist'] = wordstocker.get(self.corp_name, u"アイコン")  
            self.tmpl_val["key"]=key
            self.tmpl_val["data"]=sddb
            self.tmpl_val["adlist"]=adlist
            self.tmpl_val["line"]=line
            self.tmpl_val["room"]=room
            self.tmpl_val["page"]=page
            self.tmpl_val["pages"]=pages
    
            path = os.path.dirname(__file__) + '/../templates/' + self.dirpath
            self.response.out.write(template.render(path, self.tmpl_val))

    def post(self,**kwargs):

        if self.Secure_init(*[u"管理者",u"担当"],**kwargs):
            submit = self.request.get("submit")
            key = self.request.get("key")
            page = None
            if not key or submit == u"新規ページへ保存":
                key_name = self.corp_name + "/" + self.memberID
                mmdb = member.get_by_key_name(key_name)
                page = int(self.request.get("page"))
                if not page:
                    page = 1
                if submit == u"新規ページへ保存":
                    page = mmdb.bksearchdata_set.count() + 1
                if mmdb.bksearchdata_set.count() >= page:
                    sddb = mmdb.bksearchdata_set.order("sortkey").fetch(page)[page-1]
                else:
                    sddb = bksearchdata()
                    #参照の設定
                    #member = db.ReferenceProperty(reference_class = member, verbose_name=None, collection_name="")
                    sddb.member = mmdb.key()
                    sddb.sortkey = mmdb.getNextsdlistNum()
                    sddb.put()
            else:
                sddb = bksearchdata.get(key)
            kwargs["page"] = page
    
            for al in sddb.adlist:
                al.deladlist()
            for e in sddb.ensen:
                eu = bksearchensenutl()
                eu.ensen = e
                eu.delete()
            for m in sddb.madori:
                m.delete()
    
            
            if submit == u"ページ削除" :
                sddb.delete()
                self.get(**kwargs)
                return
    
            i = 0
            for n,v in self.request.POST.multi._items:
                if n == "listid":
                    if v:
                        lc = listcombinator(co = self.corp_name,br = self.branch_name)
                        lc.setadlist(v,sddb)
                if n == "line":
                    if v:
                        ensenutl = bksearchensenutl()
                        ensenutl.newensen(sddb,ensenmei=v,tdufknmi=self.request.POST.multi._items[i-1][1],thHnU=self.request.POST.multi._items[i+1][1],thMU=self.request.POST.multi._items[i+2][1])
                        for c in range(i+1,1000):
                            if self.request.POST.multi._items[c][0] == "line":
                                break
                            if self.request.POST.multi._items[c][0] == "station":
                                for eki in self.request.POST.multi._items[c][1].split(","):
                                    if eki:
                                        ensenutl.addeki(eki)
                                break
                if n == "mdrHysu":
                    if v or self.request.POST.multi._items[i+1][1]:
                        if v:
                            c = float(v)
                        else:
                            c = None
                        bksearchmadori(ref_bksearchdata = sddb,mdrHysu = c,mdrTyp = self.request.POST.multi._items[i+1][1],sortkey = sddb.getNextroomlistNum()).put()
                i+=1
            if self.userkey:
                sddb.modified = member.get(self.userkey)
            #bkID = db.StringProperty(verbose_name="物件番号",required=True)
            bkID = self.request.get("bkID")
            if bkID:
                sddb.bkID = bkID
            else:
                sddb.bkID = None
      
        #確認年月日
        #kknnngpL = db.DateTimeProperty(verbose_name=u"確認年月日下限")
            kknnngpL = self.request.get("kknnngpL")
            if kknnngpL:
                r = re.compile(".*:.*:.*").match(kknnngpL, 1)
                if r == None:
                    sddb.kknnngpL = timemanager.jst2utc_date(datetime.datetime.strptime(kknnngpL, "%Y/%m/%d"))
                else:
                    sddb.kknnngpL = timemanager.jst2utc_date(datetime.datetime.strptime(kknnngpL, "%Y/%m/%d %H:%M:%S"))
    #                sddb.kknnngpL = datetime.datetime.strptime(kknnngpL, "%Y/%m/%d %H:%M:%S")
            else:
                sddb.kknnngpL = None
            kknnngpU = self.request.get("kknnngpU")
            if kknnngpU:
                r = re.compile(".*:.*:.*").match(kknnngpU, 1)
                if r == None:
                    sddb.kknnngpU = timemanager.jst2utc_date(datetime.datetime.strptime(kknnngpU, "%Y/%m/%d"))
                else:
                    sddb.kknnngpU = timemanager.jst2utc_date(datetime.datetime.strptime(kknnngpU, "%Y/%m/%d %H:%M:%S"))
            else:
                sddb.kknnngpU = None
    
        #変更年月日
        #hnknngp = db.DateTimeProperty(verbose_name=u"変更年月日",auto_now_add = True)
            hnknngpL = self.request.get("hnknngpL")
            if hnknngpL:
                r = re.compile(".*:.*:.*").match(hnknngpL, 1)
                if r == None:
                    sddb.hnknngpL = timemanager.jst2utc_date(datetime.datetime.strptime(hnknngpL, "%Y/%m/%d"))
                else:
                    sddb.hnknngpL = timemanager.jst2utc_date(datetime.datetime.strptime(hnknngpL, "%Y/%m/%d %H:%M:%S"))
            else:
                sddb.hnknngpL = None
            hnknngpU = self.request.get("hnknngpU")
            if hnknngpU:
                r = re.compile(".*:.*:.*").match(hnknngpU, 1)
                if r == None:
                    sddb.hnknngpU = timemanager.jst2utc_date(datetime.datetime.strptime(hnknngpU, "%Y/%m/%d"))
                else:
                    sddb.hnknngpU = timemanager.jst2utc_date(datetime.datetime.strptime(hnknngpU, "%Y/%m/%d %H:%M:%S"))
            else:
                sddb.hnknngpU = None
    
        #登録年月日
        #turknngp = db.DateTimeProperty(verbose_name=u"登録年月日",auto_now_add = True)
            turknngpL = self.request.get("turknngpL")
            if turknngpL:
                r = re.compile(".*:.*:.*").match(turknngpL, 1)
                if r == None:
                    sddb.turknngpL = timemanager.jst2utc_date(datetime.datetime.strptime(turknngpL, "%Y/%m/%d"))
                else:
                    sddb.turknngpL = timemanager.jst2utc_date(datetime.datetime.strptime(turknngpL, "%Y/%m/%d %H:%M:%S"))
            else:
                sddb.turknngpL = None
            turknngpU = self.request.get("turknngpU")
            if turknngpU:
                r = re.compile(".*:.*:.*").match(turknngpU, 1)
                if r == None:
                    sddb.turknngpU = timemanager.jst2utc_date(datetime.datetime.strptime(turknngpU, "%Y/%m/%d"))
                else:
                    sddb.turknngpU = timemanager.jst2utc_date(datetime.datetime.strptime(turknngpU, "%Y/%m/%d %H:%M:%S"))
            else:
                sddb.turknngpU = None
    
        #更新年月日
        #ksnnngp = db.DateTimeProperty(verbose_name=u"更新年月日",auto_now=True)
            ksnnngpL = self.request.get("ksnnngpL")
            if ksnnngpL:
                r = re.compile(".*:.*:.*").match(ksnnngpL, 1)
                if r == None:
                    sddb.ksnnngpL = timemanager.jst2utc_date(datetime.datetime.strptime(ksnnngpL, "%Y/%m/%d"))
                else:
                    sddb.ksnnngpL = timemanager.jst2utc_date(datetime.datetime.strptime(ksnnngpL, "%Y/%m/%d %H:%M:%S"))
            else:
                sddb.ksnnngpL = None
            ksnnngpU = self.request.get("ksnnngpU")
            if ksnnngpU:
                r = re.compile(".*:.*:.*").match(ksnnngpU, 1)
                if r == None:
                    sddb.ksnnngpU = timemanager.jst2utc_date(datetime.datetime.strptime(ksnnngpU, "%Y/%m/%d"))
                else:
                    sddb.ksnnngpU = timemanager.jst2utc_date(datetime.datetime.strptime(ksnnngpU, "%Y/%m/%d %H:%M:%S"))
            else:
                sddb.ksnnngpU = None
        
    
        #売買賃貸区分
        #bbchntikbn = db.StringProperty(verbose_name=u"売買賃貸区分",choices=set([u"売買", u"賃貸"]))
            bbchntikbn = self.request.get("bbchntikbn")
            if bbchntikbn:
                sddb.bbchntikbn = bbchntikbn
            else:
                sddb.bbchntikbn = None
    
        
        
        #取扱い種類
        #dtsyuri = db.StringProperty(verbose_name=u"データ種類",choices=set([u"物件",u"事例",u"予約",u"商談中",u"査定中",u"重複",u"停止",u"競売"]))
            dtsyuri = self.request.get("dtsyuri")
            if dtsyuri:
                sddb.dtsyuri = dtsyuri
            else:
                sddb.dtsyuri = None
        #物件種別
        #bkknShbt = db.StringProperty(verbose_name=u"物件種別",choices=set([u"土地", u"戸建住宅等", u"マンション等", u"住宅以外の建物全部", u"住宅以外の建物一部"]))
            bkknShbt = self.request.get("bkknShbt")
            if bkknShbt:
                sddb.bkknShbt = bkknShbt
            else:
                sddb.bkknShbt = None
        #物件種目
        #bkknShmk = db.StringProperty(verbose_name=u"物件種目",choices=set([u"売地", u"借地権", u"底地権",u"新築戸建",u"中古戸建",u"新築テラス",u"中古テラス",u"店舗", u"店舗付住宅",u"住宅付店舗",u"新築マンション",u"中古マンション",u"新築タウン",u"中古タウン",u"新築リゾート",u"中古リゾート",u"事務所",u"店舗事務所", u"ビル", u"工場", u"マンション", u"倉庫", u"アパート", u"寮", u"旅館", u"ホテル",u"別荘", u"リゾート", u"文化住宅", u"その他"]))
            bkknShmk = self.request.get("bkknShmk")
            if bkknShmk:
                sddb.bkknShmk = bkknShmk
            else:
                sddb.bkknShmk = None
        #交通（分）1
        #kutuHnU = db.FloatProperty(verbose_name=u"交通（分）上限")
            kutuHnU = self.request.get("kutuHnU")
            if kutuHnU:
                sddb.kutuHnU = float(kutuHnU)
            else:
                sddb.kutuHnU = None
    
        #ペット可
        #ptflg = db.BooleanProperty(verbose_name=u"ペット可")
            ptflg = self.request.get("ptflg")
            if ptflg == "1":
                sddb.ptflg = True
            else:
                sddb.ptflg = None
        #マッチング可
        #mtngflg = db.BooleanProperty(verbose_name=u"マッチング可")
            mtngflg = self.request.get("mtngflg")
            if mtngflg == "1":
                sddb.mtngflg = True
            else:
                sddb.mtngflg = None
        #web検索許可
        #webknskflg = db.BooleanProperty(verbose_name=u"web検索許可")
            webknskflg = self.request.get("webknskflg")
            if webknskflg == "1":
                sddb.webknskflg = True
            else:
                sddb.webknskflg = None
        #建築条件
        #knckJyukn = db.BooleanProperty(verbose_name=u"建築条件")
            knckJyukn = self.request.get("knckJyukn")
            if knckJyukn == "1":
                sddb.knckJyukn = True
            else:
                sddb.knckJyukn = None
        #オーナーチェンジ
        #ornrChng = db.BooleanProperty(verbose_name=u"オーナーチェンジ")
            ornrChng = self.request.get("ornrChng")
            if ornrChng == "1":
                sddb.ornrChng = True
            else:
                sddb.ornrChng = None
        #告知事項
        #kktjkuflg = db.BooleanProperty(verbose_name=u"告知事項")
            kktjkuflg = self.request.get("kktjkuflg")
            if kktjkuflg == "1":
                sddb.kktjkuflg = True
            else:
                sddb.kktjkuflg = None
        #アイコン名
        #icons = db.StringListProperty(verbose_name=u"アイコン名")
            icons = self.request.get("icons")
            if icons:
                sddb.icons = icons
            else:
                sddb.icons = None
        #都道府県名
        #tdufknmi = db.StringProperty(verbose_name=u"都道府県名")
            tdufknmi = self.request.get("tdufknmi")
            if tdufknmi:
                sddb.tdufknmi = tdufknmi
            else:
                sddb.tdufknmi = None
        #建物名
        #ttmnmi = db.StringProperty(verbose_name=u"建物名")
            ttmnmi = self.request.get("ttmnmi")
            if ttmnmi:
                sddb.ttmnmi = ttmnmi
            else:
                sddb.ttmnmi = None
        #データ元
        #dataSource = db.StringProperty(verbose_name=u"データ元")
            dataSource = self.request.get("dataSource")
            if dataSource:
                sddb.dataSource = dataSource
            else:
                sddb.dataSource = None
        #広告転載区分
        #kukkTnsiKbn = db.StringProperty(verbose_name=u"広告転載区分",choices=set([u"広告可",u"一部可（インターネット）",u"一部可（チラシ・新聞広告）",u"広告可（但し要連絡）",u"不可",u"未確認"]))
            kukkTnsiKbn = self.request.get("kukkTnsiKbn")
            if kukkTnsiKbn:
                sddb.kukkTnsiKbn = kukkTnsiKbn
            else:
                sddb.kukkTnsiKbn = None
        #業者名
        #kiinni = db.StringProperty(verbose_name=u"業者名")
            kiinni = self.request.get("kiinni")
            if kiinni:
                sddb.kiinni = kiinni
            else:
                sddb.kiinni = None
        #接道方向
        #stduHuku = db.StringProperty(verbose_name=u"接道方向",choices=set([u"北",u"北東",u"東",u"南東",u"南",u"南西",u"西",u"北西"]))
            stduHuku = self.request.get("stduHuku")
            if stduHuku:
                sddb.stduHuku = stduHuku
            else:
                sddb.stduHuku = None
        #バルコニー方向
        #blcnyHuku = db.StringProperty(verbose_name=u"バルコニー方向",choices=set([u"北",u"北東",u"東",u"南東",u"南",u"南西",u"西",u"北西"]))
            blcnyHuku = self.request.get("blcnyHuku")
            if blcnyHuku:
                sddb.blcnyHuku = blcnyHuku
            else:
                sddb.blcnyHuku = None
        #土地面積
        #tcMnsk2L = db.FloatProperty(verbose_name=u"土地面積下限")
            tcMnsk2L = self.request.get("tcMnsk2L")
            if tcMnsk2L:
                sddb.tcMnsk2L = float(tcMnsk2L)
            else:
                sddb.tcMnsk2L = None
    
        #tcMnsk2U = db.FloatProperty(verbose_name=u"土地面積上限")
            tcMnsk2U = self.request.get("tcMnsk2U")
            if tcMnsk2U:
                sddb.tcMnsk2U = float(tcMnsk2U)
            else:
                sddb.tcMnsk2U = None
        #建物面積1
        #ttmnMnsk1L = db.FloatProperty(verbose_name=u"建物面積下限")
            ttmnMnsk1L = self.request.get("ttmnMnsk1L")
            if ttmnMnsk1L:
                sddb.ttmnMnsk1L = float(ttmnMnsk1L)
            else:
                sddb.ttmnMnsk1L = None 
    
        #ttmnMnsk1U = db.FloatProperty(verbose_name=u"建物面積上限")
            ttmnMnsk1U = self.request.get("ttmnMnsk1U")
            if ttmnMnsk1U:
                sddb.ttmnMnsk1U = float(ttmnMnsk1U)
            else:
                sddb.ttmnMnsk1U = None 
    
        #専有面積
        #snyuMnskSyuBbnMnsk2L = db.FloatProperty(verbose_name=u"専有面積下限")
            snyuMnskSyuBbnMnsk2L = self.request.get("snyuMnskSyuBbnMnsk2L")
            if snyuMnskSyuBbnMnsk2L:
                sddb.snyuMnskSyuBbnMnsk2L = float(snyuMnskSyuBbnMnsk2L)
            else:
                sddb.snyuMnskSyuBbnMnsk2L = None
        #snyuMnskSyuBbnMnsk2U = db.FloatProperty(verbose_name=u"専有面積上限")
            snyuMnskSyuBbnMnsk2U = self.request.get("snyuMnskSyuBbnMnsk2U")
            if snyuMnskSyuBbnMnsk2U:
                sddb.snyuMnskSyuBbnMnsk2U = float(snyuMnskSyuBbnMnsk2U)
            else:
                sddb.snyuMnskSyuBbnMnsk2U = None
        #価格
        #kkkuCnryuL = db.FloatProperty(verbose_name=u"価格下限")
            kkkuCnryuL = self.request.get("kkkuCnryuL")
            if kkkuCnryuL:
                sddb.kkkuCnryuL = float(kkkuCnryuL)
            else:
                sddb.kkkuCnryuL = None
        #kkkuCnryuU = db.FloatProperty(verbose_name=u"価格上限")
            kkkuCnryuU = self.request.get("kkkuCnryuU")
            if kkkuCnryuU:
                sddb.kkkuCnryuU = float(kkkuCnryuU)
            else:
                sddb.kkkuCnryuU = None
        #坪単価
        #tbTnkL = db.FloatProperty(verbose_name=u"坪単価下限")
            tbTnkL = self.request.get("tbTnkL")
            if tbTnkL:
                sddb.tbTnkL = float(tbTnkL)
            else:
                sddb.tbTnkL = None
        #tbTnkU = db.FloatProperty(verbose_name=u"坪単価上限")
            tbTnkU = self.request.get("tbTnkU")
            if tbTnkU:
                sddb.tbTnkU = float(tbTnkU)
            else:
                sddb.tbTnkU = None
        #㎡単価
        #m2TnkL = db.FloatProperty(verbose_name=u"㎡単価下限")
            m2TnkL = self.request.get("m2TnkL")
            if m2TnkL:
                sddb.m2TnkL = float(m2TnkL)
            else:
                sddb.m2TnkL = None
        #m2TnkU = db.FloatProperty(verbose_name=u"㎡単価上限")
            m2TnkU = self.request.get("m2TnkU")
            if m2TnkU:
                sddb.m2TnkU = float(m2TnkU)
            else:
                sddb.m2TnkU = None
        #想定利回り（％）
        #sutiRmwrPrcntL = db.FloatProperty(verbose_name=u"想定利回り（％）下限")
            sutiRmwrPrcntL = self.request.get("sutiRmwrPrcntL")
            if sutiRmwrPrcntL:
                sddb.sutiRmwrPrcntL = float(sutiRmwrPrcntL)
            else:
                sddb.sutiRmwrPrcntL = None
        #sutiRmwrPrcntU = db.FloatProperty(verbose_name=u"想定利回り（％）上限")
            sutiRmwrPrcntU = self.request.get("sutiRmwrPrcntU")
            if sutiRmwrPrcntU:
                sddb.sutiRmwrPrcntU = float(sutiRmwrPrcntU)
            else:
                sddb.sutiRmwrPrcntU = None 
    
        #接道接面
        #stduStmnL = db.StringProperty(verbose_name=u"接道接面下限")
            stduStmnL = self.request.get("stduStmnL")
            if stduStmnL:
                sddb.stduStmnL = stduStmnL
            else:
                sddb.stduStmnL = None
    
        #stduStmnU = db.StringProperty(verbose_name=u"接道接面上限")
            stduStmnU = self.request.get("stduStmnU")
            if stduStmnU:
                sddb.stduStmnU = stduStmnU
            else:
                sddb.stduStmnU = None 
    
        #接道幅員
        #stduFkinL = db.FloatProperty(verbose_name=u"接道幅員下限")
            stduFkinL = self.request.get("stduFkinL")
            if stduFkinL:
                sddb.stduFkinL = float(stduFkinL)
            else:
                sddb.stduFkinL = None 
    
            """
            #徒歩（分）1（1）
            #thHnU = db.FloatProperty(verbose_name=u"徒歩（分）上限")
                thHnU = self.request.get("thHnU")
                if thHnU:
                    sddb.thHnU = float(thHnU)
                else:
                    sddb.thHnU = None
        
            #徒歩（m）2（1）
            #thMU = db.FloatProperty(verbose_name=u"徒歩（m）上限")
                thMU = self.request.get("thMU")
                if thMU:
                    sddb.thMU = float(thMU)
                else:
                    sddb.thMU = None
            """
        #交通（分）1
        #kutuHnU = db.FloatProperty(verbose_name=u"交通（分）上限")
            kutuHnU = self.request.get("kutuHnU")
            if kutuHnU:
                sddb.kutuHnU = float(kutuHnU)
            else:
                sddb.kutuHnU = None
    
        #築年月（西暦）
        #cknngtSirkU = db.DateTimeProperty(verbose_name=u"築年月（西暦）上限")
            cknngtSirkU = self.request.get("cknngtSirkU")
            if cknngtSirkU:
                r = re.compile(".*:.*:.*").match(cknngtSirkU, 1)
                if r == None:
                    sddb.cknngtSirkU = timemanager.jst2utc_date(datetime.datetime.strptime(cknngtSirkU, "%Y/%m/%d"))
                else:
                    sddb.cknngtSirkU = timemanager.jst2utc_date(datetime.datetime.strptime(cknngtSirkU, "%Y/%m/%d %H:%M:%S"))
            else:
                sddb.cknngtSirkU = None
    
        #cknngtSirkL = db.DateTimeProperty(verbose_name=u"築年月（西暦）下限")
            cknngtSirkL = self.request.get("cknngtSirkL")
            if cknngtSirkL:
                r = re.compile(".*:.*:.*").match(cknngtSirkL, 1)
                if r == None:
                    sddb.cknngtSirkL = timemanager.jst2utc_date(datetime.datetime.strptime(cknngtSirkL, "%Y/%m/%d"))
                else:
                    sddb.cknngtSirkL = timemanager.jst2utc_date(datetime.datetime.strptime(cknngtSirkL, "%Y/%m/%d %H:%M:%S"))
            else:
                sddb.cknngtSirkL = None 
            sddb.put()

            if submit == u"検索":
                list = bksearchutl.do_searchdb(sddb)
                bksearchutl.addlist(self.corp_name,sddb.member,u'検索',list)
                self.redirect("/follow/" + self.corp_name + "/" + self.branch_name + "/"+ self.Sitename +"/follow.html?memberID=" + self.memberID)

            if submit == u"全ページ一括検索":
                list = bksearchutl.do_allsearch(mmdb)
                bksearchutl.addlist(self.corp_name,mmdb,u'全ページ一括検索',list)
                self.redirect("/follow/" + self.corp_name + "/" + self.branch_name + "/"+ self.Sitename +"/follow.html?memberID=" + self.memberID)
            
            self.get(**kwargs)