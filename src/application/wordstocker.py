# -*- coding: utf-8 -*-

from google.appengine.ext import db

class wordstockerdb(db.Model):
    corp = db.StringProperty(verbose_name=u"会社名")
    branch = db.StringProperty(verbose_name=u"支店名")
    site = db.StringProperty(verbose_name=u"サイト名")
    name = db.StringProperty(verbose_name=u"名前")
    word = db.StringProperty(verbose_name=u"キーワード")

class wordstocker():
    @classmethod
    def get(self,corp,name,branch=None,site=None):
        gql = wordstockerdb.all()
        gql.filter("corp = " ,corp)
        gql.filter("name = " ,name)
        if branch:
            gql.filter("branch = " ,branch)
        if site:
            gql.filter("site = " ,site)
        L=[]
        for w in gql:
            for l in L:
                if w.word == l:
                    break
            else:
                L.append(w.word)
        return L

    @classmethod
    def set(self,corp,name,word,branch=None,site=None):
        lst = self.get(corp,name,branch,site)
        if lst:
            for w in lst:
                if word == w:
                    break
            else:
                w = wordstockerdb(corp=corp,branch=branch,site=site,name=name,word=word)
                w.put()
        else:
            w = wordstockerdb(corp=corp,branch=branch,site=site,name=name,word=word)
            w.put()
        