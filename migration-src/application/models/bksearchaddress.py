# -*- coding: utf-8 -*-
from google.cloud import ndb
from application.models.bksearchdata import bksearchdata

# Note: bksearchaddress2 model reference handling updated for ndb

def getname(co, br, div, tod, ad1, ad2):
    # ndb query for bksearchaddress2
    q = bksearchaddress2.query()
    results = q.filter(bksearchaddress2.shzicmi2 == ad2).fetch()
    res = []
    for a in results:
        if a.ref_address1:
            parent_addr = a.ref_address1.get()
            if parent_addr and parent_addr.ref_bksearchaddresslist:
                parent_list = parent_addr.ref_bksearchaddresslist.get()
                if parent_list:
                    if (parent_list.division == div and
                        parent_addr.tdufknmi == tod and
                        parent_addr.shzicmi1 == ad1 and
                        parent_addr.br == br and
                        parent_addr.co == co):
                        res.append(parent_list.name)
    return res


class bksearchaddresslist(ndb.Model):
    division = ndb.StringProperty(required=True, verbose_name="区分")
    name = ndb.StringProperty(required=True, verbose_name="名前")
    co = ndb.StringProperty(required=True, verbose_name="co")
    br = ndb.StringProperty(required=True, verbose_name="br")

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

    def setadset(self, tdufknmi, shzicmi1, shzicmi2=None):
        # REVIEW-L1: Incorrect ndb query syntax - cannot filter query object directly on ndb.Model
        # The old code used ReferenceProperty collection_name to iterate
        # Fixed: Use proper ndb query syntax with filter chaining
        q = bksearchaddress.query()
        q = q.filter(bksearchaddress.ref_bksearchaddresslist == self.key)
        q = q.filter(bksearchaddress.tdufknmi == tdufknmi)
        q = q.filter(bksearchaddress.shzicmi1 == shzicmi1)
        bkad = q.get()

        if not bkad:
            bkad = bksearchaddress(co=self.co, br=self.br, tdufknmi=tdufknmi, shzicmi1=shzicmi1)
            bkad.ref_bksearchaddresslist = self.key
            bkad.put()

        if shzicmi2:
            # REVIEW-L1: Incorrect ndb query syntax - multiple filters as positional args
            # Fixed: Use proper ndb query filter chaining
            q2 = bksearchaddress2.query()
            q2 = q2.filter(bksearchaddress2.ref_address1 == bkad.key)
            q2 = q2.filter(bksearchaddress2.shzicmi2 == shzicmi2)
            skip = q2.get() is not None

            if not skip:
                s2 = bksearchaddress2(shzicmi2=shzicmi2)
                s2.ref_address1 = bkad.key
                s2.put()

        bkad.ref_bksearchaddresslist = self.key
        bkad.put()

    def deladset(self, tdufknmi=None, shzicmi1=None, shzicmi2=None):
        if shzicmi1:
            # REVIEW-L1: Incorrect ndb query syntax - multiple filters as positional args
            # Fixed: Use proper ndb query filter chaining
            q = bksearchaddress.query()
            q = q.filter(bksearchaddress.ref_bksearchaddresslist == self.key)
            q = q.filter(bksearchaddress.tdufknmi == tdufknmi)
            q = q.filter(bksearchaddress.shzicmi1 == shzicmi1)
            ad1 = q.get()

            if ad1:
                if shzicmi2:
                    # Query for address2
                    q2 = bksearchaddress2.query()
                    q2 = q2.filter(bksearchaddress2.ref_address1 == ad1.key)
                    q2 = q2.filter(bksearchaddress2.shzicmi2 == shzicmi2)
                    s = q2.get()
                    if s:
                        s.key.delete()
                else:
                    # Delete all address2 items and the address itself
                    q2 = bksearchaddress2.query().filter(bksearchaddress2.ref_address1 == ad1.key)
                    for s in q2.fetch():
                        s.key.delete()
                    ad1.key.delete()
        else:
            # Delete all addresses and their address2 items
            q = bksearchaddress.query().filter(bksearchaddress.ref_bksearchaddresslist == self.key)
            for ad in q.fetch():
                q2 = bksearchaddress2.query().filter(bksearchaddress2.ref_address1 == ad.key)
                for s in q2.fetch():
                    s.key.delete()
                ad.key.delete()


