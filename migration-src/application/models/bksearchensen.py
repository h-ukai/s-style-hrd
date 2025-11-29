# -*- coding: utf-8 -*-

from google.cloud import ndb
from application.models.bksearchdata import bksearchdata



class bksearchensen(ndb.Model):
    ref_bksearchdata = ndb.KeyProperty(kind='bksearchdata')

    #都道府県名
    tdufknmi = ndb.StringProperty(verbose_name="都道府県名")

    #沿線略称（1）
    ensenmei = ndb.StringProperty(verbose_name="沿線略称")

    #徒歩（分）1（1）
    thHnU = ndb.FloatProperty(verbose_name="徒歩（分）上限")

    #徒歩（m）2（1）
    thMU = ndb.FloatProperty(verbose_name="徒歩（m）上限")

    #ソート用連番
    sortkey = ndb.IntegerProperty()
