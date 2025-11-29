# -*- coding: utf-8 -*-

from google.cloud import ndb
from application.rotor import rotor
from application.models import Branch
import datetime
from application.wordstocker import wordstocker
from application.tantochangetasks import chagetanto


class member(ndb.Model):
    def encodeID(self, str):
        r = rotor
        return r.encode(str)

    def decodeID(self, str):
        r = rotor
        return r.decode(str)

    def trim(self, str):
        re = ""
        for s in str:
            if s == "-" or s == "(" or s == ")":
                pass
            else:
                re += s
        return re

    requestlst = ["資料請求", "問い合わせ", "条件変更", "見学希望", "検討中", "オープンハウス来場", "住所変更", "相談",
                  "他社にて契約", "辞退", "みあわせ", "物件確認", "商談中", "売却希望", "相談会来場", "場所が知りたい",
                  "NET資料請求", "査定について", "契約について", "決済について", "ローンについて", "休止", "緊急事態",
                  "クレーム", "買い付け証明", "売却条件", "買付条件", "一覧資料請求", "メール受信"]

    memberID = ndb.StringProperty(verbose_name="メンバーID")
    status = ndb.StringProperty(verbose_name="ステータス")
    CorpOrg_key_name = ndb.StringProperty(verbose_name="会社ID")
    Branch_Key_name = ndb.StringProperty(verbose_name="支店ID")
    sitename = ndb.StringProperty(verbose_name="サイト名")
    sid = ndb.StringProperty(verbose_name="セッションID")

    name = ndb.StringProperty(verbose_name="氏名")
    yomi = ndb.StringProperty(verbose_name="読み仮名")
    zip = ndb.StringProperty(verbose_name="郵便番号")
    address = ndb.StringProperty(verbose_name="住所")
    address1 = ndb.StringProperty(verbose_name="所在地１")
    address2 = ndb.StringProperty(verbose_name="所在地２")
    phone = ndb.StringProperty(verbose_name="電話")
    fax = ndb.StringProperty(verbose_name="FAX")

    CorpOrg_yomi = ndb.StringProperty(verbose_name="勤め先会社読み仮名")
    CorpOrg_yaku = ndb.StringProperty(verbose_name="勤め先会社役職")
    CorpOrg_zip = ndb.StringProperty(verbose_name="勤め先会社郵便番号")
    CorpOrg_address = ndb.StringProperty(verbose_name="勤め先会社住所")
    CorpOrg_address1 = ndb.StringProperty(verbose_name="勤め先会社所在地１")
    CorpOrg_address2 = ndb.StringProperty(verbose_name="勤め先会社所在地２")
    CorpOrg_phone = ndb.StringProperty(verbose_name="勤め先会社電話")
    CorpOrg_fax = ndb.StringProperty(verbose_name="勤め先会社FAX")

    mobilephone = ndb.StringProperty(verbose_name="携帯電話")
    mail = ndb.StringProperty(verbose_name="メールアドレス")
    netID = ndb.StringProperty(verbose_name="ネットID")
    netPass = ndb.StringProperty(verbose_name="パスワード")
    tourokunengappi = ndb.DateTimeProperty(verbose_name="登録年月日", auto_now_add=True)
    tanto = ndb.KeyProperty(kind='member', verbose_name="担当")  # Self-reference
    mno = ndb.FloatProperty(verbose_name="MNo")
    mr = ndb.FloatProperty(verbose_name="MR")
    uri = ndb.BooleanProperty(verbose_name="売")
    kai = ndb.BooleanProperty(verbose_name="買")
    kashi = ndb.BooleanProperty(verbose_name="貸")
    kari = ndb.BooleanProperty(verbose_name="借")
    baikai = ndb.StringProperty(verbose_name="媒介")
    seiyaku = ndb.StringProperty(verbose_name="成約")
    seiyakunengappi = ndb.DateTimeProperty(verbose_name="成約年月日")
    seiyakuankeito = ndb.BooleanProperty(verbose_name="成約アンケート")
    age = ndb.FloatProperty(verbose_name="年齢")
    kinzoku = ndb.FloatProperty(verbose_name="勤続年数")
    otona = ndb.FloatProperty(verbose_name="同居大人")
    kodomo = ndb.FloatProperty(verbose_name="同居子供")
    tutomesaki = ndb.StringProperty(verbose_name="勤め先")
    access = ndb.StringProperty(verbose_name="送信方法")
    zikoshikin = ndb.FloatProperty(verbose_name="自己資金")
    heisaituki = ndb.FloatProperty(verbose_name="返済予定額月々")
    heisaibonasu = ndb.FloatProperty(verbose_name="返済予定額ボーナス")
    kounyuziki = ndb.StringProperty(verbose_name="購入時期")
    kounyunen = ndb.FloatProperty(verbose_name="年")
    rank = ndb.StringProperty(verbose_name="区分")
    service = ndb.StringProperty(repeated=True, verbose_name="サービス")
    baitai = ndb.StringProperty(verbose_name="獲得媒体")
    syokai = ndb.StringProperty(verbose_name="初回アクセス")
    gyosya = ndb.StringProperty(verbose_name="紹介業者")
    bikou = ndb.TextProperty(verbose_name="備考")
    # 連番処理
    sdlist_max_num = ndb.IntegerProperty(verbose_name="検索条件リスト連番")
    LastRequestdatetime = ndb.DateTimeProperty(verbose_name="最終リクエスト日時", auto_now_add=True)
    LastSenddatetime = ndb.DateTimeProperty(verbose_name="最終送信日時", auto_now_add=True)
    SendintervaldayClass = ndb.IntegerProperty(verbose_name="送信間隔クラス", default=0)

    def put(self, **kwargs):
        # REVIEW-L2: ndb Key.get() calls are synchronous in context - ensure parent context if needed
        # REVIEW-L2: get_by_id() with UUID/string keys may fail - verify key generation
        try:
            oldme = member.get_by_id(self.key.id())
            if oldme:
                if oldme.tanto:
                    if self.tanto:
                        if self.tanto != oldme.tanto:
                            tanto_member = self.tanto.get()
                            oldme_tanto = oldme.tanto.get()
                            if tanto_member and oldme_tanto:
                                chagetanto.tantochange(self.CorpOrg_key_name, self.memberID, tanto_member.memberID, oldme_tanto.memberID)
        except Exception as e:
            # REVIEW-L2: Added exception handling for key retrieval
            print(f"Error in member.put(): {e}")
        return super(member, self).put(**kwargs)

    def reqinterval(self):
        """最終リクエスト日時の探査"""
        if not self.LastRequestdatetime:
            comblst = self.refmeslist  # メッセージコンビネータを取得
            buf = self.tourokunengappi
            for comb in comblst:  # いかにも馬鹿くさい処理である
                if self.isrequest(comb.refmes.kindname) and buf < comb.refmes.timestamp:
                    buf = comb.refmes.timestamp
            self.LastRequestdatetime = buf
            self.put()
        re = datetime.datetime.now() - self.LastRequestdatetime
        return re.days

    def sendinterval(self):
        if not self.LastSenddatetime:
            self.LastSenddatetimeset()
            return 0
        re = datetime.datetime.now() - self.LastSenddatetime
        self.SendintervaldayClass = re.days
        self.put()
        return re.days

    def isrequest(self, req):
        return req in self.requestlst

    def LastRequestdatetimeset(self):
        self.LastRequestdatetime = datetime.datetime.now()
        self.put()

    def LastSenddatetimeset(self):
        self.LastSenddatetime = datetime.datetime.now()
        self.put()

    def canSend(self, lev1noreactiondays, lev1maxsended, lev2noreactiondays, lev2maxsended, limitdistance):
        if self.rank == 'A':
            return True
        noreactiondaysStep = int(lev2noreactiondays) - int(lev1noreactiondays)
        reqi = self.reqinterval()
        reqiclass = (reqi - lev1noreactiondays) // noreactiondaysStep + 1  # //切り捨て除算
        maxsendedStep = int(lev2maxsended) - int(lev1maxsended)
        bklist = self.refbklist
        bklist.filter("sended", True)
        con = bklist.count(offset=0, limit=10000)
        sendiclass = (con - lev1maxsended) // maxsendedStep + 1  # //切り捨て除算
        if reqiclass > sendiclass:
            self.SendintervaldayClass = reqiclass
        else:
            self.SendintervaldayClass = sendiclass
        self.put()
        if self.sendinterval() < sendiclass:
            # 送信インターバルを超えていない
            if self.sendinterval() < reqiclass:
                # 無言日数インターバルを超えていない
                return False
        else:
            # 送信インターバルを超えてしまった
            if self.sendinterval() < reqiclass:
                # 無言日数がインターバルを超えていない
                return False
        if int(self.SendintervaldayClass) > int(limitdistance):
            return False
        return True

    def getNextsdlistNum(self):
        def procedure():
            if self.sdlist_max_num is None:
                self.sdlist_max_num = 0
            self.sdlist_max_num += 1
            self.put()
            return self.sdlist_max_num

        return ndb.transaction(procedure)

    def wordstock(self):
        if self.service:
            for w in self.service:
                wordstocker.set(self.CorpOrg_key_name, "サービス", w, self.Branch_Key_name, self.sitename)
