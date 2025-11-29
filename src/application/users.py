#!/usr/local/bin/python
# -*- coding: utf-8 -*-
#
"""Another login utility sample on Google App Engine : Users

Author    : OKAZAKI Hiroki (okaz@teshigoto.net, https://www.teshigoto.net/)
Version   : $Id: users.py,v 1.3 2009/02/10 04:34:08 okaz Exp $
Copyright : Copyright (c) 2009 OKAZAKI Hiroki
License   : Python
"""
from google.appengine.ext import db

class Users(db.Model):
    id = db.StringProperty(required=True)
    pwd = db.StringProperty(required=True)
    email = db.EmailProperty(required=True)
    active = db.BooleanProperty(required=True)
    entry = db.DateTimeProperty(required=True)
    update = db.DateTimeProperty()


class Logs(db.Model):
    uid = db.StringProperty(required=True)
    sid = db.StringProperty(required=True)
    ip = db.StringProperty(required=True)
    lang = db.StringProperty(required=True)
    login = db.DateTimeProperty(required=True)
    logout = db.DateTimeProperty()
