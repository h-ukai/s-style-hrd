# -*- coding: utf-8 -*-

import os
from flask import request
from google.cloud import ndb

from application.models.member import member
from application.models.bksearchdata import bksearchdata
from application.models.bkdata import BKdata
from application.models.CorpOrg import CorpOrg
from application.models.Branch import Branch
from application.models.bksearchaddress import *
from application.models.bksearchmadori import bksearchmadori
from application.bksearchensenutl import bksearchensenutl

from application.messageManager import messageManager

import datetime
import re
from application.bksearchutl import bksearchutl
from application import timemanager
from application.SecurePage import SecurePage
from application.wordstocker import wordstocker
from application.bklistutl import bklistutl


class bkdataSearchProbider(object):
    """検索データプロバイダー

    Migration Notes:
    - webapp2 RequestHandler クラスから独立したユーティリティクラスに移行
    - request パラメータは Flask request オブジェクトを使用
    - db.Model → ndb.Model
    - get_by_key_name() → ndb.Key().get()
    - .count() → len(query.fetch()) または query.count()
    - .order() → .order()（構文同じ）
    - .fetch() → .fetch()（構文同じ）
    - .key() → .key（プロパティ）
    - str(key()) → key.urlsafe().decode()
    - ReferenceProperty の逆参照（.adlist, .ensen, .madori）は StructuredProperty で対応

    REVIEW-L1: Flask request 互換のため、webapp2 の request.get() をエミュレート
    - webapp2: self.request.get("key") → Flask: self.request.values.get("key", "")
    """

    def __init__(self, corp_name, branch_name, memID, userID, userkey, memdb, tmpl_val, req):
        # REVIEW-L1: Flask request オブジェクトに webapp2 互換の get() メソッドを追加
        # 修正前: self.request = req（webapp2 の request.get() を想定）
        # 修正後: Flask request に get() メソッドをモンキーパッチで追加
        self.request = req

        # Flask request オブジェクトに webapp2 互換の get() メソッドを追加
        if hasattr(self.request, 'values') and not hasattr(self.request, 'get'):
            # Flask request の場合、webapp2 互換の get() メソッドを追加
            def _get_compat(key, default=None):
                return self.request.values.get(key, default if default is not None else "")
            self.request.get = _get_compat
        self.memberID = memID
        self.userID = userID
        self.userkey = userkey
        self.corp_name = corp_name
        self.branch_name = branch_name
        self.memdb = memdb
        self.tmpl_val = tmpl_val

    def get(self, **kwargs):

        if kwargs.get("page", None) is not None:
            page = int(kwargs.get("page", None))
        else:
            # REVIEW-L1: Flask では request.get() の代わりに request.args.get() / request.form.get() を使用
            # 修正前: self.request.get("page")
            # 修正後: self.request.args.get("page", "") または self.request.values.get("page", "")
            page_param = self.request.args.get("page", "") if hasattr(self.request, 'args') else self.request.get("page", "")
            if page_param != "":
                page = int(page_param)
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
            self.memdb = ndb.Key(member, key_name).get()
            if self.memdb:
                self.tmpl_val["membertel"] = self.memdb.phone
                self.tmpl_val["membermail"] = self.memdb.mail
                self.tmpl_val["memberyomi"] = self.memdb.yomi
                self.tmpl_val["membername"] = self.memdb.name
                self.tmpl_val["memberID"] = self.memberID

        if self.memberID:
            # ndb では Query オブジェクトから count() で件数取得
            query = bksearchdata.query(bksearchdata.member == self.memdb.key)
            allpage = query.count()
            pages = []
            for i in range(allpage):
                opstr = ""
                if self.memberID:
                    opstr = "?memberID=" + self.memberID + "&page=" + str(i+1)
                else:
                    opstr = "?page=" + str(i+1)

                pages.append({"page": i+1, "path": self.request.path + opstr})
            if page and allpage > 0:
                if allpage < page:
                    page = allpage
                # fetch() で page 件目までのデータを取得して [page-1] でアクセス
                bksearchdata_list = query.order(bksearchdata.sortkey).fetch(page)
                if bksearchdata_list:
                    sddb = bksearchdata_list[page-1]
                    key = sddb.key.urlsafe().decode()
            else:
                if allpage > 0:
                    sddb = query.order(bksearchdata.sortkey).fetch(1)[0]
                    key = sddb.key.urlsafe().decode()
                    page = 1
                else:
                    pass
            if sddb:
                # 子エンティティ参照の処理
                # ndb では StructuredProperty または KeyProperty で親子関係を定義
                # 既存の逆参照（.adlist.order()）は互換性のため、クエリで再実装
                # TODO: bksearchdata の スキーマで adlist, ensen, madori を StructuredProperty として定義されているか確認

                # adlist の処理
                if hasattr(sddb, 'adlist'):
                    for al in sddb.adlist:  # StructuredProperty の場合
                        if al.ref_bksearchaddresslist is None:
                            al.delete()
                        else:
                            adlist.append({
                                "name": al.ref_bksearchaddresslist.name,
                                "division": al.ref_bksearchaddresslist.division,
                                "key": al.ref_bksearchaddresslist.key.urlsafe().decode()
                            })

                # ensen の処理
                if hasattr(sddb, 'ensen'):
                    for ensen in sddb.ensen:  # StructuredProperty の場合
                        line.append({
                            "tdufknmi": ensen.tdufknmi,
                            "ensenmei": ensen.ensenmei,
                            "thHnU": ensen.thHnU,
                            "thMU": ensen.thMU,
                            "station": [eki.ekimei for eki in ensen.eki]
                        })

                # madori の処理
                if hasattr(sddb, 'madori'):
                    for madori in sddb.madori:  # StructuredProperty の場合
                        room.append({
                            "mdrHysu": str(madori.mdrHysu),
                            "mdrTyp": madori.mdrTyp
                        })

                sddb = timemanager.utc2jst_gql(sddb)
        self.tmpl_val['iconlist'] = wordstocker.get(self.corp_name, "アイコン")
        self.tmpl_val["key"] = key
        self.tmpl_val["data"] = sddb
        self.tmpl_val["adlist"] = adlist
        self.tmpl_val["line"] = line
        self.tmpl_val["room"] = room
        self.tmpl_val["page"] = page
        self.tmpl_val["pages"] = pages

        return self.tmpl_val

    def post(self, **kwargs):
        # REVIEW-L1: Flask では request.get() の代わりに request.values.get() を使用（POST/GETの両方に対応）
        # 修正前: self.request.get("submit")
        # 修正後: self.request.values.get("submit", "") または request.form.get("submit", "")
        submit = self.request.values.get("submit", "") if hasattr(self.request, 'values') else self.request.get("submit", "")
        key = self.request.values.get("key", "") if hasattr(self.request, 'values') else self.request.get("key", "")
        page = 1
        if not self.memberID:
            self.memberID = self.userID
        key_name = self.corp_name + "/" + self.memberID
        mmdb = ndb.Key(member, key_name).get()

        # ndb では Query オブジェクトから count() で件数取得
        query = bksearchdata.query(bksearchdata.member == mmdb.key)

        if not key or submit == "新規ページへ保存" or submit == "新規ページへ保存して検索" or submit == "search" or submit == "新規ページへ保存2" or submit == "新規ページへ保存して検索2" or submit == "search2":
            # REVIEW-L1: Flask request.values.get() に修正
            page = self.request.values.get("page", "") if hasattr(self.request, 'values') else self.request.get("page", "")
            if not page or page == "0":
                page = 1
            else:
                page = int(page)
            if submit == "新規ページへ保存" or submit == "新規ページへ保存して検索" or submit == "search" or submit == "新規ページへ保存2" or submit == "新規ページへ保存して検索2" or submit == "search2":
                page = query.count() + 1
            if query.count() >= page:
                sddb = query.order(bksearchdata.sortkey).fetch(page)[page-1]
            else:
                sddb = bksearchdata()
                sddb.member = mmdb.key
                sddb.sortkey = mmdb.getNextsdlistNum()
                sddb.put()
        else:
            sddb = ndb.Key(urlsafe=key).get()

        kwargs["page"] = page

        # 子エンティティの削除処理
        if hasattr(sddb, 'adlist'):
            for al in sddb.adlist:
                al.deladlist()
        if hasattr(sddb, 'ensen'):
            for e in sddb.ensen:
                eu = bksearchensenutl()
                eu.ensen = e
                eu.delete()
        if hasattr(sddb, 'madori'):
            for m in sddb.madori:
                m.delete()

        if submit == "ページ削除":
            sddb.delete()
            self.get(**kwargs)
            return kwargs

        i = 0
        multi = []
        if hasattr(self.request, 'GET') and hasattr(self.request.GET, 'multi'):
            multi = self.request.GET.multi
        elif hasattr(self.request, 'POST') and hasattr(self.request.POST, 'multi'):
            multi = self.request.POST.multi

        # REVIEW-L1: Flask では multi._items の代わりに request.form/args を直接参照
        # 修正前: multi._items でアクセス
        # 修正後: Flask の request.form.getlist() または request.values.to_dict(flat=False) を使用
        # TODO: 既存の webapp2 の multi 構造を Flask へ適応が必要（手動対応推奨）

        # 暫定実装: webapp2 互換性を維持するため、既存ロジックをコメントで保持
        # 実際の Flask 実装は呼び出し元のコンテキストに依存するため、要確認
        if len(multi):
            for n, v in enumerate(multi):  # multi._items の代わりに enumerate を使用
                if n < len(multi):
                    if multi[n][0] == "listid":
                        if multi[n][1]:
                            # listcombinator クラスへのアクセス - 未処理
                            lc = listcombinator(co=self.corp_name, br=self.branch_name)
                            lc.setadlist(multi[n][1], sddb)
                    if multi[n][0] == "line":
                        if multi[n][1] or (n+1 < len(multi) and multi[n+1][1]) or (n+2 < len(multi) and multi[n+2][1]):
                            ensenutl = bksearchensenutl()
                            ensenutl.newensen(
                                sddb,
                                ensenmei=multi[n][1],
                                tdufknmi=multi[n-1][1] if n > 0 else None,
                                thHnU=multi[n+1][1] if n+1 < len(multi) else None,
                                thMU=multi[n+2][1] if n+2 < len(multi) else None
                            )
                            if n+3 < len(multi) and multi[n+3][0] == "station":
                                for eki in multi[n+3][1].split(","):
                                    if eki:
                                        ensenutl.addeki(eki)
                    if multi[n][0] == "mdrHysu":
                        if multi[n][1] or (n+1 < len(multi) and multi[n+1][1]):
                            if multi[n][1]:
                                c = float(multi[n][1])
                            else:
                                c = None
                            bksearchmadori(
                                ref_bksearchdata=sddb.key,
                                mdrHysu=c,
                                mdrTyp=multi[n+1][1] if n+1 < len(multi) else None,
                                sortkey=sddb.getNextroomlistNum()
                            ).put()

        if self.userkey:
            sddb.modified = ndb.Key(urlsafe=self.userkey).get()

        bkID = self.request.get("bkID")
        if bkID:
            sddb.bkID = bkID
        else:
            sddb.bkID = None

        # 確認年月日
        kknnngpL = self.request.get("kknnngpL")
        if kknnngpL:
            r = re.compile(".*:.*:.*").match(kknnngpL, 1)
            if r is None:
                sddb.kknnngpL = timemanager.jst2utc_date(datetime.datetime.strptime(kknnngpL, "%Y/%m/%d"))
            else:
                sddb.kknnngpL = timemanager.jst2utc_date(datetime.datetime.strptime(kknnngpL, "%Y/%m/%d %H:%M:%S"))
        else:
            sddb.kknnngpL = None

        kknnngpU = self.request.get("kknnngpU")
        if kknnngpU:
            r = re.compile(".*:.*:.*").match(kknnngpU, 1)
            if r is None:
                sddb.kknnngpU = timemanager.jst2utc_date(datetime.datetime.strptime(kknnngpU, "%Y/%m/%d"))
            else:
                sddb.kknnngpU = timemanager.jst2utc_date(datetime.datetime.strptime(kknnngpU, "%Y/%m/%d %H:%M:%S"))
        else:
            sddb.kknnngpU = None

        # 変更年月日
        hnknngpL = self.request.get("hnknngpL")
        if hnknngpL:
            r = re.compile(".*:.*:.*").match(hnknngpL, 1)
            if r is None:
                sddb.hnknngpL = timemanager.jst2utc_date(datetime.datetime.strptime(hnknngpL, "%Y/%m/%d"))
            else:
                sddb.hnknngpL = timemanager.jst2utc_date(datetime.datetime.strptime(hnknngpL, "%Y/%m/%d %H:%M:%S"))
        else:
            sddb.hnknngpL = None

        hnknngpU = self.request.get("hnknngpU")
        if hnknngpU:
            r = re.compile(".*:.*:.*").match(hnknngpU, 1)
            if r is None:
                sddb.hnknngpU = timemanager.jst2utc_date(datetime.datetime.strptime(hnknngpU, "%Y/%m/%d"))
            else:
                sddb.hnknngpU = timemanager.jst2utc_date(datetime.datetime.strptime(hnknngpU, "%Y/%m/%d %H:%M:%S"))
        else:
            sddb.hnknngpU = None

        # 登録年月日
        turknngpL = self.request.get("turknngpL")
        if turknngpL:
            r = re.compile(".*:.*:.*").match(turknngpL, 1)
            if r is None:
                sddb.turknngpL = timemanager.jst2utc_date(datetime.datetime.strptime(turknngpL, "%Y/%m/%d"))
            else:
                sddb.turknngpL = timemanager.jst2utc_date(datetime.datetime.strptime(turknngpL, "%Y/%m/%d %H:%M:%S"))
        else:
            sddb.turknngpL = None

        turknngpU = self.request.get("turknngpU")
        if turknngpU:
            r = re.compile(".*:.*:.*").match(turknngpU, 1)
            if r is None:
                sddb.turknngpU = timemanager.jst2utc_date(datetime.datetime.strptime(turknngpU, "%Y/%m/%d"))
            else:
                sddb.turknngpU = timemanager.jst2utc_date(datetime.datetime.strptime(turknngpU, "%Y/%m/%d %H:%M:%S"))
        else:
            sddb.turknngpU = None

        # 更新年月日
        ksnnngpL = self.request.get("ksnnngpL")
        if ksnnngpL:
            r = re.compile(".*:.*:.*").match(ksnnngpL, 1)
            if r is None:
                sddb.ksnnngpL = timemanager.jst2utc_date(datetime.datetime.strptime(ksnnngpL, "%Y/%m/%d"))
            else:
                sddb.ksnnngpL = timemanager.jst2utc_date(datetime.datetime.strptime(ksnnngpL, "%Y/%m/%d %H:%M:%S"))
        else:
            sddb.ksnnngpL = None

        ksnnngpU = self.request.get("ksnnngpU")
        if ksnnngpU:
            r = re.compile(".*:.*:.*").match(ksnnngpU, 1)
            if r is None:
                sddb.ksnnngpU = timemanager.jst2utc_date(datetime.datetime.strptime(ksnnngpU, "%Y/%m/%d"))
            else:
                sddb.ksnnngpU = timemanager.jst2utc_date(datetime.datetime.strptime(ksnnngpU, "%Y/%m/%d %H:%M:%S"))
        else:
            sddb.ksnnngpU = None

        # 売買賃貸区分
        bbchntikbn = self.request.get("bbchntikbn")
        if bbchntikbn:
            sddb.bbchntikbn = bbchntikbn
        else:
            sddb.bbchntikbn = None

        # 取扱い種類
        dtsyuri = self.request.get("dtsyuri")
        if dtsyuri:
            sddb.dtsyuri = dtsyuri
        else:
            sddb.dtsyuri = None

        # 物件種別
        bkknShbt = self.request.get("bkknShbt")
        if bkknShbt:
            sddb.bkknShbt = bkknShbt
        else:
            sddb.bkknShbt = None

        # 物件種目
        bkknShmk = self.request.get("bkknShmk")
        if bkknShmk:
            sddb.bkknShmk = bkknShmk
        else:
            sddb.bkknShmk = None

        # 交通（分）1
        kutuHnU = self.request.get("kutuHnU")
        if kutuHnU:
            sddb.kutuHnU = float(kutuHnU)
        else:
            sddb.kutuHnU = None

        # ペット可
        ptflg = self.request.get("ptflg")
        if ptflg == "1":
            sddb.ptflg = True
        else:
            sddb.ptflg = None

        # マッチング可
        mtngflg = self.request.get("mtngflg")
        if mtngflg == "1":
            sddb.mtngflg = True
        else:
            sddb.mtngflg = None

        # web検索許可
        webknskflg = self.request.get("webknskflg")
        if webknskflg == "1":
            sddb.webknskflg = True
        else:
            sddb.webknskflg = None

        # 位置情報有
        isidkd = self.request.get("isidkd")
        if isidkd == "1":
            sddb.isidkd = True
        elif isidkd == "0":
            sddb.isidkd = False
        else:
            sddb.isidkd = None

        # 建築条件
        knckJyukn = self.request.get("knckJyukn")
        if knckJyukn == "1":
            sddb.knckJyukn = True
        else:
            sddb.knckJyukn = None

        # オーナーチェンジ
        ornrChng = self.request.get("ornrChng")
        if ornrChng == "1":
            sddb.ornrChng = True
        else:
            sddb.ornrChng = None

        # 告知事項
        kktjkuflg = self.request.get("kktjkuflg")
        if kktjkuflg == "1":
            sddb.kktjkuflg = True
        else:
            sddb.kktjkuflg = None

        # アイコン名
        icons = self.request.get("icons")
        if icons:
            sddb.icons = icons
        else:
            sddb.icons = None

        # 都道府県名
        tdufknmi = self.request.get("tdufknmi")
        if tdufknmi:
            sddb.tdufknmi = tdufknmi
        else:
            sddb.tdufknmi = None

        # 建物名
        ttmnmi = self.request.get("ttmnmi")
        if ttmnmi:
            sddb.ttmnmi = ttmnmi
        else:
            sddb.ttmnmi = None

        # 引渡時期
        hkwtsNyukyJk = self.request.get("hkwtsNyukyJk")
        if hkwtsNyukyJk:
            sddb.hkwtsNyukyJk = hkwtsNyukyJk
        else:
            sddb.hkwtsNyukyJk = None

        # データ元
        dataSource = self.request.get("dataSource")
        if dataSource:
            sddb.dataSource = dataSource
        else:
            sddb.dataSource = None

        # 作成状況
        sksijky = self.request.get("sksijky")
        if sksijky:
            sddb.sksijky = sksijky
        else:
            sddb.sksijky = None

        # 広告転載区分
        kukkTnsiKbn = self.request.get("kukkTnsiKbn")
        if kukkTnsiKbn:
            sddb.kukkTnsiKbn = kukkTnsiKbn
        else:
            sddb.kukkTnsiKbn = None

        # 業者名
        kiinni = self.request.get("kiinni")
        if kiinni:
            sddb.kiinni = kiinni
        else:
            sddb.kiinni = None

        # 接道方向
        stduHuku = self.request.get("stduHuku")
        if stduHuku:
            sddb.stduHuku = stduHuku
        else:
            sddb.stduHuku = None

        # バルコニー方向
        blcnyHuku = self.request.get("blcnyHuku")
        if blcnyHuku:
            sddb.blcnyHuku = blcnyHuku
        else:
            sddb.blcnyHuku = None

        # 土地面積
        tcMnsk2L = self.request.get("tcMnsk2L")
        if tcMnsk2L:
            sddb.tcMnsk2L = float(tcMnsk2L)
        else:
            sddb.tcMnsk2L = None

        tcMnsk2U = self.request.get("tcMnsk2U")
        if tcMnsk2U:
            sddb.tcMnsk2U = float(tcMnsk2U)
        else:
            sddb.tcMnsk2U = None

        # 建物面積1
        ttmnMnsk1L = self.request.get("ttmnMnsk1L")
        if ttmnMnsk1L:
            sddb.ttmnMnsk1L = float(ttmnMnsk1L)
        else:
            sddb.ttmnMnsk1L = None

        ttmnMnsk1U = self.request.get("ttmnMnsk1U")
        if ttmnMnsk1U:
            sddb.ttmnMnsk1U = float(ttmnMnsk1U)
        else:
            sddb.ttmnMnsk1U = None

        # 専有面積
        snyuMnskSyuBbnMnsk2L = self.request.get("snyuMnskSyuBbnMnsk2L")
        if snyuMnskSyuBbnMnsk2L:
            sddb.snyuMnskSyuBbnMnsk2L = float(snyuMnskSyuBbnMnsk2L)
        else:
            sddb.snyuMnskSyuBbnMnsk2L = None

        snyuMnskSyuBbnMnsk2U = self.request.get("snyuMnskSyuBbnMnsk2U")
        if snyuMnskSyuBbnMnsk2U:
            sddb.snyuMnskSyuBbnMnsk2U = float(snyuMnskSyuBbnMnsk2U)
        else:
            sddb.snyuMnskSyuBbnMnsk2U = None

        # 価格
        kkkuCnryuL = self.request.get("kkkuCnryuL")
        if kkkuCnryuL:
            sddb.kkkuCnryuL = float(kkkuCnryuL)
        else:
            sddb.kkkuCnryuL = None

        kkkuCnryuU = self.request.get("kkkuCnryuU")
        if kkkuCnryuU:
            sddb.kkkuCnryuU = float(kkkuCnryuU)
        else:
            sddb.kkkuCnryuU = None

        # 坪単価
        tbTnkL = self.request.get("tbTnkL")
        if tbTnkL:
            sddb.tbTnkL = float(tbTnkL)
        else:
            sddb.tbTnkL = None

        tbTnkU = self.request.get("tbTnkU")
        if tbTnkU:
            sddb.tbTnkU = float(tbTnkU)
        else:
            sddb.tbTnkU = None

        # ㎡単価
        m2TnkL = self.request.get("m2TnkL")
        if m2TnkL:
            sddb.m2TnkL = float(m2TnkL)
        else:
            sddb.m2TnkL = None

        m2TnkU = self.request.get("m2TnkU")
        if m2TnkU:
            sddb.m2TnkU = float(m2TnkU)
        else:
            sddb.m2TnkU = None

        # 想定利回り（％）
        sutiRmwrPrcntL = self.request.get("sutiRmwrPrcntL")
        if sutiRmwrPrcntL:
            sddb.sutiRmwrPrcntL = float(sutiRmwrPrcntL)
        else:
            sddb.sutiRmwrPrcntL = None

        sutiRmwrPrcntU = self.request.get("sutiRmwrPrcntU")
        if sutiRmwrPrcntU:
            sddb.sutiRmwrPrcntU = float(sutiRmwrPrcntU)
        else:
            sddb.sutiRmwrPrcntU = None

        # 接道接面
        stduStmnL = self.request.get("stduStmnL")
        if stduStmnL:
            sddb.stduStmnL = stduStmnL
        else:
            sddb.stduStmnL = None

        stduStmnU = self.request.get("stduStmnU")
        if stduStmnU:
            sddb.stduStmnU = stduStmnU
        else:
            sddb.stduStmnU = None

        # 接道幅員
        stduFkinL = self.request.get("stduFkinL")
        if stduFkinL:
            sddb.stduFkinL = float(stduFkinL)
        else:
            sddb.stduFkinL = None

        # 交通（分）1
        kutuHnU = self.request.get("kutuHnU")
        if kutuHnU:
            sddb.kutuHnU = float(kutuHnU)
        else:
            sddb.kutuHnU = None

        # 築年月（西暦）
        cknngtSirkU = self.request.get("cknngtSirkU")
        if cknngtSirkU:
            r = re.compile(".*:.*:.*").match(cknngtSirkU, 1)
            if r is None:
                sddb.cknngtSirkU = timemanager.jst2utc_date(datetime.datetime.strptime(cknngtSirkU, "%Y/%m/%d"))
            else:
                sddb.cknngtSirkU = timemanager.jst2utc_date(datetime.datetime.strptime(cknngtSirkU, "%Y/%m/%d %H:%M:%S"))
        else:
            sddb.cknngtSirkU = None

        cknngtSirkL = self.request.get("cknngtSirkL")
        if cknngtSirkL:
            r = re.compile(".*:.*:.*").match(cknngtSirkL, 1)
            if r is None:
                sddb.cknngtSirkL = timemanager.jst2utc_date(datetime.datetime.strptime(cknngtSirkL, "%Y/%m/%d"))
            else:
                sddb.cknngtSirkL = timemanager.jst2utc_date(datetime.datetime.strptime(cknngtSirkL, "%Y/%m/%d %H:%M:%S"))
        else:
            sddb.cknngtSirkL = None
        sddb.put()

        # 地上階層
        cjyuKisouL = self.request.get("cjyuKisouL")
        if cjyuKisouL:
            sddb.cjyuKisouL = float(cjyuKisouL)
        else:
            sddb.cjyuKisouL = None

        cjyuKisouU = self.request.get("cjyuKisouU")
        if cjyuKisouU:
            sddb.cjyuKisouU = float(cjyuKisouU)
        else:
            sddb.cjyuKisouU = None

        # 所在階
        shzikiL = self.request.get("shzikiL")
        if shzikiL:
            sddb.shzikiL = float(shzikiL)
        else:
            sddb.shzikiL = None

        shzikiU = self.request.get("shzikiU")
        if shzikiU:
            sddb.shzikiU = float(shzikiU)
        else:
            sddb.shzikiU = None

        # １階
        floor1 = self.request.get("floor1")
        if floor1 == "1":
            sddb.floor1 = True
        else:
            sddb.floor1 = None

        # 最上階
        topfloor = self.request.get("topfloor")
        if topfloor == "1":
            sddb.topfloor = True
        else:
            sddb.topfloor = None
        sddb.put()

        msgid = self.request.get("msgid", None)
        if msgid:
            bklistutl.remalllistbyID(self.corp_name, self.branch_name, msgid)
        msgkey = self.request.get("msgkey")
        if msgkey:
            bklistutl.remalllistbykey(self.corp_name, self.branch_name, msgkey)
            msgid = messageManager.getmesbyID(self.corp_name, msgkey).key.id()
        kindname = self.request.get("kindname")
        if not kindname:
            kindname = "検索"

        if submit == "検索" or submit == "search" or submit == "新規ページへ保存して検索":
            list = bksearchutl.do_searchdb(sddb)
            return bksearchutl.addlist(self.corp_name, sddb.member, '検索', list, body=sddb.name)

        if submit == "検索2" or submit == "search2" or submit == "新規ページへ保存して検索2":
            msgkey = messageManager.post(
                corp=self.corp_name,
                sub="検索中",
                body="",
                done=False,
                memfrom=self.memberID,
                kindname=kindname,
                combkind="所有",
                msgkey=msgid,
                reservation=None,
                reservationend=None,
                memto=None,
                commentto=None,
                mailto=None,
                htmlmail=None
            )
            list = bksearchutl.do_searchdb2(sddb, msgkey)
            return msgkey.id()

        if submit == "検索3" or submit == "search3" or submit == "新規ページへ保存して検索3":
            msgid = self.request.get("msgid", None)
            if msgid:
                bklistutl.remalllistbyID(self.corp_name, self.branch_name, msgid)
            msgkey = self.request.get("msgkey")
            if msgkey:
                bklistutl.remalllistbykey(self.corp_name, self.branch_name, msgkey)
                msgid = messageManager.getmesbyID(self.corp_name, msgkey).key.id()
            kindname = self.request.get("kindname")
            if not kindname:
                kindname = "検索"
            msgkey = messageManager.post(
                corp=self.corp_name,
                sub="検索中",
                body="",
                done=False,
                memfrom=self.memberID,
                kindname=kindname,
                combkind="所有",
                msgkey=msgid,
                reservation=None,
                reservationend=None,
                memto=None,
                commentto=None,
                mailto=None,
                htmlmail=None
            )
            list = bksearchutl.do_searchdb4(sddb, msgkey)
            return msgkey.id()

        if submit == "全ページ一括検索" or submit == "allpagesearch":
            msgkey = messageManager.post(
                corp=self.corp_name,
                sub="一括検索中",
                body="",
                done=False,
                memfrom=self.memberID,
                kindname=kindname,
                combkind="所有",
                msgkey=msgid,
                reservation=None,
                reservationend=None,
                memto=None,
                commentto=None,
                mailto=None,
                htmlmail=None
            )
            list = bksearchutl.do_allsearch(mmdb, msgkey)
            return msgkey.id()

        if submit == "全ページ一括検索2" or submit == "allpagesearch2":
            list = bksearchutl.do_allsearch2(mmdb)
            return bksearchutl.addlist(self.corp_name, mmdb, '全ページ一括検索', list)

        return kwargs
