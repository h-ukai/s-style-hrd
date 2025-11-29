# -*- coding: utf-8 -*-

from google.appengine.api import users
from google.appengine.ext import blobstore
from google.appengine.ext import db
#from google.appengine.ext import webapp
import webapp2
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp import util
import models.blob
from models.bkdata import BKdata
import email.header
import urllib
import os


class FileInfo(db.Model):
    blob = blobstore.BlobReferenceProperty(required=True)
    uploaded_by = db.UserProperty(required=True)
    uploaded_at = db.DateTimeProperty(required=True, auto_now_add=True)


class BaseHandler(webapp2.RequestHandler):
    def render_template(self, file, template_args):
        path = os.path.join(os.getcwd(), "templates", file)
        self.response.out.write(template.render(path, template_args))

    
class FileUploadFormHandler(BaseHandler):

    def get(self):
        self.render_template("upload.html", {})


class FileUploadHandler(blobstore_handlers.BlobstoreUploadHandler):
    def post(self):
        if not len(self.get_uploads(u'file')) > 0:
            self.error(404)
            return
        blob_info = self.get_uploads(u'file')[0]
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
            filename = blob_info.filename
        CorpOrg_key = self.request.get("CorpOrg_key")
        Branch_Key = self.request.get("Branch_Key")
        bkID = self.request.get("bkID")
        blobKey = str(blob_info.key())
        lobdbkey = self.setblobdb(blobKey,filename,CorpOrg_key,Branch_Key,bkID)
        self.redirect("/FileUploadFormHandler/file/%d/success" % (lobdbkey))


    def setblobdb(self,blobkey,filename,CorpOrg_key,Branch_Key,bkID):
        key_name1 = CorpOrg_key + u"/" + Branch_Key + u"/" + bkID
        bkdb = BKdata.get_by_key_name(key_name1)
        shzicmi1 = bkdb.shzicmi1
        shzicmi2 = bkdb.shzicmi2
        ttmnmi = bkdb.ttmnmi
        blobno = models.blob.blobNo.get_or_insert(key_name1,blob_key_name = key_name1)
        blobnextno = blobno.getNextNum()
        key_name2 = key_name1 + u"/" + str(blobnextno)   
        blob = models.blob.Blob.get_or_insert(key_name2)
        blob.blobNo = blobnextno
        blob.filename = filename
        blob.blobKey = blobkey
        blob.blob_key_name = key_name2
        blob.CorpOrg_key = CorpOrg_key
        blob.Branch_Key = Branch_Key
        bkID = urllib.unquote_plus(bkID).encode('raw_unicode_escape').decode('utf8')
        blob.bkID=bkID
        if shzicmi1:
            blob.shzicmi1 = shzicmi1
        else:
            blob.shzicmi1 = None
        if shzicmi2:
            blob.shzicmi2 = shzicmi2
        else:
            blob.shzicmi2 = None
        if ttmnmi:
            blob.ttmnmi = ttmnmi
        else:
            blob.ttmnmi = None
        blob.put()
        return blobnextno


    def delete(self):
        key = self.request.get('key')
        query_str = u"SELECT * FROM Blob WHERE blobKey = '" + key + "'"
        blob = db.GqlQuery (query_str)
        if blob.count()==1:
            blobstore.delete( key or '')
        blob.delete()

class AjaxSuccessHandler(BaseHandler):
    def get(self, file_id):
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.out.write('%s/FileUploadFormHandler/file/%s' % (self.request.host_url, file_id))


class FileInfoHandler(BaseHandler):
    def get(self, file_id):
        file_info = FileInfo.get_by_id(long(file_id))
        if not file_info:
            self.error(404)
            return
        self.render_template("info.html", {
                'file_info': file_info
        })


class FileDownloadHandler(blobstore_handlers.BlobstoreDownloadHandler):
    def get(self, file_id):
        file_info = FileInfo.get_by_id(long(file_id))
        if not file_info or not file_info.blob:
            self.error(404)
            return
        self.send_blob(file_info.blob, save_as=True)


class GenerateUploadUrlHandler(BaseHandler):
    def get(self):
        urlstr = ""
        CorpOrg_key = self.request.get("CorpOrg_key")
        urlstr += "CorpOrg_key=" + CorpOrg_key
        Branch_Key = self.request.get("Branch_Key")
        urlstr += "&Branch_Key=" + Branch_Key
        bkID = self.request.get("bkID")
        urlstr += "&bkID=" + bkID
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.out.write(blobstore.create_upload_url('/FileUploadFormHandler/upload?' + urlstr))
