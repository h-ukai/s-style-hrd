# -*- coding: utf-8 -*-

from google.appengine.ext import db
from message import Message
from bkdata import BKdata
from member import member

class BKlist(db.Model):
    refbk = db.ReferenceProperty(reference_class = BKdata, verbose_name="BKdataKey", collection_name="refmeslist")
    refmes = db.ReferenceProperty(reference_class = Message, verbose_name="MessageKey", collection_name="refbklist")
    refmem = db.ReferenceProperty(reference_class = member, verbose_name="MemberKey", collection_name="refbklist")
    senddate = db.DateTimeProperty(auto_now_add = True,verbose_name=u"送信日時")
    sended = db.BooleanProperty(default=False,verbose_name=u"送信済")
    listsended = db.BooleanProperty(default=False,verbose_name=u"一覧送信済")
    memo = db.StringProperty(verbose_name=u"メモ")
    kindname = db.StringProperty(verbose_name=u"アクション")
    issend = db.BooleanProperty(default=False,verbose_name=u"要送信")
