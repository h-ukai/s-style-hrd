# -*- coding: utf-8 -*-
"""
Created on 2011/02/05

@author: casper
"""
from google.cloud import ndb
from application.models import CorpOrg


class Branch(ndb.Model):
    Branch_Key_name = ndb.StringProperty()
    # REVIEW-L1: Fixed KeyProperty kind parameter - should be string not class reference
    # Changed: ndb.KeyProperty(kind=CorpOrg.CorpOrg) → ndb.KeyProperty(kind='CorpOrg')
    corp = ndb.KeyProperty(kind='CorpOrg')  # Reference to CorpOrg
    name = ndb.StringProperty()
    zip = ndb.StringProperty(repeated=True)
    address = ndb.StringProperty()
    phone = ndb.StringProperty()
    fax = ndb.StringProperty()
    Qualification = ndb.StringProperty(repeated=True)  # 会員　資格
    masterID = ndb.StringProperty()
    masterPass = ndb.StringProperty()
    bkdata_max_num = ndb.IntegerProperty()
    active = ndb.BooleanProperty(default=True)

    def getNextNum(self):
        def procedure():
            if self.bkdata_max_num is None:
                self.bkdata_max_num = 0
            self.bkdata_max_num = self.bkdata_max_num + 1
            self.put()
            return self.bkdata_max_num

        return ndb.transaction(procedure)
