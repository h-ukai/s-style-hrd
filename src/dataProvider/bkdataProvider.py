#!/usr/local/bin/python
# -*- coding: utf-8 -*-

from application.models import bkdata
from application.models import CorpOrg
from application.models import Branch
import datetime
import re
from application import timemanager
from google.appengine.ext import db

class bkdataProvider():
    def __init__(self,co,br,us=None):
        self.corp_name=co
        self.branch_name = br
        self.cknngtSirkYY = None
        self.zukickNngt1YY = None
        self.zukickNngt2YY = None
        self.zukickNngt3YY = None
        self.bkdb = None
        self.blobs = None
        self.user = None
        if us:
            self.user = us

    def search(self,bkID=None):
        if bkID:
            key_name = self.corp_name + u"/" + self.branch_name + u"/" + bkID
            bkd = bkdata.BKdata.get_by_key_name(key_name)
            if bkd:
                self.bkdb = timemanager.utc2jst_gql(bkd)

                query_str = u"SELECT * FROM Blob WHERE CorpOrg_key = '" + self.corp_name + u"' AND Branch_Key = '" + self.branch_name + u"' AND bkID = '" + bkID + u"' ORDER BY  media, pos ASC"
                self.blobs = db.GqlQuery (query_str)

                if self.bkdb.cknngtSirk:
                    self.cknngtSirkYY = self.bkdb.cknngtSirk.year
                if self.bkdb.zukickNngt1:
                    self.zukickNngt1YY = self.bkdb.zukickNngt1.year
                if self.bkdb.zukickNngt2:
                    self.zukickNngt2YY = self.bkdb.zukickNngt2.year
                if self.bkdb.zukickNngt3:
                    self.zukickNngt3YY = self.bkdb.zukickNngt3.year

    def set(self,bkID=None):
        if bkID:
            key_name = self.corp_name + u"/" + self.branch_name + u"/" + bkID
            self.bkdb = timemanager.utc2jst_gql(bkdata.BKdata.get_or_insert(key_name,bkID=bkID))

            query_str = u"SELECT * FROM Blob WHERE CorpOrg_key = '" + self.corp_name + u"' AND Branch_Key = '" + self.branch_name + u"' AND bkID = '" + bkID + u"' ORDER BY  media, pos ASC"
            self.blobs = db.GqlQuery (query_str)

            if self.bkdb.cknngtSirk:
                self.cknngtSirkYY = self.bkdb.cknngtSirk.year
            if self.bkdb.zukickNngt1:
                self.zukickNngt1YY = self.bkdb.zukickNngt1.year
            if self.bkdb.zukickNngt2:
                self.zukickNngt2YY = self.bkdb.zukickNngt2.year
            if self.bkdb.zukickNngt3:
                self.zukickNngt3YY = self.bkdb.zukickNngt3.year

    def put(self,req):
        #物件番号
        self.request=req
        bkID = self.request.get("bkID")
        if not bkID:
            br = Branch.Branch.get_or_insert(self.corp_name + "/" + self.branch_name)
            bkID = str(br.getNextNum())
        key_name = self.corp_name + "/" + self.branch_name + "/" + bkID
        bkdb = bkdata.BKdata.get_or_insert(key_name,bkID=bkID)
        bkdb.bkID = bkID

        #更新年月日
        ksnnngp = self.request.get("ksnnngp")
        if ksnnngp:
            r = re.compile(".*:.*:.*").match(ksnnngp, 1)
            if r == None:
                bkdb.ksnnngp = datetime.datetime.strptime(ksnnngp, "%Y/%m/%d")
            else:
                bkdb.ksnnngp = datetime.datetime.strptime(ksnnngp, "%Y/%m/%d %H:%M:%S")
        else:
            bkdb.ksnnngp = datetime.datetime.now()
        bkdb.ksnnngp = timemanager.jst2utc_date(bkdb.ksnnngp)
        #更新会社ID
        ksnkisID = self.request.get("ksnkisID")
        if ksnkisID:
            bkdb.ksnkisID = ksnkisID
        else:
            bkdb.ksnkisID = self.corp_name
        #更新支店ID
        ksnstnID = self.request.get("ksnstnID")
        if ksnstnID:
            bkdb.ksnstnID = ksnstnID
        else:
            bkdb.ksnstnID = self.branch_name
        #更新担当
        ksntnt = self.request.get("ksntnt")
        if ksntnt:
            bkdb.ksntnt = ksntnt
        elif self.user:
            bkdb.ksntnt = self.user
        else:
            bkdb.ksntnt = None
        #確認年月日
        kknnngp = self.request.get("kknnngp")
        if kknnngp:
            r = re.compile(".*:.*:.*").match(kknnngp, 1)
            if r == None:
                bkdb.kknnngp = datetime.datetime.strptime(kknnngp, "%Y/%m/%d")
            else:
                bkdb.kknnngp = datetime.datetime.strptime(kknnngp, "%Y/%m/%d %H:%M:%S")
        else:
            bkdb.kknnngp = datetime.datetime.now()
        bkdb.kknnngp = timemanager.jst2utc_date(bkdb.kknnngp)

        #学区
        gakku = self.request.get("gakku")
        if gakku:
            bkdb.gakku = []
            for s in gakku.split(","):
                if s != "":
                    bkdb.gakku.append(s)
        else:
            bkdb.gakku = []

        #ペット可
        ptflg = self.request.get("ptflg")
        if ptflg == "1":
            bkdb.ptflg = True
        else:
            bkdb.ptflg = False
        #マッチング可
        mtngflg = self.request.get("mtngflg")
        if mtngflg == "1":
            bkdb.mtngflg = True
        else:
            bkdb.mtngflg = False
        #広告可
        kukkk = self.request.get("kukkk")
        if kukkk == "1":
            bkdb.kukkk = True
        else:
            bkdb.kukkk = False
        #web検索許可
        webknskflg = self.request.get("webknskflg")
        if webknskflg == "1":
            bkdb.webknskflg = True
        else:
            bkdb.webknskflg = False
        #他業者可
        tgysyflg = self.request.get("tgysyflg")
        if tgysyflg == "1":
            bkdb.tgysyflg = True
        else:
            bkdb.tgysyflg = False
        #告知事項
        kktjkuflg = self.request.get("kktjkuflg")
        if kktjkuflg:
            bkdb.kktjkuflg = kktjkuflg
        else:
            bkdb.kktjkuflg = None

        #交渉可能価格
        #ksyknkkku = db.FloatProperty(verbose_name=u"交渉可能価格")
        ksyknkkku = self.request.get("ksyknkkku")
        if ksyknkkku:
            bkdb.ksyknkkku = float(ksyknkkku)
        else:
            bkdb.ksyknkkku = None

       #価格交渉可
       #kkkksyk = db.BooleanProperty(verbose_name=u"価格交渉可")
        kkkksyk = self.request.get("kkkksyk")
        if kkkksyk == '1':
            bkdb.kkkksyk  = True
        else:
            bkdb.kkkksyk = False

        #地図センター緯度経度
        center_lat = self.request.get("center_lat")
        center_lng = self.request.get("center_lng")
        if center_lat and center_lng :
            bkdb.chzsntidkd = center_lat + ',' + center_lng
        else:
            bkdb.chzsntidkd = None

        #緯度経度
        marker_lat = self.request.get("marker_lat")
        marker_lng = self.request.get("marker_lng")
        if marker_lat and marker_lng :
            bkdb.idkd =  marker_lat + ',' + marker_lng
        else:
            bkdb.idkd = None
        #地図レンジ
        chzrnj = self.request.get("chzrnj")
        if chzrnj:
            bkdb.chzrnj = int(chzrnj)
        else:
            bkdb.chzrnj = None
        #アイコン名
        icons = self.request.get("icons")
        if icons:
            bkdb.icons = []
            for s in icons.split(","):
                if s != "":
                    bkdb.icons.append(s)
        else:
            bkdb.icons = []

        #作成状況
        sksijky = self.request.get("sksijky")
        if sksijky:
            bkdb.sksijky = sksijky
        else:
            bkdb.sksijky = None
        #至急送信
        skyssnflg = self.request.get("skyssnflg")
        if skyssnflg == "1":
            bkdb.skyssnflg = True
        else:
            bkdb.skyssnflg = False
        #自動ポイント
        zdupint = self.request.get("zdupint")
        if zdupint:
            bkdb.zdupint = float(zdupint)
        else:
            bkdb.zdupint = None
        #評価ポイント
        hykpint = self.request.get("hykpint")
        if hykpint:
            bkdb.hykpint = float(hykpint)
        else:
            bkdb.hykpint = None
        #入力会社ID
        nyrykkisyID = self.request.get("nyrykkisyID")
        if nyrykkisyID:
            bkdb.nyrykkisyID = nyrykkisyID
        else:
            bkdb.nyrykkisyID = self.corp_name

        #入力支店ID
        nyrykstnID = self.request.get("nyrykstnID")
        if nyrykstnID:
            bkdb.nyrykstnID = nyrykstnID
        else:
            bkdb.nyrykstnID = self.branch_name

        #入力担当
        nyryktnt = self.request.get("nyryktnt")
        if nyryktnt:
            bkdb.nyryktnt = nyryktnt
        elif self.user:
            bkdb.nyryktnt = self.user
        else:
            bkdb.nyryktnt = None
        #データソース
        dataSource = self.request.get("dataSource")
        if dataSource:
            bkdb.dataSource = dataSource
        else:
            bkdb.dataSource = None

        #データ元物件番号
        bknbng = self.request.get("bknbng")
        if bknbng:
            bkdb.bknbng = bknbng
        else:
            bkdb.bknbng = None
        #売買賃貸区分
        bbchntikbn = self.request.get("bbchntikbn")
        if bbchntikbn:
            bkdb.bbchntikbn = bbchntikbn
        else:
            bkdb.bbchntikbn = None
        #取扱い種類
        dtsyuri = self.request.get("dtsyuri")
        if dtsyuri:
            bkdb.dtsyuri = dtsyuri
        else:
            bkdb.dtsyuri = None
        #物件種別
        bkknShbt = self.request.get("bkknShbt")
        if bkknShbt:
            bkdb.bkknShbt = bkknShbt
        else:
            bkdb.bkknShbt = None
        #物件種目
        bkknShmk = self.request.get("bkknShmk")
        if bkknShmk:
            bkdb.bkknShmk = bkknShmk
        else:
            bkdb.bkknShmk = None
        #業者名
        kiinni = self.request.get("kiinni")
        if kiinni:
            bkdb.kiinni = kiinni
        else:
            bkdb.kiinni = None
        #代表電話番号
        dihyodnwbngu = self.request.get("dihyodnwbngu")
        if dihyodnwbngu:
            bkdb.dihyodnwbngu = dihyodnwbngu
        else:
            bkdb.dihyodnwbngu = None
        #問合せ担当者（1）
        tiawsTntush = self.request.get("tiawsTntush")
        if tiawsTntush:
            bkdb.tiawsTntush = tiawsTntush
        else:
            bkdb.tiawsTntush = None
        #問合せ電話番号（1）
        tiawsDnwBngu = self.request.get("tiawsDnwBngu")
        if tiawsDnwBngu:
            bkdb.tiawsDnwBngu = tiawsDnwBngu
        else:
            bkdb.tiawsDnwBngu = None
        #Eメールアドレス（1）
        emlAdrs = self.request.get("emlAdrs")
        if emlAdrs:
            bkdb.emlAdrs = emlAdrs
        else:
            bkdb.emlAdrs = None
        #図面
        zmn = self.request.get("zmn")
        if zmn:
            bkdb.zmn = zmn
        else:
            bkdb.zmn = None

        #レインス登録年月日
        turknngp = self.request.get("turknngp")
        #'2011-01-12 22:08:27+09:00'[:-6]
        if turknngp:
            r = re.compile(".*:.*:.*").match(turknngp, 1)
            if r == None:
                bkdb.turknngp = datetime.datetime.strptime(turknngp, "%Y/%m/%d")
            else:
                bkdb.turknngp = datetime.datetime.strptime(turknngp, "%Y/%m/%d %H:%M:%S")
            bkdb.turknngp = timemanager.jst2utc_date(bkdb.turknngp)


        #変更年月日
        hnknngp = self.request.get("hnknngp")
        if hnknngp:
            r = re.compile(".*:.*:.*").match(hnknngp, 1)
            if r == None:
                bkdb.hnknngp = datetime.datetime.strptime(hnknngp, "%Y/%m/%d")
            else:
                bkdb.hnknngp = datetime.datetime.strptime(hnknngp, "%Y/%m/%d %H:%M:%S")
        else:
            bkdb.hnknngp = datetime.datetime.now()
        bkdb.hnknngp = timemanager.jst2utc_date(bkdb.hnknngp)

        #取引条件の有効期限
        trhkJyuknYukuKgnGG = self.request.get("trhkJyuknYukuKgnGG")
        trhkJyuknYukuKgnYY = self.request.get("trhkJyuknYukuKgnYY")
        trhkJyuknYukuKgnMM = self.request.get("trhkJyuknYukuKgnMM")
        trhkJyuknYukuKgnDD = self.request.get("trhkJyuknYukuKgnDD")
        if trhkJyuknYukuKgnGG == "H" and trhkJyuknYukuKgnYY and trhkJyuknYukuKgnMM and trhkJyuknYukuKgnDD:
            bkdb.trhkJyuknYukuKgn = datetime.datetime.strptime(str(1988 + int(trhkJyuknYukuKgnYY )) + "/" + trhkJyuknYukuKgnMM + "/" + trhkJyuknYukuKgnDD,"%Y/%m/%d")
            bkdb.trhkJyuknYukuKgn = timemanager.jst2utc_date(bkdb.trhkJyuknYukuKgn)
        elif trhkJyuknYukuKgnGG == "R" and trhkJyuknYukuKgnYY and trhkJyuknYukuKgnMM and trhkJyuknYukuKgnDD:
            bkdb.trhkJyuknYukuKgn = datetime.datetime.strptime(str(2018 + int(trhkJyuknYukuKgnYY )) + "/" + trhkJyuknYukuKgnMM + "/" + trhkJyuknYukuKgnDD,"%Y/%m/%d")
            bkdb.trhkJyuknYukuKgn = timemanager.jst2utc_date(bkdb.trhkJyuknYukuKgn)
        else :
            bkdb.trhkJyuknYukuKgn = None


        #新築中古区分
        sntktyukkbn = self.request.get("sntktyukkbn")
        if sntktyukkbn:
            bkdb.sntktyukkbn = sntktyukkbn
        else:
            bkdb.sntktyukkbn = None
        #都道府県名
        tdufknmi = self.request.get("tdufknmi")
        if tdufknmi:
            bkdb.tdufknmi = tdufknmi
        else:
            bkdb.tdufknmi = None
        #所在地名1
        shzicmi1 = self.request.get("shzicmi1")
        if shzicmi1:
            bkdb.shzicmi1 = shzicmi1
        else:
            bkdb.shzicmi1 = None
        #所在地名2
        shzicmi2 = self.request.get("shzicmi2")
        if shzicmi2:
            bkdb.shzicmi2 = shzicmi2
        else:
            bkdb.shzicmi2 = None
        #所在地名3
        shzicmi3 = self.request.get("shzicmi3")
        if shzicmi3:
            bkdb.shzicmi3 = shzicmi3
        else:
            bkdb.shzicmi3 = None
        #建物名
        ttmnmi = self.request.get("ttmnmi")
        if ttmnmi:
            bkdb.ttmnmi = ttmnmi
        else:
            bkdb.ttmnmi = None
        #部屋番号
        hyBngu = self.request.get("hyBngu")
        if hyBngu:
            bkdb.hyBngu = hyBngu
        else:
            bkdb.hyBngu = None
        #その他所在地表示
        sntShzicHyuj = self.request.get("sntShzicHyuj")
        if sntShzicHyuj:
            bkdb.sntShzicHyuj = sntShzicHyuj
        else:
            bkdb.sntShzicHyuj = None
        #棟番号
        tuBngu = self.request.get("tuBngu")
        if tuBngu:
            bkdb.tuBngu = tuBngu
        else:
            bkdb.tuBngu = None
        #沿線略称（1）
        ensnmi1 = self.request.get("ensnmi1")
        if ensnmi1:
            bkdb.ensnmi1 = ensnmi1
        else:
            bkdb.ensnmi1 = None
        #
        ensnmi2 = self.request.get("ensnmi2")
        if ensnmi2:
            bkdb.ensnmi2 = ensnmi2
        else:
            bkdb.ensnmi2 = None
        #
        ensnmi3 = self.request.get("ensnmi3")
        if ensnmi3:
            bkdb.ensnmi3 = ensnmi3
        else:
            bkdb.ensnmi3 = None
        #駅名（1）
        ekmi1 = self.request.get("ekmi1")
        if ekmi1:
            bkdb.ekmi1 = ekmi1
        else:
            bkdb.ekmi1 = None
        #
        ekmi2 = self.request.get("ekmi2")
        if ekmi2:
            bkdb.ekmi2 = ekmi2
        else:
            bkdb.ekmi2 = None
        #
        ekmi3 = self.request.get("ekmi3")
        if ekmi3:
            bkdb.ekmi3 = ekmi3
        else:
            bkdb.ekmi3 = None
        #徒歩（分）1（1）
        thHn11 = self.request.get("thHn11")
        if thHn11:
            bkdb.thHn11 = float(thHn11)
        else:
            bkdb.thHn11 = None
        #
        thHn12 = self.request.get("thHn12")
        if thHn12:
            bkdb.thHn12 = float(thHn12)
        else:
            bkdb.thHn12 = None
        #
        thHn13 = self.request.get("thHn13")
        if thHn13:
            bkdb.thHn13 = float(thHn13)
        else:
            bkdb.thHn13 = None
        #徒歩（m）2（1）
        thM21 = self.request.get("thM21")
        if thM21:
            bkdb.thM21 = float(thM21)
        else:
            bkdb.thM21 = None
        #
        thM22 = self.request.get("thM22")
        if thM22:
            bkdb.thM22 = float(thM22)
        else:
            bkdb.thM22 = None
        #
        thM23 = self.request.get("thM23")
        if thM23:
            bkdb.thM23 = float(thM23)
        else:
            bkdb.thM23 = None
        #バス（1）
        bs1 = self.request.get("bs1")
        if bs1:
            bkdb.bs1 = bs1
        else:
            bkdb.bs1 = None
        #
        bs2 = self.request.get("bs2")
        if bs2:
            bkdb.bs2 = bs2
        else:
            bkdb.bs2 = None
        #
        bs3 = self.request.get("bs3")
        if bs3:
            bkdb.bs3 = bs3
        else:
            bkdb.bs3 = None
        #バス路線名（1）
        bsRsnmi1 = self.request.get("bsRsnmi1")
        if bsRsnmi1:
            bkdb.bsRsnmi1 = bsRsnmi1
        else:
            bkdb.bsRsnmi1 = None
        #
        bsRsnmi2 = self.request.get("bsRsnmi2")
        if bsRsnmi2:
            bkdb.bsRsnmi2 = bsRsnmi2
        else:
            bkdb.bsRsnmi2 = None
        #
        bsRsnmi3 = self.request.get("bsRsnmi3")
        if bsRsnmi3:
            bkdb.bsRsnmi3 = bsRsnmi3
        else:
            bkdb.bsRsnmi3 = None
        #バス停名称（1）
        bstiMishu1 = self.request.get("bstiMishu1")
        if bstiMishu1:
            bkdb.bstiMishu1 = bstiMishu1
        else:
            bkdb.bstiMishu1 = None
        #
        bstiMishu2 = self.request.get("bstiMishu2")
        if bstiMishu2:
            bkdb.bstiMishu2 = bstiMishu2
        else:
            bkdb.bstiMishu2 = None
        #
        bstiMishu3 = self.request.get("bstiMishu3")
        if bstiMishu3:
            bkdb.bstiMishu3 = bstiMishu3
        else:
            bkdb.bstiMishu3 = None
        #停歩（分）（1）
        tihHn1 = self.request.get("tihHn1")
        if tihHn1:
            bkdb.tihHn1 = float(tihHn1)
        else:
            bkdb.tihHn1 = None
        #
        tihHn2 = self.request.get("tihHn2")
        if tihHn2:
            bkdb.tihHn2 = float(tihHn2)
        else:
            bkdb.tihHn2 = None
        #
        tihHn3 = self.request.get("tihHn3")
        if tihHn3:
            bkdb.tihHn3 = float(tihHn3)
        else:
            bkdb.tihHn3 = None
        #停歩（m）（1）
        tihM1 = self.request.get("tihM1")
        if tihM1:
            bkdb.tihM1 = float(tihM1)
        else:
            bkdb.tihM1 = None
        #
        tihM2 = self.request.get("tihM2")
        if tihM2:
            bkdb.tihM2 = float(tihM2)
        else:
            bkdb.tihM2 = None
        #
        tihM3 = self.request.get("tihM3")
        if tihM3:
            bkdb.tihM3 = float(tihM3)
        else:
            bkdb.tihM3 = None
        #車（km）（1）
        krmKm1 = self.request.get("krmKm1")
        if krmKm1:
            bkdb.krmKm1 = float(krmKm1)
        else:
            bkdb.krmKm1 = None
        #
        krmKm2 = self.request.get("krmKm2")
        if krmKm2:
            bkdb.krmKm2 = float(krmKm2)
        else:
            bkdb.krmKm2 = None
        #
        krmKm3 = self.request.get("krmKm3")
        if krmKm3:
            bkdb.krmKm3 = float(krmKm3)
        else:
            bkdb.krmKm3 = None
        #

        #その他交通手段
        sntKutuShdn = self.request.get("sntKutuShdn")
        if sntKutuShdn:
            bkdb.sntKutuShdn = sntKutuShdn
        else:
            bkdb.sntKutuShdn = None
        #交通（分）1
        kutuHn = self.request.get("kutuHn")
        if kutuHn:
            bkdb.kutuHn = float(kutuHn)
        else:
            bkdb.kutuHn = None
        #交通（m）2
        kutuM = self.request.get("kutuM")
        if kutuM:
            bkdb.kutuM = float(kutuM)
        else:
            bkdb.kutuM = None
        #現況
        gnkyu = self.request.get("gnkyu")
        if gnkyu:
            bkdb.gnkyu = gnkyu
        else:
            bkdb.gnkyu = None
        #現況予定年月
        gnkyuYtiNngtGG = self.request.get("gnkyuYtiNngtGG")
        gnkyuYtiNngtYY = self.request.get("gnkyuYtiNngtYY")
        gnkyuYtiNngtMM = self.request.get("gnkyuYtiNngtMM")
        if gnkyuYtiNngtGG == "H" and gnkyuYtiNngtYY and gnkyuYtiNngtMM:
            bkdb.gnkyuYtiNngt = datetime.datetime.strptime(str(1988 + int(gnkyuYtiNngtYY)) + "/" + gnkyuYtiNngtMM,"%Y/%m")
            bkdb.gnkyuYtiNngt = timemanager.jst2utc_date(bkdb.gnkyuYtiNngt)
        elif gnkyuYtiNngtGG == "R" and gnkyuYtiNngtYY and gnkyuYtiNngtMM:
            bkdb.gnkyuYtiNngt = datetime.datetime.strptime(str(2018 + int(gnkyuYtiNngtYY)) + "/" + gnkyuYtiNngtMM,"%Y/%m")
            bkdb.gnkyuYtiNngt = timemanager.jst2utc_date(bkdb.gnkyuYtiNngt)
        else:
            bkdb.gnkyuYtiNngt = None
        #

        #

        #引渡時期
        hkwtsNyukyJk = self.request.get("hkwtsNyukyJk")
        if hkwtsNyukyJk:
            bkdb.hkwtsNyukyJk = hkwtsNyukyJk
        else:
            bkdb.hkwtsNyukyJk = None
        #引渡年月（西暦）
        hkwtsNyukyNngtSirkGG = self.request.get("hkwtsNyukyNngtSirkGG")
        hkwtsNyukyNngtSirkYY = self.request.get("hkwtsNyukyNngtSirkYY")
        hkwtsNyukyNngtSirkMM = self.request.get("hkwtsNyukyNngtSirkMM")
        if hkwtsNyukyNngtSirkGG == "H" and hkwtsNyukyNngtSirkYY and hkwtsNyukyNngtSirkMM:
            bkdb.hkwtsNyukyNngtSirk = datetime.datetime.strptime(str(1988 + int(hkwtsNyukyNngtSirkYY)) + "/" + hkwtsNyukyNngtSirkMM,"%Y/%m")
            bkdb.hkwtsNyukyNngtSirk = timemanager.jst2utc_date(bkdb.hkwtsNyukyNngtSirk)
        elif hkwtsNyukyNngtSirkGG == "R" and hkwtsNyukyNngtSirkYY and hkwtsNyukyNngtSirkMM:
            bkdb.hkwtsNyukyNngtSirk = datetime.datetime.strptime(str(2018 + int(hkwtsNyukyNngtSirkYY)) + "/" + hkwtsNyukyNngtSirkMM,"%Y/%m")
            bkdb.hkwtsNyukyNngtSirk = timemanager.jst2utc_date(bkdb.hkwtsNyukyNngtSirk)
        else:
            bkdb.hkwtsNyukyNngtSirk = None
        #

        #

        #引渡旬
        hkwtsNyukyShn = self.request.get("hkwtsNyukyShn")
        if hkwtsNyukyShn:
            bkdb.hkwtsNyukyShn = hkwtsNyukyShn
        else:
            bkdb.hkwtsNyukyShn = None
        #

        #

        #

        #入居日
        #入居年月（西暦）
        nyukyNngtSirkGG = self.request.get("nyukyNngtSirkGG")
        nyukyNngtSirkYY = self.request.get("nyukyNngtSirkYY")
        nyukyNngtSirkMM = self.request.get("nyukyNngtSirkMM")
        nyukyNngtSirkDD = self.request.get("nyukyNngtSirkDD")
        if nyukyNngtSirkGG == "H" and nyukyNngtSirkYY and nyukyNngtSirkMM and nyukyNngtSirkDD:
            bkdb.nyukyNngtSirk = datetime.datetime.strptime(str(1988 + int(nyukyNngtSirkYY )) + "/" + nyukyNngtSirkMM + "/" + nyukyNngtSirkDD,"%Y/%m/%d")
            bkdb.nyukyNngtSirk = timemanager.jst2utc_date(bkdb.nyukyNngtSirk)
        elif nyukyNngtSirkGG == "R" and nyukyNngtSirkYY and nyukyNngtSirkMM and nyukyNngtSirkDD:
            bkdb.nyukyNngtSirk = datetime.datetime.strptime(str(2018 + int(nyukyNngtSirkYY )) + "/" + nyukyNngtSirkMM + "/" + nyukyNngtSirkDD,"%Y/%m/%d")
            bkdb.nyukyNngtSirk = timemanager.jst2utc_date(bkdb.nyukyNngtSirk)
        else :
            bkdb.nyukyNngtSirk = None

        #取引態様
        trhktiyu = self.request.get("trhktiyu")
        if trhktiyu:
            bkdb.trhktiyu = trhktiyu
        else:
            bkdb.trhktiyu = None
        #報酬形態
        hushuKiti = self.request.get("hushuKiti")
        if hushuKiti:
            bkdb.hushuKiti = hushuKiti
        else:
            bkdb.hushuKiti = None
        #手数料割合率
        tsuryuWraiRt = self.request.get("tsuryuWraiRt")
        if tsuryuWraiRt:
            bkdb.tsuryuWraiRt = float(tsuryuWraiRt)
        else:
            bkdb.tsuryuWraiRt = None
        #手数料
        tsuryu = self.request.get("tsuryu")
        if tsuryu:
            bkdb.tsuryu = float(tsuryu)
        else:
            bkdb.tsuryu = None
        #価格
        kkkuCnryu = self.request.get("kkkuCnryu")
        if kkkuCnryu:
            bkdb.kkkuCnryu = float(kkkuCnryu)
        else:
            bkdb.kkkuCnryu = None
        #価格消費税
        kkkuCnryuShuhzi = self.request.get("kkkuCnryuShuhzi")
        if kkkuCnryuShuhzi:
            bkdb.kkkuCnryuShuhzi = float(kkkuCnryuShuhzi)
        else:
            bkdb.kkkuCnryuShuhzi = None
        #坪単価
        tbTnk = self.request.get("tbTnk")
        if tbTnk:
            bkdb.tbTnk = float(tbTnk)
        else:
            bkdb.tbTnk = None
        #㎡単価
        m2Tnk = self.request.get("m2Tnk")
        if m2Tnk:
            bkdb.m2Tnk = float(m2Tnk)
        else:
            bkdb.m2Tnk = None
        #想定利回り（％）
        sutiRmwrPrcnt = self.request.get("sutiRmwrPrcnt")
        if sutiRmwrPrcnt:
            bkdb.sutiRmwrPrcnt = float(sutiRmwrPrcnt)
        else:
            bkdb.sutiRmwrPrcnt = None
        #面積計測方式
        mnskKisokHusk = self.request.get("mnskKisokHusk")
        if mnskKisokHusk:
            bkdb.mnskKisokHusk = mnskKisokHusk
        else:
            bkdb.mnskKisokHusk = None
        #土地面積
        tcMnsk2 = self.request.get("tcMnsk2")
        if tcMnsk2:
            bkdb.tcMnsk2 = float(tcMnsk2)
        else:
            bkdb.tcMnsk2 = None
        #土地共有持分面積
        tcMcbnSumnsk = self.request.get("tcMcbnSumnsk")
        if tcMcbnSumnsk:
            bkdb.tcMcbnSumnsk = float(tcMcbnSumnsk)
        else:
            bkdb.tcMcbnSumnsk = None
        #土地共有持分（分子）
        tcMcbnBns = self.request.get("tcMcbnBns")
        if tcMcbnBns:
            bkdb.tcMcbnBns = float(tcMcbnBns)
        else:
            bkdb.tcMcbnBns = None
        #平米の場合

        #土地共有持分（分母）
        tcMcbnBnb = self.request.get("tcMcbnBnb")
        if tcMcbnBnb:
            bkdb.tcMcbnBnb = float(tcMcbnBnb)
        else:
            bkdb.tcMcbnBnb = None
        #平米の場合

        #建物面積1
        ttmnMnsk1 = self.request.get("ttmnMnsk1")
        if ttmnMnsk1:
            bkdb.ttmnMnsk1 = float(ttmnMnsk1)
        else:
            bkdb.ttmnMnsk1 = None
        #
        ttmnMnsk2 = self.request.get("ttmnMnsk2")
        if ttmnMnsk2:
            bkdb.ttmnMnsk2 = float(ttmnMnsk2)
        else:
            bkdb.ttmnMnsk2 = None
        #専有面積
        snyuMnskSyuBbnMnsk2 = self.request.get("snyuMnskSyuBbnMnsk2")
        if snyuMnskSyuBbnMnsk2:
            bkdb.snyuMnskSyuBbnMnsk2 = float(snyuMnskSyuBbnMnsk2)
        else:
            bkdb.snyuMnskSyuBbnMnsk2 = None
        #私道負担有無
        sduFtnUm = self.request.get("sduFtnUm")
        if sduFtnUm:
            bkdb.sduFtnUm = sduFtnUm
        else:
            bkdb.sduFtnUm = None
        #私道面積
        sduMnsk = self.request.get("sduMnsk")
        if sduMnsk:
            bkdb.sduMnsk = float(sduMnsk)
        else:
            bkdb.sduMnsk = None
        #バルコニー（テラス）面積
        blcnyTrsMnsk = self.request.get("blcnyTrsMnsk")
        if blcnyTrsMnsk:
            bkdb.blcnyTrsMnsk = float(blcnyTrsMnsk)
        else:
            bkdb.blcnyTrsMnsk = None
        #専用庭面積
        snyouNwMnsk = self.request.get("snyouNwMnsk")
        if snyouNwMnsk:
            bkdb.snyouNwMnsk = float(snyouNwMnsk)
        else:
            bkdb.snyouNwMnsk = None
        #セットバック区分
        stbkKbn = self.request.get("stbkKbn")
        if stbkKbn:
            bkdb.stbkKbn = stbkKbn
        else:
            bkdb.stbkKbn = None
        #後退距離（m）
        kutiKyrM = self.request.get("kutiKyrM")
        if kutiKyrM:
            bkdb.kutiKyrM = float(kutiKyrM)
        else:
            bkdb.kutiKyrM = None
        #セットバック面積（㎡）
        stbkMnskM2 = self.request.get("stbkMnskM2")
        if stbkMnskM2:
            bkdb.stbkMnskM2 = float(stbkMnskM2)
        else:
            bkdb.stbkMnskM2 = None
        #開発面積／総面積
        kihtMnskSumnsk = self.request.get("kihtMnskSumnsk")
        if kihtMnskSumnsk:
            bkdb.kihtMnskSumnsk = float(kihtMnskSumnsk)
        else:
            bkdb.kihtMnskSumnsk = None
        #販売総面積
        hnbiSumnsk = self.request.get("hnbiSumnsk")
        if hnbiSumnsk:
            bkdb.hnbiSumnsk = float(hnbiSumnsk)
        else:
            bkdb.hnbiSumnsk = None
        #販売区画数
        hnbiKkksu = self.request.get("hnbiKkksu")
        if hnbiKkksu:
            bkdb.hnbiKkksu = float(hnbiKkksu)
        else:
            bkdb.hnbiKkksu = None
        #工事完了年月（西暦）
        kujKnryuNngtSirkGG = self.request.get("kujKnryuNngtSirkGG")
        kujKnryuNngtSirkYY = self.request.get("kujKnryuNngtSirkYY")
        kujKnryuNngtSirkMM = self.request.get("kujKnryuNngtSirkMM")
        if kujKnryuNngtSirkGG == "H" and kujKnryuNngtSirkYY and kujKnryuNngtSirkMM:
            bkdb.kujKnryuNngtSirk = datetime.datetime.strptime(str(1988 + int(kujKnryuNngtSirkYY)) + "/" + kujKnryuNngtSirkMM,"%Y/%m")
            bkdb.kujKnryuNngtSirk = timemanager.jst2utc_date(bkdb.kujKnryuNngtSirk)
        elif kujKnryuNngtSirkGG == "R" and kujKnryuNngtSirkYY and kujKnryuNngtSirkMM:
            bkdb.kujKnryuNngtSirk = datetime.datetime.strptime(str(2018 + int(kujKnryuNngtSirkYY)) + "/" + kujKnryuNngtSirkMM,"%Y/%m")
            bkdb.kujKnryuNngtSirk = timemanager.jst2utc_date(bkdb.kujKnryuNngtSirk)
        else:
            bkdb.kujKnryuNngtSirk = None


        #建築面積
        knckMnsk = self.request.get("knckMnsk")
        if knckMnsk:
            bkdb.knckMnsk = float(knckMnsk)
        else:
            bkdb.knckMnsk = None
        #
        #
        #延べ面積
        nbMnsk = self.request.get("nbMnsk")
        if nbMnsk:
            bkdb.nbMnsk = float(nbMnsk)
        else:
            bkdb.nbMnsk = None
        #敷地延長の有無
        skcEnchuUm = self.request.get("skcEnchuUm")
        if skcEnchuUm:
            bkdb.skcEnchuUm = skcEnchuUm
        else:
            bkdb.skcEnchuUm = None
        #敷地延長（30%以上表示）
        skcEnchu30PrcntIjyuHyuj = self.request.get("skcEnchu30PrcntIjyuHyuj")
        if skcEnchu30PrcntIjyuHyuj:
            bkdb.skcEnchu30PrcntIjyuHyuj = float(skcEnchu30PrcntIjyuHyuj)
        else:
            bkdb.skcEnchu30PrcntIjyuHyuj = None
        #借地料
        shkcryu = self.request.get("shkcryu")
        if shkcryu:
            bkdb.shkcryu = float(shkcryu)
        else:
            bkdb.shkcryu = None
        #借地期間
        #shkcKknYY
        shkcKknYY = self.request.get("shkcKknYY")
        if shkcKknYY:
            bkdb.shkcKknYY = float(shkcKknYY)
        else:
            bkdb.shkcKknYY = None
        #
        #shkcKknMM
        shkcKknMM = self.request.get("shkcKknMM")
        if shkcKknMM:
            bkdb.shkcKknMM = float(shkcKknMM)
        else:
            bkdb.shkcKknMM = None
        #借地期限（西暦）


        shkcKgnSirkGG = self.request.get("shkcKgnSirkGG")
        shkcKgnSirkYY = self.request.get("shkcKgnSirkYY")
        shkcKgnSirkMM = self.request.get("shkcKgnSirkMM")
        if shkcKgnSirkGG == "H" and shkcKgnSirkYY and shkcKgnSirkMM:
            bkdb.shkcKgnSirk = datetime.datetime.strptime(str(1988 + int(shkcKgnSirkYY)) + "/" + shkcKgnSirkMM,"%Y/%m")
            bkdb.shkcKgnSirk = timemanager.jst2utc_date(bkdb.shkcKgnSirk)
        elif shkcKgnSirkGG == "R" and shkcKgnSirkYY and shkcKgnSirkMM:
            bkdb.shkcKgnSirk = datetime.datetime.strptime(str(2018 + int(shkcKgnSirkYY)) + "/" + shkcKgnSirkMM,"%Y/%m")
            bkdb.shkcKgnSirk = timemanager.jst2utc_date(bkdb.shkcKgnSirk)
        else:
            bkdb.shkcKgnSirk = None


        #施設費用項目（1）
        sstHyuKumk1 = self.request.get("sstHyuKumk1")
        if sstHyuKumk1:
            bkdb.sstHyuKumk1 = sstHyuKumk1
        else:
            bkdb.sstHyuKumk1 = None
        #
        sstHyuKumk2 = self.request.get("sstHyuKumk2")
        if sstHyuKumk2:
            bkdb.sstHyuKumk2 = sstHyuKumk2
        else:
            bkdb.sstHyuKumk2 = None
        #
        sstHyuKumk3 = self.request.get("sstHyuKumk3")
        if sstHyuKumk3:
            bkdb.sstHyuKumk3 = sstHyuKumk3
        else:
            bkdb.sstHyuKumk3 = None
        #施設費用（1）
        sstHyu1 = self.request.get("sstHyu1")
        if sstHyu1:
            bkdb.sstHyu1 = float(sstHyu1)
        else:
            bkdb.sstHyu1 = None
        #
        sstHyu2 = self.request.get("sstHyu2")
        if sstHyu2:
            bkdb.sstHyu2 = float(sstHyu2)
        else:
            bkdb.sstHyu2 = None
        #
        sstHyu3 = self.request.get("sstHyu3")
        if sstHyu3:
            bkdb.sstHyu3 = float(sstHyu3)
        else:
            bkdb.sstHyu3 = None
        #国土法届出
        kkdhuTdkd = self.request.get("kkdhuTdkd")
        if kkdhuTdkd:
            bkdb.kkdhuTdkd = kkdhuTdkd
        else:
            bkdb.kkdhuTdkd = None
        #登記簿地目
        tukbCmk = self.request.get("tukbCmk")
        if tukbCmk:
            bkdb.tukbCmk = tukbCmk
        else:
            bkdb.tukbCmk = None
        #現況地目
        gnkyuCmk = self.request.get("gnkyuCmk")
        if gnkyuCmk:
            bkdb.gnkyuCmk = gnkyuCmk
        else:
            bkdb.gnkyuCmk = None
        #都市計画
        tskikk = self.request.get("tskikk")
        if tskikk:
            bkdb.tskikk = tskikk
        else:
            bkdb.tskikk = None
        #用途地域（1）
        yutCik1 = self.request.get("yutCik1")
        if yutCik1:
            bkdb.yutCik1 = yutCik1
        else:
            bkdb.yutCik1 = None
        #用途地域（2）
        yutCik2 = self.request.get("yutCik2")
        if yutCik2:
            bkdb.yutCik2 = yutCik2
        else:
            bkdb.yutCik2 = None
        #最適用途
        sitkYut = self.request.get("sitkYut")
        if sitkYut:
            bkdb.sitkYut = sitkYut
        else:
            bkdb.sitkYut = None
        #建ぺい率
        knpirt = self.request.get("knpirt")
        if knpirt:
            bkdb.knpirt = float(knpirt)
        else:
            bkdb.knpirt = None
        #容積率
        yuskrt = self.request.get("yuskrt")
        if yuskrt:
            bkdb.yuskrt = float(yuskrt)
        else:
            bkdb.yuskrt = None
        #地域地区
        cikCk = self.request.get("cikCk")
        if cikCk:
            bkdb.cikCk = cikCk
        else:
            bkdb.cikCk = None
        #土地権利
        tcKenr = self.request.get("tcKenr")
        if tcKenr:
            bkdb.tcKenr = tcKenr
        else:
            bkdb.tcKenr = None
        #付帯権利
        ftiKenr = self.request.get("ftiKenr")
        if ftiKenr:
            bkdb.ftiKenr = ftiKenr
        else:
            bkdb.ftiKenr = None
        #造作譲渡金
        zusJyutkn = self.request.get("zusJyutkn")
        if zusJyutkn:
            bkdb.zusJyutkn = float(zusJyutkn)
        else:
            bkdb.zusJyutkn = None
        #定借権利金
        tishkKenrkn = self.request.get("tishkKenrkn")
        if tishkKenrkn:
            bkdb.tishkKenrkn = float(tishkKenrkn)
        else:
            bkdb.tishkKenrkn = None
        #定借保証金
        tishkHshukn = self.request.get("tishkHshukn")
        if tishkHshukn:
            bkdb.tishkHshukn = float(tishkHshukn)
        else:
            bkdb.tishkHshukn = None
        #定借敷金
        tishkSkkn = self.request.get("tishkSkkn")
        if tishkSkkn:
            bkdb.tishkSkkn = float(tishkSkkn)
        else:
            bkdb.tishkSkkn = None
        #地勢
        csi = self.request.get("csi")
        if csi:
            bkdb.csi = csi
        else:
            bkdb.csi = None
        #建築条件
        knckJyukn = self.request.get("knckJyukn")
        if knckJyukn:
            bkdb.knckJyukn = knckJyukn
        else:
            bkdb.knckJyukn = u"無"
        #オーナーチェンジ
        ornrChng = self.request.get("ornrChng")
        if ornrChng:
            bkdb.ornrChng = ornrChng
        else:
            bkdb.ornrChng = None
        #管理組合有無
        knrKmaiUm = self.request.get("knrKmaiUm")
        if knrKmaiUm:
            bkdb.knrKmaiUm = knrKmaiUm
        else:
            bkdb.knrKmaiUm = None
        #管理形態
        knrKiti = self.request.get("knrKiti")
        if knrKiti:
            bkdb.knrKiti = knrKiti
        else:
            bkdb.knrKiti = None
        #管理会社名
        knrKishmi = self.request.get("knrKishmi")
        if knrKishmi:
            bkdb.knrKishmi = knrKishmi
        else:
            bkdb.knrKishmi = None
        #管理人状況
        knrnnJyukyu = self.request.get("knrnnJyukyu")
        if knrnnJyukyu:
            bkdb.knrnnJyukyu = knrnnJyukyu
        else:
            bkdb.knrnnJyukyu = None
        #管理費
        knrh = self.request.get("knrh")
        if knrh:
            bkdb.knrh = float(knrh)
        else:
            bkdb.knrh = None
        #管理費消費税
        knrhShuhzi = self.request.get("knrhShuhzi")
        if knrhShuhzi:
            bkdb.knrhShuhzi = float(knrhShuhzi)
        else:
            bkdb.knrhShuhzi = None
        #修繕積立金
        shznTmttkn = self.request.get("shznTmttkn")
        if shznTmttkn:
            bkdb.shznTmttkn = float(shznTmttkn)
        else:
            bkdb.shznTmttkn = None
        #その他月額費名称1
        sntGtgkhMishu1 = self.request.get("sntGtgkhMishu1")
        if sntGtgkhMishu1:
            bkdb.sntGtgkhMishu1 = sntGtgkhMishu1
        else:
            bkdb.sntGtgkhMishu1 = None
        #
        sntGtgkhMishu2 = self.request.get("sntGtgkhMishu2")
        if sntGtgkhMishu2:
            bkdb.sntGtgkhMishu2 = sntGtgkhMishu2
        else:
            bkdb.sntGtgkhMishu2 = None
        #その他月額費用金額1
        sntGtgkHyuKngk1 = self.request.get("sntGtgkHyuKngk1")
        if sntGtgkHyuKngk1:
            bkdb.sntGtgkHyuKngk1 = float(sntGtgkHyuKngk1)
        else:
            bkdb.sntGtgkHyuKngk1 = None
        #
        sntGtgkHyuKngk2 = self.request.get("sntGtgkHyuKngk2")
        if sntGtgkHyuKngk2:
            bkdb.sntGtgkHyuKngk2 = float(sntGtgkHyuKngk2)
        else:
            bkdb.sntGtgkHyuKngk2 = None
        #施主
        ssh = self.request.get("ssh")
        if ssh:
            bkdb.ssh = ssh
        else:
            bkdb.ssh = None
        #施工会社名
        skuKishmi = self.request.get("skuKishmi")
        if skuKishmi:
            bkdb.skuKishmi = skuKishmi
        else:
            bkdb.skuKishmi = None
        #分譲会社名
        bnjyuKishmi = self.request.get("bnjyuKishmi")
        if bnjyuKishmi:
            bkdb.bnjyuKishmi = bnjyuKishmi
        else:
            bkdb.bnjyuKishmi = None
        #一括下請負人
        ikktStukoinn = self.request.get("ikktStukoinn")
        if ikktStukoinn:
            bkdb.ikktStukoinn = ikktStukoinn
        else:
            bkdb.ikktStukoinn = None
        #接道状況
        stduJyukyu = self.request.get("stduJyukyu")
        if stduJyukyu:
            bkdb.stduJyukyu = stduJyukyu
        else:
            bkdb.stduJyukyu = None
        #接道種別1
        stduShbt1 = self.request.get("stduShbt1")
        if stduShbt1:
            bkdb.stduShbt1 = stduShbt1
        else:
            bkdb.stduShbt1 = None
        #接道接面1
        stduStmn1 = self.request.get("stduStmn1")
        if stduStmn1:
            bkdb.stduStmn1 = stduStmn1
        else:
            bkdb.stduStmn1 = None
        #接道位置指定1
        stduIcSti1 = self.request.get("stduIcSti1")
        if stduIcSti1:
            bkdb.stduIcSti1 = stduIcSti1
        else:
            bkdb.stduIcSti1 = None
        #接道方向1
        stduHuku1 = self.request.get("stduHuku1")
        if stduHuku1:
            bkdb.stduHuku1 = stduHuku1
        else:
            bkdb.stduHuku1 = None
        #接道幅員1
        stduFkin1 = self.request.get("stduFkin1")
        if stduFkin1:
            bkdb.stduFkin1 = float(stduFkin1)
        else:
            bkdb.stduFkin1 = None
        #接道種別2
        stduShbt2 = self.request.get("stduShbt2")
        if stduShbt2:
            bkdb.stduShbt2 = stduShbt2
        else:
            bkdb.stduShbt2 = None
        #接道接面2
        stduStmn2 = self.request.get("stduStmn2")
        if stduStmn2:
            bkdb.stduStmn2 = float(stduStmn2)
        else:
            bkdb.stduStmn2 = None
        #接道位置指定2
        stduIcSti2 = self.request.get("stduIcSti2")
        if stduIcSti2:
            bkdb.stduIcSti2 = stduIcSti2
        else:
            bkdb.stduIcSti2 = None
        #接道方向2
        stduHuku2 = self.request.get("stduHuku2")
        if stduHuku2:
            bkdb.stduHuku2 = stduHuku2
        else:
            bkdb.stduHuku2 = None
        #接道幅員2
        stduFkin2 = self.request.get("stduFkin2")
        if stduFkin2:
            bkdb.stduFkin2 = float(stduFkin2)
        else:
            bkdb.stduFkin2 = None
        #接道種別3
        stduShbt3 = self.request.get("stduShbt3")
        if stduShbt3:
            bkdb.stduShbt3 = stduShbt3
        else:
            bkdb.stduShbt3 = None
        #接道接面3
        stduStmn3 = self.request.get("stduStmn3")
        if stduStmn3:
            bkdb.stduStmn3 = float(stduStmn3)
        else:
            bkdb.stduStmn3 = None
        #接道位置指定3
        stduIcSti3 = self.request.get("stduIcSti3")
        if stduIcSti3:
            bkdb.stduIcSti3 = stduIcSti3
        else:
            bkdb.stduIcSti3 = None
        #接道方向3
        stduHuku3 = self.request.get("stduHuku3")
        if stduHuku3:
            bkdb.stduHuku3 = stduHuku3
        else:
            bkdb.stduHuku3 = None
        #接道幅員3
        stduFkin3 = self.request.get("stduFkin3")
        if stduFkin3:
            bkdb.stduFkin3 = float(stduFkin3)
        else:
            bkdb.stduFkin3 = None
        #接道種別4
        stduShbt4 = self.request.get("stduShbt4")
        if stduShbt4:
            bkdb.stduShbt4 = stduShbt4
        else:
            bkdb.stduShbt4 = None
        #接道接面4
        stduStmn4 = self.request.get("stduStmn4")
        if stduStmn4:
            bkdb.stduStmn4 = float(stduStmn4)
        else:
            bkdb.stduStmn4 = None
        #接道位置指定4
        stduIcSti4 = self.request.get("stduIcSti4")
        if stduIcSti4:
            bkdb.stduIcSti4 = stduIcSti4
        else:
            bkdb.stduIcSti4 = None
        #接道方向4
        stduHuku4 = self.request.get("stduHuku4")
        if stduHuku4:
            bkdb.stduHuku4 = stduHuku4
        else:
            bkdb.stduHuku4 = None
        #接道幅員4
        stduFkin4 = self.request.get("stduFkin4")
        if stduFkin4:
            bkdb.stduFkin4 = float(stduFkin4)
        else:
            bkdb.stduFkin4 = None
        #接道舗装
        stduHsu = self.request.get("stduHsu")
        if stduHsu:
            bkdb.stduHsu = stduHsu
        else:
            bkdb.stduHsu = None
        #間取タイプ（1）
        mdrTyp1 = self.request.get("mdrTyp1")
        if mdrTyp1:
            bkdb.mdrTyp1 = mdrTyp1
        else:
            bkdb.mdrTyp1 = None
        #間取部屋数（1）
        mdrHysu1 = self.request.get("mdrHysu1")
        if mdrHysu1:
            bkdb.mdrHysu1 = float(mdrHysu1)
        else:
            bkdb.mdrHysu1 = None
        #部屋位置

        #納戸数
        nuKsu1 = self.request.get("nuKsu1")
        if nuKsu1:
            bkdb.nuKsu1 = float(nuKsu1)
        else:
            bkdb.nuKsu1 = None
        #室所在階1（1）
        stShziki11 = self.request.get("stShziki11")
        if stShziki11:
            bkdb.stShziki11 = float(stShziki11)
        else:
            bkdb.stShziki11 = None
        #室タイプ1（1）
        stTyp11 = self.request.get("stTyp11")
        if stTyp11:
            bkdb.stTyp11 = stTyp11
        else:
            bkdb.stTyp11 = None
        #室広さ1（1）
        stHrs11 = self.request.get("stHrs11")
        if stHrs11:
            bkdb.stHrs11 = float(stHrs11)
        else:
            bkdb.stHrs11 = None
        #室数1（1）
        stsu11 = self.request.get("stsu11")
        if stsu11:
            bkdb.stsu11 = float(stsu11)
        else:
            bkdb.stsu11 = None
        #室所在階2（1）
        stShziki21 = self.request.get("stShziki21")
        if stShziki21:
            bkdb.stShziki21 = float(stShziki21)
        else:
            bkdb.stShziki21 = None
        #室タイプ2（1）
        stTyp21 = self.request.get("stTyp21")
        if stTyp21:
            bkdb.stTyp21 = stTyp21
        else:
            bkdb.stTyp21 = None
        #室広さ2（1）
        stHrs21 = self.request.get("stHrs21")
        if stHrs21:
            bkdb.stHrs21 = float(stHrs21)
        else:
            bkdb.stHrs21 = None
        #室数2（1）
        stsu21 = self.request.get("stsu21")
        if stsu21:
            bkdb.stsu21 = float(stsu21)
        else:
            bkdb.stsu21 = None
        #室所在階3（1）
        stShziki31 = self.request.get("stShziki31")
        if stShziki31:
            bkdb.stShziki31 = float(stShziki31)
        else:
            bkdb.stShziki31 = None
        #室タイプ3（1）
        stTyp31 = self.request.get("stTyp31")
        if stTyp31:
            bkdb.stTyp31 = stTyp31
        else:
            bkdb.stTyp31 = None
        #室広さ3（1）
        stHrs31 = self.request.get("stHrs31")
        if stHrs31:
            bkdb.stHrs31 = float(stHrs31)
        else:
            bkdb.stHrs31 = None
        #室数3（1）
        stsu31 = self.request.get("stsu31")
        if stsu31:
            bkdb.stsu31 = float(stsu31)
        else:
            bkdb.stsu31 = None
        #室所在階4（1）
        stShziki41 = self.request.get("stShziki41")
        if stShziki41:
            bkdb.stShziki41 = float(stShziki41)
        else:
            bkdb.stShziki41 = None
        #室タイプ4（1）
        stTyp41 = self.request.get("stTyp41")
        if stTyp41:
            bkdb.stTyp41 = stTyp41
        else:
            bkdb.stTyp41 = None
        #室広さ4（1）
        stHrs41 = self.request.get("stHrs41")
        if stHrs41:
            bkdb.stHrs41 = float(stHrs41)
        else:
            bkdb.stHrs41 = None
        #室数4（1）
        stsu41 = self.request.get("stsu41")
        if stsu41:
            bkdb.stsu41 = float(stsu41)
        else:
            bkdb.stsu41 = None
        #室所在階5（1）
        stShziki51 = self.request.get("stShziki51")
        if stShziki51:
            bkdb.stShziki51 = float(stShziki51)
        else:
            bkdb.stShziki51 = None
        #室タイプ5（1）
        stTyp51 = self.request.get("stTyp51")
        if stTyp51:
            bkdb.stTyp51 = stTyp51
        else:
            bkdb.stTyp51 = None
        #室広さ5（1）
        stHrs51 = self.request.get("stHrs51")
        if stHrs51:
            bkdb.stHrs51 = float(stHrs51)
        else:
            bkdb.stHrs51 = None
        #室数5（1）
        stsu51 = self.request.get("stsu51")
        if stsu51:
            bkdb.stsu51 = float(stsu51)
        else:
            bkdb.stsu51 = None
        #室所在階6（1）
        stShziki61 = self.request.get("stShziki61")
        if stShziki61:
            bkdb.stShziki61 = float(stShziki61)
        else:
            bkdb.stShziki61 = None
        #室タイプ6（1）
        stTyp61 = self.request.get("stTyp61")
        if stTyp61:
            bkdb.stTyp61 = stTyp61
        else:
            bkdb.stTyp61 = None
        #室広さ6（1）
        stHrs61 = self.request.get("stHrs61")
        if stHrs61:
            bkdb.stHrs61 = float(stHrs61)
        else:
            bkdb.stHrs61 = None
        #室数6（1）
        stsu61 = self.request.get("stsu61")
        if stsu61:
            bkdb.stsu61 = float(stsu61)
        else:
            bkdb.stsu61 = None
        #室所在階7（1）
        stShziki71 = self.request.get("stShziki71")
        if stShziki71:
            bkdb.stShziki71 = float(stShziki71)
        else:
            bkdb.stShziki71 = None
        #室タイプ7（1）
        stTyp71 = self.request.get("stTyp71")
        if stTyp71:
            bkdb.stTyp71 = stTyp71
        else:
            bkdb.stTyp71 = None
        #室広さ7（1）
        stHrs71 = self.request.get("stHrs71")
        if stHrs71:
            bkdb.stHrs71 = float(stHrs71)
        else:
            bkdb.stHrs71 = None
        #室数7（1）
        stsu71 = self.request.get("stsu71")
        if stsu71:
            bkdb.stsu71 = float(stsu71)
        else:
            bkdb.stsu71 = None
        #間取りその他（1）
        mdrSnt1 = self.request.get("mdrSnt1")
        if mdrSnt1:
            bkdb.mdrSnt1 = mdrSnt1
        else:
            bkdb.mdrSnt1 = None
        #駐車場在否
        chushjyuZih = self.request.get("chushjyuZih")
        if chushjyuZih:
            bkdb.chushjyuZih = chushjyuZih
        else:
            bkdb.chushjyuZih = None
        #駐車場月額
        chushjyuGtgk = self.request.get("chushjyuGtgk")
        if chushjyuGtgk:
            bkdb.chushjyuGtgk = float(chushjyuGtgk)
        else:
            bkdb.chushjyuGtgk = None
        #駐車場月額消費税
        chushjyuGtgkShuhzi = self.request.get("chushjyuGtgkShuhzi")
        if chushjyuGtgkShuhzi:
            bkdb.chushjyuGtgkShuhzi = float(chushjyuGtgkShuhzi)
        else:
            bkdb.chushjyuGtgkShuhzi = None


        #駐車場敷金
        chushjyuSkknGk = self.request.get("chushjyuSkknGk")
        if chushjyuSkknGk:
            bkdb.chushjyuSkknGk = float(chushjyuSkknGk)
        else:
            bkdb.chushjyuSkknGk = None
        #駐車場敷金円ヶ月
        chushjyuSkknKgt = self.request.get("chushjyuSkknKgt")
        if chushjyuSkknKgt:
            bkdb.chushjyuSkknKgt = chushjyuSkknKgt
        else:
            bkdb.chushjyuSkknKgt = None
        #駐車場礼金
        chushjyuRiknGk = self.request.get("chushjyuRiknGk")
        if chushjyuRiknGk:
            bkdb.chushjyuRiknGk = float(chushjyuRiknGk)
        else:
            bkdb.chushjyuRiknGk = None
        #駐車場礼金円ヶ月
        chushjyuRiknKgt = self.request.get("chushjyuRiknKgt")
        if chushjyuRiknKgt:
            bkdb.chushjyuRiknKgt = chushjyuRiknKgt
        else:
            bkdb.chushjyuRiknKgt = None

        #建物構造
        ttmnKuzu = self.request.get("ttmnKuzu")
        if ttmnKuzu:
            bkdb.ttmnKuzu = ttmnKuzu
        else:
            bkdb.ttmnKuzu = None
        #建物工法
        ttmnKuhu = self.request.get("ttmnKuhu")
        if ttmnKuhu:
            bkdb.ttmnKuhu = ttmnKuhu
        else:
            bkdb.ttmnKuhu = None
        #建物形式
        ttmnKisk = self.request.get("ttmnKisk")
        if ttmnKisk:
            bkdb.ttmnKisk = ttmnKisk
        else:
            bkdb.ttmnKisk = None
        #地上階層
        cjyuKisou = self.request.get("cjyuKisou")
        if cjyuKisou:
            bkdb.cjyuKisou = float(cjyuKisou)
        else:
            bkdb.cjyuKisou = None
        #地下階層
        ckaKisou = self.request.get("ckaKisou")
        if ckaKisou:
            bkdb.ckaKisou = float(ckaKisou)
        else:
            bkdb.ckaKisou = None
        #所在階
        shziki = self.request.get("shziki")
        if shziki:
            bkdb.shziki = float(shziki)
        else:
            bkdb.shziki = None
        #築年月（西暦）
        cknngtSirkYY = self.request.get("cknngtSirkYY")
        cknngtSirkMM = self.request.get("cknngtSirkMM")
        if cknngtSirkYY and cknngtSirkMM:
            bkdb.cknngtSirk = datetime.datetime.strptime(cknngtSirkYY + "/" + cknngtSirkMM,"%Y/%m")
            bkdb.cknngtSirk = timemanager.jst2utc_date(bkdb.cknngtSirk)
        else:
            bkdb.cknngtSirk = None

        #総戸数
        suksu = self.request.get("suksu")
        if suksu:
            bkdb.suksu = float(suksu)
        else:
            bkdb.suksu = None
        #棟総戸数
        tuSuksu = self.request.get("tuSuksu")
        if tuSuksu:
            bkdb.tuSuksu = float(tuSuksu)
        else:
            bkdb.tuSuksu = None
        #連棟戸数
        rntuKsu = self.request.get("rntuKsu")
        if rntuKsu:
            bkdb.rntuKsu = float(rntuKsu)
        else:
            bkdb.rntuKsu = None
        #バルコニー方向（1）
        blcnyHuku1 = self.request.get("blcnyHuku1")
        if blcnyHuku1:
            bkdb.blcnyHuku1 = blcnyHuku1
        else:
            bkdb.blcnyHuku1 = None
        #
        blcnyHuku2 = self.request.get("blcnyHuku2")
        if blcnyHuku2:
            bkdb.blcnyHuku2 = blcnyHuku2
        else:
            bkdb.blcnyHuku2 = None
        #
        blcnyHuku3 = self.request.get("blcnyHuku3")
        if blcnyHuku3:
            bkdb.blcnyHuku3 = blcnyHuku3
        else:
            bkdb.blcnyHuku3 = None
        #増改築年月1
        zukickNngt1YY = self.request.get("zukickNngt1YY")
        zukickNngt1MM = self.request.get("zukickNngt1MM")
        if zukickNngt1YY and zukickNngt1MM:
            bkdb.zukickNngt1 = datetime.datetime.strptime(zukickNngt1YY + "/" + zukickNngt1MM,"%Y/%m")
            bkdb.zukickNngt1 = timemanager.jst2utc_date(bkdb.zukickNngt1)
        else:
            bkdb.zukickNngt1 = None
        #

        #増改築履歴1
        zukickRrk1 = self.request.get("zukickRrk1")
        if zukickRrk1:
            bkdb.zukickRrk1 = zukickRrk1
        else:
            bkdb.zukickRrk1 = None
        #増改築年月2
        zukickNngt2YY = self.request.get("zukickNngt2YY")
        zukickNngt2MM = self.request.get("zukickNngt2MM")
        if zukickNngt2YY and zukickNngt2MM:
            bkdb.zukickNngt2 = datetime.datetime.strptime(zukickNngt2YY + "/" + zukickNngt2MM,"%Y/%m")
            bkdb.zukickNngt2 = timemanager.jst2utc_date(bkdb.zukickNngt2)
        else:
            bkdb.zukickNngt2 = None
        #

        #増改築履歴2
        zukickRrk2 = self.request.get("zukickRrk2")
        if zukickRrk2:
            bkdb.zukickRrk2 = zukickRrk2
        else:
            bkdb.zukickRrk2 = None
        #増改築年月3
        zukickNngt3YY = self.request.get("zukickNngt3YY")
        zukickNngt3MM = self.request.get("zukickNngt3MM")
        if zukickNngt3YY and zukickNngt3MM:
            bkdb.zukickNngt3 = datetime.datetime.strptime(zukickNngt3YY + "/" + zukickNngt3MM,"%Y/%m")
            bkdb.zukickNngt3 = timemanager.jst2utc_date(bkdb.zukickNngt3)
        else:
            bkdb.zukickNngt3 = None
        #

        #増改築履歴3
        zukickRrk3 = self.request.get("zukickRrk3")
        if zukickRrk3:
            bkdb.zukickRrk3 = zukickRrk3
        else:
            bkdb.zukickRrk3 = None
        #
        #周辺環境1（フリー）
        shuhnKnkyu1Fre = self.request.get("shuhnKnkyu1Fre")
        if shuhnKnkyu1Fre:
            bkdb.shuhnKnkyu1Fre = shuhnKnkyu1Fre
        else:
            bkdb.shuhnKnkyu1Fre = None
        #距離1
        kyr1 = self.request.get("kyr1")
        if kyr1:
            bkdb.kyr1 = float(kyr1)
        else:
            bkdb.kyr1 = None
        #時間1
        jkn1 = self.request.get("jkn1")
        if jkn1:
            bkdb.jkn1 = float(jkn1)
        else:
            bkdb.jkn1 = None
        #周辺アクセス１
        shuhnAccs1 = self.request.get("shuhnAccs1")
        if shuhnAccs1:
            bkdb.shuhnAccs1 = shuhnAccs1
        else:
            bkdb.shuhnAccs1 = None
        #
        shuhnKnkyu2Fre = self.request.get("shuhnKnkyu2Fre")
        if shuhnKnkyu2Fre:
            bkdb.shuhnKnkyu2Fre = shuhnKnkyu2Fre
        else:
            bkdb.shuhnKnkyu2Fre = None
        #
        kyr2 = self.request.get("kyr2")
        if kyr2:
            bkdb.kyr2 = float(kyr2)
        else:
            bkdb.kyr2 = None
        #
        jkn2 = self.request.get("jkn2")
        if jkn2:
            bkdb.jkn2 = float(jkn2)
        else:
            bkdb.jkn2 = None
        #
        shuhnAccs2 = self.request.get("shuhnAccs2")
        if shuhnAccs2:
            bkdb.shuhnAccs2 = shuhnAccs2
        else:
            bkdb.shuhnAccs2 = None
        #
        shuhnKnkyu3Fre = self.request.get("shuhnKnkyu3Fre")
        if shuhnKnkyu3Fre:
            bkdb.shuhnKnkyu3Fre = shuhnKnkyu3Fre
        else:
            bkdb.shuhnKnkyu3Fre = None
        #
        kyr3 = self.request.get("kyr3")
        if kyr3:
            bkdb.kyr3 = float(kyr3)
        else:
            bkdb.kyr3 = None
        #
        jkn3 = self.request.get("jkn3")
        if jkn3:
            bkdb.jkn3 = float(jkn3)
        else:
            bkdb.jkn3 = None
        #
        shuhnAccs3 = self.request.get("shuhnAccs3")
        if shuhnAccs3:
            bkdb.shuhnAccs3 = shuhnAccs3
        else:
            bkdb.shuhnAccs3 = None
        #
        shuhnKnkyu4Fre = self.request.get("shuhnKnkyu4Fre")
        if shuhnKnkyu4Fre:
            bkdb.shuhnKnkyu4Fre = shuhnKnkyu4Fre
        else:
            bkdb.shuhnKnkyu4Fre = None
        #
        kyr4 = self.request.get("kyr4")
        if kyr4:
            bkdb.kyr4 = float(kyr4)
        else:
            bkdb.kyr4 = None
        #
        jkn4 = self.request.get("jkn4")
        if jkn4:
            bkdb.jkn4 = float(jkn4)
        else:
            bkdb.jkn4 = None
        #
        shuhnAccs4 = self.request.get("shuhnAccs4")
        if shuhnAccs4:
            bkdb.shuhnAccs4 = shuhnAccs4
        else:
            bkdb.shuhnAccs4 = None
        #
        shuhnKnkyu5Fre = self.request.get("shuhnKnkyu5Fre")
        if shuhnKnkyu5Fre:
            bkdb.shuhnKnkyu5Fre = shuhnKnkyu5Fre
        else:
            bkdb.shuhnKnkyu5Fre = None
        #
        kyr5 = self.request.get("kyr5")
        if kyr5:
            bkdb.kyr5 = float(kyr5)
        else:
            bkdb.kyr5 = None
        #
        jkn5 = self.request.get("jkn5")
        if jkn5:
            bkdb.jkn5 = float(jkn5)
        else:
            bkdb.jkn5 = None
        #
        shuhnAccs5 = self.request.get("shuhnAccs5")
        if shuhnAccs5:
            bkdb.shuhnAccs5 = shuhnAccs5
        else:
            bkdb.shuhnAccs5 = None
        #備考1
        bku1 = self.request.get("bku1")
        if bku1:
            bkdb.bku1 = bku1
        else:
            bkdb.bku1 = None
        #備考2
        bku2 = self.request.get("bku2")
        if bku2:
            bkdb.bku2 = bku2
        else:
            bkdb.bku2 = None
        #自社管理欄
        jshKnrrn = self.request.get("jshKnrrn")
        if jshKnrrn:
            bkdb.jshKnrrn = jshKnrrn
        else:
            bkdb.jshKnrrn = None
        #再建築不可フラグ
        siknckFkFlg = self.request.get("siknckFkFlg")
        if siknckFkFlg == "1":
            bkdb.siknckFkFlg = True
        else:
            bkdb.siknckFkFlg = False
        #
        #
        #<売地>

        #取引主任者
        trhkShnnsh = self.request.get("trhkShnnsh")
        if trhkShnnsh:
            bkdb.trhkShnnsh = trhkShnnsh
        else:
            bkdb.trhkShnnsh = None
        #容積率の制限内容
        yuskrtSignNiyu = self.request.get("yuskrtSignNiyu")
        if yuskrtSignNiyu:
            bkdb.yuskrtSignNiyu = yuskrtSignNiyu
        else:
            bkdb.yuskrtSignNiyu = None
        #その他の法令上の制限
        sntHurijyuSign = self.request.get("sntHurijyuSign")
        if sntHurijyuSign:
            bkdb.sntHurijyuSign = sntHurijyuSign
        else:
            bkdb.sntHurijyuSign = None
        #販売最小面積
        bnjyuTkcHnbiSishouMnsk = self.request.get("bnjyuTkcHnbiSishouMnsk")
        if bnjyuTkcHnbiSishouMnsk:
            bkdb.bnjyuTkcHnbiSishouMnsk = float(bnjyuTkcHnbiSishouMnsk)
        else:
            bkdb.bnjyuTkcHnbiSishouMnsk = None
        #販売最大面積
        bnjyuTkcHnbiSidiMnsk = self.request.get("bnjyuTkcHnbiSidiMnsk")
        if bnjyuTkcHnbiSidiMnsk:
            bkdb.bnjyuTkcHnbiSidiMnsk = float(bnjyuTkcHnbiSidiMnsk)
        else:
            bkdb.bnjyuTkcHnbiSidiMnsk = None
        #価格帯区画数
        bnjyuTkcKkkutiKsuKkksuFrom = self.request.get("bnjyuTkcKkkutiKsuKkksuFrom")
        if bnjyuTkcKkkutiKsuKkksuFrom:
            bkdb.bnjyuTkcKkkutiKsuKkksuFrom = float(bnjyuTkcKkkutiKsuKkksuFrom)
        else:
            bkdb.bnjyuTkcKkkutiKsuKkksuFrom = None
        bnjyuTkcKkkutiKsuKkksuTo = self.request.get("bnjyuTkcKkkutiKsuKkksuTo")
        if bnjyuTkcKkkutiKsuKkksuTo:
            bkdb.bnjyuTkcKkkutiKsuKkksuTo = float(bnjyuTkcKkkutiKsuKkksuTo)
        else:
            bkdb.bnjyuTkcKkkutiKsuKkksuTo = None
        #販売最低価格
        bnjyuTkcHnbiSitiKkku = self.request.get("bnjyuTkcHnbiSitiKkku")
        if bnjyuTkcHnbiSitiKkku:
            bkdb.bnjyuTkcHnbiSitiKkku = float(bnjyuTkcHnbiSitiKkku)
        else:
            bkdb.bnjyuTkcHnbiSitiKkku = None
        #販売最高価格
        bnjyuTkcHnbiSikuKkku = self.request.get("bnjyuTkcHnbiSikuKkku")
        if bnjyuTkcHnbiSikuKkku:
            bkdb.bnjyuTkcHnbiSikuKkku = float(bnjyuTkcHnbiSikuKkku)
        else:
            bkdb.bnjyuTkcHnbiSikuKkku = None
        #最多価格帯区画数
        bnjyuTkcSitKkkutiKsuKkksu = self.request.get("bnjyuTkcSitKkkutiKsuKkksu")
        if bnjyuTkcSitKkkutiKsuKkksu:
            bkdb.bnjyuTkcSitKkkutiKsuKkksu = float(bnjyuTkcSitKkkutiKsuKkksu)
        else:
            bkdb.bnjyuTkcSitKkkutiKsuKkksu = None

        #最多価格帯
        bnjyuTkcSitKkkuti = self.request.get("bnjyuTkcSitKkkuti")
        if bnjyuTkcSitKkkuti:
            bkdb.bnjyuTkcSitKkkuti = float(bnjyuTkcSitKkkuti)
        else:
            bkdb.bnjyuTkcSitKkkuti = None
        #管理費等
        bnjyuTkcKnrhtu = self.request.get("bnjyuTkcKnrhtu")
        if bnjyuTkcKnrhtu:
            bkdb.bnjyuTkcKnrhtu = float(bnjyuTkcKnrhtu)
        else:
            bkdb.bnjyuTkcKnrhtu = None
        #現況有姿分譲地
        bnjyuTkcGnkyuYusBnjyuc = self.request.get("bnjyuTkcGnkyuYusBnjyuc")
        if bnjyuTkcGnkyuYusBnjyuc == "1":
            bkdb.bnjyuTkcGnkyuYusBnjyuc = True
        else:
            bkdb.bnjyuTkcGnkyuYusBnjyuc = None
        #その他一時金名称１
        sntIcjknMishu1 = self.request.get("sntIcjknMishu1")
        if sntIcjknMishu1:
            bkdb.sntIcjknMishu1 = sntIcjknMishu1
        else:
            bkdb.sntIcjknMishu1 = None
        #金額１
        kngk1 = self.request.get("kngk1")
        if kngk1:
            bkdb.kngk1 = float(kngk1)
        else:
            bkdb.kngk1 = None
        #その他一時金名称2
        sntIcjknMishu2 = self.request.get("sntIcjknMishu2")
        if sntIcjknMishu2:
            bkdb.sntIcjknMishu2 = sntIcjknMishu2
        else:
            bkdb.sntIcjknMishu2 = None
        #金額2
        kngk2 = self.request.get("kngk2")
        if kngk2:
            bkdb.kngk2 = float(kngk2)
        else:
            bkdb.kngk2 = None
        #その他一時金名称3
        sntIcjknMishu3 = self.request.get("sntIcjknMishu3")
        if sntIcjknMishu3:
            bkdb.sntIcjknMishu3 = sntIcjknMishu3
        else:
            bkdb.sntIcjknMishu3 = None
        #金額3
        kngk3 = self.request.get("kngk3")
        if kngk3:
            bkdb.kngk3 = float(kngk3)
        else:
            bkdb.kngk3 = None
        #その他一時金名称4
        sntIcjknMishu4 = self.request.get("sntIcjknMishu4")
        if sntIcjknMishu4:
            bkdb.sntIcjknMishu4 = sntIcjknMishu4
        else:
            bkdb.sntIcjknMishu4 = None
        #金額4
        kngk4 = self.request.get("kngk4")
        if kngk4:
            bkdb.kngk4 = float(kngk4)
        else:
            bkdb.kngk4 = None
        #その他一時金名称5
        sntIcjknMishu5 = self.request.get("sntIcjknMishu5")
        if sntIcjknMishu5:
            bkdb.sntIcjknMishu5 = sntIcjknMishu5
        else:
            bkdb.sntIcjknMishu5 = None
        #金額5
        kngk5 = self.request.get("kngk5")
        if kngk5:
            bkdb.kngk5 = float(kngk5)
        else:
            bkdb.kngk5 = None
        #
        #備考３
        bku3 = self.request.get("bku3")
        if bku3:
            bkdb.bku3 = bku3
        else:
            bkdb.bku3 = None
        #備考４
        bku4 = self.request.get("bku4")
        if bku4:
            bkdb.bku4 = bku4
        else:
            bkdb.bku4 = None

        #広告用備考
        kkkybku = self.request.get("kkkybku")
        if kkkybku:
            bkdb.kkkybku = []
            for s in kkkybku.split(","):
                if s != "":
                    bkdb.kkkybku.append(s)
        else:
            bkdb.kkkybku = []


        #名称又は商号
        kukknsMishuShugu = self.request.get("kukknsMishuShugu")
        if kukknsMishuShugu:
            bkdb.kukknsMishuShugu = kukknsMishuShugu
        else:
            bkdb.kukknsMishuShugu = None
        #事務所所在地
        kukknsJmshShzic = self.request.get("kukknsJmshShzic")
        if kukknsJmshShzic:
            bkdb.kukknsJmshShzic = kukknsJmshShzic
        else:
            bkdb.kukknsJmshShzic = None
        #事務所電話番号
        kukknsJmshDnwBngu = self.request.get("kukknsJmshDnwBngu")
        if kukknsJmshDnwBngu:
            bkdb.kukknsJmshDnwBngu = kukknsJmshDnwBngu
        else:
            bkdb.kukknsJmshDnwBngu = None
        #宅建業法による免許番号
        tkkngyuhuMnkyBngu = self.request.get("tkkngyuhuMnkyBngu")
        if tkkngyuhuMnkyBngu:
            bkdb.tkkngyuhuMnkyBngu = tkkngyuhuMnkyBngu
        else:
            bkdb.tkkngyuhuMnkyBngu = None
        #都市計画法その他
        tskikkhuSnt = self.request.get("tskikkhuSnt")
        if tskikkhuSnt:
            bkdb.tskikkhuSnt = tskikkhuSnt
        else:
            bkdb.tskikkhuSnt = None
        #広告転載区分
        kukkTnsiKbn = self.request.get("kukkTnsiKbn")
        if kukkTnsiKbn:
            bkdb.kukkTnsiKbn = kukkTnsiKbn
        else:
            bkdb.kukkTnsiKbn = None
        #
        #私道負担割合
        sduFtnWraiBns = self.request.get("sduFtnWraiBns")
        if sduFtnWraiBns:
            bkdb.sduFtnWraiBns = float(sduFtnWraiBns)
        else:
            bkdb.sduFtnWraiBns = None
        #
        sduFtnWraiBnb = self.request.get("sduFtnWraiBnb")
        if sduFtnWraiBnb:
            bkdb.sduFtnWraiBnb = float(sduFtnWraiBnb)
        else:
            bkdb.sduFtnWraiBnb = None
        #
        sduFtnWraiBnsM2 = self.request.get("sduFtnWraiBnsM2")
        if sduFtnWraiBnsM2:
            bkdb.sduFtnWraiBnsM2 = float(sduFtnWraiBnsM2)
        else:
            bkdb.sduFtnWraiBnsM2 = None
        #
        sduFtnWraiBnbM2 = self.request.get("sduFtnWraiBnbM2")
        if sduFtnWraiBnbM2:
            bkdb.sduFtnWraiBnbM2 = float(sduFtnWraiBnbM2)
        else:
            bkdb.sduFtnWraiBnbM2 = None
        #部分面積名１
        bbnMnskMishu1 = self.request.get("bbnMnskMishu1")
        if bbnMnskMishu1:
            bkdb.bbnMnskMishu1 = bbnMnskMishu1
        else:
            bkdb.bbnMnskMishu1 = None
        #部分面積１
        bbnMnskM21 = self.request.get("bbnMnskM21")
        if bbnMnskM21:
            bkdb.bbnMnskM21 = float(bbnMnskM21)
        else:
            bkdb.bbnMnskM21 = None
        #部分面積名２
        bbnMnskMishu2 = self.request.get("bbnMnskMishu2")
        if bbnMnskMishu2:
            bkdb.bbnMnskMishu2 = float(bbnMnskMishu2)
        else:
            bkdb.bbnMnskMishu2 = None
        #部分面積２
        bbnMnskM22 = self.request.get("bbnMnskM22")
        if bbnMnskM22:
            bkdb.bbnMnskM22 = float(bbnMnskM22)
        else:
            bkdb.bbnMnskM22 = None
        #
        #
        #<売外全>

        #媒介契約年月日
        bikiKiykNngppSirkGG = self.request.get("bikiKiykNngppSirkGG")
        bikiKiykNngppSirkYY = self.request.get("bikiKiykNngppSirkYY")
        bikiKiykNngppSirkMM = self.request.get("bikiKiykNngppSirkMM")
        bikiKiykNngppSirkDD = self.request.get("bikiKiykNngppSirkDD")
        if bikiKiykNngppSirkGG == "H" and bikiKiykNngppSirkYY and bikiKiykNngppSirkMM and bikiKiykNngppSirkDD:
            bkdb.bikiKiykNngppSirk = datetime.datetime.strptime(str(1988 + int(bikiKiykNngppSirkYY )) + "/" + bikiKiykNngppSirkMM + "/" + bikiKiykNngppSirkDD,"%Y/%m/%d")
            bkdb.bikiKiykNngppSirk = timemanager.jst2utc_date(bkdb.bikiKiykNngppSirk)
        elif bikiKiykNngppSirkGG == "R" and bikiKiykNngppSirkYY and bikiKiykNngppSirkMM and bikiKiykNngppSirkDD:
            bkdb.bikiKiykNngppSirk = datetime.datetime.strptime(str(2018 + int(bikiKiykNngppSirkYY )) + "/" + bikiKiykNngppSirkMM + "/" + bikiKiykNngppSirkDD,"%Y/%m/%d")
            bkdb.bikiKiykNngppSirk = timemanager.jst2utc_date(bkdb.bikiKiykNngppSirk)
        else :
            bkdb.bikiKiykNngppSirk = None
        #

        #

        #

        #建築確認コード
        knckKknnCd = self.request.get("knckKknnCd")
        if knckKknnCd:
            bkdb.knckKknnCd = knckKknnCd
        else:
            bkdb.knckKknnCd = None
        #建築確認番号
        knckKknnBngu = self.request.get("knckKknnBngu")
        if knckKknnBngu:
            bkdb.knckKknnBngu = knckKknnBngu
        else:
            bkdb.knckKknnBngu = None
        #その他一時金なしフラグ
        sntIcjknNsFlg = self.request.get("sntIcjknNsFlg")
        if sntIcjknNsFlg == "1":
            bkdb.sntIcjknNsFlg = True
        else:
            bkdb.sntIcjknNsFlg = False
        #駐車場月額（最低値）
        chushjyuGtgkSitic = self.request.get("chushjyuGtgkSitic")
        if chushjyuGtgkSitic:
            bkdb.chushjyuGtgkSitic = float(chushjyuGtgkSitic)
        else:
            bkdb.chushjyuGtgkSitic = None
        #駐車場月額（最高値）
        chushjyuGtgkSikuc = self.request.get("chushjyuGtgkSikuc")
        if chushjyuGtgkSikuc:
            bkdb.chushjyuGtgkSikuc = float(chushjyuGtgkSikuc)
        else:
            bkdb.chushjyuGtgkSikuc = None
        #駐車場無料フラグ
        chushjyuMryuFlg = self.request.get("chushjyuMryuFlg")
        if chushjyuMryuFlg == "1":
            bkdb.chushjyuMryuFlg = False
        else:
            bkdb.chushjyuMryuFlg = None
        #

        #駐車場距離
        chushjyuKyrM = self.request.get("chushjyuKyrM")
        if chushjyuKyrM:
            bkdb.chushjyuKyrM = float(chushjyuKyrM)
        else:
            bkdb.chushjyuKyrM = None
        #駐車場形式
        chushjyuKisk = self.request.get("chushjyuKisk")
        if chushjyuKisk:
            bkdb.chushjyuKisk = chushjyuKisk
        else:
            bkdb.chushjyuKisk = None
        #駐車場屋根状況
        chushjyuYnJyukyu = self.request.get("chushjyuYnJyukyu")
        if chushjyuYnJyukyu:
            bkdb.chushjyuYnJyukyu = chushjyuYnJyukyu
        else:
            bkdb.chushjyuYnJyukyu = None


        """
        #周辺環境１(フリー)
        shuhnKnkyu1Fre = self.request.get("shuhnKnkyu1Fre")
        if shuhnKnkyu1Fre:
            bkdb.shuhnKnkyu1Fre = shuhnKnkyu1Fre
        else:
            bkdb.shuhnKnkyu1Fre = None

        kyr1 = self.request.get("kyr1")
        if kyr1:
            bkdb.kyr1 = kyr1
        else:
            bkdb.kyr1 = None
        #時間
        shuhnAccs1 = self.request.get("shuhnAccs1")
        if shuhnAccs1:
            bkdb.shuhnAccs1 = shuhnAccs1
        else:
            bkdb.shuhnAccs1 = None
        jkn1 = self.request.get("jkn1")
        if jkn1:
            bkdb.jkn1 = float(jkn1)
        else:
            bkdb.jkn1 = None
        """
        #周辺環境２(フリー)
        shuhnKnkyu2Fre = self.request.get("shuhnKnkyu2Fre")
        if shuhnKnkyu2Fre:
            bkdb.shuhnKnkyu2Fre = shuhnKnkyu2Fre
        else:
            bkdb.shuhnKnkyu2Fre = None
        kyr2 = self.request.get("kyr2")
        if kyr2:
            bkdb.kyr2 = float(kyr2)
        else:
            bkdb.kyr2 = None
        #時間
        shuhnAccs2 = self.request.get("shuhnAccs2")
        if shuhnAccs2:
            bkdb.shuhnAccs2 = shuhnAccs2
        else:
            bkdb.shuhnAccs2 = None
        jkn2 = self.request.get("jkn2")
        if jkn2:
            bkdb.jkn2 = float(jkn2)
        else:
            bkdb.jkn2 = None
        #周辺環境３(フリー)
        shuhnKnkyu3Fre = self.request.get("shuhnKnkyu3Fre")
        if shuhnKnkyu3Fre:
            bkdb.shuhnKnkyu3Fre = shuhnKnkyu3Fre
        else:
            bkdb.shuhnKnkyu3Fre = None
        kyr3 = self.request.get("kyr3")
        if kyr3:
            bkdb.kyr3 = float(kyr3)
        else:
            bkdb.kyr3 = None
        #時間
        shuhnAccs3 = self.request.get("shuhnAccs3")
        if shuhnAccs3:
            bkdb.shuhnAccs3 = shuhnAccs3
        else:
            bkdb.shuhnAccs3 = None
        jkn3 = self.request.get("jkn3")
        if jkn3:
            bkdb.jkn3 = float(jkn3)
        else:
            bkdb.jkn3 = None
        #周辺環境４(フリー)
        shuhnKnkyu4Fre = self.request.get("shuhnKnkyu4Fre")
        if shuhnKnkyu4Fre:
            bkdb.shuhnKnkyu4Fre = shuhnKnkyu4Fre
        else:
            bkdb.shuhnKnkyu4Fre = None
        kyr4 = self.request.get("kyr4")
        if kyr4:
            bkdb.kyr4 = float(kyr4)
        else:
            bkdb.kyr4 = None
        #時間
        shuhnAccs4 = self.request.get("shuhnAccs4")
        if shuhnAccs4:
            bkdb.shuhnAccs4 = shuhnAccs4
        else:
            bkdb.shuhnAccs4 = None
        jkn4 = self.request.get("jkn4")
        if jkn4:
            bkdb.jkn4 = float(jkn4)
        else:
            bkdb.jkn4 = None
        #周辺環境５(フリー)
        shuhnKnkyu5Fre = self.request.get("shuhnKnkyu5Fre")
        if shuhnKnkyu5Fre:
            bkdb.shuhnKnkyu5Fre = shuhnKnkyu5Fre
        else:
            bkdb.shuhnKnkyu5Fre = None
        kyr5 = self.request.get("kyr5")
        if kyr5:
            bkdb.kyr5 = float(kyr5)
        else:
            bkdb.kyr5 = None
        #時間
        shuhnAccs5 = self.request.get("shuhnAccs5")
        if shuhnAccs5:
            bkdb.shuhnAccs5 = shuhnAccs5
        else:
            bkdb.shuhnAccs5 = None
        jkn5 = self.request.get("jkn5")
        if jkn5:
            bkdb.jkn5 = float(jkn5)
        else:
            bkdb.jkn5 = None

        #設備（フリースペース）
        stbFrespc = self.request.get("stbFrespc")
        if stbFrespc:
            bkdb.stbFrespc = stbFrespc
        else:
            bkdb.stbFrespc = None
        #条件(フリースペース）
        tkkJkuFrespc = self.request.get("tkkJkuFrespc")
        if tkkJkuFrespc:
            bkdb.tkkJkuFrespc = tkkJkuFrespc
        else:
            bkdb.tkkJkuFrespc = None
        #建物面積１F
        ttmnMnsk1F = self.request.get("ttmnMnsk1F")
        if ttmnMnsk1F:
            bkdb.ttmnMnsk1F = float(ttmnMnsk1F)
        else:
            bkdb.ttmnMnsk1F = None
        #建物面積２F
        ttmnMnsk2F = self.request.get("ttmnMnsk2F")
        if ttmnMnsk2F:
            bkdb.ttmnMnsk2F = float(ttmnMnsk2F)
        else:
            bkdb.ttmnMnsk2F = None
        #建物面積３F
        ttmnMnsk3F = self.request.get("ttmnMnsk3F")
        if ttmnMnsk3F:
            bkdb.ttmnMnsk3F = float(ttmnMnsk3F)
        else:
            bkdb.ttmnMnsk3F = None
        #建物面積その他
        ttmnMnskSnt = self.request.get("ttmnMnskSnt")
        if ttmnMnskSnt:
            bkdb.ttmnMnskSnt = float(ttmnMnskSnt)
        else:
            bkdb.ttmnMnskSnt = None
        #
        #
        #<売外一>

        #角部屋フラグ
        hyIc1 = self.request.get("hyIc1")
        if hyIc1 == "1":
            bkdb.hyIc1 = True
        else:
            bkdb.hyIc1 = False

        #管理費なしフラグ
        knrhNsFlg = self.request.get("knrhNsFlg")
        if knrhNsFlg == "1":
            bkdb.knrhNsFlg = True
        else:
            bkdb.knrhNsFlg = False
        #管理費帯
        knrhtiFrom = self.request.get("knrhtiFrom")
        if knrhtiFrom:
            bkdb.knrhtiFrom = float(knrhtiFrom)
        else:
            bkdb.knrhtiFrom = None
        #
        knrhtiTo = self.request.get("knrhtiTo")
        if knrhtiTo:
            bkdb.knrhtiTo = float(knrhtiTo)
        else:
            bkdb.knrhtiTo = None
        #修繕積立金
        shuznTmttkn = self.request.get("shuznTmttkn")
        if shuznTmttkn:
            bkdb.shuznTmttkn = float(shuznTmttkn)
        else:
            bkdb.shuznTmttkn = None
        #修繕積立金なしフラグ
        shznTmttknNsFlg = self.request.get("shznTmttknNsFlg")
        if shznTmttknNsFlg == "1":
            bkdb.shznTmttknNsFlg = True
        else:
            bkdb.shznTmttknNsFlg = False
        #修繕積立金下限
        shznTmttknFrom = self.request.get("shznTmttknFrom")
        if shznTmttknFrom:
            bkdb.shznTmttknFrom = float(shznTmttknFrom)
        else:
            bkdb.shznTmttknFrom = None
        #修繕積立金上限
        shznTmttknTo = self.request.get("shznTmttknTo")
        if shznTmttknTo:
            bkdb.shznTmttknTo = float(shznTmttknTo)
        else:
            bkdb.shznTmttknTo = None
        #
        #
        #<売一戸建>

        #
        #
        #
        #
        #間取タイプ（2）
        mdrTyp2 = self.request.get("mdrTyp2")
        if mdrTyp2:
            bkdb.mdrTyp2 = mdrTyp2
        else:
            bkdb.mdrTyp2 = None
        #間取部屋数（2）
        mdrHysu2 = self.request.get("mdrHysu2")
        if mdrHysu2:
            bkdb.mdrHysu2 = float(mdrHysu2)
        else:
            bkdb.mdrHysu2 = None
        #室所在階1（2）
        stShziki12 = self.request.get("stShziki12")
        if stShziki12:
            bkdb.stShziki12 = float(stShziki12)
        else:
            bkdb.stShziki12 = None
        #室タイプ1（2）
        stTyp12 = self.request.get("stTyp12")
        if stTyp12:
            bkdb.stTyp12 = stTyp12
        else:
            bkdb.stTyp12 = None
        #室広さ1（2）
        stHrs12 = self.request.get("stHrs12")
        if stHrs12:
            bkdb.stHrs12 = float(stHrs12)
        else:
            bkdb.stHrs12 = None
        #室数1（2）
        stsu12 = self.request.get("stsu12")
        if stsu12:
            bkdb.stsu12 = float(stsu12)
        else:
            bkdb.stsu12 = None
        #室所在階2（2）
        stShziki22 = self.request.get("stShziki22")
        if stShziki22:
            bkdb.stShziki22 = float(stShziki22)
        else:
            bkdb.stShziki22 = None
        #室タイプ2（2）
        stTyp22 = self.request.get("stTyp22")
        if stTyp22:
            bkdb.stTyp22 = stTyp22
        else:
            bkdb.stTyp22 = None
        #室広さ2（2）
        stHrs22 = self.request.get("stHrs22")
        if stHrs22:
            bkdb.stHrs22 = float(stHrs22)
        else:
            bkdb.stHrs22 = None
        #室数2（2）
        stsu22 = self.request.get("stsu22")
        if stsu22:
            bkdb.stsu22 = float(stsu22)
        else:
            bkdb.stsu22 = None
        #室所在階3（2）
        stShziki32 = self.request.get("stShziki32")
        if stShziki32:
            bkdb.stShziki32 = float(stShziki32)
        else:
            bkdb.stShziki32 = None
        #室タイプ3（2）
        stTyp32 = self.request.get("stTyp32")
        if stTyp32:
            bkdb.stTyp32 = stTyp32
        else:
            bkdb.stTyp32 = None
        #室広さ3（2）
        stHrs32 = self.request.get("stHrs32")
        if stHrs32:
            bkdb.stHrs32 = float(stHrs32)
        else:
            bkdb.stHrs32 = None
        #室数3（2）
        stsu32 = self.request.get("stsu32")
        if stsu32:
            bkdb.stsu32 = float(stsu32)
        else:
            bkdb.stsu32 = None
        #室所在階4（2）
        stShziki42 = self.request.get("stShziki42")
        if stShziki42:
            bkdb.stShziki42 = float(stShziki42)
        else:
            bkdb.stShziki42 = None
        #室タイプ4(2)
        stTyp42 = self.request.get("stTyp42")
        if stTyp42:
            bkdb.stTyp42 = stTyp42
        else:
            bkdb.stTyp42 = None
        #室広さ4(2)
        stHrs42 = self.request.get("stHrs42")
        if stHrs42:
            bkdb.stHrs42 = float(stHrs42)
        else:
            bkdb.stHrs42 = None
        #室数4(2)
        stsu42 = self.request.get("stsu42")
        if stsu42:
            bkdb.stsu42 = float(stsu42)
        else:
            bkdb.stsu42 = None
        #室所在階5(2)
        stShziki52 = self.request.get("stShziki52")
        if stShziki52:
            bkdb.stShziki52 = float(stShziki52)
        else:
            bkdb.stShziki52 = None
        #室タイプ5(2)
        stTyp52 = self.request.get("stTyp52")
        if stTyp52:
            bkdb.stTyp52 = stTyp52
        else:
            bkdb.stTyp52 = None
        #室広さ5(2)
        stHrs52 = self.request.get("stHrs52")
        if stHrs52:
            bkdb.stHrs52 = float(stHrs52)
        else:
            bkdb.stHrs52 = None
        #室数5(2)
        stsu52 = self.request.get("stsu52")
        if stsu52:
            bkdb.stsu52 = float(stsu52)
        else:
            bkdb.stsu52 = None
        #室所在階6(2)
        stShziki62 = self.request.get("stShziki62")
        if stShziki62:
            bkdb.stShziki62 = float(stShziki62)
        else:
            bkdb.stShziki62 = None
        #室タイプ6(2)
        stTyp62 = self.request.get("stTyp62")
        if stTyp62:
            bkdb.stTyp62 = stTyp62
        else:
            bkdb.stTyp62 = None
        #室広さ6(2)
        stHrs62 = self.request.get("stHrs62")
        if stHrs62:
            bkdb.stHrs62 = float(stHrs62)
        else:
            bkdb.stHrs62 = None
        #室数6(2)
        stsu62 = self.request.get("stsu62")
        if stsu62:
            bkdb.stsu62 = float(stsu62)
        else:
            bkdb.stsu62 = None
        #室所在階7(2)
        stShziki72 = self.request.get("stShziki72")
        if stShziki72:
            bkdb.stShziki72 = float(stShziki72)
        else:
            bkdb.stShziki72 = None
        #室タイプ7(2)
        stTyp72 = self.request.get("stTyp72")
        if stTyp72:
            bkdb.stTyp72 = stTyp72
        else:
            bkdb.stTyp72 = None
        #室広さ7(2)
        stHrs72 = self.request.get("stHrs72")
        if stHrs72:
            bkdb.stHrs72 = float(stHrs72)
        else:
            bkdb.stHrs72 = None
        #室数7(2)
        stsu72 = self.request.get("stsu72")
        if stsu72:
            bkdb.stsu72 = float(stsu72)
        else:
            bkdb.stsu72 = None
        #間取りその他(2)
        mdrSnt2 = self.request.get("mdrSnt2")
        if mdrSnt2:
            bkdb.mdrSnt2 = mdrSnt2
        else:
            bkdb.mdrSnt2 = None
        #分譲戸建販売戸数
        bnjyuKdtHnbiKsu = self.request.get("bnjyuKdtHnbiKsu")
        if bnjyuKdtHnbiKsu:
            bkdb.bnjyuKdtHnbiKsu = float(bnjyuKdtHnbiKsu)
        else:
            bkdb.bnjyuKdtHnbiKsu = None
        #価格帯戸数
        bnjyuKdtKkkutiKsuKkksuFrom = self.request.get("bnjyuKdtKkkutiKsuKkksuFrom")
        if bnjyuKdtKkkutiKsuKkksuFrom:
            bkdb.bnjyuKdtKkkutiKsuKkksuFrom = float(bnjyuKdtKkkutiKsuKkksuFrom)
        else:
            bkdb.bnjyuKdtKkkutiKsuKkksuFrom = None
        bnjyuKdtKkkutiKsuKkksuTo = self.request.get("bnjyuKdtKkkutiKsuKkksuTo")
        if bnjyuKdtKkkutiKsuKkksuTo:
            bkdb.bnjyuKdtKkkutiKsuKkksuTo = float(bnjyuKdtKkkutiKsuKkksuTo)
        else:
            bkdb.bnjyuKdtKkkutiKsuKkksuTo = None


        #販売最低価格
        bnjyuKdtHnbiSitiKkku = self.request.get("bnjyuKdtHnbiSitiKkku")
        if bnjyuKdtHnbiSitiKkku:
            bkdb.bnjyuKdtHnbiSitiKkku = float(bnjyuKdtHnbiSitiKkku)
        else:
            bkdb.bnjyuKdtHnbiSitiKkku = None
        #販売最高価格
        bnjyuKdtHnbiSikuKkku = self.request.get("bnjyuKdtHnbiSikuKkku")
        if bnjyuKdtHnbiSikuKkku:
            bkdb.bnjyuKdtHnbiSikuKkku = float(bnjyuKdtHnbiSikuKkku)
        else:
            bkdb.bnjyuKdtHnbiSikuKkku = None

        #販売土地最小面積
        bnjyuKdtHnbiTcSishouMnsk = self.request.get("bnjyuKdtHnbiTcSishouMnsk")
        if bnjyuKdtHnbiTcSishouMnsk:
            bkdb.bnjyuKdtHnbiTcSishouMnsk = float(bnjyuKdtHnbiTcSishouMnsk)
        else:
            bkdb.bnjyuKdtHnbiTcSishouMnsk = None
        #販売土地最大面積
        bnjyuKdtHnbiTcSidiMnsk = self.request.get("bnjyuKdtHnbiTcSidiMnsk")
        if bnjyuKdtHnbiTcSidiMnsk:
            bkdb.bnjyuKdtHnbiTcSidiMnsk = float(bnjyuKdtHnbiTcSidiMnsk)
        else:
            bkdb.bnjyuKdtHnbiTcSidiMnsk = None
        #販売建物最小面積
        bnjyuKdtHnbiTtmnSishouMnsk = self.request.get("bnjyuKdtHnbiTtmnSishouMnsk")
        if bnjyuKdtHnbiTtmnSishouMnsk:
            bkdb.bnjyuKdtHnbiTtmnSishouMnsk = float(bnjyuKdtHnbiTtmnSishouMnsk)
        else:
            bkdb.bnjyuKdtHnbiTtmnSishouMnsk = None
        #販売建物最大面積
        bnjyuKdtHnbiTtmnSidiMnsk = self.request.get("bnjyuKdtHnbiTtmnSidiMnsk")
        if bnjyuKdtHnbiTtmnSidiMnsk:
            bkdb.bnjyuKdtHnbiTtmnSidiMnsk = float(bnjyuKdtHnbiTtmnSidiMnsk)
        else:
            bkdb.bnjyuKdtHnbiTtmnSidiMnsk = None
        #最多価格帯戸数
        bnjyuKdtSitKkkutiKsuKkksu = self.request.get("bnjyuKdtSitKkkutiKsuKkksu")
        if bnjyuKdtSitKkkutiKsuKkksu:
            bkdb.bnjyuKdtSitKkkutiKsuKkksu = float(bnjyuKdtSitKkkutiKsuKkksu)
        else:
            bkdb.bnjyuKdtSitKkkutiKsuKkksu = None
        #最多価格帯
        bnjyuKdtSitKkkuti = self.request.get("bnjyuKdtSitKkkuti")
        if bnjyuKdtSitKkkuti:
            bkdb.bnjyuKdtSitKkkuti = float(bnjyuKdtSitKkkuti)
        else:
            bkdb.bnjyuKdtSitKkkuti = None
        #管理費
        bnjyuKdtKnrh = self.request.get("bnjyuKdtKnrh")
        if bnjyuKdtKnrh:
            bkdb.bnjyuKdtKnrh = float(bnjyuKdtKnrh)
        else:
            bkdb.bnjyuKdtKnrh = None

        bkdb.put()
        return bkdb.bkID
