# -*- coding: utf-8 -*-
'''
Created on 2011/02/05

@author: casper
'''
from google.appengine.ext import db
import CorpOrg

class Branch(db.Model):
    Branch_Key_name = db.StringProperty()
    corp = db.ReferenceProperty(CorpOrg.CorpOrg)
    name = db.StringProperty()
    zip = db.StringListProperty()
    address = db.PostalAddressProperty()
    phone = db.PhoneNumberProperty()
    fax = db.PhoneNumberProperty()
    Qualification = db.StringListProperty() #会員　資格
    masterID = db.StringProperty()
    masterPass=db.StringProperty()
    bkdata_max_num = db.IntegerProperty()
    active = db.BooleanProperty(default=True)

    def getNextNum(self):
        def procedure():
            if self.bkdata_max_num is None:
                self.bkdata_max_num = 0
            self.bkdata_max_num = self.bkdata_max_num + 1
            self.put()
            return self.bkdata_max_num
        return db.run_in_transaction(procedure)