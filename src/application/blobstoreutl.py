# -*- coding: utf-8 -*-
#from google.appengine.dist import use_library
#use_library('django', '1.2')

import os.path
import urllib
from google.appengine.ext import blobstore
#from google.appengine.ext import webapp
import webapp2
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.ext.webapp import template
from google.appengine.api.images import get_serving_url
import sys
import email.header
from models.bkdata import BKdata

from google.appengine.ext import db
import models.blob

class BlobstoreUtlHandler(webapp2.RequestHandler):
    def get(self):
        path = self.request.path
        pathParts = path.split(u'/')
        CorpOrg_key  = pathParts[2]
        Branch_Key = pathParts[3]
        bkID = pathParts[4]
        keypath =  CorpOrg_key + u"/" + Branch_Key + u"/" + bkID
        # アップロード用の URL を作成
        # アップロードに成功したら /upload に移動させる
        #upload_url = blobstore.create_upload_url('/upload/')
        upload_url = blobstore.create_upload_url(u'/upload/' + keypath)
        edit_url = u"/upload/" + keypath
        multiupload_url = u"/FileUploadFormHandler?CorpOrg_key=" + CorpOrg_key + u"&Branch_Key=" + Branch_Key + u"&bkID=" + bkID
        # Blobstore に保存されているファイルを取得
        bkID = urllib.unquote_plus(pathParts[4]).encode('raw_unicode_escape').decode('utf8')
        query_str = u"SELECT * FROM Blob WHERE CorpOrg_key = '" + CorpOrg_key + u"' AND Branch_Key = '" + Branch_Key  + u"' AND bkID = '" + bkID + u"' ORDER BY  media, pos ASC"
        blobs = db.GqlQuery (query_str)
        mblobs = []
        cblobs = []
        chk = ""
        if blobs.count()>=1:
            chk = blobs[0].media
            for blob in blobs:
                if blob.filename and blob.html==None:
                    root, ext = os.path.splitext(blob.filename)
                    ext = ext.lower().strip(".")
                    blob.fileextension = ext
                    if (ext == u"jpeg") or (ext == u"jpg") or (ext == u"png") or (ext == u"gif") or (ext == u"bmp"):
                        try:
                            blob.thumbnailurl = get_serving_url(blob.blobKey,size=100,crop=False)
                            blob.bloburl = get_serving_url(blob.blobKey)
                            blob.html = u"<a href=\"" + blob.bloburl + u"\"  target=\"_blank\" ><img src=\"" + blob.thumbnailurl + u"\" title=\"" + blob.filename + u"\" /></a>"
                        finally:
                            pass
                    else:
                        blob.bloburl = u"/serve/" + blob.blobKey + u"/" + blob.filename
                        blob.html = u"<a href=\"" + blob.bloburl + u"\">" +  blob.filename + u"</a>"
                    blob.put()
                if chk != blob.media:
                    mblobs.append({"media":chk,"cblob":cblobs})
                    chk = blob.media
                    cblobs = []
                cblobs.append(blob)
            mblobs.append({"media":blob.media,"cblob":cblobs})
        key_name = CorpOrg_key + u"/" + Branch_Key + u"/" + bkID
        bkdb = BKdata.get_or_insert(key_name,bkID=bkID)
        tempblobs1 = []
        tempblobs2 = []
        if bkdb.shzicmi1 and bkdb.shzicmi2:
            where = u" WHERE CorpOrg_key = '" + CorpOrg_key + u"'"
            where += u" AND shzicmi1 = '" + bkdb.shzicmi1 + u"'"
            where += u" AND shzicmi2 = '" + bkdb.shzicmi2 + u"'"
            query_str = u"SELECT * FROM Blob" + where + u" ORDER BY  bkID, media, pos ASC"
            tempblobs1 = db.GqlQuery (query_str)
        for b in tempblobs1:
            for t in tempblobs2:
                if b.blobKey == t.blobKey:
                    break
            else:
                tempblobs2.append(b)

        if bkdb.ttmnmi:
            where = u" WHERE CorpOrg_key = '" + CorpOrg_key + u"'"
            where += u" AND ttmnmi = '" + bkdb.ttmnmi + u"'"
            query_str = u"SELECT * FROM Blob" + where + u" ORDER BY  bkID, media, pos ASC"
            tempblobs1 = db.GqlQuery (query_str)

        for b in tempblobs1:
            for t in tempblobs2:
                if b.blobKey == t.blobKey:
                    break
            else:
                tempblobs2.append(b)
        # テンプレートを使って出力
        data = dict(
                blobs=mblobs,
                upload_url=upload_url,
                edit_url=edit_url,
                samples = tempblobs2,
                multiupload_url = multiupload_url,
                bkID = bkID
                )
        #path = os.path.dirname(__file__) + '../templates/blobstoreutl.html'
        path = os.path.join(os.path.dirname(__file__), u'../templates/blobstoreutl.html')
        self.response.out.write(template.render(path, data))


