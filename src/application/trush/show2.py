# -*- coding: utf-8 -*-

#from google.appengine.dist import use_library
#use_library('django', '1.2')


import os
#from google.appengine.ext import webapp
import webapp2
from google.appengine.ext.webapp import template
from django.utils import simplejson
from google.appengine.api import urlfetch
from google.appengine.ext import db
from application.GqlEncoder import GqlJsonEncoder
from models import bkdata
import session
#os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

class Show(webapp2.RequestHandler):
    def get(self):
        
        """
        "https://s-style-hrd.appspot.com/show/s-style/hon/www.chikusaku-mansion.com/bkdata/article.html?id=59&media=wev"
        "https://localhost:8080/show/s-style/hon/www.chikusaku-mansion.com/bkdata/article.html?id=59&media=wev"
        pathParts = path.split(u'/')
        request.path [u'', u'show', u's-style', u'hon', u'sitename',u'command',u'bkdata.html?id=59]
        request.url [u'https:', u'', u's-style-hrd.appspot.com', u'show', u's-style', u'hon', u'sitename',u'command',u'bkdata.html?id=59]
        """
        path = self.request.path
        pathParts = path.split(u'/') 
        CorpOrg_key  = pathParts[2]
        Branch_Key = pathParts[3]
        Sitename = pathParts[4]
        Command = pathParts[5]
        templ = CorpOrg_key + "/" + Branch_Key + "/" + Sitename + "/" + Command + "/" + pathParts[6].split(u'?')[0]
        self.tmpl_val = {}
        entitys = {}
        """
        selecl searvice
        """
        if Command == "bkdata":
            bkID = self.request.get("id")
            if bkID:
                key_name =  CorpOrg_key + u"/" + Branch_Key + u"/" + bkID
                bkdb = bkdata.BKdata.get_by_key_name(key_name)
                if bkdb.mtngflg and bkdb.webknskflg:
                    if not(bkdb.kukkTnsiKbn == u"広告可" or bkdb.kukkTnsiKbn == u"一部可（インターネット）" or bkdb.kukkTnsiKbn == u"広告可（但し要連絡）"):
                        self.tmpl_val['corp_name'] = CorpOrg_key
                        self.tmpl_val['branch_name'] = Branch_Key
                        self.tmpl_val['sitename'] = Sitename
                        """
                        ここでセッションチェック表示してよいデータか確認する
                        """
                        ssn = session.Session(self.request, self.response)
                        if not ssn.chk_ssn():
                            urlstr = "corp_name=" + CorpOrg_key
                            urlstr = urlstr + "&branch_name=" + Branch_Key
                            urlstr = urlstr + "&sitename=" + Sitename
                            urlstr = urlstr + "&togo=" + self.request.path
                            self.redirect('/login?' + urlstr)
                            return
                        self.tmpl_val['user'] = ssn.get_ssn_data('user')
                    self.tmpl_val['sitename'] = Sitename
                    query_str = u"SELECT * FROM Blob WHERE CorpOrg_key = '" + bkdb.nyrykkisyID + u"' AND Branch_Key = '" + bkdb.nyrykstnID + u"' AND bkID = '" + bkdb.bkID + u"' AND media = '" + self.media + u"' ORDER BY pos ASC"
                    blobs = db.GqlQuery (query_str)
                    b2 = []
                    heimenzu = None
                    for c in blobs:
                        if c.pos.isdigit():
                            b2.append(c)
                        elif c.pos == "平面図":
                            heimenzu = c
                    kakakuM = None
                    kakakuB = None
                    if bkdb.kkkuCnryu:
                        kakakuM = GqlJsonEncoder.moneyfmt(int(bkdb.kkkuCnryu/100)/100,0)
                    tknngt = None
                    if bkdb.cknngtSirk:
                        tknngt = bkdb.cknngtSirk.year
                        if int(tknngt) < 1989:
                            tknngt = u"昭和" + str(tknngt-1925) + u"年" 
                        elif int(tknngt) >= 1989:
                            tknngt = u"平成" + str(tknngt-1988) + u"年"
                        else:
                            tknngt = tknngt + u"年"
                    data = GqlJsonEncoder.GQLmoneyfmt(bkdb)
                    entitys = {"bkdata":data,"picdata":b2,"kakakuM":kakakuM,"tknngtG":tknngt,"heimenzu":heimenzu}        
                else:
                    templ = CorpOrg_key + "/" + Branch_Key + "/" + Sitename + "/" + Command + "/" + "sorry.html"
            else:
                templ = CorpOrg_key + "/" + Branch_Key + "/" + Sitename + "/" + Command + "/" + "sorry.html"
        
       
        
        self.tmpl_val["data"] = entitys
        path = os.path.dirname(__file__) + '/../templates/' + templ
        self.response.out.write(template.render(path, self.tmpl_val))

    def post(self):

        self.get()