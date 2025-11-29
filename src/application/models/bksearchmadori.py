# -*- coding: utf-8 -*-

from google.appengine.ext import db
from bksearchdata import bksearchdata

class bksearchmadori(db.Model):

    ref_bksearchdata = db.ReferenceProperty(reference_class = bksearchdata,collection_name = 'madori')
    #間取部屋数（1）
    mdrHysu = db.FloatProperty(verbose_name=u"間取部屋数")
    #間取タイプ（1）
    mdrTyp = db.StringProperty(verbose_name=u"間取タイプ", choices=set([u"ワンルーム",u"K",u"DK",u"LK",u"LDK",u"SK",u"SDK",u"SLK",u"SLDK"]))
    #ソート用連番
    sortkey = db.IntegerProperty()
