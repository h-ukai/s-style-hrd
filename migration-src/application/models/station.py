# -*- coding: utf-8 -*-
"""
#      駅・沿線情報ダウンロードサービス
#      https://www.ekidata.jp/download/index.html
#
鉄道概要コード    rr_cd    整数2桁    -    ○    鉄道会社概要コード
路線コード    line_cd    整数5桁    -    ○    鉄道コード + エリアコード + 連番
※大手私鉄のみエリアコード = 0
駅コード    station_cd    整数7桁    ○    ○    路線コード + 連番
路線並び順    line_sort    整数5桁    -    -    新路線追加時等に調整
駅並び順    station_sort    整数7桁    -    -    新駅追加時等に調整
駅グループコード    station_g_cd    整数7桁    -    ○    複数路線駅をコードで統一
駅タイプ    r_type    整数1桁    -    ○    １：通常駅　2：地下鉄駅
鉄道概要名    rr_name    文字列 64byte    -    ○    JR/大手私鉄/その他
路線名    line_name    文字列 128byte    -    ○    路線名称
駅名    station_name    文字列 128byte    -    ○    駅名称
都道府県コード    pref_cd    整数2桁    -    ○    北海道～沖縄＋その他
緯度    lat    数値    -    -    小数点含む [ 世界測地系(WGS84) ]
経度    lng    数値    -    -    小数点含む [ 世界測地系(WGS84) ]
表示フラグ    f_flag    0 or 1    -    ○    ０：非表示　１：表示

"""
from google.cloud import ndb

class Station(ndb.Model):
    rr_cd = ndb.StringProperty(verbose_name='rr_cd')
    line_cd = ndb.StringProperty(verbose_name='line_cd')
    station_cd = ndb.StringProperty(verbose_name='station_cd')
    line_sort = ndb.StringProperty(verbose_name='line_sort')
    station_sort = ndb.StringProperty(verbose_name='station_sort')
    station_g_cd = ndb.StringProperty(verbose_name='station_g_cd')
    r_type = ndb.StringProperty(verbose_name='r_type')
    rr_name = ndb.StringProperty(verbose_name='rr_name')
    line_name = ndb.StringProperty(verbose_name='line_name')
    station_name = ndb.StringProperty(verbose_name='station_name')
    pref_cd = ndb.StringProperty(verbose_name='pref_cd')
    lon = ndb.FloatProperty(verbose_name='lon')
    lat = ndb.FloatProperty(verbose_name='lat')
    f_flag = ndb.StringProperty(verbose_name='f_flag')

class Line(ndb.Model):
    rr_cd = ndb.StringProperty(verbose_name='rr_cd')
    line_cd = ndb.StringProperty(verbose_name='line_cd')
    line_sort = ndb.StringProperty(verbose_name='line_sort')
    r_type = ndb.StringProperty(verbose_name='r_type')
    rr_name = ndb.StringProperty(verbose_name='rr_name')
    line_name = ndb.StringProperty(verbose_name='line_name')
    pref_cd = ndb.StringProperty(verbose_name='pref_cd')
