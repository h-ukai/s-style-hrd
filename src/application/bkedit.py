#!/usr/local/bin/python
# -*- coding: utf-8 -*-
#

'''

 1 class JsonField(CharField):
 2     """ JSONデータをポストする場合のフィールド。AJAXに便利かも """
 3     
 4     def __init__(self, *args, **kwargs):
 5         super(JsonField, self).__init__(*args, **kwargs)
 6 
 7     def clean(self, value):
 8         from google.appengine.dist import use_library
use_library('django', '1.2')
from django.utils import simplejson
 9         value = super(JsonField, self).clean(value)
10         try:
11             json_data = simplejson.loads(value)
12         except Exception, e:
13             raise ValidationError(self.error_messages['invalid'])
14         return json_data

セレクトボックスや、チェックボックスで複数チェックされてリクエストされた場合に、チェックされた全ての値を読み取るには、
request.POST.getlist(キー)
とやる。キーに対応する全ての値がリストで貰える。
https://djangoproject.jp/doc/ja/1.0/ref/request-response.html

'''
#from google.appengine.dist import use_library
#use_library('django', '1.2')

import os
#from google.appengine.ext import webapp
import webapp2
from google.appengine.ext.webapp import template
from models import bkdata
from models import Branch
from google.appengine.ext import db
import datetime
import re

from dataProvider.bkdataProvider import bkdataProvider
from application.timemanager import utc2jst_date
from wordstocker import wordstocker
#timemanager.utc2jst_date(utc)
#timemanager.jst2utc_date(jst)

#os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
#from google.appengine.dist import use_library
#use_library('django', '1.2')

