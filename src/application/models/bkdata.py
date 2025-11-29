# -*- coding: utf-8 -*-

from google.appengine.ext import db
import Branch
import datetime
from application.wordstocker import wordstocker
from geo.geomodel import GeoModel
from application.GqlEncoder import GqlJsonEncoder
from application.models.bksearchaddress import getname
import application.timemanager as timemanager
import urllib

class BKdata(GeoModel):

#   ↑モジュール名.クラス名.メソッド名
    def setjson(self):
        pass
    def getjson(self):
        pass


    def makedata(self,media):
        if media:
            query_str = u"SELECT * FROM Blob WHERE CorpOrg_key = '" + self.nyrykkisyID + u"' AND Branch_Key = '" + self.nyrykstnID + u"' AND bkID = '" + self.bkID + u"' AND media = '" + media + u"' ORDER BY media,pos ASC"
            blobs = db.GqlQuery (query_str)
            b2 = []
            heimenzu = None
            for c in blobs:
                if c.pos != u"平面図":
                    b2.append(c)
                else :
                    heimenzu = c
        else :
            query_str = u"SELECT * FROM Blob WHERE CorpOrg_key = '" + self.nyrykkisyID + u"' AND Branch_Key = '" + self.nyrykstnID + u"' AND bkID = '" + self.bkID + u"' ORDER BY media,pos ASC"
            blobs = db.GqlQuery (query_str)
            b2 = []
            heimenzu = None
            for c in blobs:
                if c.pos != u"平面図":
                    b2.append(c)
                else :
                    heimenzu = c
        webkkkk = False
        if self.kukkTnsiKbn in [u"広告可",u"一部可（インターネット）",u"広告可（但し要連絡）"]:
            webkkkk = True
        totitubo = None
        if self.tcMnsk2:
            totitubo = float(int(self.tcMnsk2 * 0.3025 * 100))/100
        tatemonotubo = None
        if self.ttmnMnsk1:
            tatemonotubo = float(int(self.ttmnMnsk1 * 0.3025 * 100))/100
        kakakuM = None
        if self.kkkuCnryu:
            kakakuM = GqlJsonEncoder.floatfmt(float(int(self.kkkuCnryu/100))/100)
        tknngt = None
        if self.cknngtSirk:
            # tknngt = self.cknngtSirk.year # 2016/10/16utc2jst
            tknngt = timemanager.utc2jst_date(self.cknngtSirk).year
            if int(tknngt) < 1989:
                tknngt = u"昭和" + str(tknngt-1925) + u"年"
            elif int(tknngt) >= 1989:
                tknngt = u"平成" + str(tknngt-1988) + u"年"
            elif int(tknngt) >= 2019:
                tknngt = u"令和" + str(tknngt-2018) + u"年"
            else:
                tknngt = tknngt + u"年"
        #【{{data.bkdata.bkID}}】{{data.bkdata.ttmnmi}}について
        mailmsg = u'【' + self.bkID + u'】'
        if self.ttmnmi:
            mailmsg += self.ttmnmi
        if self.bkknShmk:
            mailmsg += self.bkknShmk
        mailmsg += u'について'
        mailmsgCP932 = urllib.quote_plus(mailmsg.encode("CP932"))

        #getname(cls,co,br,div,tod,ad1,ad2):
        """
                    すべての物件についてput()を回したあとは下記は不要となる
                    メディアの取り扱いについて　平面図について　広告可について　詳細にチェックすること
        """
        if self.tdufknmi and self.shzicmi1 and self.shzicmi2 and self.gakku == []:
            self.gakku = getname(self.nyrykkisyID,self.nyrykstnID,u"小学校区",self.tdufknmi,self.shzicmi1,self.shzicmi2)
        gakkuS = self.gakku
        data = GqlJsonEncoder.GQLtimeandmoneyfmt(self)
        """
        show の makedata は　"auth":self.auth　を持つので要注意！！！
        """
        entitys = { "mailmsg":mailmsg, "mailmsgCP932":mailmsgCP932,"bkdatakey":self.key(),"bkdata":data,"picdata":b2,"kakakuM":kakakuM,"totitubo":totitubo,"tatemonotubo":tatemonotubo,"tknngtG":tknngt,"heimenzu":heimenzu,"webkkkk":webkkkk,"gakkuS":gakkuS}
        return entitys

    def getsearchkey(self,l):
        res = []
        for i in xrange(0,len(l)):
            if res:
                res.append(l[0]+l[i])
            else:
                res.append(l[i])
            for i2 in xrange(1,len(res)-1):
                res.append(res[i2]+l[i])
        return res


    def put(self):
        #トリガ処理
        if not self.ksyknkkku:
            #self.kkkksyk = False
            if self.kkkuCnryu:
                self.ksyknkkku = self.kkkuCnryu
        #else:
            #self.kkkksyk = True
        #if not (self.ksnkisID and self.ksnstnID and self.ksntnt):
            #raise AssertionError, u"更新者情報が足りません"
        if not self.kknnngp:
            self.kknnngp = datetime.datetime.now()
        if not self.hnknngp:
            self.hnknngp = datetime.datetime.now()
        if not self.ksnnngp :
            self.ksnnngp = datetime.datetime.now()
        if self.bkID == u"bkID_enpty_ress_dumy" or self.bkID == None :
            br = Branch.Branch.get_or_insert(self.corp.name + u"/" + self.branch.name)
            self.bkID = str(br.getNextNum())
            self.key_name = self.corp.name + u"/" + self.branch.name + u"/" + self.bkID
        if not self.sksijky:
            self.sksijky = u"請求チェック"
        if not self.kukkTnsiKbn:
            self.kukkTnsiKbn = u"未確認"
        if self.icons:
            self.isicon = True
            for w in self.icons:
                wordstocker.set(self.nyrykkisyID,u"アイコン",w,self.nyrykstnID)
        else:
            self.isicon = False
        if self.idkd:
            self.location = self.idkd
            self.update_location()
            self.isidkd = True
        else:
            self.location = None
            self.isidkd = False
        #kukkTnsiKbn = db.StringProperty(verbose_name=u"広告転載区分", choices=set([u"広告可",u"一部可（インターネット）",u"一部可（チラシ・新聞広告）",u"広告可（但し要連絡）",u"不可",u"未確認"]))

        if self.kukkTnsiKbn in [u"広告可",u"一部可（インターネット）",u"一部可（チラシ・新聞広告）",u"広告可（但し要連絡）"]:
            self.kukkk = True
        else:
            self.kukkk = False

        if self.tdufknmi and self.shzicmi1 and self.shzicmi2 and self.gakku == []:
            self.gakku = getname(self.nyrykkisyID,self.nyrykstnID,u"小学校区",self.tdufknmi,self.shzicmi1,self.shzicmi2)
        #GqlJsonEncoder(ensure_ascii=False).encode(entitys)
        #self.gakkuS = None

        #nyrykkisyID入力会社ID   bbchntikbn売買賃貸区分  dtsyuri取扱い種類  bkknShbt物件種別 bkknShmk物件種目  sksijky作成状況 isiconアイコンあり isidkd座標有り kukkk広告可
        l=['corp:' + str(self.nyrykkisyID),
        '/bbchntikbn:' + str(self.bbchntikbn),
        '/dtsyuri:' + str(self.dtsyuri),
        '/bkknShbt:' + str(self.bkknShbt),
        '/bkknShmk:' + str(self.bkknShmk),
        '/sksijky:' + str(self.sksijky),
        '/isicon:' + str(self.isicon),
        '/isidkd:' + str(self.isidkd),
        '/kukkk:' + str(self.kukkk)]
        self.searchkeys = self.getsearchkey(l)

        return db.Model.put(self)


    #物件番号
    bkID = db.StringProperty(verbose_name="物件番号",required=True)
    #更新年月日
    ksnnngp = db.DateTimeProperty(verbose_name=u"更新年月日",auto_now=True)
    #更新会社ID
    ksnkisID = db.StringProperty(verbose_name=u"更新会社ID")
    #更新支店ID
    ksnstnID = db.StringProperty(verbose_name=u"更新支店ID")
    #更新担当
    ksntnt = db.StringProperty(verbose_name=u"更新担当")
    #確認年月日
    kknnngp = db.DateTimeProperty(verbose_name=u"確認年月日",auto_now_add=True)

    #検索キー
    searchkeys = db.StringListProperty(verbose_name=u"検索キー")

    #json
    json = db.TextProperty(verbose_name=u"JSON")

    #isicon
    isicon = db.BooleanProperty(verbose_name=u"アイコンあり",default=False)

    #小学校区
    gakku = db.StringListProperty(verbose_name=u"小学校区",default=[])
