#!/usr/local/bin/python
# -*- coding: utf-8 -*-
#from google.appengine.dist import use_library
#use_library('django', '1.2')

#from google.appengine.ext import webapp
import webapp2
import os
from google.appengine.ext.webapp import template
from models import bkdata
from models import CorpOrg
from models import Branch
from google.appengine.ext import db

#os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
#
class bkdchk(webapp2.RequestHandler):
    def get(self):
        shzicmi1 = self.request.get("shzicmi1")
        shzicmi2 = self.request.get("shzicmi2")
        bkID = self.request.get("bkID")
        self.corp = u"s-style"
        self.branch = u"hon"
        bkdb = None
        if bkID:
            key_name = self.corp + u"/" + self.branch + u"/" + bkID
            bkdb = bkdata.BKdata.get_or_insert(key_name,bkID=bkID)            
        Default = {"tdufknmi":u"愛知県"}
        self.tmpl_val = {
                         u"current":bkdb,
                         u"def":Default,
                         u"shzicmi1":shzicmi1,
                         u"shzicmi2":shzicmi2
                         }
        if bkdb:
            if bkdb.snyuMnskSyuBbnMnsk2:
                self.tmpl_val["snyuMnskSyuBbnMnsk2"] = bkdb.snyuMnskSyuBbnMnsk2
            elif bkdb.tcMnsk2:
                self.tmpl_val["tcMnsk2"] = bkdb.tcMnsk2
        
        
        path = os.path.dirname(__file__) + '/../templates/bkdchk.html'
        self.response.out.write(template.render(path, self.tmpl_val))

    def post(self):

        self.get()