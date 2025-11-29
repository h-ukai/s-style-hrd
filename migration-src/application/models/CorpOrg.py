# -*- coding: utf-8 -*-

from google.cloud import ndb


class CorpOrg(ndb.Model):
    CorpOrg_key_name = ndb.StringProperty()
    name = ndb.StringProperty()
    zip = ndb.StringProperty(repeated=True)
    address = ndb.StringProperty()
    phone = ndb.StringProperty()
    fax = ndb.StringProperty()
    Qualification = ndb.StringProperty(repeated=True)
    masterID = ndb.StringProperty()
    masterPass = ndb.StringProperty()
    memberID_max_num = ndb.IntegerProperty()
    active = ndb.BooleanProperty(default=True)
    tourokunengappi = ndb.DateTimeProperty(auto_now_add=True)

    def getNextIDNum(self):
        def procedure():
            if self.memberID_max_num is None:
                self.memberID_max_num = 0
            self.memberID_max_num += 1
            self.put()
            return self.memberID_max_num

        return ndb.transaction(procedure)
