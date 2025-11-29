# -*- coding: utf-8 -*-

from google.appengine.ext import db

class matchingdate(db.Model):
    CorpOrg_key_name = db.StringProperty(verbose_name=u"会社ID",required=True) 
    Branch_Key_name = db.StringProperty(verbose_name=u"支店ID")
    sitename = db.StringProperty(verbose_name=u"サイト名")
    matchingdate = db.DateTimeProperty(auto_now_add = True,verbose_name=u"タイムスタンプ")

    def getlast(self):
        lastdate = self.all()
        lastdate.filter("CorpOrg_key_name = ", self.CorpOrg_key_name)
        if self.Branch_Key_name:
            lastdate.filter("Branch_Key_name = ", self.Branch_Key_name)
        if self.sitename:
            lastdate.filter("sitename = ", self.sitename)
        lastdate.order('-matchingdate')
        l=lastdate.fetch(1)
        if l.count():
            return l[0].matchingdate
        else:
            return None
