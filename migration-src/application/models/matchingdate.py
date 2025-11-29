# -*- coding: utf-8 -*-

from google.cloud import ndb


class matchingdate(ndb.Model):
    """マッチング日付記録モデル

    Migration Notes:
    - db.Model → ndb.Model
    - db.StringProperty → ndb.StringProperty（構文変更なし）
    - db.DateTimeProperty → ndb.DateTimeProperty（構文同じ）
    - .all() → query() に変更
    - filter() → .filter() に変更
    - order() → .order() に変更（構文は '-' プレフィックス同じ）
    - .fetch() → .fetch() に変更
    - .count() は fetch() で取得した list の len() を使用
    """

    # 会社ID
    CorpOrg_key_name = ndb.StringProperty(name="CorpOrg_key_name")

    # 支店ID
    Branch_Key_name = ndb.StringProperty(name="Branch_Key_name")

    # サイト名
    sitename = ndb.StringProperty(name="sitename")

    # マッチング日付（自動タイムスタンプ）
    matchingdate = ndb.DateTimeProperty(auto_now_add=True, name="matchingdate")

    def getlast(self):
        """最後のマッチング日付を取得

        Returns:
            最後のマッチング日付（datetime オブジェクト）、または None
        """
        # ndb では query() メソッドを使用
        query = matchingdate.query()
        query = query.filter(matchingdate.CorpOrg_key_name == self.CorpOrg_key_name)

        if self.Branch_Key_name:
            query = query.filter(matchingdate.Branch_Key_name == self.Branch_Key_name)

        if self.sitename:
            query = query.filter(matchingdate.sitename == self.sitename)

        # order() で降順（'-' プレフィックス）
        query = query.order(-matchingdate.matchingdate)

        # fetch() で最大 1 件取得
        l = query.fetch(1)

        # list の len() で件数チェック
        if len(l) > 0:
            return l[0].matchingdate
        else:
            return None
