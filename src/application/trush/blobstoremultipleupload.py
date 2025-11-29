# -*- coding: utf-8 -*-
#
# jQuery File Upload Plugin GAE Python Example 1.1.4
# https://github.com/blueimp/jQuery-File-Upload
#
# Copyright 2011, Sebastian Tschan
# https://blueimp.net
#
# Licensed under the MIT license:
# https://www.opensource.org/licenses/MIT
#

from __future__ import with_statement
from google.appengine.api import files, images
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers
import json, re, urllib
#from google.appengine.dist import use_library
#use_library('django', '1.2')
from django.utils import simplejson
#from google.appengine.ext import webapp
import webapp2
import models.blob
import email.header
from google.appengine.ext import db

WEBSITE = 'https://lcalhost:8080/test2.html'
MIN_FILE_SIZE = 1 # bytes
MAX_FILE_SIZE = 20000000 # 20Mbytes
IMAGE_TYPES = re.compile('image/(gif|p?jpeg|(x-)?png)')
ACCEPT_FILE_TYPES = IMAGE_TYPES
THUMBNAIL_MODIFICATOR = '=s80' # max width / height
EXPIRATION_TIME = 300 # seconds

def cleanup(blob_keys):
    blobstore.delete(blob_keys)

class UploadHandler(webapp2.RequestHandler):

    
    def initialize(self, request, response):
        super(UploadHandler, self).initialize(request, response)
        self.response.headers['Access-Control-Allow-Origin'] = '*'
        self.response.headers[
            'Access-Control-Allow-Methods'
        ] = 'OPTIONS, HEAD, GET, POST, PUT, DELETE'
    
    def validate(self, file):
        if file['size'] < MIN_FILE_SIZE:
            file['error'] = 'minFileSize'
        elif file['size'] > MAX_FILE_SIZE:
            file['error'] = 'maxFileSize'
        #elif not ACCEPT_FILE_TYPES.match(file['type']):
            #file['error'] = 'acceptFileTypes'
        else:
            return True
        return False
    
    def get_file_size(self, file):
        file.seek(0, 2) # Seek to the end of the file
        size = file.tell() # Get the position of EOF
        file.seek(0) # Reset the file position to the beginning
        return size
    
    def write_blob(self, data, info):
        blob = files.blobstore.create(
            mime_type=info['type'],
            _blobinfo_uploaded_filename=info['name']
        )
        with files.open(blob, 'a') as f:
            f.write(data)
        files.finalize(blob)
        return files.blobstore.get_blob_key(blob)
    
    def handle_upload(self):
        results = []
        blob_keys = []
        for name, fieldStorage in self.request.POST.items():
            if type(fieldStorage) is unicode:
                continue
            result = {}
            result['name'] = re.sub(r'^.*\\', '',
                fieldStorage.filename)
            result['type'] = fieldStorage.type
            result['size'] = self.get_file_size(fieldStorage.file)
            if self.validate(result):
                blob_key = str(
                    self.write_blob(fieldStorage.value, result)
                )
                blob_keys.append(blob_key)
                result['delete_type'] = 'DELETE'
                result['delete_url'] = self.request.host_url +\
                    '/?key=' + urllib.quote(blob_key, '')
                if (IMAGE_TYPES.match(result['type'])):
                    try:
                        result['url'] = images.get_serving_url(
                            blob_key,
                            secure_url=self.request.host_url\
                                .startswith('https')
                        )
                        result['thumbnail_url'] = result['url'] +\
                            THUMBNAIL_MODIFICATOR
                    except: # Could not get an image serving url
                        pass
                if not 'url' in result:
                    result['url'] = self.request.host_url +\
                        '/' + blob_key + '/' + urllib.quote(
                            result['name'].encode('utf-8'), '')
            results.append(result)
        """
        #あとで消す
        deferred.defer(
            cleanup,
            blob_keys,
            _countdown=EXPIRATION_TIME
        )
        """
        return results
    
    def options(self):
        pass
        
    def head(self):
        pass
    
    def get(self,arg):
        self.redirect(WEBSITE)
    
    def post(self,arg):
        if (self.request.get('_method') == 'DELETE'):
            return self.delete()
        s = simplejson.dumps(self.handle_upload(), separators=(',',':'))
        redirect = self.request.get('redirect')
        if redirect:
            return self.redirect(str(
                redirect.replace('%s', urllib.quote(s, ''), 1)
            ))
        if 'application/json' in self.request.headers.get('Accept'):
            self.response.headers['Content-Type'] = 'application/json'
        self.response.out.write(s)

    def setblobdb(self,blobkey,filename,CorpOrg_key,Branch_Key,bkID,shzicmi1=None,shzicmi2=None,ttmnmi=None):
        key_name1 = CorpOrg_key + u"/" + Branch_Key + u"/" + bkID
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


    def delete(self):
        key = self.request.get('key')
        query_str = u"SELECT * FROM Blob WHERE blobKey = '" + key + "'"
        blob = db.GqlQuery (query_str)
        if blob.count()==1:
            blobstore.delete( key or '')
        blob.delete()


class DownloadHandler(blobstore_handlers.BlobstoreDownloadHandler):
    def get(self, key, filename):
        if not blobstore.get(key):
            self.error(404)
        else:
            # Cache for the expiration time:
            self.response.headers['Cache-Control'] =\
                'public,max-age=%d' % EXPIRATION_TIME
            self.send_blob(key, save_as=filename)
