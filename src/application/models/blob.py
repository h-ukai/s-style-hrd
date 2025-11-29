# -*- coding: utf-8 -*-
#

from google.appengine.ext import db

class Blob(db.Model):
    blob_key_name = db.StringProperty(verbose_name=u"blob_key_name")
    CorpOrg_key = db.StringProperty(verbose_name=u"CorpOrg_key")
    Branch_Key = db.StringProperty(verbose_name=u"Branch_Key")
    bkID = db.StringProperty(verbose_name=u"bkID")
    blobNo = db.IntegerProperty(verbose_name=u"blobNo")
    blobkind = db.StringProperty(verbose_name=u"blobkind")
    title = db.StringProperty(verbose_name=u"title")
    content = db.StringProperty(multiline=True,verbose_name=u"content")
    filename = db.StringProperty(verbose_name=u"filename")
    fileextension = db.StringProperty(verbose_name=u"fileextension")
    media = db.StringProperty(verbose_name=u"media")
    pos = db.StringProperty(verbose_name=u"pos")
    thumbnailurl = db.StringProperty(verbose_name=u"thumbnailurl")
    bloburl = db.StringProperty(verbose_name=u"bloburl")
    html =  db.StringProperty(verbose_name=u"html")
    blobKey = db.StringProperty(verbose_name=u"blobKey")
    shzicmi1 = db.StringProperty(verbose_name=u"shzicmi1")
    shzicmi2 = db.StringProperty(verbose_name=u"shzicmi2")
    ttmnmi = db.StringProperty(verbose_name=u"ttmnmi")
    date = db.DateTimeProperty(auto_now_add=True,verbose_name=u"date")

class blobNo(db.Model):
    blob_key_name = db.StringProperty()
    max = db.IntegerProperty()
    def getNextNum(self):
        def procedure():
            if self.max is None:
                self.max = 0
            self.max = self.max + 1
            self.put()
            return self.max
        return db.run_in_transaction(procedure)