#!/usr/local/bin/python
# -*- coding: utf-8 -*-
#
"""Another login utility sample on Google App Engine : Proc

Author    : OKAZAKI Hiroki (okaz@teshigoto.net, https://www.teshigoto.net/)
Version   : $Id: proc.py,v 1.3 2009/02/04 08:21:15 okaz Exp $
Copyright : Copyright (c) 2009 OKAZAKI Hiroki
License   : Python
"""
import view
import session
import os
#from google.appengine.ext import webapp
import webapp2
from google.appengine.ext.webapp import template

class Proc(webapp2.RequestHandler):

    def __init__(self,request, response):
        self.initialize(request, response)
        self.tmpl_val = {}
        self.tmpl_val['error_msg'] = ''

    def get(self):
        self.post()

    def post(self):
        #
        # session management
        #
        self.tmpl_val['corp_name'] = self.request.get('corp_name')
        self.tmpl_val['branch_name'] = self.request.get('branch_name')
        self.tmpl_val['sitename'] = self.request.get('sitename')
        ssn = session.Session(self.request, self.response)
        if not ssn.chk_ssn():
            urlstr = "corp_name=" + self.tmpl_val['corp_name']
            urlstr = urlstr + "&branch_name=" + self.tmpl_val['branch_name'] 
            urlstr = urlstr + "&sitename=" + self.tmpl_val['sitename'] 
            urlstr = urlstr + "&togo=" + self.request.path
            self.redirect(str('/login?' + urlstr))
            return
        #
        # main command processing here
        #
        self.response.out.write("proc")

        #
        # view rendering
        #
        path = os.path.dirname(__file__) + '/../templates/test.html'
        self.response.out.write(template.render(path, self.tmpl_val))
