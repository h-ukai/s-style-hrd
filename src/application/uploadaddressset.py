# -*- coding: utf-8 -*-

# テスト用URL
# https://localhost:8080/csvupload/addressset.html
#from google.appengine.ext import webapp
import webapp2
from google.appengine.ext.webapp import template

import os
import csv
import sys
import datetime
from models.bksearchaddress import bksearchaddresslist
from models.bksearchaddress import *
from StringIO import StringIO

class addresssetupload(webapp2.RequestHandler):

    l=0
    e=0
    message = []
    date = ''
    def __init__(self,request, response):
        self.initialize(request, response)
        self.tmpl_val = {}
        self.tmpl_val['error_msg'] = ''
        self.auth = False
        self.corp_name= u"s-style"
        self.branch_name = u"hon"
    
    def get(self,**kwargs):
        self.source = self.request.get("source")
        self.tmpl_val ['source'] = self.source
        self.tmpl_val ['result'] = self.message 
        
        path = os.path.dirname(__file__) + '/../templates/uploadadresslist.html'
        self.response.out.write(template.render(path, self.tmpl_val))

    """
   
    def ntos(n):
        return unicode(n).translate(fulltable) if n != 0 else ''
    """
    
# アップロードしたCSVファイル内容をデータストアへ保存
    def post(self,**kwargs):
        self.message = []
        self.date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        rawfile = self.request.get('file')
        csvfile = csv.reader(StringIO(rawfile))
        enc = 'cp932' #アップロードデータはSift-Jis
        name = None
        list = None
        for cont in csvfile  :
            self.l +=1
            if self.l==1:
                continue #一行目強制読み飛ばし
            if len(cont) > 0 :
                self.e = 0
                try:
                    if name != self.nunicode(cont[1], enc):
                        division = self.nunicode(cont[0], enc)
                        name = self.nunicode(cont[1], enc)
                        list = bksearchaddresslist(division = division , name = name , co = self.corp_name , br = self.branch_name)
                        list.put()
                    list.setadset(self.nunicode(cont[2], enc), self.nunicode(cont[3], enc), self.nunicode(cont[4], enc))
                    self.e+=1
                    self.message.append("DataPutSuccess:line" + str(self.l) +"・・・・・OK")
                except Exception:
                    self.message.append("DataPutError:line" + str(self.l) + " elements" + str(self.e) + u":" + str(str(sys.exc_info()[0])))
                    continue
                
        self.get(**kwargs)

    def nunicode(self,text,enc):
        try:
            result = None
            if text != None and text != "":
                result = unicode(text, enc,errors='replace')
        except Exception:
            self.message.append(u"error:line" + str(self.l) +" elements" + str(self.e) + " :" + str(sys.exc_info()[0]))
        finally:
            return result

class MyError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)