# -*- coding: utf-8 -*-

from google.cloud import ndb
from application.models.member import member
from application import timemanager


class bksearchdata(ndb.Model):

    def put(self, **kwargs):
        # トリガ処理
        # bkID = ndb.StringProperty(verbose_name="物件番号")
        # Check if we're in a transaction
        ctx = ndb.get_context()
        if not ctx.in_transaction():
            namestr = ""
            if self.bkID:
                namestr += "物件番号:" + self.bkID

            # 売買賃貸区分
            # bbchntikbn = ndb.StringProperty(verbose_name="売買賃貸区分", choices={"売買", "賃貸"})
            if self.bbchntikbn:
                namestr += self.bbchntikbn
            # 取扱い種類
            # dtsyuri = ndb.StringProperty(verbose_name="データ種類", choices={"物件","事例","予約","商談中","査定中","重複","停止","競売","現場","サンプル"})
            if self.dtsyuri:
                namestr += self.dtsyuri
            """
            # 物件種別
            # bkknShbt = ndb.StringProperty(verbose_name="物件種別", choices={"土地", "戸建住宅等", "マンション等", "住宅以外の建物全部", "住宅以外の建物一部"})
            if self.bkknShbt:
                namestr += self.bkknShbt + " "
            """
            # 物件種目
            # bkknShmk = ndb.StringProperty(verbose_name="物件種目", choices={"売地", "借地権", "底地権","新築戸建","中古戸建","新築テラス","中古テラス", "店舗", "店舗付住宅", "住宅付店舗","新築マンション","中古マンション","新築タウン","中古タウン","新築リゾート","中古リゾート","事務所", "店舗事務所", "ビル", "工場", "マンション", "倉庫", "アパート", "寮", "旅館", "ホテル", "別荘", "リゾート", "文化住宅", "その他"})
            if self.bkknShmk:
                namestr += self.bkknShmk

            # REVIEW-L2: self.adlist, self.ensen, self.madori プロパティの定義が見つからない
            # 推奨: これらは KeyProperty(repeated=True) または StructuredProperty で定義すべき
            # 現状では AttributeError が発生する可能性がある
            if self.adlist:
                # REVIEW-L1: Incorrect ndb query syntax - Query(kind=...) with bare filter
                # Fixed: Use proper ndb.Model.query() syntax
                q = self.adlist
                for adlist_key in q:
                    adlist_entity = adlist_key.get()
                    if adlist_entity and adlist_entity.ref_bksearchaddresslist:
                        ref_list = adlist_entity.ref_bksearchaddresslist.get()
                        if ref_list and ref_list.name == "個別指定":
                            # Query address items - use proper ndb syntax
                            from application.models.bksearchaddress import bksearchaddress, bksearchaddress2
                            q_addr = bksearchaddress.query().filter(
                                bksearchaddress.ref_bksearchaddresslist == ref_list.key
                            )
                            for ad1 in q_addr.fetch():
                                if ad1.tdufknmi:
                                    namestr += "・" + ad1.tdufknmi
                                if ad1.shzicmi1:
                                    namestr += "・" + ad1.shzicmi1
                                # Check for nested address2 items
                                q_addr2 = bksearchaddress2.query().filter(
                                    bksearchaddress2.ref_address1 == ad1.key
                                )
                                if q_addr2.get():
                                    namestr += "の一部"
                        else:
                            namestr += "・" + ref_list.name

            if self.ensen:
                # REVIEW-L1: Incorrect ndb query syntax - Query(kind=...) with bare filter/order
                # Fixed: Use proper ndb.Model.query() syntax with filter chaining
                for ens_key in self.ensen:
                    ens = ens_key.get()
                    if ens and ens.ensenmei:
                        namestr += "・" + ens.ensenmei
                        # Query eki items - use proper ndb syntax
                        from application.models.bksearchensen import bksearchensen
                        q_eki = bksearchensen.query()
                        q_eki = q_eki.filter(bksearchensen.ref_ensen == ens.key)
                        q_eki = q_eki.order(bksearchensen.sortkey)
                        for eki in q_eki.fetch():
                            if eki.ekimei:
                                namestr += "-" + eki.ekimei
                        if ens.thHnU:
                            namestr += "-徒歩" + str(ens.thHnU) + "分以内"

                        if ens.thMU:
                            namestr += "-" + str(ens.thHnU) + "m以内"

            if self.madori:
                # REVIEW-L1: Incorrect ndb query syntax - Query(kind=...) with bare filter/order
                # Fixed: Use proper ndb.Model.query() syntax with filter chaining
                madoristr = ""
                from application.models.bksearchmadori import bksearchmadori
                q_madori = bksearchmadori.query()
                q_madori = q_madori.filter(bksearchmadori.ref_bksearchdata == self.key)
                q_madori = q_madori.order(bksearchmadori.sortkey)
                for mad in q_madori.fetch():
                    madoristr += " " + str(mad.mdrHysu) + mad.mdrTyp
                if madoristr != "":
                    namestr += "・間取り" + madoristr

            # 交通（分）1
            # kutuHnU = ndb.FloatProperty(verbose_name="交通（分）上限")
            if self.kutuHnU:
                namestr += "・交通" + str(self.kutuHnU) + "分以内"

            # 土地面積
            # tcMnsk2L = ndb.FloatProperty(verbose_name="土地面積下限")
            if self.tcMnsk2L or self.tcMnsk2U:
                namestr += "・土地面積:"
            if self.tcMnsk2L:
                namestr += str(self.tcMnsk2L) + "㎡以上"
            # tcMnsk2U = ndb.FloatProperty(verbose_name="土地面積上限")
            if self.tcMnsk2U:
                namestr += str(self.tcMnsk2U) + "㎡以下"
            # 建物面積1
            # ttmnMnsk1L = ndb.FloatProperty(verbose_name="建物面積下限")
            if self.ttmnMnsk1L or self.ttmnMnsk1U:
                namestr += "・建物面積:" + str(self.blcnyHuku)
            if self.ttmnMnsk1L:
                namestr += str(self.ttmnMnsk1L) + "㎡以上"
            # ttmnMnsk1U = ndb.FloatProperty(verbose_name="建物面積上限")
            if self.ttmnMnsk1U:
                namestr += "" + str(self.ttmnMnsk1U) + "㎡以下"
            # 専有面積
            # snyuMnskSyuBbnMnsk2L = ndb.FloatProperty(verbose_name="専有面積下限")
            if self.snyuMnskSyuBbnMnsk2L or self.snyuMnskSyuBbnMnsk2U:
                namestr += "・専有面積:"
            if self.snyuMnskSyuBbnMnsk2L:
                namestr += str(self.snyuMnskSyuBbnMnsk2L) + "㎡以上"
            # snyuMnskSyuBbnMnsk2U = ndb.FloatProperty(verbose_name="専有面積上限")
            if self.snyuMnskSyuBbnMnsk2U:
                namestr += str(self.snyuMnskSyuBbnMnsk2U) + "㎡以下"

            # 価格
            # kkkuCnryuL = ndb.FloatProperty(verbose_name="価格下限")
            # kkkuCnryuU = ndb.FloatProperty(verbose_name="価格上限")
            if self.kkkuCnryuL or self.kkkuCnryuU:
                namestr += "・価格:"
            if self.kkkuCnryuL:
                namestr += str(self.kkkuCnryuL) + "万円以上"
            if self.kkkuCnryuU:
                namestr += str(self.kkkuCnryuU) + "万円以下"

            # 坪単価
            # tbTnkL = ndb.FloatProperty(verbose_name="坪単価下限")
            # tbTnkU = ndb.FloatProperty(verbose_name="坪単価上限")
            if self.tbTnkL or self.tbTnkU:
                namestr += "・坪単価:"
            if self.tbTnkL:
                namestr += str(self.tbTnkL) + "万円以上"
            if self.tbTnkU:
                namestr += str(self.tbTnkU) + "万円以下"
            # ㎡単価
            # m2TnkL = ndb.FloatProperty(verbose_name="㎡単価下限")
            # m2TnkU = ndb.FloatProperty(verbose_name="㎡単価上限")
            if self.m2TnkL or self.m2TnkU:
                namestr += "・㎡単価:"
            if self.m2TnkL:
                namestr += str(self.m2TnkL) + "万円以上"
            if self.m2TnkU:
                namestr += str(self.m2TnkU) + "万円以下"

            # 想定利回り（％）
            # sutiRmwrPrcntL = ndb.FloatProperty(verbose_name="想定利回り（％）下限")
            # sutiRmwrPrcntU = ndb.FloatProperty(verbose_name="想定利回り（％）上限")
            if self.sutiRmwrPrcntL or self.sutiRmwrPrcntU:
                namestr += "・想定利回り:"
            if self.sutiRmwrPrcntL:
                namestr += str(self.sutiRmwrPrcntL) + "%以上"
            if self.sutiRmwrPrcntU:
                namestr += str(self.sutiRmwrPrcntU) + "%以下"

            # 接道接面
            # stduStmnL = ndb.StringProperty(verbose_name="接道接面下限")
            # stduStmnU = ndb.StringProperty(verbose_name="接道接面上限")
            if self.stduStmnL or self.stduStmnU:
                namestr += "・接道:"
            if self.stduStmnL:
                namestr += str(self.stduStmnL) + "m以上"
            if self.stduStmnU:
                namestr += str(self.stduStmnU) + "m以上"

            # 接道幅員
            # stduFkinL = ndb.FloatProperty(verbose_name="接道幅員下限")
            if self.stduFkinL:
                namestr += "・幅員" + str(self.stduFkinL) + "m以上"

            # 接道方向
            # stduHuku = ndb.StringProperty(verbose_name="接道方向", choices={"北","北東","東","南東","南","南西","西","北西"})
            if self.stduHuku:
                namestr += "・接道方向:" + self.stduHuku

            # バルコニー方向
            # blcnyHuku = ndb.StringProperty(verbose_name="バルコニー方向", choices={"北","北東","東","南東","南","南西","西","北西"})
            if self.blcnyHuku:
                namestr += "・バルコニー方向:" + self.blcnyHuku

            # 築年月（西暦）
            # cknngtSirkU = ndb.DateTimeProperty(verbose_name="築年月（西暦）上限")
            # cknngtSirkL = ndb.DateTimeProperty(verbose_name="築年月（西暦）下限")
            if self.cknngtSirkU or self.cknngtSirkL:
                namestr += "・築年月:"
            if self.cknngtSirkU:
                namestr += timemanager.utc2jst_date(self.cknngtSirkU).strftime("%Y/%m/%d") + "から"
            if self.cknngtSirkL:
                namestr += timemanager.utc2jst_date(self.cknngtSirkL).strftime("%Y/%m/%d") + "まで"

            # 地上階層
            # cjyuKisou = ndb.FloatProperty(verbose_name="地上階層")
            # cjyuKisouL = ndb.FloatProperty(verbose_name="地上階層下限")
            # cjyuKisouU = ndb.FloatProperty(verbose_name="地上階層上限")
            if self.cjyuKisouU or self.cjyuKisouL:
                namestr += "・地上階:"
            if self.cjyuKisouL:
                namestr += str(self.cjyuKisouL) + "階以上"
            if self.cjyuKisouU:
                namestr += str(self.cjyuKisouU) + "階以下"

            # 所在階
            # shzikiU = ndb.FloatProperty(verbose_name="所在階上限")
            # shzikiL = ndb.FloatProperty(verbose_name="所在階下限")
            if self.shzikiU or self.shzikiL:
                namestr += "・所在階:"
            if self.shzikiL:
                namestr += str(self.shzikiL) + "階以上"
            if self.shzikiU:
                namestr += str(self.shzikiU) + "階以下"
            # １階
            # floor1 = ndb.BooleanProperty(verbose_name="１階")
            if self.floor1:
                namestr += "・１階"
            # 最上階
            # topfloor = ndb.BooleanProperty(verbose_name="最上階")
            if self.topfloor:
                namestr += "・最上階"
            # ペット可
            # ptflg = ndb.BooleanProperty(verbose_name="ペット可")
            if self.ptflg:
                namestr += "・ペット可"
            # 建築条件なし
            # knckJyukn = ndb.BooleanProperty(verbose_name="建築条件")
            if self.knckJyukn:
                namestr += "・建築条件なし"
            # オーナーチェンジ
            # ornrChng = ndb.BooleanProperty(verbose_name="オーナーチェンジ")
            if self.ornrChng:
                namestr += "・オーナーチェンジ"
            # 位置情報有無
            # isidkd = ndb.BooleanProperty(verbose_name="位置情報有無")
            if self.isidkd:
                namestr += "・位置情報あり"
            elif self.isidkd == False:
                namestr += "・位置情報なし"
            # 告知事項なし
            # kktjkuflg = ndb.BooleanProperty(verbose_name="告知事項")
            if self.kktjkuflg:
                namestr += "・告知事項あり"
            # アイコン名
            # icons = ndb.StringProperty(verbose_name="アイコン名")
            if self.icons:
                namestr += "・アイコングループ:" + self.icons

            # 建物名
            # ttmnmi = ndb.StringProperty(verbose_name="建物名")
            if self.ttmnmi:
                namestr += "・建物名:" + self.ttmnmi
            # 引渡時期
            # hkwtsNyukyJk = ndb.StringProperty(verbose_name="引渡時期")
            if self.hkwtsNyukyJk:
                namestr += "・引渡時期:" + self.hkwtsNyukyJk
            # データ元
            # dataSource = ndb.StringProperty(verbose_name="データ元")
            if self.dataSource:
                namestr += "・データ元:" + self.dataSource
            # 広告転載区分
            # kukkTnsiKbn = ndb.StringProperty(verbose_name="広告転載区分", choices={"広告可","一部可（インターネット）","一部可（チラシ・新聞広告）","広告可（但し要連絡）","不可","未確認"})
            if self.kukkTnsiKbn:
                namestr += "・広告転載区分:" + self.kukkTnsiKbn
            # 業者名
            # kiinni = ndb.StringProperty(verbose_name="業者名")
            if self.kiinni:
                namestr += "・業者名:" + self.kiinni

            if namestr == "":
                namestr = "設定なし"
            self.name = namestr

        return super(bksearchdata, self).put(**kwargs)

    # REVIEW-L1: ndb.KeyProperty の kind パラメータに文字列ではなくクラス名を使用している
    # 修正前: modified = ndb.KeyProperty(kind=member, verbose_name="更新担当")
    # 修正前: member_key = ndb.KeyProperty(kind=member, verbose_name="メンバー")
    # 修正後: modified = ndb.KeyProperty(kind='member', verbose_name="更新担当")
    # 修正後: member_key = ndb.KeyProperty(kind='member', verbose_name="メンバー")
    modified = ndb.KeyProperty(kind='member', verbose_name="更新担当")
    member_key = ndb.KeyProperty(kind='member', verbose_name="メンバー")
    timestamp = ndb.DateTimeProperty(verbose_name="最終更新", auto_now=True)

    bkID = ndb.StringProperty(verbose_name="物件番号")

    # 確認年月日
    kknnngpL = ndb.DateTimeProperty(verbose_name="確認年月日下限")
    kknnngpU = ndb.DateTimeProperty(verbose_name="確認年月日上限")
    # 変更年月日
    # hnknngp = ndb.DateTimeProperty(verbose_name="変更年月日",auto_now_add = True)
    hnknngpL = ndb.DateTimeProperty(verbose_name="変更年月日下限")
    hnknngpU = ndb.DateTimeProperty(verbose_name="変更年月日上限")
    # 登録年月日
    # turknngp = ndb.DateTimeProperty(verbose_name="登録年月日",auto_now_add = True)
    turknngpL = ndb.DateTimeProperty(verbose_name="登録年月日下限")
    turknngpU = ndb.DateTimeProperty(verbose_name="登録年月日上限")
    # 更新年月日
    # ksnnngp = ndb.DateTimeProperty(verbose_name="更新年月日",auto_now=True)
    ksnnngpL = ndb.DateTimeProperty(verbose_name="更新年月日下限")
    ksnnngpU = ndb.DateTimeProperty(verbose_name="更新年月日上限")

    # 売買賃貸区分
    bbchntikbn = ndb.StringProperty(verbose_name="売買賃貸区分", choices={"売買", "賃貸"})
    # 取扱い種類
    dtsyuri = ndb.StringProperty(verbose_name="データ種類", choices={"物件", "事例", "予約", "商談中", "査定中", "重複", "停止", "競売", "現場", "サンプル"})
    # 物件種別
    bkknShbt = ndb.StringProperty(verbose_name="物件種別", choices={"土地", "戸建住宅等", "マンション等", "住宅以外の建物全部", "住宅以外の建物一部", "賃貸一戸建", "賃貸マンション", "賃貸土地", "賃貸外全", "賃貸外一", "その他"})
    # 物件種目
    bkknShmk = ndb.StringProperty(verbose_name="物件種目", choices={"売地", "借地権", "底地権", "新築戸建", "中古戸建", "新築テラス", "中古テラス", "店舗", "店舗付住宅", "住宅付店舗", "新築マンション", "中古マンション", "新築タウン", "中古タウン", "新築リゾート", "中古リゾート", "店舗事務所", "ビル", "工場", "マンション", "倉庫", "アパート", "寮", "旅館", "ホテル", "別荘", "リゾート", "文化住宅", "貸家", "テラス", "マンション", "タウン", "間借り", "居住用地", "事業用地", "店舗戸建", "旅館等", "寮", "別荘", "ビル", "住宅付店舗戸建", "店舗事務所", "店舗一部", "事務所", "住宅付店舗一部", "マンション一室", "その他"})
    # ペット可
    ptflg = ndb.BooleanProperty(verbose_name="ペット可")
    # マッチング可
    mtngflg = ndb.BooleanProperty(verbose_name="マッチング可", default=True)
    # web検索許可
    webknskflg = ndb.BooleanProperty(verbose_name="web検索許可", default=True)
    # 位置情報有無
    isidkd = ndb.BooleanProperty(verbose_name="位置情報有無")
    # 建築条件なし
    knckJyukn = ndb.BooleanProperty(verbose_name="建築条件")
    # オーナーチェンジ
    ornrChng = ndb.BooleanProperty(verbose_name="オーナーチェンジ")
    # 告知事項なし
    kktjkuflg = ndb.BooleanProperty(verbose_name="告知事項")
    # アイコン名
    icons = ndb.StringProperty(verbose_name="アイコン名")
    # 作成状況
    sksijky = ndb.StringProperty(verbose_name="作成状況", choices={"請求チェック", "一覧のみ", "資料請求", "依頼中", "入手不可", "入手済み", "分類チェック", "不要", "未作成", "作成済み", "HP掲載"})
    # 交通（分）1
    kutuHnU = ndb.FloatProperty(verbose_name="交通（分）上限")
    # 建物名
    ttmnmi = ndb.StringProperty(verbose_name="建物名")
    # 引渡時期
    hkwtsNyukyJk = ndb.StringProperty(verbose_name="引渡時期")
    # データ元
    dataSource = ndb.StringProperty(verbose_name="データ元")
    # 広告転載区分
    kukkTnsiKbn = ndb.StringProperty(verbose_name="広告転載区分", choices={"広告可", "一部可(インターネット)", "一部可(チラシ・新聞広告)", "広告可(但し要連絡)", "不可", "未確認"})
    # 業者名
    kiinni = ndb.StringProperty(verbose_name="業者名")

    # 間取タイプ
    mdrTyp = ndb.StringProperty(verbose_name="間取タイプ", choices={"ワンルーム", "K", "DK", "LK", "LDK", "SK", "SDK", "SLK", "SLDK"})
    # 間取部屋数
    mdrHysu = ndb.FloatProperty(verbose_name="間取部屋数")

    # 接道方向
    stduHuku = ndb.StringProperty(verbose_name="接道方向", choices={"北", "北東", "東", "南東", "南", "南西", "西", "北西"})

    # バルコニー方向
    blcnyHuku = ndb.StringProperty(verbose_name="バルコニー方向", choices={"北", "北東", "東", "南東", "南", "南西", "西", "北西"})

    # 土地面積
    tcMnsk2L = ndb.FloatProperty(verbose_name="土地面積下限")
    tcMnsk2U = ndb.FloatProperty(verbose_name="土地面積上限")
    # 建物面積1
    ttmnMnsk1L = ndb.FloatProperty(verbose_name="建物面積下限")
    ttmnMnsk1U = ndb.FloatProperty(verbose_name="建物面積上限")
    # 専有面積
    snyuMnskSyuBbnMnsk2L = ndb.FloatProperty(verbose_name="専有面積下限")
    snyuMnskSyuBbnMnsk2U = ndb.FloatProperty(verbose_name="専有面積上限")
    # 価格
    kkkuCnryuL = ndb.FloatProperty(verbose_name="価格下限")
    kkkuCnryuU = ndb.FloatProperty(verbose_name="価格上限")
    # 坪単価
    tbTnkL = ndb.FloatProperty(verbose_name="坪単価下限")
    tbTnkU = ndb.FloatProperty(verbose_name="坪単価上限")
    # ㎡単価
    m2TnkL = ndb.FloatProperty(verbose_name="㎡単価下限")
    m2TnkU = ndb.FloatProperty(verbose_name="㎡単価上限")
    # 想定利回り(%)
    sutiRmwrPrcntL = ndb.FloatProperty(verbose_name="想定利回り(%)下限")
    sutiRmwrPrcntU = ndb.FloatProperty(verbose_name="想定利回り(%)上限")

    # 接道接面
    stduStmnL = ndb.StringProperty(verbose_name="接道接面下限")
    stduStmnU = ndb.StringProperty(verbose_name="接道接面上限")

    # 接道幅員
    stduFkinL = ndb.FloatProperty(verbose_name="接道幅員下限")

    # 築年月(西暦)
    cknngtSirkL = ndb.DateTimeProperty(verbose_name="築年月(西暦)下限")
    cknngtSirkU = ndb.DateTimeProperty(verbose_name="築年月(西暦)上限")
    # 地上階層
    # cjyuKisou = ndb.FloatProperty(verbose_name="地上階層")
    cjyuKisouL = ndb.FloatProperty(verbose_name="地上階層下限")
    cjyuKisouU = ndb.FloatProperty(verbose_name="地上階層上限")

    # 所在階
    shzikiL = ndb.FloatProperty(verbose_name="所在階下限")
    shzikiU = ndb.FloatProperty(verbose_name="所在階上限")

    # １階
    floor1 = ndb.BooleanProperty(verbose_name="１階")
    # 最上階
    topfloor = ndb.BooleanProperty(verbose_name="最上階")

    sortkey = ndb.IntegerProperty(verbose_name="ソートキー")

    # 検索条件名
    name = ndb.StringProperty(verbose_name="検索条件名")

    # 連番処理
    adlist_max_num = ndb.IntegerProperty(verbose_name="所在地リスト連番")
    linelist_max_num = ndb.IntegerProperty(verbose_name="所在地リスト連番")
    roomlist_max_num = ndb.IntegerProperty(verbose_name="所在地リスト連番")

    def getNextadlistNum(self):
        @ndb.transactional
        def procedure():
            if self.adlist_max_num is None:
                self.adlist_max_num = 0
            self.adlist_max_num += 1
            self.put()
            return self.adlist_max_num
        return procedure()

    def getNextlinelistNum(self):
        @ndb.transactional
        def procedure():
            if self.linelist_max_num is None:
                self.linelist_max_num = 0
            self.linelist_max_num += 1
            self.put()
            return self.linelist_max_num
        return procedure()

    def getNextroomlistNum(self):
        @ndb.transactional
        def procedure():
            if self.roomlist_max_num is None:
                self.roomlist_max_num = 0
            self.roomlist_max_num += 1
            self.put()
            return self.roomlist_max_num
        return procedure()
