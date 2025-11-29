# -*- coding: utf-8 -*-

from google.appengine.ext import db
from application.rotor import rotor
import Branch
import datetime

class member2(db.Model):
    def encodeID(self,str):
        r=rotor
        return r.encode(str)
    def decodeID(self,str):
        r=rotor
        return r.decode(str)
    def trim(self,str):
        re =""
        for s in str:
            if s == "-" or s == "(" or s == ")" :
                pass
            else:
                re += s
        return re
    memberID = db.StringProperty(verbose_name=u"メンバーID")
    status = db.StringProperty(verbose_name=u"ステータス", choices=set([u"管理者",u"業者",u"建築業者",u"紹介者",u"顧客",u"担当",u"その他"]))
    CorpOrg_key_name = db.StringProperty(verbose_name=u"会社ID")
    Branch_Key_name = db.StringProperty(verbose_name=u"支店ID")
    sitename = db.StringProperty(verbose_name=u"サイト名")

    name = db.StringProperty(verbose_name=u"氏名")
    yomi = db.StringProperty(verbose_name=u"読み仮名")
    zip = db.PostalAddressProperty(verbose_name=u"郵便番号")
    address = db.StringProperty(verbose_name=u"住所")
    address1 = db.StringProperty(verbose_name=u"所在地１")
    address2 = db.StringProperty(verbose_name=u"所在地２")
    phone = db.PhoneNumberProperty(verbose_name=u"電話")
    fax = db.PhoneNumberProperty(verbose_name=u"FAX")

    CorpOrg_yomi = db.StringProperty(verbose_name=u"勤め先会社読み仮名")
    CorpOrg_zip = db.PostalAddressProperty(verbose_name=u"勤め先会社郵便番号")
    CorpOrg_address = db.StringProperty(verbose_name=u"勤め先会社住所")
    CorpOrg_address1 = db.StringProperty(verbose_name=u"勤め先会社所在地１")
    CorpOrg_address2 = db.StringProperty(verbose_name=u"勤め先会社所在地２")
    CorpOrg_phone = db.PhoneNumberProperty(verbose_name=u"勤め先会社電話")
    CorpOrg_fax = db.PhoneNumberProperty(verbose_name=u"勤め先会社FAX")
    
    mobilephone = db.PhoneNumberProperty(verbose_name=u"携帯電話")
    mail = db.EmailProperty(verbose_name=u"メールアドレス")
    netID = db.StringProperty(verbose_name=u"ネットID")
    netPass = db.StringProperty(verbose_name=u"パスワード")
    tourokunengappi = db.DateTimeProperty(verbose_name=u"登録年月日",auto_now_add = True)
    tanto = db.SelfReferenceProperty(verbose_name=u"担当", collection_name="mytanto")
    mno = db.FloatProperty(verbose_name=u"MNo")
    mr = db.FloatProperty(verbose_name=u"MR")
    uri = db.BooleanProperty(verbose_name=u"売")
    kai = db.BooleanProperty(verbose_name=u"買")
    kashi = db.BooleanProperty(verbose_name=u"貸")
    kari = db.BooleanProperty(verbose_name=u"借")
    baikai = db.StringProperty(verbose_name=u"媒介", choices=set([u"未",u"一般",u"専任",u"専属専任",u"その他"]))
    seiyaku = db.StringProperty(verbose_name=u"成約", choices=set([u"未成約",u"成約",u"契予",u"決予",u"辞退",u"休止",u"ブラック",u"仮",u"その他"]))
    seiyakunengappi = db.DateTimeProperty(verbose_name=u"成約年月日")
    seiyakuankeito = db.BooleanProperty(verbose_name=u"成約アンケート")
    age = db.FloatProperty(verbose_name=u"年齢")
    kinzoku = db.FloatProperty(verbose_name=u"勤続年数")
    otona = db.FloatProperty(verbose_name=u"同居大人")
    kodomo = db.FloatProperty(verbose_name=u"同居子供")
    tutomesaki = db.StringProperty(verbose_name=u"勤め先")
    access = db.StringProperty(verbose_name=u"送信方法", choices=set([u"メール",u"FAX",u"郵送",u"手渡し",u"その他"]))
    zikoshikin = db.FloatProperty(verbose_name=u"自己資金") 
    heisaituki = db.FloatProperty(verbose_name=u"返済予定額月々")
    heisaibonasu = db.FloatProperty(verbose_name=u"返済予定額ボーナス")
    kounyuziki = db.StringProperty(verbose_name=u"購入時期")
    kounyunen = db.FloatProperty(verbose_name=u"年")
    rank = db.StringProperty(verbose_name=u"区分")
    service = db.StringListProperty(verbose_name=u"サービス")
    baitai = db.StringProperty(verbose_name=u"獲得媒体")
    syokai = db.StringProperty(verbose_name=u"初回アクセス")
    gyosya = db.StringProperty(verbose_name=u"紹介業者")
    bikou =  db.StringProperty(verbose_name=u"備考",multiline=True)
    
    

