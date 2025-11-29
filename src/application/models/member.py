# -*- coding: utf-8 -*-

from google.appengine.ext import db
from application.rotor import rotor
import Branch
import datetime
from application.wordstocker import wordstocker
from application.tantochangetasks import chagetanto


class member(db.Model):
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

    requestlst = [u"資料請求",u"問い合わせ",u"条件変更",u"見学希望",u"検討中",u"オープンハウス来場",u"住所変更",u"相談",u"他社にて契約",u"辞退",u"みあわせ",u"物件確認",u"商談中",u"売却希望",u"相談会来場",u"場所が知りたい",u"NET資料請求",u"査定について",u"契約について",u"決済について",u"ローンについて",u"休止",u"緊急事態",u"クレーム",u"買い付け証明",u"売却条件",u"買付条件",u"一覧資料請求",u"メール受信"]

    memberID = db.StringProperty(verbose_name=u"メンバーID")
    status = db.StringProperty(verbose_name=u"ステータス", choices=set([u"CorpOrg",u"system",u"admin",u"管理者",u"業者",u"建築業者",u"紹介者",u"顧客",u"担当",u"その他"]))
    CorpOrg_key_name = db.StringProperty(verbose_name=u"会社ID")
    Branch_Key_name = db.StringProperty(verbose_name=u"支店ID")
    sitename = db.StringProperty(verbose_name=u"サイト名")
    sid = db.StringProperty(verbose_name=u"セッションID")

    name = db.StringProperty(verbose_name=u"氏名")
    yomi = db.StringProperty(verbose_name=u"読み仮名")
    zip = db.PostalAddressProperty(verbose_name=u"郵便番号")
    address = db.StringProperty(verbose_name=u"住所")
    address1 = db.StringProperty(verbose_name=u"所在地１")
    address2 = db.StringProperty(verbose_name=u"所在地２")
    phone = db.PhoneNumberProperty(verbose_name=u"電話")
    fax = db.PhoneNumberProperty(verbose_name=u"FAX")

    CorpOrg_yomi = db.StringProperty(verbose_name=u"勤め先会社読み仮名")
    CorpOrg_yaku = db.StringProperty(verbose_name=u"勤め先会社役職")
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
    #連番処理
    sdlist_max_num = db.IntegerProperty(verbose_name=u"検索条件リスト連番")
    LastRequestdatetime = db.DateTimeProperty(verbose_name=u"最終リクエスト日時",auto_now_add = True)
    LastSenddatetime = db.DateTimeProperty(verbose_name=u"最終送信日時",auto_now_add = True)
    SendintervaldayClass = db.IntegerProperty(verbose_name=u"送信間隔クラス",default = 0)

    def put(self):
        oldme = self.get(self.key())
        if oldme :
            if oldme.tanto:
                if self.tanto:
                    if self.tanto != oldme.tanto:
                        chagetanto.tantochange(self.CorpOrg_key_name, self.memberID, self.tanto.memberID, oldme.tanto.memberID)
        return db.Model.put(self)

    def reqinterval(self):
        '''
        最終リクエスト日時の探査
        '''
        if not self.LastRequestdatetime:
            comblst = self.refmeslist #メッセージコンビネータを取得
            buf =  self.tourokunengappi
            for comb in comblst: #いかにも馬鹿くさい処理である
                if self.isrequest(comb.refmes.kindname)  and buf < comb.refmes.timestamp:
                    buf = comb.refmes.timestamp
            self.LastRequestdatetime = buf
            self.put()
        re =datetime.datetime.now()-self.LastRequestdatetime
        return re.days

    def sendinterval(self):
        if not self.LastSenddatetime:
            self.LastSenddatetimeset()
            return 0
        re =datetime.datetime.now()-self.LastSenddatetime
        self.SendintervaldayClass = re.days
        self.put()
        return re.days


    def isrequest(self,req):
        return req in self.requestlst

    def LastRequestdatetimeset(self):
        self.LastRequestdatetime = datetime.datetime.now()
        self.put()
    def LastSenddatetimeset(self):
        self.LastSenddatetime = datetime.datetime.now()
        self.put()

    def canSend(self,lev1noreactiondays,lev1maxsended,lev2noreactiondays,lev2maxsended,limitdistance):
        if self.rank == 'A':
            return True
        noreactiondaysStep = int(lev2noreactiondays) - int(lev1noreactiondays)
        reqi = self.reqinterval()
        reqiclass = (reqi - lev1noreactiondays)//noreactiondaysStep+1 #//切り捨て除算
        maxsendedStep = int(lev2maxsended) - int(lev1maxsended)
        bklist = self.refbklist
        bklist.filter("sended",True)
        con = bklist.count(offset=0,limit=10000)
        sendiclass = (con - lev1maxsended)//maxsendedStep+1 #//切り捨て除算
        if reqiclass > sendiclass:
            self.SendintervaldayClass = reqiclass
        else :
            self.SendintervaldayClass = sendiclass
        self.put()
        if self.sendinterval() < sendiclass:
            #送信インターバルを超えていない
            if self.sendinterval() < reqiclass:
            #無言日数インターバルを超えていない
                return False
        else:
            #送信インターバルを超えてしまった
            if self.sendinterval() < reqiclass:
            #無言日数がインターバルを超えていない
                return False
        if int(self.SendintervaldayClass) > int(limitdistance):
            return False
        return True

    def getNextsdlistNum(self):
        def procedure():
            if self.sdlist_max_num is None:
                self.sdlist_max_num = 0
            self.sdlist_max_num += 1
            db.Model.put(self)
            return self.sdlist_max_num
        return db.run_in_transaction(procedure)

    def wordstock(self):
        if self.service:
            for w in self.service:
                wordstocker.set(self.CorpOrg_key_name,u"サービス",w,self.Branch_Key_name,self.sitename)




