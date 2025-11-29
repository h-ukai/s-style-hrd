# -*- coding: utf-8 -*-

from google.cloud import ndb
from application.models.message import Message
from application.models.bkdata import BKdata
from application.models.member import member

class BKlist(ndb.Model):
    refbk = ndb.KeyProperty(kind=BKdata, verbose_name="BKdataKey")
    refmes = ndb.KeyProperty(kind=Message, verbose_name="MessageKey")
    refmem = ndb.KeyProperty(kind=member, verbose_name="MemberKey")
    senddate = ndb.DateTimeProperty(auto_now_add = True,verbose_name=u"送信日時")
    sended = ndb.BooleanProperty(default=False,verbose_name=u"送信済")
    listsended = ndb.BooleanProperty(default=False,verbose_name=u"一覧送信済")
    memo = ndb.StringProperty(verbose_name=u"メモ")
    kindname = ndb.StringProperty(verbose_name=u"アクション")
    issend = ndb.BooleanProperty(default=False,verbose_name=u"要送信")

