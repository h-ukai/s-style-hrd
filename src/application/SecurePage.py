# -*- coding: utf-8 -*-

import os
from SecurePageBase import SecurePageBase
from google.appengine.ext.webapp import template

class SecurePage(SecurePageBase):

    def Secure_init(self,*status,**kwargs):
        SecurePageBase.Secure_init(self,**kwargs)
        if self.auth == False:
            urlstr = "corp_name=" + self.corp_name
            urlstr = urlstr + "&branch_name=" + self.branch_name
            urlstr = urlstr + "&sitename=" + self.Sitename
            urlstr = urlstr + "&togo=" + self.request.path
            urlstr = urlstr + "&userpagebase=" + self.tmpl_val['userpagebase']
#           ssn.set_ssn_data("togo", urllib.quote_plus(self.request.path))
            self.redirect(str('/login?' + urlstr))
            return
        if not self.tmpl_val["status"] in status:
            self.tmpl_val['error_msg'] = u'必要なステータスがありません'
            templ = self.corp_name + "/" + self.branch_name + "/" + self.Sitename + "/" + "sorry.html"
            path = os.path.dirname(__file__) + '/../templates/' + templ
            self.response.out.write(template.render(path, self.tmpl_val))
            return False
        return True

    def get(self,**kwargs):
        pass

    def post(self,**kwargs):
        self.get(**kwargs)