#    gakkuS = db.StringProperty(verbose_name=u"小学校区")

    #ペット可
    ptflg = db.BooleanProperty(verbose_name=u"ペット可")
    #マッチング可
    mtngflg = db.BooleanProperty(verbose_name=u"マッチング可",default=True)
    #広告可
    kukkk = db.BooleanProperty(verbose_name=u"広告可")
    #web検索許可
    webknskflg = db.BooleanProperty(verbose_name=u"web検索許可",default=True)
    #他業者可
    tgysyflg = db.BooleanProperty(verbose_name=u"他業者紹介可")
    #重複チェック
    duplicationcheck = db.BooleanProperty(verbose_name=u"重複チェック")

    #告知事項
    kktjkuflg = db.StringProperty(verbose_name=u"告知事項")

    #交渉可能価格
    ksyknkkku = db.FloatProperty(verbose_name=u"交渉可能価格")

    #価格交渉可
    kkkksyk = db.BooleanProperty(verbose_name=u"価格交渉可")

    #地図センター緯度経度
    chzsntidkd = db.GeoPtProperty(verbose_name=u"地図センター緯度経度")

    #緯度経度
    idkd = db.GeoPtProperty(verbose_name=u"緯度経度")
    isidkd = db.BooleanProperty(verbose_name=u"位置情報有",default=False)

    #地図レンジ
    chzrnj = db.IntegerProperty(verbose_name=u"地図レンジ")
    #アイコン名
    icons = db.StringListProperty(verbose_name=u"アイコン名")

    #作成状況
    sksijky = db.StringProperty(verbose_name=u"作成状況",choices=set([u"請求チェック",u"一覧のみ",u"資料請求",u"依頼中",u"入手不可",u"入手済み",u"分類チェック",u"不要",u"未作成",u"作成済み",u"ＨＰ掲載"]))
    #至急送信
    skyssnflg = db.BooleanProperty(verbose_name=u"至急送信")
    #自動ポイント
    zdupint = db.FloatProperty(verbose_name=u"自動ポイント")
    #評価ポイント
    hykpint = db.FloatProperty(verbose_name=u"評価ポイント")
    #入力会社ID
    nyrykkisyID = db.StringProperty(verbose_name=u"入力会社ID")
    #入力支店ID
    nyrykstnID = db.StringProperty(verbose_name=u"入力支店ID")
    #入力担当
    nyryktnt = db.StringProperty(verbose_name=u"入力担当")

    #データ元
    dataSource = db.StringProperty(verbose_name=u"データ元")

    #データ元物件番号
    bknbng = db.StringProperty(verbose_name=u"データ元物件番号")
    #売買賃貸区分
    bbchntikbn = db.StringProperty(verbose_name=u"売買賃貸区分", choices=set([u"売買", u"賃貸", u"その他"]))
    #取扱い種類
    dtsyuri = db.StringProperty(verbose_name=u"データ種類", choices=set([u"物件",u"事例",u"予約",u"商談中",u"査定中",u"重複",u"停止",u"競売",u"現場",u"サンプル", u"その他"]))
    #物件種別
    bkknShbt = db.StringProperty(verbose_name=u"物件種別", choices=set([u"土地", u"戸建住宅等", u"マンション等", u"住宅以外の建物全部", u"住宅以外の建物一部",u"賃貸一戸建",u"賃貸マンション",u"賃貸土地",u"賃貸外全",u"賃貸外一", u"その他"]))
    #物件種目
    bkknShmk = db.StringProperty(verbose_name=u"物件種目", choices=set([u"売地", u"借地権", u"底地権",u"新築戸建",u"中古戸建",u"新築テラス",u"中古テラス", u"店舗", u"店舗付住宅", u"住宅付店舗",u"新築マンション",u"中古マンション",u"新築タウン",u"中古タウン",u"新築リゾート",u"中古リゾート",u"店舗事務所", u"ビル", u"工場", u"マンション", u"倉庫", u"アパート", u"寮", u"旅館", u"ホテル", u"別荘", u"リゾート", u"文化住宅", u"貸家",u"テラス",u"マンション",u"タウン",u"間借り",u"居住用地",u"事業用地",u"店舗戸建",u"旅館等",u"寮",u"住宅付店舗戸建",u"店舗事務所",u"店舗一部",u"事務所",u"住宅付店舗一部",u"マンション一室",u"その他"]))
    #業者名
    kiinni = db.StringProperty(verbose_name=u"業者名")
    #代表電話番号
    dihyodnwbngu = db.PhoneNumberProperty(verbose_name=u"代表電話番号")
    #問合せ担当者（1）
    tiawsTntush = db.StringProperty(verbose_name=u"問合せ担当者（1）")
    #問合せ電話番号（1）
    tiawsDnwBngu = db.PhoneNumberProperty(verbose_name=u"問合せ電話番号（1）")
    #Eメールアドレス（1）
    emlAdrs = db.EmailProperty(verbose_name=u"Eメールアドレス（1）")
    #図面
    zmn = db.StringProperty(verbose_name=u"図面")
    #登録年月日
    turknngp = db.DateTimeProperty(verbose_name=u"登録年月日",auto_now_add = True)
    #変更年月日
    hnknngp = db.DateTimeProperty(verbose_name=u"変更年月日",auto_now_add = True)
    #取引条件の有効期限
    trhkJyuknYukuKgn = db.DateTimeProperty(verbose_name=u"取引条件の有効期限")
    #

    #

    #

    #新築中古区分
    sntktyukkbn = db.StringProperty(verbose_name=u"新築中古区分")
    #都道府県名
    tdufknmi = db.StringProperty(verbose_name=u"都道府県名")
    #所在地名1
    shzicmi1 = db.StringProperty(verbose_name=u"所在地名1")
    #所在地名2
    shzicmi2 = db.StringProperty(verbose_name=u"所在地名2")
    #所在地名3
    shzicmi3 = db.StringProperty(verbose_name=u"所在地名3")
    #建物名
    ttmnmi = db.StringProperty(verbose_name=u"建物名")
    #部屋番号
    hyBngu = db.StringProperty(verbose_name=u"部屋番号")
    #その他所在地表示
    sntShzicHyuj = db.StringProperty(verbose_name=u"その他所在地表示")
    #棟番号
    tuBngu = db.StringProperty(verbose_name=u"棟番号")
    #沿線略称（1）
    ensnmi1 = db.StringProperty(verbose_name=u"沿線略称（1）")
    #
    ensnmi2 = db.StringProperty(verbose_name=u"沿線略称（2）")
    #
    ensnmi3 = db.StringProperty(verbose_name=u"沿線略称（3）")
    #駅名（1）
    ekmi1 = db.StringProperty(verbose_name=u"駅名（1）")
    #
    ekmi2 = db.StringProperty(verbose_name=u"駅名（2）")
    #
    ekmi3 = db.StringProperty(verbose_name=u"駅名（3）")
    #徒歩（分）1（1）
    thHn11 = db.FloatProperty(verbose_name=u"徒歩（分）1（1）")
    #
    thHn12 = db.FloatProperty(verbose_name=u"徒歩（分）1（2）")
    #
    thHn13 = db.FloatProperty(verbose_name=u"徒歩（分）1（3）")
    #徒歩（m）2（1）
    thM21 = db.FloatProperty(verbose_name=u"徒歩（m）2（1）")
    #
    thM22 = db.FloatProperty(verbose_name=u"徒歩（m）2（2）")
    #
    thM23 = db.FloatProperty(verbose_name=u"徒歩（m）2（3）")
    #バス（1）
    bs1 = db.StringProperty(verbose_name=u"バス（1）")
    #
    bs2 = db.StringProperty(verbose_name=u"バス（2）")
    #
    bs3 = db.StringProperty(verbose_name=u"バス（3）")
    #バス路線名（1）
    bsRsnmi1 = db.StringProperty(verbose_name=u"バス路線名（1）")
    #
    bsRsnmi2 = db.StringProperty(verbose_name=u"バス路線名（2）")
    #
    bsRsnmi3 = db.StringProperty(verbose_name=u"バス路線名（3）")
    #バス停名称（1）
    bstiMishu1 = db.StringProperty(verbose_name=u"バス停名称（1）")
    #
    bstiMishu2 = db.StringProperty(verbose_name=u"バス停名称（2）")
    #
    bstiMishu3 = db.StringProperty(verbose_name=u"バス停名称（3）")
    #停歩（分）（1）
    tihHn1 = db.FloatProperty(verbose_name=u"停歩（分）（1）")
    #
    tihHn2 = db.FloatProperty(verbose_name=u"停歩（分）（2）")
    #
    tihHn3 = db.FloatProperty(verbose_name=u"停歩（分）（3）")
    #停歩（m）（1）
    tihM1 = db.FloatProperty(verbose_name=u"停歩（m）（1）")
    #
    tihM2 = db.FloatProperty(verbose_name=u"停歩（m）（2）")
    #
    tihM3 = db.FloatProperty(verbose_name=u"停歩（m）（3）")
    #車（km）（1）
    krmKm1 = db.FloatProperty(verbose_name=u"車（km）（1）")
    #
    krmKm2 = db.FloatProperty(verbose_name=u"車（km）（2）")
    #
    krmKm3 = db.FloatProperty(verbose_name=u"車（km）（3）")
    #

    #その他交通手段
    sntKutuShdn = db.StringProperty(verbose_name=u"その他交通手段")
    #交通（分）1
    kutuHn = db.FloatProperty(verbose_name=u"交通（分）1")
    #交通（m）2
    kutuM = db.FloatProperty(verbose_name=u"交通（m）2")
    #現況
    gnkyu = db.StringProperty(verbose_name=u"現況", choices=set([u"更地",u"上物有",u"居住中",u"空家",u"賃貸中",u"未完成"]))
    #現況予定年月
    gnkyuYtiNngt = db.DateTimeProperty(verbose_name=u"現況予定年月")
    #

    #

    #引渡時期
    hkwtsNyukyJk = db.StringProperty(verbose_name=u"引渡時期", choices=set([u"即時",u"相談",u"期日指定",u"予定"]))
    #引渡年月（西暦）
    hkwtsNyukyNngtSirk = db.DateTimeProperty(verbose_name=u"引渡年月（西暦）")
    #

    #

    #引渡旬
    hkwtsNyukyShn = db.StringProperty(verbose_name=u"引渡旬", choices=set([u"上旬",u"中旬",u"下旬"]))
    #入居年月（西暦）
    nyukyNngtSirk = db.DateTimeProperty(verbose_name=u"入居年月（西暦）")
    #

    #

    #

    #入居日

    #取引態様
    trhktiyu = db.StringProperty(verbose_name=u"取引態様", choices=set([u"売主",u"代理",u"専属",u"専任",u"一般"]))
    #報酬形態
    hushuKiti = db.StringProperty(verbose_name=u"報酬形態", choices=set([u"分かれ",u"当方不払",u"当方片手数",u"代理折半",u"相談"]))
    #手数料割合率
    tsuryuWraiRt = db.FloatProperty(verbose_name=u"手数料割合率")
    #手数料
    tsuryu = db.FloatProperty(verbose_name=u"手数料")
    #価格
    kkkuCnryu = db.FloatProperty(verbose_name=u"価格")
    #価格消費税
    kkkuCnryuShuhzi = db.FloatProperty(verbose_name=u"価格消費税")
    #坪単価
    tbTnk = db.FloatProperty(verbose_name=u"坪単価")
    #㎡単価
    m2Tnk = db.FloatProperty(verbose_name=u"㎡単価")
    #想定利回り（％）
    sutiRmwrPrcnt = db.FloatProperty(verbose_name=u"想定利回り（％）")
    #面積計測方式
    mnskKisokHusk = db.StringProperty(verbose_name=u"面積計測方式", choices=set([u"公簿",u"実測",u"壁芯",u"内法"]))
    #土地面積
    tcMnsk2 = db.FloatProperty(verbose_name=u"土地面積")
    #土地共有持分面積
    tcMcbnSumnsk = db.FloatProperty(verbose_name=u"土地共有持分面積")
    #土地共有持分（分子）
    tcMcbnBns = db.FloatProperty(verbose_name=u"土地共有持分（分子）")
    #平米の場合

    #土地共有持分（分母）
    tcMcbnBnb = db.FloatProperty(verbose_name=u"土地共有持分（分母）")
    #平米の場合

    #建物面積1
    ttmnMnsk1 = db.FloatProperty(verbose_name=u"建物面積1")
    #
    ttmnMnsk2 = db.FloatProperty(verbose_name=u"建物面積2")
    #専有面積
    snyuMnskSyuBbnMnsk2 = db.FloatProperty(verbose_name=u"専有面積")
    #私道負担有無
    sduFtnUm = db.StringProperty(verbose_name=u"私道負担有無", choices=set([u"有",u"無"]))
    #私道面積
    sduMnsk = db.FloatProperty(verbose_name=u"私道面積")
    #バルコニー（テラス）面積
    blcnyTrsMnsk = db.FloatProperty(verbose_name=u"バルコニー（テラス）面積")
    #専用庭面積
    snyouNwMnsk = db.FloatProperty(verbose_name=u"専用庭面積")
    #セットバック区分
    stbkKbn = db.StringProperty(verbose_name=u"セットバック区分", choices=set([u"無",u"有",u"済"]))
    #後退距離（m）
    kutiKyrM = db.FloatProperty(verbose_name=u"後退距離（m）")
    #セットバック面積（㎡）
    stbkMnskM2 = db.FloatProperty(verbose_name=u"セットバック面積（㎡）")
    #開発面積／総面積
    kihtMnskSumnsk = db.FloatProperty(verbose_name=u"開発面積／総面積")
    #販売総面積
    hnbiSumnsk = db.FloatProperty(verbose_name=u"販売総面積")
    #販売区画数
    hnbiKkksu = db.FloatProperty(verbose_name=u"販売区画数")
    #工事完了年月（西暦）
    #kujKnryuNngtSirkGG #kujKnryuNngtSirkYY #kujKnryuNngtSirkMM
    kujKnryuNngtSirk = db.DateTimeProperty(verbose_name=u"工事完了年月（西暦）")
    #建築面積
    knckMnsk = db.FloatProperty(verbose_name=u"建築面積")
    #
    #
    #延べ面積
    nbMnsk = db.FloatProperty(verbose_name=u"延べ面積")
    #敷地延長の有無
    skcEnchuUm = db.StringProperty(verbose_name=u"敷地延長の有無", choices=set([u"有",u"無"]))
    #敷地延長（30%以上表示）
    skcEnchu30PrcntIjyuHyuj = db.FloatProperty(verbose_name=u"敷地延長（30%以上表示）")
    #借地料
    shkcryu = db.FloatProperty(verbose_name=u"借地料")
    #借地期間
    shkcKknYY = db.FloatProperty(verbose_name=u"借地期間年")
    shkcKknMM = db.FloatProperty(verbose_name=u"借地期間月")
    #shkcKknYY
    #
    #shkcKknMM
    #借地期限（西暦）
    shkcKgnSirk = db.DateTimeProperty(verbose_name=u"借地期限（西暦）")
    #shkcKgnSirkGG
    #
    #shkcKgnSirkYY
    #
    #shkcKgnSirkMM
    #施設費用項目（1）
    sstHyuKumk1 = db.StringProperty(verbose_name=u"施設費用項目（1）")
    #
    sstHyuKumk2 = db.StringProperty(verbose_name=u"施設費用項目（2）")
    #
    sstHyuKumk3 = db.StringProperty(verbose_name=u"施設費用項目（3）")
    #施設費用（1）
    sstHyu1 = db.FloatProperty(verbose_name=u"施設費用（1）")
    #
    sstHyu2 = db.FloatProperty(verbose_name=u"施設費用（2）")
    #
    sstHyu3 = db.FloatProperty(verbose_name=u"施設費用（3）")
    #国土法届出
    kkdhuTdkd = db.StringProperty(verbose_name=u"国土法届出", choices=set([u"要",u"中",u"不要"]))
    #登記簿地目
    tukbCmk = db.StringProperty(verbose_name=u"登記簿地目", choices=set([u"宅地",u"田",u"畑",u"山林",u"雑種",u"他"]))
    #現況地目
    gnkyuCmk = db.StringProperty(verbose_name=u"現況地目", choices=set([u"宅地",u"田",u"畑",u"山林",u"雑種",u"他"]))
    #都市計画
    tskikk = db.StringProperty(verbose_name=u"都市計画", choices=set([u"市街",u"調整",u"非線引き",u"域外",u"準都市"]))
    #用途地域（1）
    yutCik1 = db.StringProperty(verbose_name=u"用途地域（1）", choices=set([u"一低",u"二中",u"二住",u"近商",u"商業",u"準工",u"工業",u"工専",u"二低",u"一中",u"一住",u"準住",u"無指定"]))
    #用途地域（2）
    yutCik2 = db.StringProperty(verbose_name=u"用途地域（2）", choices=set([u"一低",u"二中",u"二住",u"近商",u"商業",u"準工",u"工業",u"工専",u"二低",u"一中",u"一住",u"準住",u"無指定"]))
    #最適用途
    sitkYut = db.StringProperty(verbose_name=u"最適用途", choices=set([u"住宅用地",u"マンション用地",u"ビル用地",u"店舗用地",u"工業用地",u"配送センター用地",u"営業所用地",u"保養所用地",u"その他用地",u"事務所用地",u"別荘用地",u"倉庫用地",u"資材置場用地",u"家庭菜園用地",u"アパート用地",u"社宅社員寮用地",u"病院診療所用地",u"畑・農地用地",u"事業用地",u"駐車場用地",u"リゾート向"]))
    #建ぺい率
    knpirt = db.FloatProperty(verbose_name=u"建ぺい率")
    #容積率
    yuskrt = db.FloatProperty(verbose_name=u"容積率")
    #地域地区
    cikCk = db.StringProperty(verbose_name=u"地域地区", choices=set([u"防火",u"準防火",u"高度",u"高度利用",u"風致",u"文教",u"その他"]))
    #土地権利
    tcKenr = db.StringProperty(verbose_name=u"土地権利", choices=set([u"所有権",u"旧法地上",u"旧法賃借",u"普通地上",u"定期地上",u"普通賃借",u"定期賃借",u"他"]))

    #付帯権利
    ftiKenr = db.StringProperty(verbose_name=u"付帯権利", choices=set([u"抵当権",u"温泉利用権"]))
    #造作譲渡金
    zusJyutkn = db.FloatProperty(verbose_name=u"造作譲渡金")
    #定借権利金
    tishkKenrkn = db.FloatProperty(verbose_name=u"定借権利金")
    #定借保証金
    tishkHshukn = db.FloatProperty(verbose_name=u"定借保証金")
    #定借敷金
    tishkSkkn = db.FloatProperty(verbose_name=u"定借敷金")
    #地勢
    csi = db.StringProperty(verbose_name=u"地勢", choices=set([u"平坦",u"高台",u"低地",u"ひな段",u"傾斜地",u"その他"]))
    #建築条件
    knckJyukn = db.StringProperty(verbose_name=u"建築条件", choices=set([u"有",u"無"]),default=u'無')
    #オーナーチェンジ
    ornrChng = db.StringProperty(verbose_name=u"オーナーチェンジ")
    #管理組合有無
    knrKmaiUm = db.StringProperty(verbose_name=u"管理組合有無", choices=set([u"有",u"無"]),default=u'無')
    #管理費
    knrh = db.FloatProperty(verbose_name=u"管理費")
    #管理費消費税
    knrhShuhzi = db.FloatProperty(verbose_name=u"管理費消費税")
    #管理形態
    knrKiti = db.StringProperty(verbose_name=u"管理形態", choices=set([u"自主管理",u"管理会社に一部委託",u"管理会社に全部委託"]))
    #管理会社名
    knrKishmi = db.StringProperty(verbose_name=u"管理会社名")
    #管理人状況
    knrnnJyukyu = db.StringProperty(verbose_name=u"管理人状況", choices=set([u"常駐",u"日勤",u"巡回"]))
    #修繕積立金
    shznTmttkn = db.FloatProperty(verbose_name=u"修繕積立金")
    #その他月額費名称1
    sntGtgkhMishu1 = db.StringProperty(verbose_name=u"その他月額費名称1")
    #
    sntGtgkhMishu2 = db.StringProperty(verbose_name=u"その他月額費名称2")
    #その他月額費用金額1
    sntGtgkHyuKngk1 = db.FloatProperty(verbose_name=u"その他月額費用金額1")
    #
    sntGtgkHyuKngk2 = db.FloatProperty(verbose_name=u"その他月額費用金額2")
    #施主
    ssh = db.StringProperty(verbose_name=u"施主")
    #施工会社名
    skuKishmi = db.StringProperty(verbose_name=u"施工会社名")
    #分譲会社名
    bnjyuKishmi = db.StringProperty(verbose_name=u"分譲会社名")
    #一括下請負人
    ikktStukoinn = db.StringProperty(verbose_name=u"一括下請負人")
    #接道状況
    stduJyukyu = db.StringProperty(verbose_name=u"接道状況", choices=set([u"一方",u"角地",u"三方",u"四方",u"二方"]))
    #接道種別1
    stduShbt1 = db.StringProperty(verbose_name=u"接道種別1", choices=set([u"公道",u"私道"]))
    #接道接面1
    stduStmn1 = db.StringProperty(verbose_name=u"接道接面1")
    #接道位置指定1
    stduIcSti1 = db.StringProperty(verbose_name=u"接道位置指定1", choices=set([u"有",u"無"]))
    #接道方向1
    stduHuku1 = db.StringProperty(verbose_name=u"接道方向1", choices=set([u"北",u"北東",u"東",u"南東",u"南",u"南西",u"西",u"北西"]))
    #接道幅員1
    stduFkin1 = db.FloatProperty(verbose_name=u"接道幅員1")
    #接道種別2
    stduShbt2 = db.StringProperty(verbose_name=u"接道種別2", choices=set([u"公道",u"私道"]))
    #接道接面2
    stduStmn2 = db.FloatProperty(verbose_name=u"接道接面2")
    #接道位置指定2
    stduIcSti2 = db.StringProperty(verbose_name=u"接道位置指定2", choices=set([u"有",u"無"]))
    #接道方向2
    stduHuku2 = db.StringProperty(verbose_name=u"接道方向2", choices=set([u"北",u"北東",u"東",u"南東",u"南",u"南西",u"西",u"北西"]))
    #接道幅員2
    stduFkin2 = db.FloatProperty(verbose_name=u"接道幅員2")
    #接道種別3
    stduShbt3 = db.StringProperty(verbose_name=u"接道種別3", choices=set([u"公道",u"私道"]))
    #接道接面3
    stduStmn3 = db.FloatProperty(verbose_name=u"接道接面3")
    #接道位置指定3
    stduIcSti3 = db.StringProperty(verbose_name=u"接道位置指定3", choices=set([u"有",u"無"]))
    #接道方向3
    stduHuku3 = db.StringProperty(verbose_name=u"接道方向3", choices=set([u"北",u"北東",u"東",u"南東",u"南",u"南西",u"西",u"北西"]))
    #接道幅員3
    stduFkin3 = db.FloatProperty(verbose_name=u"接道幅員3")
    #接道種別4
    stduShbt4 = db.StringProperty(verbose_name=u"接道種別4", choices=set([u"公道",u"私道"]))
    #接道接面4
    stduStmn4 = db.FloatProperty(verbose_name=u"接道接面4")
    #接道位置指定4
    stduIcSti4 = db.StringProperty(verbose_name=u"接道位置指定4", choices=set([u"有",u"無"]))
    #接道方向4
    stduHuku4 = db.StringProperty(verbose_name=u"接道方向4", choices=set([u"北",u"北東",u"東",u"南東",u"南",u"南西",u"西",u"北西"]))
    #接道幅員4
    stduFkin4 = db.FloatProperty(verbose_name=u"接道幅員4")
    #接道舗装
    stduHsu = db.StringProperty(verbose_name=u"接道舗装", choices=set([u"有",u"無"]))
    #間取タイプ（1）
    mdrTyp1 = db.StringProperty(verbose_name=u"間取タイプ（1）", choices=set([u"ワンルーム",u"K",u"DK",u"LK",u"LDK",u"SK",u"SDK",u"SLK",u"SLDK"]))
    #間取部屋数（1）
    mdrHysu1 = db.FloatProperty(verbose_name=u"間取部屋数（1）")
    #部屋位置

    #納戸数
    nuKsu1 = db.FloatProperty(verbose_name=u"納戸数")
    #室所在階1（1）
    stShziki11 = db.FloatProperty(verbose_name=u"室所在階1（1）")
    #室タイプ1（1）
    stTyp11 = db.StringProperty(verbose_name=u"室タイプ1（1）", choices=set([u"和",u"洋",u"DK",u"LDK",u"L",u"D",u"K",u"S",u"その他"]))
    #室広さ1（1）
    stHrs11 = db.FloatProperty(verbose_name=u"室広さ1（1）")
    #室数1（1）
    stsu11 = db.FloatProperty(verbose_name=u"室数1（1）")
    #室所在階2（1）
    stShziki21 = db.FloatProperty(verbose_name=u"室所在階2（1）")
    #室タイプ2（1）
    stTyp21 = db.StringProperty(verbose_name=u"室タイプ2（1）", choices=set([u"和",u"洋",u"DK",u"LDK",u"L",u"D",u"K",u"S",u"その他"]))
    #室広さ2（1）
    stHrs21 = db.FloatProperty(verbose_name=u"室広さ2（1）")
    #室数2（1）
    stsu21 = db.FloatProperty(verbose_name=u"室数2（1）")
    #室所在階3（1）
    stShziki31 = db.FloatProperty(verbose_name=u"室所在階3（1）")
    #室タイプ3（1）
    stTyp31 = db.StringProperty(verbose_name=u"室タイプ3（1）", choices=set([u"和",u"洋",u"DK",u"LDK",u"L",u"D",u"K",u"S",u"その他"]))
    #室広さ3（1）
    stHrs31 = db.FloatProperty(verbose_name=u"室広さ3（1）")
    #室数3（1）
    stsu31 = db.FloatProperty(verbose_name=u"室数3（1）")
    #室所在階4（1）
    stShziki41 = db.FloatProperty(verbose_name=u"室所在階4（1）")
    #室タイプ4（1）
    stTyp41 = db.StringProperty(verbose_name=u"室タイプ4（1）", choices=set([u"和",u"洋",u"DK",u"LDK",u"L",u"D",u"K",u"S",u"その他"]))
    #室広さ4（1）
    stHrs41 = db.FloatProperty(verbose_name=u"室広さ4（1）")
    #室数4（1）
    stsu41 = db.FloatProperty(verbose_name=u"室数4（1）")
    #室所在階5（1）
    stShziki51 = db.FloatProperty(verbose_name=u"室所在階5（1）")
    #室タイプ5（1）
    stTyp51 = db.StringProperty(verbose_name=u"室タイプ5（1）", choices=set([u"和",u"洋",u"DK",u"LDK",u"L",u"D",u"K",u"S",u"その他"]))
    #室広さ5（1）
    stHrs51 = db.FloatProperty(verbose_name=u"室広さ5（1）")
    #室数5（1）
    stsu51 = db.FloatProperty(verbose_name=u"室数5（1）")
    #室所在階6（1）
    stShziki61 = db.FloatProperty(verbose_name=u"室所在階6（1）")
    #室タイプ6（1）
    stTyp61 = db.StringProperty(verbose_name=u"室タイプ6（1）", choices=set([u"和",u"洋",u"DK",u"LDK",u"L",u"D",u"K",u"S",u"その他"]))
    #室広さ6（1）
    stHrs61 = db.FloatProperty(verbose_name=u"室広さ6（1）")
    #室数6（1）
    stsu61 = db.FloatProperty(verbose_name=u"室数6（1）")
    #室所在階7（1）
    stShziki71 = db.FloatProperty(verbose_name=u"室所在階7（1）")
    #室タイプ7（1）
    stTyp71 = db.StringProperty(verbose_name=u"室タイプ7（1）", choices=set([u"和",u"洋",u"DK",u"LDK",u"L",u"D",u"K",u"S",u"その他"]))
    #室広さ7（1）
    stHrs71 = db.FloatProperty(verbose_name=u"室広さ7（1）")
    #室数7（1）
    stsu71 = db.FloatProperty(verbose_name=u"室数7（1）")
    #間取りその他（1）
    mdrSnt1 = db.StringProperty(verbose_name=u"間取りその他（1）")
    #駐車場在否
    chushjyuZih = db.StringProperty(verbose_name=u"駐車場在否", choices=set([u"空有",u"空無",u"近隣確保",u"無",u"有"]))
    #駐車場月額
    chushjyuGtgk = db.FloatProperty(verbose_name=u"駐車場月額")
    #駐車場月額消費税
    chushjyuGtgkShuhzi = db.FloatProperty(verbose_name=u"駐車場月額消費税")
    #駐車場敷金（額）
    chushjyuSkknGk = db.FloatProperty(verbose_name=u"駐車場敷金（額）")
    #駐車場敷金（ヶ月）
    chushjyuSkknKgt = db.StringProperty(verbose_name=u"駐車場敷金（ヶ月）", choices=set([u"円",u"ヶ月"]))
    #駐車場礼金（額）
    chushjyuRiknGk = db.FloatProperty(verbose_name=u"駐車場礼金（額）")
    #駐車場礼金（ヶ月）
    chushjyuRiknKgt = db.StringProperty(verbose_name=u"駐車場礼金（ヶ月）", choices=set([u"円",u"ヶ月"]))
    #建物構造
    ttmnKuzu = db.StringProperty(verbose_name=u"建物構造", choices=set([u"木造",u"ブロック",u"鉄骨造",u"RC",u"SRC",u"PC",u"HPC",u"軽量鉄骨",u"その他"]))
    #建物工法
    ttmnKuhu = db.StringProperty(verbose_name=u"建物工法", choices=set([u"在来",u"2×4"]))
    #建物形式
    ttmnKisk = db.StringProperty(verbose_name=u"建物形式")
    #地上階層
    cjyuKisou = db.FloatProperty(verbose_name=u"地上階層")
    #地下階層
    ckaKisou = db.FloatProperty(verbose_name=u"地下階層")
    #所在階
    shziki = db.FloatProperty(verbose_name=u"所在階")
    #築年月（西暦）
    cknngtSirk = db.DateTimeProperty(verbose_name=u"築年月（西暦）")
    #

    #総戸数
    suksu = db.FloatProperty(verbose_name=u"総戸数")
    #棟総戸数
    tuSuksu = db.FloatProperty(verbose_name=u"棟総戸数")
    #連棟戸数
    rntuKsu = db.FloatProperty(verbose_name=u"連棟戸数")
    #バルコニー方向（1）
    blcnyHuku1 = db.StringProperty(verbose_name=u"バルコニー方向（1）", choices=set([u"北",u"北東",u"東",u"南東",u"南",u"南西",u"西",u"北西"]))
    #
    blcnyHuku2 = db.StringProperty(verbose_name=u"バルコニー方向（2）", choices=set([u"北",u"北東",u"東",u"南東",u"南",u"南西",u"西",u"北西"]))
    #
    blcnyHuku3 = db.StringProperty(verbose_name=u"バルコニー方向（3）", choices=set([u"北",u"北東",u"東",u"南東",u"南",u"南西",u"西",u"北西"]))
    #増改築年月1
    zukickNngt1 = db.DateTimeProperty(verbose_name=u"増改築年月1")
    #

    #増改築履歴1
    zukickRrk1 = db.StringProperty(verbose_name=u"増改築履歴1")
    #増改築年月2
    zukickNngt2 = db.DateTimeProperty(verbose_name=u"増改築年月2")
    #

    #増改築履歴2
    zukickRrk2 = db.StringProperty(verbose_name=u"増改築履歴2")
    #増改築年月3
    zukickNngt3 = db.DateTimeProperty(verbose_name=u"増改築年月3")
    #

    #増改築履歴3
    zukickRrk3 = db.StringProperty(verbose_name=u"増改築履歴3")
    #
    #周辺環境1（フリー）
    shuhnKnkyu1Fre = db.StringProperty(verbose_name=u"周辺環境1（フリー）")
    #距離1
    kyr1 = db.FloatProperty(verbose_name=u"距離1")
    #時間1
    jkn1 = db.FloatProperty(verbose_name=u"時間1")
    #周辺アクセス１
    shuhnAccs1 = db.StringProperty(verbose_name=u"周辺アクセス１", choices=set([u"徒歩",u"車"]))
    #
    shuhnKnkyu2Fre = db.StringProperty(verbose_name=u"周辺環境2（フリー）")
    #
    kyr2 = db.FloatProperty(verbose_name=u"距離2")
    #
    jkn2 = db.FloatProperty(verbose_name=u"時間2")
    #
    shuhnAccs2 = db.StringProperty(verbose_name=u"周辺アクセス２", choices=set([u"徒歩",u"車"]))
    #
    shuhnKnkyu3Fre = db.StringProperty(verbose_name=u"周辺環境3（フリー）")
    #
    kyr3 = db.FloatProperty(verbose_name=u"距離3")
    #
    jkn3 = db.FloatProperty(verbose_name=u"時間3")
    #
    shuhnAccs3 = db.StringProperty(verbose_name=u"周辺アクセス３", choices=set([u"徒歩",u"車"]))
    #
    shuhnKnkyu4Fre = db.StringProperty(verbose_name=u"周辺環境4（フリー）")
    #
    kyr4 = db.FloatProperty(verbose_name=u"距離4")
    #
    jkn4 = db.FloatProperty(verbose_name=u"時間4")
    #
    shuhnAccs4 = db.StringProperty(verbose_name=u"周辺アクセス４", choices=set([u"徒歩",u"車"]))
    #
    shuhnKnkyu5Fre = db.StringProperty(verbose_name=u"周辺環境5（フリー）")
    #
    kyr5 = db.FloatProperty(verbose_name=u"距離5")
    #
    jkn5 = db.FloatProperty(verbose_name=u"時間5")
    #
    shuhnAccs5 = db.StringProperty(verbose_name=u"周辺アクセス５", choices=set([u"徒歩",u"車"]))
    #備考1
    bku1 = db.StringProperty(verbose_name=u"備考1",multiline=True)
    #備考2
    bku2 = db.StringProperty(verbose_name=u"備考2",multiline=True)
    #自社管理欄
    jshKnrrn = db.StringProperty(verbose_name=u"自社管理欄",multiline=True)
    #再建築不可フラグ
    siknckFkFlg = db.BooleanProperty(verbose_name=u"再建築不可フラグ")
    #
    #
    #<売地>

    #取引主任者
    trhkShnnsh = db.StringProperty(verbose_name=u"取引主任者")
    #容積率の制限内容
    yuskrtSignNiyu = db.StringProperty(verbose_name=u"容積率の制限内容")
    #その他の法令上の制限
    sntHurijyuSign = db.StringProperty(verbose_name=u"その他の法令上の制限")
    #販売最小面積
    bnjyuTkcHnbiSishouMnsk = db.FloatProperty(verbose_name=u"販売最小面積")
    #販売最大面積
    bnjyuTkcHnbiSidiMnsk = db.FloatProperty(verbose_name=u"販売最大面積")
    #価格帯区画数
    bnjyuTkcKkkutiKsuKkksuFrom = db.FloatProperty(verbose_name=u"価格帯区画数~")
    bnjyuTkcKkkutiKsuKkksuTo = db.FloatProperty(verbose_name=u"価格帯区画数")
    #販売最低価格
    bnjyuTkcHnbiSitiKkku = db.FloatProperty(verbose_name=u"販売最低価格")
    #販売最高価格
    bnjyuTkcHnbiSikuKkku = db.FloatProperty(verbose_name=u"販売最高価格")
    #最多価格帯区画数
    bnjyuTkcSitKkkutiKsuKkksu = db.FloatProperty(verbose_name=u"最多価格帯区画数")
    #最多価格帯
    bnjyuTkcSitKkkuti = db.FloatProperty(verbose_name=u"最多価格帯")
    #管理費等
    bnjyuTkcKnrhtu = db.FloatProperty(verbose_name=u"管理費等")
    #現況有姿分譲地
    bnjyuTkcGnkyuYusBnjyuc = db.BooleanProperty(verbose_name=u"現況有姿分譲地")
    #その他一時金名称１
    sntIcjknMishu1 = db.StringProperty(verbose_name=u"その他一時金名称１")
    #金額１
    kngk1 = db.FloatProperty(verbose_name=u"金額１")
    #その他一時金名称2
    sntIcjknMishu2 = db.StringProperty(verbose_name=u"その他一時金名称2")
    #金額2
    kngk2 = db.FloatProperty(verbose_name=u"金額2")
    #その他一時金名称3
    sntIcjknMishu3 = db.StringProperty(verbose_name=u"その他一時金名称3")
    #金額3
    kngk3 = db.FloatProperty(verbose_name=u"金額3")
    #その他一時金名称4
    sntIcjknMishu4 = db.StringProperty(verbose_name=u"その他一時金名称4")
    #金額4
    kngk4 = db.FloatProperty(verbose_name=u"金額4")
    #その他一時金名称5
    sntIcjknMishu5 = db.StringProperty(verbose_name=u"その他一時金名称5")
    #金額5
    kngk5 = db.FloatProperty(verbose_name=u"金額5")
    #
    #備考３
    bku3 = db.StringProperty(verbose_name=u"備考3",multiline=True)
    #備考４
    bku4 = db.StringProperty(verbose_name=u"備考4",multiline=True)
    #広告用備考
    kkkybku = db.StringListProperty(verbose_name=u"広告用備考")
    #名称又は商号
    kukknsMishuShugu = db.StringProperty(verbose_name=u"名称又は商号")
    #事務所所在地
    kukknsJmshShzic = db.StringProperty(verbose_name=u"事務所所在地")
    #事務所電話番号
    kukknsJmshDnwBngu = db.StringProperty(verbose_name=u"事務所電話番号")
    #宅建業法による免許番号
    tkkngyuhuMnkyBngu = db.StringProperty(verbose_name=u"宅建業法による免許番号")
    #都市計画法その他
    tskikkhuSnt = db.StringProperty(verbose_name=u"都市計画法その他")
    #広告転載区分
    kukkTnsiKbn = db.StringProperty(verbose_name=u"広告転載区分", choices=set([u"広告可",u"一部可（インターネット）",u"一部可（チラシ・新聞広告）",u"広告可（但し要連絡）",u"不可",u"未確認"]),default=u"未確認")
    #
    #画像

    #
    files = db.StringProperty(verbose_name=u"画像１")
    #私道負担割合
    sduFtnWraiBns = db.FloatProperty(verbose_name=u"私道負担割合分子")
    #
    sduFtnWraiBnb = db.FloatProperty(verbose_name=u"私道負担割合分母")
    #
    sduFtnWraiBnsM2 = db.FloatProperty(verbose_name=u"私道負担割合分子平米")
    #
    sduFtnWraiBnbM2 = db.FloatProperty(verbose_name=u"私道負担割合分母平米")
    #部分面積名１
    bbnMnskMishu1 = db.StringProperty(verbose_name=u"部分面積名１")
    #部分面積１
    bbnMnskM21 = db.FloatProperty(verbose_name=u"部分面積１")
    #部分面積名２
    bbnMnskMishu2 = db.FloatProperty(verbose_name=u"部分面積名２")
    #部分面積２
    bbnMnskM22 = db.FloatProperty(verbose_name=u"部分面積２")
    #
    #
    #<売外全>

    #媒介契約年月日
    bikiKiykNngppSirk = db.DateTimeProperty(verbose_name=u"媒介契約年月日")
    #

    #

    #

    #建築確認コード
    knckKknnCd = db.StringProperty(verbose_name=u"建築確認コード", choices=set([u"済",u"無",u"申請中"]))
    #建築確認番号
    knckKknnBngu = db.StringProperty(verbose_name=u"建築確認番号")
    #その他一時金なしフラグ
    sntIcjknNsFlg = db.BooleanProperty(verbose_name=u"その他一時金なしフラグ")
    #駐車場月額（最低値）
    chushjyuGtgkSitic = db.FloatProperty(verbose_name=u"駐車場月額（最低値）")
    #駐車場月額（最高値）
    chushjyuGtgkSikuc = db.FloatProperty(verbose_name=u"駐車場月額（最高値）")
    #駐車場無料フラグ
    chushjyuMryuFlg = db.BooleanProperty(verbose_name=u"駐車場無料フラグ")
    #

    #駐車場距離
    chushjyuKyrM = db.FloatProperty(verbose_name=u"駐車場距離")
    #駐車場形式
    chushjyuKisk = db.StringProperty(verbose_name=u"駐車場形式", choices=set([u"自走",u"機械"]))
    #駐車場屋根状況
    chushjyuYnJyukyu = db.StringProperty(verbose_name=u"駐車場屋根状況", choices=set([u"屋根あり",u"屋根なし"]))
    #駐車場敷金
    chushjyuSkknGk = db.FloatProperty(verbose_name=u"駐車場敷金")
    chushjyuSkknKgt = db.StringProperty(verbose_name=u"駐車場敷金円ヶ月", choices=set([u"円",u"ヶ月"]))
    #駐車場礼金
    chushjyuRiknGk = db.FloatProperty(verbose_name=u"駐車場礼金")
    chushjyuRiknKgt = db.StringProperty(verbose_name=u"駐車場礼金円ヶ月", choices=set([u"円",u"ヶ月"]))
    #周辺環境１(フリー)
    shuhnKnkyu1Fre = db.StringProperty(verbose_name=u"周辺環境１")
    kyr1 = db.FloatProperty(verbose_name=u"周辺環境１距離")
    #時間
    shuhnAccs1 = db.StringProperty(verbose_name=u"周辺環境１時間種類", choices=set([u"徒歩",u"車"]))
    jkn1 = db.FloatProperty(verbose_name=u"周辺環境１時間")
    #周辺環境２(フリー)
    shuhnKnkyu2Fre = db.StringProperty(verbose_name=u"周辺環境２")
    kyr2 = db.FloatProperty(verbose_name=u"周辺環境２距離")
    #時間
    shuhnAccs2 = db.StringProperty(verbose_name=u"周辺環境２時間種類", choices=set([u"徒歩",u"車"]))
    jkn2 = db.FloatProperty(verbose_name=u"周辺環境２時間")
    #周辺環境３(フリー)
    shuhnKnkyu3Fre = db.StringProperty(verbose_name=u"周辺環境３")
    kyr3 = db.FloatProperty(verbose_name=u"周辺環境３距離")
    #時間
    shuhnAccs3 = db.StringProperty(verbose_name=u"周辺環境３時間種類", choices=set([u"徒歩",u"車"]))
    jkn3 = db.FloatProperty(verbose_name=u"周辺環境３時間")
    #周辺環境４(フリー)
    shuhnKnkyu4Fre = db.StringProperty(verbose_name=u"周辺環境４")
    kyr4 = db.FloatProperty(verbose_name=u"周辺環境４距離")
    #時間
    shuhnAccs4 = db.StringProperty(verbose_name=u"周辺環境４時間種類", choices=set([u"徒歩",u"車"]))
    jkn4 = db.FloatProperty(verbose_name=u"周辺環境４時間")
    #周辺環境５(フリー)
    shuhnKnkyu5Fre = db.StringProperty(verbose_name=u"周辺環境５")
    kyr5 = db.FloatProperty(verbose_name=u"周辺環境５距離")
    #時間
    shuhnAccs5 = db.StringProperty(verbose_name=u"周辺環境５時間種類", choices=set([u"徒歩",u"車"]))
    jkn5 = db.FloatProperty(verbose_name=u"周辺環境５時間")

    #設備（フリースペース）
    stbFrespc = db.StringProperty(verbose_name=u"設備",multiline=True)
    #条件(フリースペース）
    tkkJkuFrespc = db.StringProperty(verbose_name=u"条件",multiline=True)
    #建物面積１F
    ttmnMnsk1F = db.FloatProperty(verbose_name=u"建物面積１F")
    #建物面積２F
    ttmnMnsk2F = db.FloatProperty(verbose_name=u"建物面積２F")
    #建物面積３F
    ttmnMnsk3F = db.FloatProperty(verbose_name=u"建物面積３F")
    #建物面積その他
    ttmnMnskSnt = db.StringProperty(verbose_name=u"建物面積その他")
    #
    #
    #<売外一>

    #角部屋フラグ
    hyIc1 = db.BooleanProperty(verbose_name=u"角部屋フラグ")

    #管理費なしフラグ
    knrhNsFlg = db.BooleanProperty(verbose_name=u"管理費なしフラグ")
    #管理費帯
    knrhtiFrom = db.FloatProperty(verbose_name=u"管理費帯下限")
    knrhtiTo = db.FloatProperty(verbose_name=u"管理費帯上限")
    #修繕積立金
    shuznTmttkn = db.FloatProperty(verbose_name=u"修繕積立金")
    #修繕積立金なしフラグ
    shznTmttknNsFlg = db.BooleanProperty(verbose_name=u"修繕積立金なしフラグ")
    #修繕積立金下限
    shznTmttknFrom = db.FloatProperty(verbose_name=u"修繕積立金下限")
    #修繕積立金上限
    shznTmttknTo = db.FloatProperty(verbose_name=u"修繕積立金上限")

    #
    #<売一戸建>

    #
    #
    #
    #
    #間取タイプ（2）
    mdrTyp2 = db.StringProperty(verbose_name=u"間取タイプ（2）", choices=set([u"ワンルーム",u"K",u"DK",u"LK",u"LDK",u"SK",u"SDK",u"SLK",u"SLDK"]))
    #間取部屋数（2）
    mdrHysu2 = db.FloatProperty(verbose_name=u"間取部屋数（2）")
    #室所在階1（2）
    stShziki12 = db.FloatProperty(verbose_name=u"室所在階1（2）")
    #室タイプ1（2）
    stTyp12 = db.StringProperty(verbose_name=u"室タイプ1（2）", choices=set([u"和",u"洋",u"DK",u"LDK",u"L",u"D",u"K",u"S",u"その他"]))
    #室広さ1（2）
    stHrs12 = db.FloatProperty(verbose_name=u"室広さ1（2）")
    #室数1（2）
    stsu12 = db.FloatProperty(verbose_name=u"室数1（2）")
    #室所在階2（2）
    stShziki22 = db.FloatProperty(verbose_name=u"室所在階2（2）")
    #室タイプ2（2）
    stTyp22 = db.StringProperty(verbose_name=u"室タイプ2（2）", choices=set([u"和",u"洋",u"DK",u"LDK",u"L",u"D",u"K",u"S",u"その他"]))
    #室広さ2（2）
    stHrs22 = db.FloatProperty(verbose_name=u"室広さ2（2）")
    #室数2（2）
    stsu22 = db.FloatProperty(verbose_name=u"室数2（2）")
    #室所在階3（2）
    stShziki32 = db.FloatProperty(verbose_name=u"室所在階3（2）")
    #室タイプ3（2）
    stTyp32 = db.StringProperty(verbose_name=u"室タイプ3（2）", choices=set([u"和",u"洋",u"DK",u"LDK",u"L",u"D",u"K",u"S",u"その他"]))
    #室広さ3（2）
    stHrs32 = db.FloatProperty(verbose_name=u"室広さ3（2）")
    #室数3（2）
    stsu32 = db.FloatProperty(verbose_name=u"室数3（2）")
    #室所在階4（2）
    stShziki42 = db.FloatProperty(verbose_name=u"室所在階4（2）")
    #室タイプ4(2)
    stTyp42 = db.StringProperty(verbose_name=u"室タイプ4(2)", choices=set([u"和",u"洋",u"DK",u"LDK",u"L",u"D",u"K",u"S",u"その他"]))
    #室広さ4(2)
    stHrs42 = db.FloatProperty(verbose_name=u"室広さ4(2)")
    #室数4(2)
    stsu42 = db.FloatProperty(verbose_name=u"室数4(2)")
    #室所在階5(2)
    stShziki52 = db.FloatProperty(verbose_name=u"室所在階5(2)")
    #室タイプ5(2)
    stTyp52 = db.StringProperty(verbose_name=u"室タイプ5(2)", choices=set([u"和",u"洋",u"DK",u"LDK",u"L",u"D",u"K",u"S",u"その他"]))
    #室広さ5(2)
    stHrs52 = db.FloatProperty(verbose_name=u"室広さ5(2)")
    #室数5(2)
    stsu52 = db.FloatProperty(verbose_name=u"室数5(2)")
    #室所在階6(2)
    stShziki62 = db.FloatProperty(verbose_name=u"室所在階6(2)")
    #室タイプ6(2)
    stTyp62 = db.StringProperty(verbose_name=u"室タイプ6(2)", choices=set([u"和",u"洋",u"DK",u"LDK",u"L",u"D",u"K",u"S",u"その他"]))
    #室広さ6(2)
    stHrs62 = db.FloatProperty(verbose_name=u"室広さ6(2)")
    #室数6(2)
    stsu62 = db.FloatProperty(verbose_name=u"室数6(2)")
    #室所在階7(2)
    stShziki72 = db.FloatProperty(verbose_name=u"室所在階7(2)")
    #室タイプ7(2)
    stTyp72 = db.StringProperty(verbose_name=u"室タイプ7(2)", choices=set([u"和",u"洋",u"DK",u"LDK",u"L",u"D",u"K",u"S",u"その他"]))
    #室広さ7(2)
    stHrs72 = db.FloatProperty(verbose_name=u"室広さ7(2)")
    #室数7(2)
    stsu72 = db.FloatProperty(verbose_name=u"室数7(2)")
    #間取りその他(2)
    mdrSnt2 = db.StringProperty(verbose_name=u"間取りその他(2)")

    #分譲戸建販売戸数
    bnjyuKdtHnbiKsu = db.FloatProperty(verbose_name=u"分譲戸建販売戸数")
    #価格帯戸数
    bnjyuKdtKkkutiKsuKkksuFrom = db.FloatProperty(verbose_name=u"価格帯戸数下限")
    bnjyuKdtKkkutiKsuKkksuTo = db.FloatProperty(verbose_name=u"価格帯戸数上限")
    #販売最低価格
    bnjyuKdtHnbiSitiKkku = db.FloatProperty(verbose_name=u"販売最低価格")
    #販売最高価格
    bnjyuKdtHnbiSikuKkku = db.FloatProperty(verbose_name=u"販売最高価格")
    #販売土地最小面積
    bnjyuKdtHnbiTcSishouMnsk = db.FloatProperty(verbose_name=u"販売土地最小面積")
    #販売土地最大面積
    bnjyuKdtHnbiTcSidiMnsk = db.FloatProperty(verbose_name=u"販売土地最大面積")
    #販売建物最小面積
    bnjyuKdtHnbiTtmnSishouMnsk = db.FloatProperty(verbose_name=u"販売建物最小面積")
    #販売建物最大面積
    bnjyuKdtHnbiTtmnSidiMnsk = db.FloatProperty(verbose_name=u"販売建物最大面積")
    #最多価格帯戸数
    bnjyuKdtSitKkkutiKsuKkksu = db.FloatProperty(verbose_name=u"最多価格帯戸数")
    #最多価格帯
    bnjyuKdtSitKkkuti = db.FloatProperty(verbose_name=u"最多価格帯")
    #管理費
    bnjyuKdtKnrh = db.FloatProperty(verbose_name=u"管理費")


class BKdatajson(db.Model):
    ref_BKdata = db.ReferenceProperty(reference_class = BKdata,collection_name = u'jsonset')
    name = db.StringProperty()
    jsondata = db.TextProperty()

