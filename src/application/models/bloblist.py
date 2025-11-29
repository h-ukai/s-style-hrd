# -*- coding: utf-8 -*-
#

from google.appengine.ext import db

class Bloblist(db.Model):
    bloblist_key_name = db.StringProperty()
    CorpOrg_key = db.StringProperty()
    Branch_Key = db.StringProperty()
    bkID = db.StringProperty()
    blobNo = db.IntegerProperty()
    blobkind = db.StringProperty()
    title = db.StringProperty()
    content = db.StringProperty(multiline=True)
    filename = db.StringProperty()
    media = db.StringProperty()
    pos = db.StringProperty()
    thumbnailurl = db.StringProperty()
    bloburl = db.StringProperty()
    html =  db.StringProperty()
    blobKey = db.StringProperty()
    date = db.DateTimeProperty(auto_now_add=True)
    shzicmi1 = db.StringProperty()
    shzicmi2 = db.StringProperty()


class bloblistNo(db.Model):
    bloblist_key_name = db.StringProperty()
    max = db.IntegerProperty()
    def getNextNum(self):
        def procedure():
            if self.max is None:
                self.max = 0
            self.max = self.max + 1
            self.put()
            return self.max
        return db.run_in_transaction(procedure)