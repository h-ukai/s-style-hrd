# -*- coding: utf-8 -*-

import os
#from google.appengine.ext import webapp
import webapp2
from google.appengine.ext.webapp import template

from models.member import member
from models.bksearchdata import bksearchdata
from models.bkdata import BKdata
from models.CorpOrg import CorpOrg
from models.Branch import Branch
from models.bksearchaddress import *
from models.bksearchmadori import bksearchmadori
from dataProvider.bkdataSearchProvider import bkdataSearchProbider
from bksearchensenutl import bksearchensenutl


import datetime
import re
from bksearchutl import bksearchutl
import timemanager
from SecurePage import SecurePage
from wordstocker import wordstocker
class bksearch(SecurePage):


    def get(self,**kwargs):

        if self.Secure_init(*[u"管理者",u"担当"],**kwargs):
            bksp = bkdataSearchProbider(self.corp_name,self.branch_name,self.memberID,self.userID,self.userkey,self.memdb,self.tmpl_val,self.request)
            self.tmpl_val = bksp.get(**kwargs)
            path = os.path.dirname(__file__) + '/../templates/' + self.dirpath
            self.response.out.write(template.render(path, self.tmpl_val))

    def post(self,**kwargs):

        if self.Secure_init(*[u"管理者",u"担当"],**kwargs):
            """
            if kwargs == None:
                kwargs = {}
            """
            submit = self.request.get("submit")
            bksp = bkdataSearchProbider(self.corp_name,self.branch_name,self.memberID,self.userID,self.userkey,self.memdb,self.tmpl_val,self.request)
            kwargs = bksp.post(**kwargs)

            if submit == u"検索" or submit == "search" or submit == u"新規ページへ保存して検索" or submit == u"検索2" or submit == "search2" or submit == u"新規ページへ保存して検索2" or submit == u"検索3" or submit == "search3" or submit == u"新規ページへ保存して検索3" or submit == u"全ページ一括検索" or submit == "allpagesearch" or submit == u"全ページ一括検索2" or submit == "allpagesearch2":
                self.redirect(str("/follow/" + self.corp_name + "/" + self.branch_name + "/"+ self.Sitename +"/follow.html?memberID=" + self.memberID))
                return

            self.get(**kwargs)
