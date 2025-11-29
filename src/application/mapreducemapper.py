# -*- coding: utf-8 -*-

from google.appengine.ext import db
from google.appengine.ext import blobstore
from google.appengine.api.images import get_serving_url
import os.path

def bkdataput(entity):
    entity.put()

def bkdlistupdate(entity):
    return #安全装置
    if entity.refmes:
        msgcomb = entity.refmes.refmemlist.filter("combkind = ", "所有").fetch(1)
        if len(msgcomb):
            entity.refmem = msgcomb[0].refmem
            entity.put()

def bloburlschange(entity):
    if entity.blobKey:
        blobkey = blobstore.BlobMigrationRecord.get_new_blob_key(entity.blobKey)
        if blobkey:
            entity.blobKey = str(blobkey)
            ext = entity.fileextension
            if not ext:
                root, ext = os.path.splitext(entity.filename)
                ext = ext.lower().strip(".")
                entity.fileextension = ext
            if (ext == u"jpeg") or (ext == u"jpg") or (ext == u"png") or (ext == u"gif") or (ext == u"bmp"):
                try:
                    entity.thumbnailurl = get_serving_url(entity.blobKey,size=100,crop=False)
                    entity.bloburl = get_serving_url(entity.blobKey)
                    entity.html = u"<a href=\"" + entity.bloburl + u"\"  target=\"_blank\" >"
                    if entity.thumbnailurl:
                        entity.html += u"<img src=\"" + entity.thumbnailurl + u"\""
                        if entity.title:
                            entity.html += u"title=\"" + entity.title
                        if entity.content:
                            entity.html += u":" + entity.content
                        entity.html +=  u"\" />"
                    entity.html += u"</a>"
                except:
                    entity.html = u"error"
            else:
                entity.bloburl = u"/serve/" + entity.blobKey + u"/" + entity.filename
                entity.html = u"<a href=\"" + entity.bloburl + u"\">" +  entity.filename + u"</a>"
            entity.put()
        """ for test """
    #    return entity



def message(entity):
    return