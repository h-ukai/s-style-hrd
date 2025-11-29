# -*- coding: utf-8 -*- 
import os
from google.appengine.ext import db
#from google.appengine.ext import webapp
import webapp2
from google.appengine.ext.webapp import template

from models.member import member
from models.bksearchaddress import bksearchaddresslist


import datetime
import bksearchutl

class addresslist(webapp2.RequestHandler):


    def __init__(self,request, response):
        self.initialize(request, response)
        self.tmpl_val = {}
        self.tmpl_val['error_msg'] = ''
        self.auth = False
        self.corp_name= u"s-style"
        self.branch_name = u"hon"

    def get(self,**kwargs):
        Message=""
        division = self.request.get("division")
        name = self.request.get("listname")
        modal = self.request.get("modal")
        if kwargs.get("Message",None):
            Message = kwargs.get("Message",None)
        if kwargs.get("memberID",None) == None:
            memberID = self.request.get("memberID")
        else :
            memberID = kwargs.get("memberID",None)
        if not memberID:
            memberID = "testuser0001"
        key = kwargs.get("key",None) 
        if not key:
            if self.request.get(u"submit")!=u"削除する":
                key = self.request.get("listid")
        now = datetime.datetime.now() # datetime.datetime(2009, 7, 8, 22, 59, 0, 688787)

        self.tmpl_val = {
                         "memberID": memberID,
                         "division": division,
                         "listname":name,
                         "modal":modal,
                         "key":key,
                         "now":now,
                         "Message":Message
                         }
        path = os.path.dirname(__file__) + '/../templates/addresslist.html'
        self.response.out.write(template.render(path, self.tmpl_val))

    def post(self,**kwargs):
        str1 = self.request.get(u"submit")
        division = self.request.get(u"division")
        name = self.request.get(u"listname")
        co = u"s-style"
        br = u"hon"
        if name and division:
            listid = self.request.get("listid")
            if listid:
                adlist = bksearchaddresslist.get(listid)
                adlist.division=division
                adlist.name=name
            else:
                adlist = bksearchaddresslist(co=co,br=br,division=division,name=name)
            adlist.put()
    
            if str1==u"削除する":
                adlist.deladset()
                adlist.delete()
                adlist = None
            if str1==u"保存する":
                adlist.deladset()
                i = 0
                for n,v in self.request.POST.multi._items:
                    if n == "address1":
                        '''
                        if self.request.POST.multi._items[i+1][0] == "address1id":
                            address1id = self.request.POST.multi._items[i+1][1]
                            if address1id:
                                ad1 = bksearchaddresslist.get(db.Key(address1id))
                        else:                             
                            ad1 = bksearchaddress(co=co,br=br)
                        ad1.shzicmi1 = v
                        ad1.tdufknmi = self.request.POST.multi._items[i-1][1]
                        ad1.ref_bksearchaddresslist = adlist.key()
                        ad1.put()
                        '''
                        shzicmi1 = v
                        tdufknmi = self.request.POST.multi._items[i-1][1]
                        if shzicmi1:
                            if self.request.POST.multi._items[i+2][0]=="address2":
                                address2 = self.request.POST.multi._items[i+2][1]
                                if address2:
                                    address2list = address2.split(',')
                                    for ad2 in address2list:
                                        adlist.setadset(tdufknmi, shzicmi1, ad2)
                                else:
                                    adlist.setadset(tdufknmi, shzicmi1)
                    i+=1
            if adlist:
                kwargs['key']=str(adlist.key())
        else:
            kwargs['Message']="区分またはアドレスリストがありません"
        self.get(**kwargs)