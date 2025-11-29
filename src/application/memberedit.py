#!/usr/local/bin/python
# -*- coding: utf-8 -*-
#

'''

 1 class JsonField(CharField):
 2     """ JSONデータをポストする場合のフィールド。AJAXに便利かも """
 3     
 4     def __init__(self, *args, **kwargs):
 5         super(JsonField, self).__init__(*args, **kwargs)
 6 
 7     def clean(self, value):
 8         from google.appengine.dist import use_library
 9         value = super(JsonField, self).clean(value)
10         try:
11             json_data = simplejson.loads(value)
12         except Exception, e:
13             raise ValidationError(self.error_messages['invalid'])
14         return json_data

セレクトボックスや、チェックボックスで複数チェックされてリクエストされた場合に、チェックされた全ての値を読み取るには、
request.POST.getlist(キー)
とやる。キーに対応する全ての値がリストで貰える。
https://djangoproject.jp/doc/ja/1.0/ref/request-response.html

'''
#from google.appengine.dist import use_library
#use_library('django', '1.2')

import os
#from google.appengine.ext import webapp
import webapp2
from google.appengine.ext.webapp import template
from models import member
from models import CorpOrg
from models import Branch
import models.blob
from google.appengine.ext import db
import datetime
import re
import timemanager
from SecurePage import SecurePage
from wordstocker import wordstocker


#os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
#from google.appengine.dist import use_library
#use_library('django', '1.2')

