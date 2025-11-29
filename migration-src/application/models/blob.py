# -*- coding: utf-8 -*-
#

from google.cloud import ndb

class Blob(ndb.Model):
    blob_key_name = ndb.StringProperty(verbose_name=u"blob_key_name")
    CorpOrg_key = ndb.StringProperty(verbose_name=u"CorpOrg_key")
    Branch_Key = ndb.StringProperty(verbose_name=u"Branch_Key")
    bkID = ndb.StringProperty(verbose_name=u"bkID")
    blobNo = ndb.IntegerProperty(verbose_name=u"blobNo")
    blobkind = ndb.StringProperty(verbose_name=u"blobkind")
    title = ndb.StringProperty(verbose_name=u"title")
    # REVIEW-L1: multiline content requires TextProperty (StringProperty has 1500 byte limit)
    # 修正前: content = ndb.StringProperty(verbose_name=u"content")
    # 修正後: content = ndb.TextProperty(verbose_name=u"content")
    content = ndb.TextProperty(verbose_name=u"content")
    filename = ndb.StringProperty(verbose_name=u"filename")
    fileextension = ndb.StringProperty(verbose_name=u"fileextension")
    media = ndb.StringProperty(verbose_name=u"media")
    pos = ndb.StringProperty(verbose_name=u"pos")
    thumbnailurl = ndb.StringProperty(verbose_name=u"thumbnailurl")
    bloburl = ndb.StringProperty(verbose_name=u"bloburl")
    html = ndb.StringProperty(verbose_name=u"html")
    blobKey = ndb.StringProperty(verbose_name=u"blobKey")
    shzicmi1 = ndb.StringProperty(verbose_name=u"shzicmi1")
    shzicmi2 = ndb.StringProperty(verbose_name=u"shzicmi2")
    ttmnmi = ndb.StringProperty(verbose_name=u"ttmnmi")
    date = ndb.DateTimeProperty(auto_now_add=True,verbose_name=u"date")

class blobNo(ndb.Model):
    blob_key_name = ndb.StringProperty()
    max = ndb.IntegerProperty()
    def getNextNum(self):
        @ndb.transactional
        def procedure(key):
            entity = key.get()
            if entity.max is None:
                entity.max = 0
            entity.max = entity.max + 1
            entity.put()
            return entity.max
        return procedure(self.key)

