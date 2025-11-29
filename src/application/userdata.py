#!/usr/local/bin/python
# -*- coding: utf-8 -*-

from google.appengine.ext import db
import unicodedata

"""
文字列の正規化
>>> s = 'ﾌｶﾞホゲ-%*@AＢＣ−％＊＠１２3'.decode('euc-jp')
>>> n = unicodedata.normalize('NFKC', s)
>>> print n.encode('euc-jp')
フガホゲ-%*@ABC−%*@123
"""
class BKdata(db.Model):
    bkid = db.StringProperty(required=True)
    address = db.StringProperty()
    name = db.StringProperty()
    building = db.StringProperty()
    date = db.DateTimeProperty()
