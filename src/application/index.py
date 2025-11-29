# -*- coding: utf-8 -*-

#from google.appengine.dist import use_library
#use_library('django', '1.2')


import os
import re
#from google.appengine.ext import webapp
import webapp2
from google.appengine.ext.webapp import template
from google.appengine.ext import db
from application.GqlEncoder import GqlJsonEncoder
from application.bklistutl import bklistutl
from models import bkdata
import session
from SecurePageBase import SecurePageBase
from chkauth import dbsession
import urllib
from models.bksearchaddress import getname
#os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
#from google.appengine.dist import use_library
#use_library('django', '1.2')

class index(webapp2.RequestHandler):

    def getdatabyID(self,mesid):
        CorpOrg_key = 's-style'
        if mesid:
            bkdb = bklistutl.getlistbyID(CorpOrg_key,mesid)
            if bkdb:
                bklist = bkdb.fetch(50, 0)
                lst = []
                for bkl in bklist:
                    lst.append(bkl.refbk.makedata("web"))
                return lst

    def get(self,**kwargs):

        """
        https://s-style-hrd.appspot.com/show/s-style/hon/www.chikusaku-mansion.com/bklistmesID/bklist.html?offset=0&media=web&mesID=537763
        https://s-style-hrd.appspot.com/show/s-style/hon/www.chikusaku-mansion.com/bklistmesID/bklist.html?offset=0&media=web&mesID=
        https://localhost:8080/show/s-style/hon/www.chikusaku-mansion.com/bklistmesID/bklist.html?offset=0&media=web&mesID=
        """
        tmpl_val = {}
        data = {}
        data["bkdatauri"]= u"https://s-style-hrd.appspot.com/show/s-style/hon/www.s-style.ne.jp/bkdata/article.html?media=web&id="
        data["bkdatauri2"]= u"https://s-style-hrd.appspot.com/show/s-style/hon/www.chikusaku-mansion.com/bkdata/article.html?media=web&id="

        tmpl_val["data"]=data


        """
        tmpl_val["tochi"] = self.getdatabyID(773)
        tmpl_val["mansion"] = self.getdatabyID(773)
        """

        #604180 土地
        tmpl_val["tochi"] = self.getdatabyID(604180)
        #593326 新築一戸建
        tmpl_val["shinchiku"] = self.getdatabyID(593326)
        #599278 中古一戸建
        tmpl_val["tyuukoko"] = self.getdatabyID(599278)
        #595317 中古マンション
        tmpl_val["chukoman"] = self.getdatabyID(595317)
        #602284 収益物件（その他）
        tmpl_val["syueki"] = self.getdatabyID(602284)
        #611083 賃貸物件
        tmpl_val["tintai"] = self.getdatabyID(611083)
        #623121 売買物件
        tmpl_val["mansion"] = self.getdatabyID(623121)
        path = os.path.dirname(__file__) + '/../templates/index.html'
        self.response.out.write(template.render(path, tmpl_val))

    def post(self,**kwargs):
        self.get(**kwargs)
