# -*- coding: utf-8 -*-

from google.appengine.ext import db

class CorpOrg(db.Model):
    CorpOrg_key_name = db.StringProperty() 
    name = db.StringProperty()
    zip = db.StringListProperty()
    address = db.PostalAddressProperty()
    phone = db.PhoneNumberProperty()
    fax = db.PhoneNumberProperty()
    Qualification = db.StringListProperty()
    masterID = db.StringProperty()
    masterPass=db.StringProperty()
    memberID_max_num = db.IntegerProperty()
    active = db.BooleanProperty(default = True)
    tourokunengappi = db.DateTimeProperty(auto_now_add = True)
    
    def getNextIDNum(self):
        def procedure():
            if self.memberID_max_num is None:
                self.memberID_max_num = 0
            self.memberID_max_num += 1
            self.put()
            return self.memberID_max_num
        return db.run_in_transaction(procedure)