class MemberEdit(SecurePage):


    def get(self,**kwargs):
        
        if self.Secure_init(*[u"管理者",u"担当"],**kwargs):
            
            if kwargs.get("sitename",None) == None:
                sitename = self.request.get("sitename")
            if sitename == 'backoffice':
                sitename = self.corp_name
   
            gql = member.member.all()
            gql.filter(" CorpOrg_key_name = " ,self.corp_name)
            gql.filter(" status = " ,u"担当")
            listtanto = []
            for e in gql:
                e2 = {}
                e2["name"]=e.name
                e2["key"]=str(e.key())
                listtanto.append(e2)
            gql = member.member.all()
            gql.filter(" CorpOrg_key_name = " ,self.corp_name)
            gql.filter(" status = " ,u"管理者")
            for e in gql:
                e2 = {}
                e2["name"]=e.name
                e2["key"]=str(e.key())
                listtanto.append(e2)
    
            self.tmpl_val["tanto"]=listtanto

            self.tmpl_val['servicelist'] = wordstocker.get(self.corp_name, u"サービス")

            path = os.path.dirname(__file__) + '/../templates/memberedit.html'
            self.response.out.write(template.render(path, self.tmpl_val))

    def post(self,**kwargs):
        if self.Secure_init(*[u"管理者",u"担当"]):

            if not self.memberID:
                co = CorpOrg.CorpOrg.get_by_key_name(self.corp_name)
                self.memberID = str(co.getNextIDNum())
            key_name = self.corp_name + "/" + self.memberID
            memdb = member.member.get_or_insert(key_name)
    
            #db.StringProperty(verbose_name=u"メンバーID"
            memdb.memberID = self.memberID
    
            #db.StringProperty(verbose_name=u"ステータス", choices=set([u"業者",u"建築業者",u"紹介者",u"顧客",u"担当",u"その他"])
            status = self.request.get("status")
            memdb.status = status if status else None
    
            #db.StringProperty(verbose_name=u"会社ID"
            memdb.CorpOrg_key_name = self.corp_name if self.corp_name else None
            
            #db.StringProperty(verbose_name=u"支店ID"
            memdb.Branch_Key_name = self.branch_name if self.branch_name else None
            
            #db.StringProperty(verbose_name=u"サイト名"
            sitename = self.request.get("sitename")
            memdb.sitename = sitename if sitename else None
            
            #db.StringProperty(verbose_name=u"氏名"
            name = self.request.get("name")
            memdb.name = name if name else None
            
            #db.StringProperty(verbose_name=u"読み仮名"
            yomi = self.request.get("yomi")
            memdb.yomi = yomi if yomi else None
            
            #db.PostalAddressProperty(verbose_name=u"郵便番号"
            zip = self.request.get("zip")
            memdb.zip = zip if zip else None
    
            #db.StringProperty(verbose_name=u"住所"
            address = self.request.get("address")
            memdb.address = address if address else None
    
            #db.StringProperty(verbose_name=u"所在地１"
            address1 = self.request.get("address1")
            memdb.address1 = address1 if address1 else None
    
            #db.StringProperty(verbose_name=u"所在地２"
            address2 = self.request.get("address2")
            memdb.address2 = address2 if address2 else None
    
            #db.PhoneNumberProperty(verbose_name=u"電話"
            phone = self.request.get("phone")
            memdb.phone = phone if phone else None
    
            #db.PhoneNumberProperty(verbose_name=u"FAX"
            fax = self.request.get("fax")
            memdb.fax = fax if fax else None
    
            #db.PhoneNumberProperty(verbose_name=u"携帯電話"
            mobilephone = self.request.get("mobilephone")
            memdb.mobilephone = mobilephone if mobilephone else None
    
            #db.EmailProperty(verbose_name=u"メールアドレス"
            mail = self.request.get("mail")
            memdb.mail = mail if mail else None
    
            #db.StringProperty(verbose_name=u"ネットID"
            netID = self.request.get("netID")
            memdb.netID = netID if netID else None
    
            #db.StringProperty(verbose_name=u"パスワード"
            netPass = self.request.get("netPass")
            memdb.netPass = netPass if netPass else None
    
            #db.TimeProperty(verbose_name=u"登録年月日",auto_now_add = True
            tourokunengappi = self.request.get("tourokunengappi")
            if tourokunengappi or tourokunengappi !="" :
                r = re.compile(".*:.*:.*").match(tourokunengappi, 1)
                if r == None:
                    memdb.tourokunengappi = timemanager.jst2utc_date(datetime.datetime.strptime(tourokunengappi, "%Y/%m/%d"))     
                else:
                    memdb.tourokunengappi = timemanager.jst2utc_date(datetime.datetime.strptime(tourokunengappi, "%Y/%m/%d %H:%M:%S"))
            else:
                memdb.hnknngp = self.now
    
    
            #db.SelfReferenceProperty(verbose_name=u"担当", collection_name="mytanto"
            tanto = self.request.get("tanto")
            if tanto and str(memdb.key())!=tanto:
                memdb.tanto = db.Key(tanto)
            else:
                memdb.tanto = None
    #        memdb.tanto = db.Key(tanto) if tanto else None
    
            #db.FloatProperty(verbose_name=u"MNo"
            mno = self.request.get("mno")
            memdb.mno = float(mno) if mno else None
    
            #db.FloatProperty(verbose_name=u"MR"
            mr = self.request.get("mr")
            memdb.mr = float(mr) if mr else None
    
            #db.BooleanProperty(verbose_name=u"売"
            uri = self.request.get("uri")
            memdb.uri = bool(uri) if uri == "1" else None
    
            #db.BooleanProperty(verbose_name=u"買"
            kai = self.request.get("kai")
            memdb.kai = bool(kai) if kai == "1" else None
    
            #db.BooleanProperty(verbose_name=u"貸"
            kashi = self.request.get("kashi")
            memdb.kashi = bool(kashi) if kashi == "1" else None
    
            #db.BooleanProperty(verbose_name=u"借"
            kari = self.request.get("kari")
            memdb.kari = bool(kari) if kari == "1" else None
    
            #db.StringProperty(verbose_name=u"媒介", choices=set([u"未",u"一般",u"専任",u"専属専任",u"その他"])
            baikai = self.request.get("baikai")
            memdb.baikai = baikai if baikai else None
    
            #db.StringProperty(verbose_name=u"成約", choices=set([u"未成約",u"成約",u"契予",u"決予",u"辞退",u"休止",u"ブラック",u"その他"])
            seiyaku = self.request.get("seiyaku")
            memdb.seiyaku = seiyaku if seiyaku else None
    
            #db.DateTimeProperty(verbose_name=u"成約年月日"
            seiyakunengappi = self.request.get("seiyakunengappi")
            if seiyakunengappi or seiyakunengappi!="":
                r = re.compile(".*:.*:.*").match(seiyakunengappi, 1)
                if r == None:
                    memdb.seiyakunengappi = timemanager.jst2utc_date(datetime.datetime.strptime(seiyakunengappi, "%Y/%m/%d"))    
                else:
                    memdb.seiyakunengappi = timemanager.jst2utc_date(datetime.datetime.strptime(seiyakunengappi, "%Y/%m/%d %H:%M:%S"))
            else:
                memdb.hnknngp = None
    
            #db.BooleanProperty(verbose_name=u"成約アンケート"
            seiyakuankeito = self.request.get("seiyakuankeito")
            memdb.seiyakuankeito = bool(seiyakuankeito) if seiyakuankeito == "1" else None
    
            #db.FloatProperty(verbose_name=u"年齢"
            age = self.request.get("age")
            memdb.age = float(age) if age else None
    
            #db.FloatProperty(verbose_name=u"勤続年数"
            kinzoku = self.request.get("kinzoku")
            memdb.kinzoku = float(kinzoku) if kinzoku else None
    
            #db.FloatProperty(verbose_name=u"同居大人"
            otona = self.request.get("otona")
            memdb.otona = float(otona) if otona else None
    
            #db.FloatProperty(verbose_name=u"同居子供"
            kodomo = self.request.get("kodomo")
            memdb.kodomo = float(kodomo) if kodomo else None
    
            #db.StringProperty(verbose_name=u"勤め先"
            tutomesaki = self.request.get("tutomesaki")
            memdb.tutomesaki = tutomesaki if tutomesaki else None

            #CorpOrg_yomi = db.StringProperty(verbose_name=u"勤め先会社読み仮名")
            CorpOrg_yomi = self.request.get("CorpOrg_yomi")
            memdb.CorpOrg_yomi = CorpOrg_yomi if CorpOrg_yomi else None
    
            #CorpOrg_yaku = db.StringProperty(verbose_name=u"勤め先会社役職")
            CorpOrg_yaku = self.request.get("CorpOrg_yaku")
            memdb.CorpOrg_yaku = CorpOrg_yaku if CorpOrg_yaku else None

            #CorpOrg_zip = db.PostalAddressProperty(verbose_name=u"勤め先会社郵便番号")
            CorpOrg_zip = self.request.get("CorpOrg_zip")
            memdb.CorpOrg_zip = CorpOrg_zip if CorpOrg_zip else None
    
            #CorpOrg_address = db.StringProperty(verbose_name=u"勤め先会社住所")
            CorpOrg_address = self.request.get("CorpOrg_address")
            memdb.CorpOrg_address = CorpOrg_address if CorpOrg_address else None
    
            #CorpOrg_address1 = db.StringProperty(verbose_name=u"勤め先会社所在地１")
            CorpOrg_address1 = self.request.get("CorpOrg_address1")
            memdb.CorpOrg_address1 = CorpOrg_address1 if CorpOrg_address1 else None
    
            #CorpOrg_address2 = db.StringProperty(verbose_name=u"勤め先会社所在地２")
            CorpOrg_address2 = self.request.get("CorpOrg_address2")
            memdb.CorpOrg_address2 = CorpOrg_address2 if CorpOrg_address2 else None
    
            #CorpOrg_phone = db.PhoneNumberProperty(verbose_name=u"勤め先会社電話")
            CorpOrg_phone = self.request.get("CorpOrg_phone")
            memdb.CorpOrg_phone = CorpOrg_phone if CorpOrg_phone else None
    
            #CorpOrg_fax = db.PhoneNumberProperty(verbose_name=u"勤め先会社FAX")        CorpOrg_yomi = self.request.get("CorpOrg_yomi")
            CorpOrg_fax = self.request.get("CorpOrg_fax")
            memdb.CorpOrg_fax = CorpOrg_fax if CorpOrg_fax else None

            #db.StringProperty(verbose_name=u"送信方法", choices=set([u"メール",u"FAX",u"郵送",u"手渡し",u"その他"])
            access = self.request.get("access")
            memdb.access = access if access else None
    
            #db.FloatProperty(verbose_name=u"自己資金") 
            zikoshikin = self.request.get("zikoshikin")
            memdb.zikoshikin = float(zikoshikin) if zikoshikin else None
    
            #db.FloatProperty(verbose_name=u"返済予定額月々"
            heisaituki = self.request.get("heisaituki")
            memdb.heisaituki = float(heisaituki) if heisaituki else None
    
            #db.FloatProperty(verbose_name=u"返済予定額ボーナス"
            heisaibonasu = self.request.get("heisaibonasu")
            memdb.heisaibonasu = float(heisaibonasu) if heisaibonasu else None
    
            #db.StringProperty(verbose_name=u"購入時期"
            kounyuziki = self.request.get("kounyuziki")
            memdb.kounyuziki = kounyuziki if kounyuziki else None
    
            #db.FloatProperty(verbose_name=u"年"
            kounyunen = self.request.get("kounyunen")
            memdb.kounyunen = float(kounyunen) if kounyunen else None
    
            #db.StringProperty(verbose_name=u"区分"
            rank = self.request.get("rank")
            memdb.rank = rank if rank else None
    
            #db.StringListProperty(verbose_name=u"サービス"
            service = self.request.get("service")
            if service:
                memdb.service = []
                for s in service.split(","):
                    if s != "":
                        memdb.service.append(s)
            else:
                memdb.service = []
    
            #db.StringProperty(verbose_name=u"獲得媒体"
            baitai = self.request.get("baitai")
            memdb.baitai = baitai if baitai else None
    
            #db.StringProperty(verbose_name=u"初回アクセス"
            syokai = self.request.get("syokai")
            memdb.syokai = syokai if syokai else None
    
            #db.StringProperty(verbose_name=u"紹介業者"
            gyosya = self.request.get("gyosya")
            memdb.gyosya = gyosya if gyosya else None
    
            #db.StringProperty(verbose_name=u"備考"
            bikou = self.request.get("bikou")
            memdb.bikou =  bikou

            memdb.put()
            memdb.wordstock()
            
            kwargs = {"memberID":memdb.memberID}
            
            self.get(**kwargs)