class BKEdit(webapp2.RequestHandler):

    #corp = CorpOrg.CorpOrg()
    #branch = Branch.Branch()

    def __init__(self,request, response):
        self.initialize(request, response)
        self.tmpl_val = {}
        self.tmpl_val['error_msg'] = ''
        self.auth = False
        
        #self.corp = CorpOrg.CorpOrg.get_or_insert(u"s-style",CorpOrg_key_name = u"s-style")
        #self.branch = Branch.Branch.get_or_insert(u"s-style/hon",parent = self.corp,Branch_Key_name = u"s-style/hon")
        self.corp_name= u"s-style"
        self.branch_name = u"hon"
    def get(self,**kwargs):
        #file = open('example_12.json') #.read().decode('utf8')
        '''
            file = codecs.open('example_12.json', 'r', 'shift_jis')
            a = simplejson.load(file)
            print a
        '''
        bkdp=None
        if kwargs.get(u"bkID",None) == None:
            bkID = self.request.get(u"bkID")
            if bkID:
                bkdp = bkdataProvider(self.corp_name,self.branch_name)
                bkdp.search(bkID)

        else :
            bkID =kwargs.get(u"bkID",None)
            bkdp = bkdataProvider(self.corp_name,self.branch_name)
            bkdp.set(bkID)

        bkdb = {}
        blobs = {}
        """
            [1989,u"平成",1],
            [1988,u"昭和",63],
            [1926,u"昭和",1]
        """
        nengolist = []
        #昭和年号作成
        for i in range(1926, 1989):
            nengolist.insert(0, [i,u"昭和",i-1925])        
        #平成年号作成
        for i in range(1989, 2019):
            nengolist.insert(0, [i,u"平成",i-1988])
        #令和年号作成
        now = utc2jst_date(datetime.datetime.now()) # datetime.datetime(2009, 7, 8, 22, 59, 0, 688787)
        for i in range(2019, now.year+2):
            nengolist.insert(0, [i,u"令和",i-2018])
        
        cknngtSirkYY = None
        zukickNngt1YY = None
        zukickNngt2YY = None
        zukickNngt3YY = None
        kujKnryuNngtSirkYY = None
        kujKnryuNngtSirkGG = None
        gnkyuYtiNngtYY = None
        gnkyuYtiNngtGG = None
        hkwtsNyukyNngtSirkYY = None
        hkwtsNyukyNngtSirkGG = None
        nyukyNngtSirkYY = None
        nyukyNngtSirkGG = None
        trhkJyuknYukuKgnYY = None
        trhkJyuknYukuKgnGG = None
        bikiKiykNngppSirkYY = None
        bikiKiykNngppSirkGG = None
        shkcKgnSirkYY = None
        shkcKgnSirkGG = None
        
        if bkdp:
            bkdb = bkdp.bkdb
            blobs = bkdp.blobs
            cknngtSirkYY = bkdp.cknngtSirkYY
            zukickNngt1YY = bkdp.zukickNngt1YY
            zukickNngt2YY = bkdp.zukickNngt2YY
            zukickNngt3YY = bkdp.zukickNngt3YY
            if bkdb.kujKnryuNngtSirk and bkdb.kujKnryuNngtSirk.year > 2018:
                kujKnryuNngtSirkYY=bkdb.kujKnryuNngtSirk.year-2018
                kujKnryuNngtSirkGG = "R"
            elif bkdb.kujKnryuNngtSirk :
                kujKnryuNngtSirkYY=bkdb.kujKnryuNngtSirk.year-1988
                kujKnryuNngtSirkGG = "H"
                 
            if bkdb.gnkyuYtiNngt and bkdb.gnkyuYtiNngt.year > 2018:
                gnkyuYtiNngtYY = bkdb.gnkyuYtiNngt.year-2018
                gnkyuYtiNngtGG = "R"
            elif bkdb.gnkyuYtiNngt:
                gnkyuYtiNngtYY = bkdb.gnkyuYtiNngt.year-1988
                gnkyuYtiNngtGG = "H"
    
            if bkdb.hkwtsNyukyNngtSirk and bkdb.hkwtsNyukyNngtSirk.year > 2018:
                hkwtsNyukyNngtSirkYY = bkdb.hkwtsNyukyNngtSirk.year-2018
                hkwtsNyukyNngtSirkGG = "R"
            elif bkdb.hkwtsNyukyNngtSirk:
                hkwtsNyukyNngtSirkYY = bkdb.hkwtsNyukyNngtSirk.year-1988
                hkwtsNyukyNngtSirkGG = "H"
    
            if bkdb.nyukyNngtSirk and bkdb.nyukyNngtSirk.year > 2018:
                nyukyNngtSirkYY = bkdb.nyukyNngtSirk.year-2018
                nyukyNngtSirkGG = "R"
            elif bkdb.nyukyNngtSirk:
                nyukyNngtSirkYY = bkdb.nyukyNngtSirk.year-1988
                nyukyNngtSirkGG = "H"
    
            if bkdb.trhkJyuknYukuKgn and bkdb.trhkJyuknYukuKgn.year > 2018:
                trhkJyuknYukuKgnYY = bkdb.trhkJyuknYukuKgn.year-2018
                trhkJyuknYukuKgnGG = "R"
            elif bkdb.trhkJyuknYukuKgn:
                trhkJyuknYukuKgnYY = bkdb.trhkJyuknYukuKgn.year-1988
                trhkJyuknYukuKgnGG = "H"
    
            if bkdb.bikiKiykNngppSirk and bkdb.bikiKiykNngppSirk.year > 2018:
                bikiKiykNngppSirkYY = bkdb.bikiKiykNngppSirk.year-2018
                bikiKiykNngppSirkGG = "R"
            elif bkdb.bikiKiykNngppSirk :
                bikiKiykNngppSirkYY = bkdb.bikiKiykNngppSirk.year-1988
                bikiKiykNngppSirkGG = "H"
    
            if bkdb.shkcKgnSirk and bkdb.shkcKgnSirk.year > 2018:
                shkcKgnSirkYY = bkdb.shkcKgnSirk.year-2018
                shkcKgnSirkGG = "R"
            elif bkdb.shkcKgnSirk:
                shkcKgnSirkYY = bkdb.shkcKgnSirk.year-1988
                shkcKgnSirkGG = "H"
       
        self.tmpl_val = {
                         u"bkID":bkID,
                         u"bkdb":bkdb,
                         u"blobs":blobs,
                         u"nengolist":nengolist,
                         u"cknngtSirkYY":cknngtSirkYY,
                         u"zukickNngt1YY":zukickNngt1YY,
                         u"zukickNngt2YY":zukickNngt2YY,
                         u"zukickNngt3YY":zukickNngt3YY,
                         u"kujKnryuNngtSirkGG":kujKnryuNngtSirkGG,
                         u"gnkyuYtiNngtGG":gnkyuYtiNngtGG,
                         u"hkwtsNyukyNngtSirkGG":hkwtsNyukyNngtSirkGG,
                         u"nyukyNngtSirkGG":nyukyNngtSirkGG,
                         u"trhkJyuknYukuKgnGG":trhkJyuknYukuKgnGG,
                         u"bikiKiykNngppSirkGG":bikiKiykNngppSirkGG,
                         u"shkcKgnSirkGG":shkcKgnSirkGG,
                         u"kujKnryuNngtSirkYY":kujKnryuNngtSirkYY,
                         u"gnkyuYtiNngtYY":gnkyuYtiNngtYY,
                         u"hkwtsNyukyNngtSirkYY":hkwtsNyukyNngtSirkYY,
                         u"nyukyNngtSirkYY":nyukyNngtSirkYY,
                         u"trhkJyuknYukuKgnYY":trhkJyuknYukuKgnYY,
                         u"bikiKiykNngppSirkYY":bikiKiykNngppSirkYY,
                         u"shkcKgnSirkYY":shkcKgnSirkYY,
                         u"iconlist":wordstocker.get(self.corp_name, u"アイコン")
                         }
        path = os.path.dirname(__file__) + u'/../templates/bkedit.html'
        self.response.out.write(template.render(path, self.tmpl_val))

    def post(self,**kwargs):
        
        #ログインユーザーを設定する
        bkdp = bkdataProvider(self.corp_name,self.branch_name) #(self,req,co,br,us=None):
        bkID=bkdp.put(self.request);

        kwargs = {"bkID":bkID}
        
        self.get(**kwargs)