class UploadHandler(blobstore_handlers.BlobstoreUploadHandler):
    def post(self):
        path = self.request.path
        pathParts = path.split(u'/')
        key_name1 = pathParts[2] + u"/" + pathParts[3] + u"/" + pathParts[4]
        key_name2 =""
        if len(pathParts) > 5:
            key_name2 = key_name1 + u"/" + pathParts[5]
        else:
            blobno = models.blob.blobNo.get_or_insert(key_name1,blob_key_name = key_name1)
            blobnextno = blobno.getNextNum()
            key_name2 = key_name1 + u"/" + str(blobnextno)

        str1 = self.request.get(u"submit")
        if str1==u"削除":
            self.delete(key_name2,key_name1)
            return

        blob = models.blob.Blob.get_or_insert(key_name2)
        if not blob.blobNo:
            blob.blobNo = blobnextno

    # Blobstore にアップロードされたファイルの情報を取得
        blob_info = self.get_uploads(u'file')
        """
        blobstore_handlers.BlobstoreUploadHandler の self.get_uploads で取得した
        blob_info.filename は確かに"=?ISO-2022-JP?B?.." だし、長いファイル名だと
                    ぶち切れている。
                    しかし、blobstore.BlobInfo.get(blob_info.key()) して、しっかり取得すると
                    デコード済みなファイル名を完璧に取得できる。
        if len(files)>0:
            blob_info = files[0]
            s = blob_info.filename
            for line in email.header.decode_header(s):
                blob.filename = line[0].decode(line[1] if line[1] else 'utf-8')
            blob.blobKey = str(blob_info.key())
        """
        if blob_info:
            blob_info = blobstore.BlobInfo.get(blob_info.key())
            blob.filename = blob_info.filename
        else:
            if str1==u"登録":
                self.redirect(str(u'/BlobstoreUtl/%s' % key_name1))
                return
            if str1==u"追加":
                bloburl = self.request.get(u"bloburl")
                if bloburl and bloburl!=u"None":
                    blob.bloburl = bloburl
                thumbnailurl = self.request.get(u"thumbnailurl")
                if thumbnailurl and thumbnailurl!=u"None":
                    blob.thumbnailurl = thumbnailurl
                filename = self.request.get(u"filename")
                if filename and filename!=u"None":
                    blob.filename = filename
                html = self.request.get(u"html")
                if html and html!=u"None":
                    blob.html = html
                blobKey = self.request.get(u"blobKey")
                if blobKey and blobKey!=u"None":
                    blob.blobKey = blobKey

        blob.blob_key_name = key_name2
        blob.CorpOrg_key = pathParts[2]
        blob.Branch_Key = pathParts[3]
        bkID = urllib.unquote_plus(pathParts[4]).encode('raw_unicode_escape').decode('utf8')
