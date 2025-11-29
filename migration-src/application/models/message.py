# -*- coding: utf-8 -*-

from google.cloud import ndb

class Message(ndb.Model):
    corp = ndb.StringProperty(verbose_name="会社")
    body = ndb.TextProperty(verbose_name="本文")
    subject = ndb.StringProperty(verbose_name="表題")
    kindname = ndb.StringProperty(verbose_name="アクション")
    done = ndb.BooleanProperty(verbose_name="済", default=False)
    kill = ndb.BooleanProperty(verbose_name="消", default=False)
    timestamp = ndb.DateTimeProperty(auto_now_add=True, verbose_name="タイムスタンプ")
    reservation = ndb.DateTimeProperty(auto_now_add=True, verbose_name="予定日")
    reservationend = ndb.DateTimeProperty(auto_now_add=True, verbose_name="予定終了日")
    commentTo = ndb.KeyProperty(kind='Message', verbose_name="コメント先")
