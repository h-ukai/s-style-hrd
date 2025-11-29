# -*- coding: utf-8 -*-

from google.appengine.ext import db

class Message(db.Model):
    corp = db.StringProperty(verbose_name=u"会社")
    body = db.TextProperty(verbose_name=u"本文")
    subject = db.StringProperty(verbose_name=u"表題")
    kindname = db.StringProperty(verbose_name=u"アクション")
    done = db.BooleanProperty(verbose_name=u"済",default=False)
    kill = db.BooleanProperty(verbose_name=u"消",default=False)
    timestamp = db.DateTimeProperty(auto_now_add = True,verbose_name=u"タイムスタンプ")
    reservation = db.DateTimeProperty(auto_now_add = True,verbose_name=u"予定日")
    reservationend = db.DateTimeProperty(auto_now_add = True,verbose_name=u"予定終了日")
    commentTo = db.SelfReference(collection_name=u"refmes",verbose_name=u"コメント先")