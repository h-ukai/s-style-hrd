# -*- coding: utf-8 -*-

from google.cloud import ndb
from application.models.bksearchensen import bksearchensen


class bksearcheki(ndb.Model):
    ref_ensen = ndb.KeyProperty(kind='bksearchensen')
    #駅名（1）
    ekimei = ndb.StringProperty(verbose_name="駅名（1）")