# REVIEW-L1: ndb.KeyProperty の kind パラメータに文字列ではなくクラス名を使用している
# 修正前: ref_bksearchaddresslist = ndb.KeyProperty(kind=bksearchaddresslist, verbose_name='adset')
# 修正後: ref_bksearchaddresslist = ndb.KeyProperty(kind='bksearchaddresslist', verbose_name='adset')
class bksearchaddress(ndb.Model):
    ref_bksearchaddresslist = ndb.KeyProperty(kind='bksearchaddresslist', verbose_name='adset')
    # 所在地名1
    co = ndb.StringProperty(required=True, verbose_name="co")
    br = ndb.StringProperty(required=True, verbose_name="br")
    tdufknmi = ndb.StringProperty(verbose_name="都道府県名")
    shzicmi1 = ndb.StringProperty(verbose_name="所在地名1")
    # shzicmi2 = ndb.StringProperty(verbose_name="所在地名2")
    """
    def getbkdata(self,**kwargs):

        query = BKdata.query()

        # 更新年月日
        # ksnnngp = ndb.DateTimeProperty(verbose_name="更新年月日",auto_now=True)
        if kwargs["ksnnngpL"]:
            query.filter('ksnnngp >=', kwargs["ksnnngpL"])
        if kwargs["ksnnngpU"]:
            query.filter('ksnnngp <=', kwargs["ksnnngpU"])
        # 確認年月日
        # kknnngp = ndb.DateTimeProperty(verbose_name="確認年月日",auto_now_add=True)
        if kwargs["kknnngpL"]:
            query.filter('kknnngp >=', kwargs["kknnngpL"])
        if kwargs["kknnngpU"]:
            query.filter('kknnngp <=', kwargs["kknnngpU"])
        # 登録年月日
        # turknngp = ndb.DateTimeProperty(verbose_name="登録年月日",auto_now_add = True)
        if kwargs["turknngpL"]:
            query.filter('turknngp >=', kwargs["turknngpL"])
        if kwargs["turknngpU"]:
            query.filter('turknngp <=', kwargs["turknngpU"])
        # 変更年月日
        # hnknngp = ndb.DateTimeProperty(verbose_name="変更年月日",auto_now_add = True)
        if kwargs["hnknngpL"]:
            query.filter('hnknngp >=', kwargs["hnknngpL"])
        if kwargs["hnknngpU"]:
            query.filter('hnknngp <=', kwargs["hnknngpU"])

        query.filter('nyrykkisyID =', self.co)
        # query.filter('nyrykstnID =', self.br)
        # query.filter('tdufknmi　=', self.tdufknmi)
        # query.filter('shzicmi1 =', self.shzicmi1)
        # if self.shzicmi2:
            # query.filter('shzicmi2 =', self.shzicmi2)

        """"""
        if timeCategory == 'ksnnngp' or timeCategory == 'kknnngp' or timeCategory == 'turknngp' or timeCategory == 'hnknngp':
            if timeuper:
                query.filter(timeCategory + ' <=', timeuper)
            if timelower:
                query.filter(timeCategory + ' >=', timelower)
        """"""

        # query.order('-date')
        results = query.fetch(1000)
        return results
    """

