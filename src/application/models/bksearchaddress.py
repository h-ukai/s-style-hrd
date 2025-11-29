# -*- coding: utf-8 -*-
import sys 
stdin = sys.stdin 
stdout = sys.stdout 
reload(sys) 
sys.setdefaultencoding('utf-8') 
sys.stdin = stdin 
sys.stdout = stdout

from google.appengine.ext import db
from bksearchdata import bksearchdata
#from bksearchaddress2 import bksearchaddress2

def getname(co,br,div,tod,ad1,ad2):
    a2=bksearchaddress2.all()
    a2.filter('shzicmi2 = ',ad2)
    res = []
    for a in a2:
        if a.ref_address1.ref_bksearchaddresslist.division == div and a.ref_address1.tdufknmi == tod and a.ref_address1.shzicmi1 == ad1 and a.ref_address1.br == br and a.ref_address1.co == co:
            res.append(a.ref_address1.ref_bksearchaddresslist.name)
    return res




#from bkdata import BKdata


class bksearchaddresslist(db.Model):
    division = db.StringProperty(required=True,verbose_name=u"区分")
    name = db.StringProperty(required=True,verbose_name=u"名前")
    co = db.StringProperty(required=True,verbose_name=u"co")
    br = db.StringProperty(required=True,verbose_name=u"br")
    
    """    
    def getbkdata(self,**kwargs):
        for set in self.adset:
            entitysb = set.getbkdata(**kwargs)
            res = []
            for t in entitysb:
                for t2 in res:
                    if t2.bkID == t.bkID:
                        break
                else:
                    res.append(t)
        return res
    """
    def setadset(self,tdufknmi, shzicmi1, shzicmi2=None):
        bkad = None
        for ad in self.adset:
            if ad.tdufknmi == tdufknmi and ad.shzicmi1 == shzicmi1:
                bkad = ad
                break
        if not bkad:
            bkad = bksearchaddress(co = self.co,br = self.br,tdufknmi=tdufknmi,shzicmi1=shzicmi1)
            bkad.put()
        if shzicmi2:
            skip = False
            for s in bkad.address2list:
                if s.shzicmi2 == shzicmi2:
                    skip = True
                    break
            if not skip:
                s2=bksearchaddress2(shzicmi2 = shzicmi2)
                s2.ref_address1 = bkad.key()
                s2.put()
        bkad.ref_bksearchaddresslist = self.key()
        bkad.put()

    def deladset(self,tdufknmi=None, shzicmi1=None, shzicmi2=None):
        if shzicmi1:
            for ad in self.adset:
                if ad.tdufknmi == tdufknmi and ad.shzicmi1 == shzicmi1:
                    ad1 = ad
                    break
            if shzicmi2:
                for s in ad1.address2list:
                    if s.shzicmi2 == shzicmi2:
                        s.delete()
                        break
            else:
                for s in ad1.address2list:
                    s.delete()
                ad1.delete()
        else:
            for ad in self.adset:
                for s in ad.address2list:
                    s.delete()                
                ad.delete()
        
class bksearchaddress(db.Model):
    ref_bksearchaddresslist = db.ReferenceProperty(reference_class = bksearchaddresslist,collection_name = u'adset')
    #所在地名1
    co = db.StringProperty(required=True,verbose_name=u"co")
    br = db.StringProperty(required=True,verbose_name=u"br")
    tdufknmi = db.StringProperty(verbose_name=u"都道府県名")
    shzicmi1 = db.StringProperty(verbose_name=u"所在地名1")
