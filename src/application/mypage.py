# -*- coding: utf-8 -*-

import os
#from google.appengine.ext import webapp
import webapp2
from google.appengine.ext.webapp import template

from SecurePage import SecurePage
from models.member import member

class mypage(SecurePage):

    def get(self,**kwargs):
        if self.Secure_init(*[u"管理者",u"担当",u"顧客"],**kwargs):
            if self.filename == "mypagetop.html":
                path = os.path.join( os.getcwd(),'templates',self.corp_name,self.branch_name,self.Sitename,'mypagetop.html')
            self.response.out.write(template.render(path, self.tmpl_val))

    def post(self,**kwargs):

        self.get(**kwargs)