# REVIEW-L1: ndb.KeyProperty の kind パラメータに文字列ではなくクラス名を使用している
# 修正前: ref_address1 = ndb.KeyProperty(kind=bksearchaddress, verbose_name='address2list')
# 修正後: ref_address1 = ndb.KeyProperty(kind='bksearchaddress', verbose_name='address2list')
class bksearchaddress2(ndb.Model):
    ref_address1 = ndb.KeyProperty(kind='bksearchaddress', verbose_name='address2list')
    # 所在地名2
    shzicmi2 = ndb.StringProperty(verbose_name="所在地名2")


"""
class addresscombinator(ndb.Model):
    co = ndb.StringProperty(required=True,verbose_name="co")
    br = ndb.StringProperty(required=True,verbose_name="br")
    ref_bksearchaddressset = ndb.KeyProperty(kind=bksearchaddress, verbose_name='adlist')
    ref_bksearchaddresslist = ndb.KeyProperty(kind=bksearchaddresslist, verbose_name='adset')
    def getbkdata(self,**kwargs):
        return self.ref_bksearchaddressset.get().getbkdata(**kwargs)
"""


# REVIEW-L1: ndb.KeyProperty の kind パラメータに文字列ではなくクラス名を使用している
# 修正前: ref_bksearchaddresslist = ndb.KeyProperty(kind=bksearchaddresslist, verbose_name='searchdata')
# 修正前: ref_bksearchdata = ndb.KeyProperty(kind=bksearchdata, verbose_name='adlist')
# 修正後: ref_bksearchaddresslist = ndb.KeyProperty(kind='bksearchaddresslist', verbose_name='searchdata')
# 修正後: ref_bksearchdata = ndb.KeyProperty(kind='bksearchdata', verbose_name='adlist')
class listcombinator(ndb.Model):
    co = ndb.StringProperty(required=True, verbose_name="co")
    br = ndb.StringProperty(required=True, verbose_name="br")
    ref_bksearchaddresslist = ndb.KeyProperty(kind='bksearchaddresslist', verbose_name='searchdata')
    ref_bksearchdata = ndb.KeyProperty(kind='bksearchdata', verbose_name='adlist')
    # ソート用連番
    sortkey = ndb.IntegerProperty()

    def setadlist(self, listkey, bksd):
        # REVIEW-L1: ndb.Key() の第1引数にクラス名ではなく文字列を指定
        # 修正前: self.ref_bksearchaddresslist = ndb.Key(bksearchaddresslist, listkey)
        # 修正後: self.ref_bksearchaddresslist = ndb.Key('bksearchaddresslist', listkey)
        self.ref_bksearchdata = bksd.key
        self.sortkey = bksd.getNextadlistNum()
        self.ref_bksearchaddresslist = ndb.Key('bksearchaddresslist', listkey)
        self.put()

    def deladlist(self):
        self.key.delete()


def setad2(co, br, tdufknmi, shzicmi1, shzicmi2=None):
    key_name = co + "/" + br + "/" + tdufknmi + "/" + shzicmi1
    adset = bksearchaddress.get_or_insert(
        key_name,
        co=co, br=br, tdufknmi=tdufknmi, shzicmi1=shzicmi1
    )
    if shzicmi2:
        setshzicmi2(adset, shzicmi2)
    adset.put()
    return adset


def setshzicmi2(adset, shzicmi2):
    ad2 = bksearchaddress2(shzicmi2=shzicmi2)
    ad2.ref_address1 = adset.key
    ad2.put()


class DataError(Exception):
    """Base class for exceptions in this module."""
    pass


# コンソールテスト用
# from application.models.bksearchaddress import test

class addtest():
    def test1(self):
        """
        a = bksearchaddresslist.get_or_insert("s-style/hon/小学校/千種", co="s-style", br="hon", division="小学校", name="千種")
        b = addresscombinator(co="s-style", br="hon", ref_bksearchaddresslist=a.key)
        b.put()
        b.setadset("愛知県", "名古屋市千種区", "若水2丁目")
        res = a.getbkdata("kknnngp", "2011/06/01", "2011/09/02")
        """
        return 0
