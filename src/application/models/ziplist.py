# -*- coding: utf-8 -*-
from google.appengine.ext import db

# Create your models here.
"""
郵便番号データファイルでは、以下の順に配列しています。
全国地方公共団体コード(JIS X0401、X0402)………　半角数字
(旧)郵便番号(5桁)………………………………………　半角数字
郵便番号(7桁)………………………………………　半角数字
都道府県名　…………　半角カタカナ(コード順に掲載)　(注1)
市区町村名　…………　半角カタカナ(コード順に掲載)　(注1)
町域名　………………　半角カタカナ(五十音順に掲載)　(注1)
都道府県名　…………　漢字(コード順に掲載)　(注1,2)
市区町村名　…………　漢字(コード順に掲載)　(注1,2)
町域名　………………　漢字(五十音順に掲載)　(注1,2)
一町域が二以上の郵便番号で表される場合の表示　(注3)　(「1」は該当、「0」は該当せず)
小字毎に番地が起番されている町域の表示　(注4)　(「1」は該当、「0」は該当せず)
丁目を有する町域の場合の表示　(「1」は該当、「0」は該当せず)
一つの郵便番号で二以上の町域を表す場合の表示　(注5)　(「1」は該当、「0」は該当せず)
更新の表示（注6）（「0」は変更なし、「1」は変更あり、「2」廃止（廃止データのみ使用））
変更理由　(「0」は変更なし、「1」市政・区政・町政・分区・政令指定都市施行、「2」住居表示の実施、「3」区画整理、「4」郵便区調整等、「5」訂正、「6」廃止(廃止データのみ使用))

大口事業所

大口事業所の所在地のＪＩＳコード（5バイト）
大口事業所名（カナ）（100バイト）
大口事業所名（漢字）（160バイト）
都道府県名（漢字）（8バイト）
市区町村名（漢字）（24バイト）
町域名（漢字）（24バイト）
小字名、丁目、番地等（漢字）（124バイト）
大口事業所個別番号（7バイト）
旧郵便番号（5バイト）
取扱支店名（漢字）（40バイト）
個別番号の種別の表示（1バイト）　「0」大口事業所　「1」私書箱
複数番号の有無（1バイト）
「0」複数番号無し
「1」複数番号を設定している場合の個別番号の1
「2」複数番号を設定している場合の個別番号の2
「3」複数番号を設定している場合の個別番号の3

"""
class ziplist(db.Model):
    cityno = db.StringProperty(verbose_name=u'全国地方公共団体コード')
    oldzip = db.StringProperty(verbose_name=u'旧郵便番号')
    zipcode = db.StringProperty(verbose_name=u'郵便番号')
    fulladdress = db.StringProperty(verbose_name=u'所在地')
    prefkana = db.StringProperty(verbose_name=u'都道府県名カナ')
    pref = db.StringProperty(verbose_name=u'都道府県名')
    citykana = db.StringProperty(verbose_name=u'市区町村名カナ')
    city = db.StringProperty(verbose_name=u'市区町村名')
    townkana = db.StringProperty(verbose_name=u'町域名カナ')
    town = db.StringProperty(verbose_name=u'町域名')
    
    address = db.StringProperty(verbose_name=u'小字名、丁目、番地等（漢字）')
    companykana = db.StringProperty(verbose_name=u'大口事業所名カナ')
    company = db.StringProperty(verbose_name=u'大口事業所名')
    
    two_code = db.StringProperty(verbose_name=u'一町域が二以上の郵便番号で表される場合の表示')
    banchi = db.StringProperty(verbose_name=u'小字毎に番地が起番されている町域の表示')
    chome =db.StringProperty(verbose_name=u'丁目を有する町域の場合の表示')
    two_town = db.StringProperty(verbose_name=u'一つの郵便番号で二以上の町域を表す場合の表示')

