#!/usr/local/bin/python
# -*- coding: utf-8 -*-

#from google.appengine.ext import webapp
import webapp2
from application.models.member import member
from application.bksearchutl import bksearchutl
from application.messageManager import messageManager
from application.bklistutl import bklistutl
from application import timemanager

import datetime

class cronjobs(webapp2.RequestHandler):

    def get(self):
        key_name = "s-style/systemwebsearch@s-style"
        mmdb = member.get_by_key_name(key_name)
        corp = mmdb.CorpOrg_key_name
        branch = mmdb.Branch_Key_name
        dat = ""
        if mmdb:
            sddblist = mmdb.bksearchdata_set.order("sortkey")
            meslist = messageManager.getmeslist("s-style",mmdb,order="reservation")
            kknnngp = datetime.datetime.now()
            kknnngp = timemanager.utc2jst_date(kknnngp)
            kknnngp = timemanager.add_months(kknnngp,-1)
            kknnngp = kknnngp.strftime("%Y/%m/%d") 
            i = 0
            for sddb in sddblist:
                if dat:
                    dat += ","
                while meslist[i].done: #済は飛ばす
                    i += 1
                bklistutl.remalllistbykey(corp,branch,meslist[i].key())
                #dat += bksearchutl.do_searchdb2(sddb,msgkey=meslist[i].key(),hnknngpL=kknnngp)
                dat += bksearchutl.do_searchdb2(sddb,msgkey=meslist[i].key())
                i += 1
        self.response.out.write(dat)
