# -*- coding: utf-8 -*-

from google.appengine.ext import db
import member
from application import timemanager

class bksearchdata(db.Model):

    def put(self):
        #トリガ処理
        #bkID = db.StringProperty(verbose_name=u"物件番号")
        if not db.is_in_transaction():
            db.Model.put(self)
            namestr =""
            if self.bkID:
                namestr += u"物件番号：" + self.bkID

            #売買賃貸区分
            #bbchntikbn = db.StringProperty(verbose_name=u"売買賃貸区分", choices=set([u"売買", u"賃貸"]))
            if self.bbchntikbn:
                namestr += self.bbchntikbn
            #取扱い種類
            #dtsyuri = db.StringProperty(verbose_name=u"データ種類", choices=set([u"物件",u"事例",u"予約",u"商談中",u"査定中",u"重複",u"停止",u"競売",u"現場",u"サンプル"]))
            if self.dtsyuri:
                namestr += self.dtsyuri
            """
            #物件種別
            #bkknShbt = db.StringProperty(verbose_name=u"物件種別", choices=set([u"土地", u"戸建住宅等", u"マンション等", u"住宅以外の建物全部", u"住宅以外の建物一部"]))
            if self.bkknShbt:
                namestr += self.bkknShbt + u" "
            """
            #物件種目
            #bkknShmk = db.StringProperty(verbose_name=u"物件種目", choices=set([u"売地", u"借地権", u"底地権",u"新築戸建",u"中古戸建",u"新築テラス",u"中古テラス", u"店舗", u"店舗付住宅", u"住宅付店舗",u"新築マンション",u"中古マンション",u"新築タウン",u"中古タウン",u"新築リゾート",u"中古リゾート",u"事務所", u"店舗事務所", u"ビル", u"工場", u"マンション", u"倉庫", u"アパート", u"寮", u"旅館", u"ホテル", u"別荘", u"リゾート", u"文化住宅", u"その他"]))
            if self.bkknShmk:
                namestr += self.bkknShmk

            if self.adlist:
                for adlist in self.adlist:
                    if adlist.ref_bksearchaddresslist.name == u"個別指定":
                        for ad1 in adlist.ref_bksearchaddresslist.adset:
                            if ad1.tdufknmi:
                                namestr += u"・" + ad1.tdufknmi
                            if ad1.shzicmi1:
                                namestr += u"・" + ad1.shzicmi1
                            if ad1.address2list:
                                namestr += u"の一部"
                    else:
                        namestr += u"・" + adlist.ref_bksearchaddresslist.name
            if self.ensen:
                for ens in self.ensen.order("sortkey"):
                    if ens.ensenmei:
                        namestr += u"・" + ens.ensenmei
                        for eki in ens.eki:
                            if eki.ekimei:
                                namestr += u"-" + eki.ekimei
                        if ens.thHnU:
                            namestr += u"-徒歩" + str(ens.thHnU) + u"分以内"

                        if ens.thMU:
                            namestr += u"-" + str(ens.thHnU) + u"ｍ以内"
            if self.madori:
                madoristr = ""
                for mad in self.madori.order("sortkey"):
                    madoristr += u" " + str(mad.mdrHysu) + mad.mdrTyp
                if madoristr != "":
                    namestr += u"・間取り" + madoristr

            #交通（分）1
            #kutuHnU = db.FloatProperty(verbose_name=u"交通（分）上限")
            if self.kutuHnU:
                namestr += u"・交通" + str(self.kutuHnU) + u"分以内"

            #土地面積
            #tcMnsk2L = db.FloatProperty(verbose_name=u"土地面積下限")
            if self.tcMnsk2L or self.tcMnsk2U:
                namestr += u"・土地面積："
            if self.tcMnsk2L:
                namestr += str(self.tcMnsk2L) + u"㎡以上"
            #tcMnsk2U = db.FloatProperty(verbose_name=u"土地面積上限")
            if self.tcMnsk2U:
                namestr += str(self.tcMnsk2U) + u"㎡以下"
            #建物面積1
            #ttmnMnsk1L = db.FloatProperty(verbose_name=u"建物面積下限")
            if self.ttmnMnsk1L or self.ttmnMnsk1U:
                namestr += u"・建物面積：" + str(self.blcnyHuku)
            if self.ttmnMnsk1L:
                namestr += str(self.ttmnMnsk1L) + u"㎡以上"
            #ttmnMnsk1U = db.FloatProperty(verbose_name=u"建物面積上限")
            if self.ttmnMnsk1U:
                namestr += u"" + str(self.ttmnMnsk1U) + u"㎡以下"
            #専有面積
            #snyuMnskSyuBbnMnsk2L = db.FloatProperty(verbose_name=u"専有面積下限")
            if self.snyuMnskSyuBbnMnsk2L or self.snyuMnskSyuBbnMnsk2U:
                namestr += u"・専有面積："
            if self.snyuMnskSyuBbnMnsk2L:
                namestr += str(self.snyuMnskSyuBbnMnsk2L) + u"㎡以上"
            #snyuMnskSyuBbnMnsk2U = db.FloatProperty(verbose_name=u"専有面積上限")
            if self.snyuMnskSyuBbnMnsk2U:
                namestr += str(self.snyuMnskSyuBbnMnsk2U) + u"㎡以下"

            #価格
            #kkkuCnryuL = db.FloatProperty(verbose_name=u"価格下限")
            #kkkuCnryuU = db.FloatProperty(verbose_name=u"価格上限")
            if self.kkkuCnryuL or self.kkkuCnryuU:
                namestr += u"・価格："
            if self.kkkuCnryuL:
                namestr += str(self.kkkuCnryuL) + u"万円以上"
            if self.kkkuCnryuU:
                namestr += str(self.kkkuCnryuU) + u"万円以下"

            #坪単価
            #tbTnkL = db.FloatProperty(verbose_name=u"坪単価下限")
            #tbTnkU = db.FloatProperty(verbose_name=u"坪単価上限")
            if self.tbTnkL or self.tbTnkU:
                namestr += u"・坪単価："
            if self.tbTnkL :
                namestr += str(self.tbTnkL) + u"万円以上"
            if self.tbTnkU:
                namestr += str(self.tbTnkU) + u"万円以下"
            #㎡単価
            #m2TnkL = db.FloatProperty(verbose_name=u"㎡単価下限")
            #m2TnkU = db.FloatProperty(verbose_name=u"㎡単価上限")
            if self.m2TnkL or self.m2TnkU:
                namestr += u"・㎡単価："
            if self.m2TnkL:
                namestr += str(self.m2TnkL) + u"万円以上"
            if self.m2TnkU:
                namestr += str(self.m2TnkU) + u"万円以下"

            #想定利回り（％）
            #sutiRmwrPrcntL = db.FloatProperty(verbose_name=u"想定利回り（％）下限")
            #sutiRmwrPrcntU = db.FloatProperty(verbose_name=u"想定利回り（％）上限")
            if self.sutiRmwrPrcntL or self.sutiRmwrPrcntU:
                namestr += u"・想定利回り："
            if self.sutiRmwrPrcntL:
                namestr += str(self.sutiRmwrPrcntL) + u"％以上"
            if self.sutiRmwrPrcntU:
                namestr += str(self.sutiRmwrPrcntU) + u"％以下"


            #接道接面
            #stduStmnL = db.StringProperty(verbose_name=u"接道接面下限")
            #stduStmnU = db.StringProperty(verbose_name=u"接道接面上限")
            if self.stduStmnL or self.stduStmnU:
                namestr += u"・接道："
            if self.stduStmnL:
                namestr += str(self.stduStmnL) + u"ｍ以上"
            if self.stduStmnU:
                namestr += str(self.stduStmnU) + u"ｍ以上"

            #接道幅員
            #stduFkinL = db.FloatProperty(verbose_name=u"接道幅員下限")
            if self.stduFkinL:
                namestr += u"・幅員" + str(self.stduFkinL) + u"ｍ以上"

            #接道方向
            #stduHuku = db.StringProperty(verbose_name=u"接道方向", choices=set([u"北",u"北東",u"東",u"南東",u"南",u"南西",u"西",u"北西"]))
            if self.stduHuku:
                namestr += u"・接道方向：" + self.stduHuku

            #バルコニー方向
            #blcnyHuku = db.StringProperty(verbose_name=u"バルコニー方向", choices=set([u"北",u"北東",u"東",u"南東",u"南",u"南西",u"西",u"北西"]))
            if self.blcnyHuku:
                namestr += u"・バルコニー方向：" + self.blcnyHuku

            #築年月（西暦）
            #cknngtSirkU = db.DateTimeProperty(verbose_name=u"築年月（西暦）上限")
            #cknngtSirkL = db.DateTimeProperty(verbose_name=u"築年月（西暦）下限")
            if self.cknngtSirkU or self.cknngtSirkL:
                namestr += u"・築年月："
            if self.cknngtSirkU:
                namestr += timemanager.utc2jst_date(self.cknngtSirkU).strftime("%Y/%m/%d") + u"から"
            if self.cknngtSirkL:
                namestr += timemanager.utc2jst_date(self.cknngtSirkL).strftime("%Y/%m/%d") + u"まで"

            #地上階層
            #cjyuKisou = db.FloatProperty(verbose_name=u"地上階層")
            #cjyuKisouL = db.FloatProperty(verbose_name=u"地上階層下限")
            #cjyuKisouU = db.FloatProperty(verbose_name=u"地上階層上限")
            if self.cjyuKisouU or self.cjyuKisouL:
                namestr += u"・地上階："
            if self.cjyuKisouL:
                namestr += str(self.cjyuKisouL) + u"階以上"
            if self.cjyuKisouU:
                namestr += str(self.cjyuKisouU) + u"階以下"

            #所在階
            #shzikiU = db.FloatProperty(verbose_name=u"所在階上限")
            #shzikiL = db.FloatProperty(verbose_name=u"所在階下限")
            if self.shzikiU or self.shzikiL:
                namestr += u"・所在階："
            if self.shzikiL:
                namestr += str(self.shzikiL) + u"階以上"
            if self.shzikiU:
                namestr += str(self.shzikiU) + u"階以下"
            #１階
            #floor1 = db.BooleanProperty(verbose_name=u"１階")
            if self.floor1:
                namestr += u"・１階"
            #最上階
            #topfloor = db.BooleanProperty(verbose_name=u"最上階")
            if self.topfloor:
                namestr += u"・最上階"
            #ペット可
            #ptflg = db.BooleanProperty(verbose_name=u"ペット可")
            if self.ptflg:
                namestr += u"・ペット可"
            #建築条件なし
            #knckJyukn = db.BooleanProperty(verbose_name=u"建築条件")
            if self.knckJyukn:
                namestr += u"・建築条件なし"
            #オーナーチェンジ
            #ornrChng = db.BooleanProperty(verbose_name=u"オーナーチェンジ")
            if self.ornrChng:
                namestr += u"・オーナーチェンジ"
            #位置情報有無
            #isidkd = db.BooleanProperty(verbose_name=u"位置情報有無")
            if self.isidkd:
                namestr += u"・位置情報あり"
            elif self.isidkd == False:
                namestr += u"・位置情報なし"
            #告知事項なし
            #kktjkuflg = db.BooleanProperty(verbose_name=u"告知事項")
            if self.kktjkuflg:
                namestr += u"・告知事項あり"
            #アイコン名
            #icons = db.StringProperty(verbose_name=u"アイコン名")
            if self.icons:
                namestr += u"・アイコングループ：" + self.icons

            #建物名
            #ttmnmi = db.StringProperty(verbose_name=u"建物名")
            if self.ttmnmi:
                namestr += u"・建物名：" + self.ttmnmi
            #引渡時期
            #hkwtsNyukyJk = db.StringProperty(verbose_name=u"引渡時期")
            if self.hkwtsNyukyJk:
                namestr += u"・引渡時期：" + self.hkwtsNyukyJk
            #データ元
            #dataSource = db.StringProperty(verbose_name=u"データ元")
            if self.dataSource:
                namestr += u"・データ元：" + self.dataSource
            #広告転載区分
            #kukkTnsiKbn = db.StringProperty(verbose_name=u"広告転載区分", choices=set([u"広告可",u"一部可（インターネット）",u"一部可（チラシ・新聞広告）",u"広告可（但し要連絡）",u"不可",u"未確認"]))
            if self.kukkTnsiKbn:
                namestr += u"・広告転載区分：" + self.kukkTnsiKbn
            #業者名
            #kiinni = db.StringProperty(verbose_name=u"業者名")
            if self.kiinni:
                namestr += u"・業者名：" + self.kiinni

            """
            #確認年月日
            #kknnngpL = db.DateTimeProperty(verbose_name=u"確認年月日下限")
            #kknnngpU = db.DateTimeProperty(verbose_name=u"確認年月日上限")
            if self.kknnngpL or self.kknnngpU:
                namestr += u" 確認年月日:"
            if self.kknnngpL:
                namestr += timemanager.utc2jst_date(self.kknnngpL).strftime("%Y/%m/%d %H:%M:%S") + u"から"
            if self.kknnngpU:
                namestr += timemanager.utc2jst_date(self.kknnngpU).strftime("%Y/%m/%d %H:%M:%S") + u"まで"
            #変更年月日
            #hnknngpL = db.DateTimeProperty(verbose_name=u"変更年月日下限",auto_now_add = True)
            #hnknngpU = db.DateTimeProperty(verbose_name=u"変更年月日上限",auto_now_add = True)
            if self.hnknngpL or self.hnknngpU:
                namestr += u" 変更年月日:"
            if self.hnknngpL:
                namestr += timemanager.utc2jst_date(self.hnknngpL).strftime("%Y/%m/%d %H:%M:%S") + u"から"
            if self.hnknngpU:
                namestr += timemanager.utc2jst_date(self.hnknngpU).strftime("%Y/%m/%d %H:%M:%S") + u"まで"
            #登録年月日
            #turknngpL = db.DateTimeProperty(verbose_name=u"登録年月日下限")
            #turknngpU = db.DateTimeProperty(verbose_name=u"登録年月日上限")
            if self.turknngpL or self.turknngpU:
                namestr += u" 登録年月日:"
            if self.turknngpL:
                namestr += timemanager.utc2jst_date(self.turknngpL).strftime("%Y/%m/%d %H:%M:%S") + u"から"
            if self.turknngpU:
                namestr += timemanager.utc2jst_date(self.turknngpU).strftime("%Y/%m/%d %H:%M:%S") + u"まで"
            #更新年月日
            #ksnnngpL = db.DateTimeProperty(verbose_name=u"更新年月日",auto_now=True)
            #ksnnngpU = db.DateTimeProperty(verbose_name=u"更新年月日",auto_now=True)
            if self.ksnnngpL or self.ksnnngpU:
                namestr += u" 更新年月日:"
            if self.ksnnngpL:
                namestr += timemanager.utc2jst_date(self.ksnnngpL).strftime("%Y/%m/%d %H:%M:%S") + u"から"
            if self.ksnnngpU:
                namestr += timemanager.utc2jst_date(self.ksnnngpU).strftime("%Y/%m/%d %H:%M:%S") + u"まで"
            """
            if namestr == "":
                namestr = u"設定なし"
            self.name = namestr
            return db.Model.put(self)

    modified = db.ReferenceProperty(member.member, verbose_name=u"更新担当", collection_name="modifiedbksearchdata_set")
    member = db.ReferenceProperty(member.member, verbose_name=u"メンバー", collection_name="bksearchdata_set")
    timestamp = db.DateTimeProperty(verbose_name=u"最終更新",auto_now=True)


    bkID = db.StringProperty(verbose_name=u"物件番号")

    #確認年月日
    kknnngpL = db.DateTimeProperty(verbose_name=u"確認年月日下限")
    kknnngpU = db.DateTimeProperty(verbose_name=u"確認年月日上限")
    #変更年月日
    #hnknngp = db.DateTimeProperty(verbose_name=u"変更年月日",auto_now_add = True)
    hnknngpL = db.DateTimeProperty(verbose_name=u"変更年月日下限")
    hnknngpU = db.DateTimeProperty(verbose_name=u"変更年月日上限")
    #登録年月日
    #turknngp = db.DateTimeProperty(verbose_name=u"登録年月日",auto_now_add = True)
    turknngpL = db.DateTimeProperty(verbose_name=u"登録年月日下限")
    turknngpU = db.DateTimeProperty(verbose_name=u"登録年月日上限")
    #更新年月日
    #ksnnngp = db.DateTimeProperty(verbose_name=u"更新年月日",auto_now=True)
    ksnnngpL = db.DateTimeProperty(verbose_name=u"更新年月日下限")
    ksnnngpU = db.DateTimeProperty(verbose_name=u"更新年月日上限")

    #売買賃貸区分
    bbchntikbn = db.StringProperty(verbose_name=u"売買賃貸区分", choices=set([u"売買", u"賃貸"]))
    #取扱い種類
    dtsyuri = db.StringProperty(verbose_name=u"データ種類", choices=set([u"物件",u"事例",u"予約",u"商談中",u"査定中",u"重複",u"停止",u"競売",u"現場",u"サンプル"]))
    #物件種別
    bkknShbt = db.StringProperty(verbose_name=u"物件種別", choices=set([u"土地", u"戸建住宅等", u"マンション等", u"住宅以外の建物全部", u"住宅以外の建物一部",u"賃貸一戸建",u"賃貸マンション",u"賃貸土地",u"賃貸外全",u"賃貸外一", u"その他"]))
    #物件種目
    bkknShmk = db.StringProperty(verbose_name=u"物件種目", choices=set([u"売地", u"借地権", u"底地権",u"新築戸建",u"中古戸建",u"新築テラス",u"中古テラス", u"店舗", u"店舗付住宅", u"住宅付店舗",u"新築マンション",u"中古マンション",u"新築タウン",u"中古タウン",u"新築リゾート",u"中古リゾート",u"店舗事務所", u"ビル", u"工場", u"マンション", u"倉庫", u"アパート", u"寮", u"旅館", u"ホテル", u"別荘", u"リゾート", u"文化住宅", u"貸家",u"テラス",u"マンション",u"タウン",u"間借り",u"居住用地",u"事業用地",u"店舗戸建",u"旅館等",u"寮",u"別荘",u"ビル",u"住宅付店舗戸建",u"店舗事務所",u"店舗一部",u"事務所",u"住宅付店舗一部",u"マンション一室",u"その他"]))
    #ペット可
    ptflg = db.BooleanProperty(verbose_name=u"ペット可")
    #マッチング可
    mtngflg = db.BooleanProperty(verbose_name=u"マッチング可",default=True)
    #web検索許可
    webknskflg = db.BooleanProperty(verbose_name=u"web検索許可",default=True)
    #位置情報有無
    isidkd = db.BooleanProperty(verbose_name=u"位置情報有無")
    #建築条件なし
    knckJyukn = db.BooleanProperty(verbose_name=u"建築条件")
    #オーナーチェンジ
    ornrChng = db.BooleanProperty(verbose_name=u"オーナーチェンジ")
    #告知事項なし
    kktjkuflg = db.BooleanProperty(verbose_name=u"告知事項")
    #アイコン名
    icons = db.StringProperty(verbose_name=u"アイコン名")
    #作成状況
    sksijky = db.StringProperty(verbose_name=u"作成状況",choices=set([u"請求チェック",u"一覧のみ",u"資料請求",u"依頼中",u"入手不可",u"入手済み",u"分類チェック",u"不要",u"未作成",u"作成済み",u"ＨＰ掲載"]))
    #交通（分）1
    kutuHnU = db.FloatProperty(verbose_name=u"交通（分）上限")
    #建物名
    ttmnmi = db.StringProperty(verbose_name=u"建物名")
    #引渡時期
    hkwtsNyukyJk = db.StringProperty(verbose_name=u"引渡時期")
    #データ元
    dataSource = db.StringProperty(verbose_name=u"データ元")
    #広告転載区分
    kukkTnsiKbn = db.StringProperty(verbose_name=u"広告転載区分", choices=set([u"広告可",u"一部可（インターネット）",u"一部可（チラシ・新聞広告）",u"広告可（但し要連絡）",u"不可",u"未確認"]))
    #業者名
    kiinni = db.StringProperty(verbose_name=u"業者名")

    #間取タイプ
    mdrTyp = db.StringProperty(verbose_name=u"間取タイプ", choices=set([u"ワンルーム",u"K",u"DK",u"LK",u"LDK",u"SK",u"SDK",u"SLK",u"SLDK"]))
    #間取部屋数
    mdrHysu = db.FloatProperty(verbose_name=u"間取部屋数")

    #接道方向
    stduHuku = db.StringProperty(verbose_name=u"接道方向", choices=set([u"北",u"北東",u"東",u"南東",u"南",u"南西",u"西",u"北西"]))

    #バルコニー方向
    blcnyHuku = db.StringProperty(verbose_name=u"バルコニー方向", choices=set([u"北",u"北東",u"東",u"南東",u"南",u"南西",u"西",u"北西"]))

    #土地面積
    tcMnsk2L = db.FloatProperty(verbose_name=u"土地面積下限")
    tcMnsk2U = db.FloatProperty(verbose_name=u"土地面積上限")
    #建物面積1
    ttmnMnsk1L = db.FloatProperty(verbose_name=u"建物面積下限")
    ttmnMnsk1U = db.FloatProperty(verbose_name=u"建物面積上限")
    #専有面積
    snyuMnskSyuBbnMnsk2L = db.FloatProperty(verbose_name=u"専有面積下限")
    snyuMnskSyuBbnMnsk2U = db.FloatProperty(verbose_name=u"専有面積上限")
    #価格
    kkkuCnryuL = db.FloatProperty(verbose_name=u"価格下限")
    kkkuCnryuU = db.FloatProperty(verbose_name=u"価格上限")
    #坪単価
    tbTnkL = db.FloatProperty(verbose_name=u"坪単価下限")
    tbTnkU = db.FloatProperty(verbose_name=u"坪単価上限")
    #㎡単価
    m2TnkL = db.FloatProperty(verbose_name=u"㎡単価下限")
    m2TnkU = db.FloatProperty(verbose_name=u"㎡単価上限")
    #想定利回り（％）
    sutiRmwrPrcntL = db.FloatProperty(verbose_name=u"想定利回り（％）下限")
    sutiRmwrPrcntU = db.FloatProperty(verbose_name=u"想定利回り（％）上限")

    #接道接面
    stduStmnL = db.StringProperty(verbose_name=u"接道接面下限")
    stduStmnU = db.StringProperty(verbose_name=u"接道接面上限")

    #接道幅員
    stduFkinL = db.FloatProperty(verbose_name=u"接道幅員下限")

    #築年月（西暦）
    cknngtSirkL = db.DateTimeProperty(verbose_name=u"築年月（西暦）下限")
    cknngtSirkU = db.DateTimeProperty(verbose_name=u"築年月（西暦）上限")
    #地上階層
    #cjyuKisou = db.FloatProperty(verbose_name=u"地上階層")
    cjyuKisouL = db.FloatProperty(verbose_name=u"地上階層下限")
    cjyuKisouU = db.FloatProperty(verbose_name=u"地上階層上限")

    #所在階
    shzikiL = db.FloatProperty(verbose_name=u"所在階下限")
    shzikiU = db.FloatProperty(verbose_name=u"所在階上限")

    #１階
    floor1 = db.BooleanProperty(verbose_name=u"１階")
    #最上階
    topfloor = db.BooleanProperty(verbose_name=u"最上階")

    sortkey = db.IntegerProperty(verbose_name=u"ソートキー")

    #検索条件名
    name = db.StringProperty(verbose_name=u"検索条件名")

    #連番処理
    adlist_max_num = db.IntegerProperty(verbose_name=u"所在地リスト連番")
    linelist_max_num = db.IntegerProperty(verbose_name=u"所在地リスト連番")
    roomlist_max_num = db.IntegerProperty(verbose_name=u"所在地リスト連番")
    def getNextadlistNum(self):
        def procedure():
            if self.adlist_max_num is None:
                self.adlist_max_num = 0
            self.adlist_max_num += 1
            self.put()
            return self.adlist_max_num
        return db.run_in_transaction(procedure)
    def getNextlinelistNum(self):
        def procedure():
            if self.linelist_max_num is None:
                self.linelist_max_num = 0
            self.linelist_max_num += 1
            self.put()
            return self.linelist_max_num
        return db.run_in_transaction(procedure)
    def getNextroomlistNum(self):
        def procedure():
            if self.roomlist_max_num is None:
                self.roomlist_max_num = 0
            self.roomlist_max_num += 1
            self.put()
            return self.roomlist_max_num
        return db.run_in_transaction(procedure)