#        bkID = pathParts[4]
        key_name = blob.CorpOrg_key + u"/" + blob.Branch_Key + u"/" + bkID
        bkdb = BKdata.get_or_insert(key_name,bkID=bkID)

        shzicmi1 = u"None"
        shzicmi2 = u"None"
        ttmnmi = u"None"
        if bkdb.shzicmi1:
            shzicmi1 = bkdb.shzicmi1
        if bkdb.shzicmi2:
            shzicmi2 = bkdb.shzicmi2
        if bkdb.ttmnmi:
            ttmnmi = bkdb.ttmnmi

        blob.bkID = bkID
        blobkind = self.request.get(u"blobkind")
        if blobkind and blobkind!=u"None":
            blob.blobkind = blobkind
        else:
            blob.blobkind = None
        title = self.request.get(u"title")
        if title and title != u"None":
            blob.title = title
        else:
            blob.titlel = None
        content = self.request.get(u"content")
        if content and content != u"None":
            blob.content = content
            ext = blob.fileextension
            if not ext:
                root, ext = os.path.splitext(blob.filename)
                ext = ext.lower().strip(".")
                blob.fileextension = ext

            if (ext == u"jpeg") or (ext == u"jpg") or (ext == u"png") or (ext == u"gif") or (ext == u"bmp"):
                try:
                    blob.thumbnailurl = get_serving_url(blob.blobKey,size=100,crop=False)
                    blob.bloburl = get_serving_url(blob.blobKey)
                    blob.html = u"<a href=\"" + blob.bloburl + u"\"  target=\"_blank\" >"
                    if blob.thumbnailurl:
                        blob.html += u"<img src=\"" + blob.thumbnailurl + u"\""
                        if blob.title:
                            blob.html += u"title=\"" + blob.title
                        if blob.content:
                            blob.html += ":" + blob.content
                        blob.html +=  u"\" />"
                    blob.html += u"</a>"
                except:
                    blob.html = u"error"
                """
            if (ext == u"jpeg") or (ext == u"jpg") or (ext == u"png") or (ext == u"gif") or (ext == u"bmp"):
                try:
                    blob.thumbnailurl = get_serving_url(blob.blobKey,size=100,crop=False)
                    blob.bloburl = get_serving_url(blob.blobKey)
                    blob.html = u"<a href=\"" + blob.bloburl + u"\"  target=\"_blank\" ><img src=\"" + blob.thumbnailurl + u"\" title=\"" + blob.title + ":" + blob.content + u"\" /></a>"
                except:
                    pass
                """
            else:
                blob.bloburl = u"/serve/" + blob.blobKey + u"/" + blob.filename
                blob.html = u"<a href=\"" + blob.bloburl + u"\">" +  blob.filename + u"</a>"

        else:
            blob.content = None
        media = self.request.get(u"media")
        if media and media != u"None":
            blob.media = media
        else:
            blob.media = None
        pos = self.request.get(u"pos")
        if pos and pos != u"None":
            blob.pos = pos
        else:
            blob.pos = None
        if shzicmi1 and shzicmi1 != u"None":
            blob.shzicmi1 = shzicmi1
        else:
            blob.shzicmi1 = None
        if shzicmi2 and shzicmi2 != u"None":
            blob.shzicmi2 = shzicmi2
        else:
            blob.shzicmi2 = None
        if ttmnmi and ttmnmi != u"None":
            blob.ttmnmi = ttmnmi
        else:
            blob.ttmnmi = None

        blob.put()
        # ファイル表示用の URL へリダイレクト
        #self.redirect('/serve/%s' % blob_info.key())
        self.redirect(str(u'/BlobstoreUtl/%s' % key_name1))

    def delete(self,key_name,path):
    # Blobstore にアップロードされたファイルの情報を取得
        try:
            #self.response.out.write(key_name)
            blob = models.blob.Blob.get_by_key_name(key_name)
            if blob:
                if blob.blobKey:
                    query_str = u"SELECT * FROM Blob WHERE blobKey = '" + blob.blobKey + "'"
                    tempblobs2 = db.GqlQuery (query_str)
                    if tempblobs2.count()==1:
                        blob_info = blobstore.get(blob.blobKey)
                        if blob_info:
                            blob_info.delete()
                blob.delete()
                self.redirect(str(u'/BlobstoreUtl/%s' % path))
            #self.response.out.write(blob)
        except Exception, e:
            self.response.out.write(repr(e)+'\n')
        # ファイル表示用の URL へリダイレクト
        #self.redirect('/serve/%s' % blob_info.key())
        #self.redirect(u'/BlobstoreUtl/%s' % path)

class ServeHandler(blobstore_handlers.BlobstoreDownloadHandler):
    def get(self, blob_key):
        blob_key = str(urllib.unquote(blob_key)).split("/")[0]

        # BlobKeyを指定してファイルを取得
        blob_info = blobstore.BlobInfo.get(blob_key)

        # 結果をクライアントに返す
        self.send_blob(blob_info)


