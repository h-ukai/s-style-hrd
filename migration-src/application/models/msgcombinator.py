# -*- coding: utf-8 -*-

from google.cloud import ndb
from application.models.member import member
from application.models.message import Message

# https://appengine-cookbook.appspot.com/recipe/getting-dbreferenceproperty-key-without-loading-entity

# REVIEW-L1: ndb.KeyProperty の kind パラメータに文字列ではなくクラス名を使用している
# 修正前: refmem = ndb.KeyProperty(kind=member, verbose_name=None)
# 修正後: refmem = ndb.KeyProperty(kind='member', verbose_name=None)
class msgcombinator(ndb.Model):
    refmem = ndb.KeyProperty(kind='member', verbose_name=None)
    refmes = ndb.KeyProperty(kind='Message', verbose_name=None)
    combkind = ndb.StringProperty(verbose_name="種類", choices={"送信", "受信", "所有", "参照"}, default="所有")
    confirm = ndb.BooleanProperty(default=False)  # confirmの意味や和訳。 【動詞】 【他動詞】確認する
