# -*- coding: utf-8 -*-
#      位置参照情報ダウンロードサービス
#      https://nlftp.mlit.go.jp/isj/index.html
#      地名データ

from google.cloud import ndb
from . import Branch
import datetime


class address1(ndb.Model):
    """市区町村レベルの住所マスタ

    Migration Notes:
    - db.Model → ndb.Model
    - db.StringProperty → ndb.StringProperty（構文変更なし）
    """

    # 市区町村コード
    cityno = ndb.StringProperty(name="cityno")

    # 都道府県名
    todofukenmei = ndb.StringProperty(name="todofukenmei")

    # 市区町村名
    shikutyosonmei = ndb.StringProperty(name="shikutyosonmei")


class address2(ndb.Model):
    """大字・町丁目レベルの住所マスタ

    Migration Notes:
    - db.Model → ndb.Model
    - db.StringProperty → ndb.StringProperty（構文変更なし）
    """

    # 都道府県名
    todofukenmei = ndb.StringProperty(name="todofukenmei")

    # 市区町村名
    shikutyosonmei = ndb.StringProperty(name="shikutyosonmei")

    # 大字・町丁目
    ooazatyotyome = ndb.StringProperty(name="ooazatyotyome")


class address3(ndb.Model):
    """街区符号・地番レベルの住所マスタ（位置情報付き）

    Migration Notes:
    - db.Model → ndb.Model
    - db.StringProperty → ndb.StringProperty（構文変更なし）
    - db.IntegerProperty → ndb.IntegerProperty（構文変更なし）
    - db.FloatProperty → ndb.FloatProperty（構文変更なし）
    """

    # 都道府県名
    todofukenmei = ndb.StringProperty(name="todofukenmei")

    # 市区町村名
    shikutyosonmei = ndb.StringProperty(name="shikutyosonmei")

    # 大字・町丁目
    ooazatyotyome = ndb.StringProperty(name="ooazatyotyome")

    # 街区符号・地番
    gaikubanchi = ndb.StringProperty(name="gaikubanchi")

    # 座標系番号
    zahyoukeibangou = ndb.IntegerProperty(name="zahyoukeibangou")

    # X座標
    x = ndb.FloatProperty(name="x")

    # Y座標
    y = ndb.FloatProperty(name="y")

    # 緯度
    lat = ndb.FloatProperty(name="lat")

    # 経度
    lng = ndb.FloatProperty(name="lng")

    # 住居表示フラグ
    jukyohyojiflg = ndb.StringProperty(name="jukyohyojiflg")

    # 代表フラグ
    daihyoflg = ndb.StringProperty(name="daihyoflg")

    # 更新前履歴フラグ
    kousinmaerirekiflg = ndb.StringProperty(name="kousinmaerirekiflg")

    # 更新後履歴フラグ
    kousingorirekiflg = ndb.StringProperty(name="kousingorirekiflg")