#    shzicmi2 = db.StringProperty(verbose_name=u"所在地名2")
    """
    def getbkdata(self,**kwargs):

        query = BKdata.all()

        #更新年月日
        #ksnnngp = db.DateTimeProperty(verbose_name=u"更新年月日",auto_now=True)
        if kwargs["ksnnngpL"]:
            query.filter(u'ksnnngp >=', kwargs["ksnnngpL"])
        if kwargs["ksnnngpU"]:
            query.filter(u'ksnnngp <=', kwargs["ksnnngpU"])
        #確認年月日
        #kknnngp = db.DateTimeProperty(verbose_name=u"確認年月日",auto_now_add=True)
        if kwargs["kknnngpL"]:
            query.filter(u'kknnngp >=', kwargs["kknnngpL"])
        if kwargs["kknnngpU"]:
            query.filter(u'kknnngp <=', kwargs["kknnngpU"])
        #登録年月日
        #turknngp = db.DateTimeProperty(verbose_name=u"登録年月日",auto_now_add = True)
        if kwargs["turknngpL"]:
            query.filter(u'turknngp >=', kwargs["turknngpL"])
        if kwargs["turknngpU"]:
            query.filter(u'turknngp <=', kwargs["turknngpU"])
        #変更年月日
        #hnknngp = db.DateTimeProperty(verbose_name=u"変更年月日",auto_now_add = True)
        if kwargs["hnknngpL"]:
            query.filter(u'hnknngp >=', kwargs["hnknngpL"])
        if kwargs["hnknngpU"]:
            query.filter(u'hnknngp <=', kwargs["hnknngpU"])

        query.filter(u'nyrykkisyID =', self.co)
        #query.filter(u'nyrykstnID =', self.br)
        #query.filter(u'tdufknmi　=', self.tdufknmi)
        #query.filter(u'shzicmi1 =', self.shzicmi1)
        #if self.shzicmi2:
            #query.filter(u'shzicmi2 =', self.shzicmi2)

        """"""
        if timeCategory == u'ksnnngp' or timeCategory == u'kknnngp' or timeCategory == u'turknngp' or timeCategory == u'hnknngp':     
            if timeuper:
                query.filter(timeCategory + u' <=', timeuper)
            if timelower:
                query.filter(timeCategory + u' >=', timelower)
        """"""

        #query.order('-date')
        results = query.fetch(1000)
        return results
    """
class bksearchaddress2(db.Model):
    ref_address1 = db.ReferenceProperty(reference_class = bksearchaddress,collection_name = 'address2list')
    #所在地名2
    shzicmi2 = db.StringProperty(verbose_name=u"所在地名2")


"""       
class addresscombinator(db.Model):
    co = db.StringProperty(required=True,verbose_name=u"co")
    br = db.StringProperty(required=True,verbose_name=u"br")
    ref_bksearchaddressset = db.ReferenceProperty(reference_class = bksearchaddress,collection_name = u'adlist')
    ref_bksearchaddresslist = db.ReferenceProperty(reference_class = bksearchaddresslist,collection_name = u'adset')
    def getbkdata(self,**kwargs):
        return self.ref_bksearchaddressset.getbkdata(**kwargs)
"""

class listcombinator(db.Model):
    co = db.StringProperty(required=True,verbose_name=u"co")
    br = db.StringProperty(required=True,verbose_name=u"br")
    ref_bksearchaddresslist = db.ReferenceProperty(reference_class = bksearchaddresslist,collection_name = u'searchdata')
    ref_bksearchdata = db.ReferenceProperty(reference_class = bksearchdata,collection_name = u'adlist')
    #ソート用連番
    sortkey = db.IntegerProperty()

    def setadlist(self,listkey,bksd):
        self.ref_bksearchdata = bksd
        self.sortkey = bksd.getNextadlistNum()
        self.ref_bksearchaddresslist = bksearchaddresslist.get(listkey)
        self.put()
    def deladlist(self):
        self.delete()

def setad2(co,br,tdufknmi,shzicmi1,shzicmi2=None):
    adset = bksearchaddress.get_or_insert(co + u"/" + br + u"/" + tdufknmi + u"/" + shzicmi1 ,co = co,br = br,tdufknmi = tdufknmi,shzicmi1 = shzicmi1,shzicmi2 = shzicmi2)
    if shzicmi2:
        setshzicmi2(shzicmi2)
    adset.put()
    return adset

def setshzicmi2(adset,shzicmi2):
    ad2 = bksearchaddress2(None,None,shzicmi2=shzicmi2)
    ad2.ref_address1 = adset
    ad2.put()





class DataError(Exception):
    """Base class for exceptions in this module."""
    pass


#コンソールテスト用
#from application.models.bksearchaddress import test

class addtest():
    def test1(self):
        """
        a = bksearchaddresslist.get_or_insert(u"s-style" + u"/" + u"hon" + u"/" + u"小学校" + u"/" + u"千種", co = u"s-style", br = u"hon", division = u"小学校",name = u"千種")
        b = addresscombinator(co = u"s-style", br = u"hon",ref_bksearchaddresslist = a.key())
        b.put()
        b.setadset(u"愛知県",u"名古屋市千種区",u"若水２丁目")
        res = a.getbkdata(u"kknnngp",u"2011/06/01",u"2011/09/02")
        """
        return 0
