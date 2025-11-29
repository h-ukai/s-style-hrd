# -*- coding: utf-8 -*-

from google.appengine.ext import db
from bksearchdata import bksearchdata



class bksearchensen(db.Model):

    ref_bksearchdata = db.ReferenceProperty(reference_class = bksearchdata,collection_name = 'ensen')
    
    #都道府県名
    tdufknmi = db.StringProperty(verbose_name=u"都道府県名")

    #沿線略称（1）
    ensenmei = db.StringProperty(verbose_name=u"沿線略称")

    #徒歩（分）1（1）
    thHnU = db.FloatProperty(verbose_name=u"徒歩（分）上限")

    #徒歩（m）2（1）
    thMU = db.FloatProperty(verbose_name=u"徒歩（m）上限")

    #ソート用連番
    sortkey = db.IntegerProperty()

