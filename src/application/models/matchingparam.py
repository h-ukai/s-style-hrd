# -*- coding: utf-8 -*-

from google.appengine.ext import db

class matchingparam(db.Model):
    CorpOrg_key_name = db.StringProperty(verbose_name=u"会社ID",required=True)
    Branch_Key_name = db.StringProperty(verbose_name=u"支店ID")
    sitename = db.StringProperty(verbose_name=u"サイト名")
    matchingtarget = db.StringProperty(verbose_name=u"マッチング対象物件")
    service = db.StringProperty(default=u"マッチング",verbose_name=u"マッチング対象サービス名")
    lev1noreactiondays = db.IntegerProperty(default=30,verbose_name=u"lev1無言日数")
    lev1maxsended = db.IntegerProperty(default=100,verbose_name=u"lev1最大物件送信数")
    lev2noreactiondays = db.IntegerProperty(default=60,verbose_name=u"lev2無言日数")
    lev2maxsended = db.IntegerProperty(default=150,verbose_name=u"lev2最大物件送信数")
    limitdistance = db.IntegerProperty(default=100,verbose_name=u"最長間隔日数")
    subject = db.StringProperty(verbose_name=u"タイトル")
    body = db.StringProperty(verbose_name=u"本文",multiline=True)
    media = db.StringProperty(default=u"web",verbose_name=u"メディア")
    seikyu =  db.StringProperty(verbose_name=u"請求")
    sousinsyurui = db.StringProperty(verbose_name=u"送信種類")
