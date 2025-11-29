# -*- coding: utf-8 -*-

import os
#from google.appengine.ext import webapp
import webapp2
from google.appengine.ext.webapp import template

from SecurePage import SecurePage
from models.member import member

class follow(SecurePage):

    def get(self,**kwargs):
        if self.Secure_init(*[u"管理者",u"担当"],**kwargs):
            if self.memberID == "" or not self.memberID:
                self.memberID = self.userID
                key_name = self.corp_name + "/" + self.memberID
                self.memdb = member.get_by_key_name(key_name)
                self.tmpl_val["membertel"]=self.memdb.phone
                self.tmpl_val["membermail"]=self.memdb.mail
                self.tmpl_val["memberyomi"]=self.memdb.yomi
                self.tmpl_val["membername"]=self.memdb.name
                self.tmpl_val["memberID"]= self.memberID
            path = os.path.dirname(__file__) + '/../templates/' + self.dirpath
            self.response.out.write(template.render(path, self.tmpl_val))

    def post(self,**kwargs):

        self.get(**kwargs)