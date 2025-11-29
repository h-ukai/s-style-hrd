# -*- coding: utf-8 -*-

from google.appengine.ext import db
from bksearchensen import bksearchensen


class bksearcheki(db.Model):
    ref_ensen = db.ReferenceProperty(reference_class = bksearchensen,collection_name = 'eki')
    #駅名（1）
    ekimei = db.StringProperty(verbose_name=u"駅名（1）")
