#!/usr/local/bin/python
# -*- coding: utf-8 -*-

#from google.appengine.ext import webapp
import webapp2
import os
from google.appengine.ext.webapp import template


#os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
#from google.appengine.dist import use_library
#use_library('django', '1.2')

class bkjoukyoulist(webapp2.RequestHandler):
    def get(self):
        self.tmpl_val = {}
        
        
        path = os.path.dirname(__file__) + '/../templates/bkjoukyoulist.html'
        self.response.out.write(template.render(path, self.tmpl_val))

    def post(self):

        self.get()