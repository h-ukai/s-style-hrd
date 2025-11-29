# -*- coding: utf-8 -*-

from google.appengine.ext import db
from google.appengine.ext.db import polymodel
from application.models.member import member
from message import Message

# https://appengine-cookbook.appspot.com/recipe/getting-dbreferenceproperty-key-without-loading-entity

class msgcombinator(db.Model):
    refmem = db.ReferenceProperty(reference_class = member, verbose_name=None, collection_name="refmeslist")
    refmes = db.ReferenceProperty(reference_class = Message, verbose_name=None, collection_name="refmemlist")
    combkind = db.StringProperty(verbose_name=u"種類",choices=set([u"送信",u"受信",u"所有",u"参照"]),default=u"所有")
    confirm = db.BooleanProperty(default=False) #confirmの意味や和訳。 【動詞】 【他動詞】確認する