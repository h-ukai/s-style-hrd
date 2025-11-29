# -*- coding: utf-8 -*-

from google.cloud import ndb

class wordstockerdb(ndb.Model):
    """キーワード保存モデル"""
    # REVIEW-L1: マイグレーションルール適用漏れ: Python 3では u"" は不要
    # 修正前: verbose_name=u"会社名" など
    # 修正後: verbose_name="会社名" など
    corp = ndb.StringProperty(verbose_name="会社名")
    branch = ndb.StringProperty(verbose_name="支店名")
    site = ndb.StringProperty(verbose_name="サイト名")
    name = ndb.StringProperty(verbose_name="名前")
    word = ndb.StringProperty(verbose_name="キーワード")

class wordstocker():
    @classmethod
    def get(cls, corp, name, branch=None, site=None):
        """キーワード一覧を取得"""
        # Python 2: db.Model.all() → Python 3: ndb.Model.query()
        query = wordstockerdb.query(wordstockerdb.corp == corp, wordstockerdb.name == name)

        if branch:
            query = query.filter(wordstockerdb.branch == branch)
        if site:
            query = query.filter(wordstockerdb.site == site)

        # 結果を処理
        L = []
        for w in query.fetch():
            # 重複チェック
            if w.word not in L:
                L.append(w.word)
        return L

    @classmethod
    def set(cls, corp, name, word, branch=None, site=None):
        """キーワード登録"""
        lst = cls.get(corp, name, branch, site)
        if lst:
            # リスト内に同じキーワードがあるかチェック
            if word not in lst:
                w = wordstockerdb(corp=corp, branch=branch, site=site, name=name, word=word)
                w.put()
        else:
            # 新規登録
            w = wordstockerdb(corp=corp, branch=branch, site=site, name=name, word=word)
            w.put()
