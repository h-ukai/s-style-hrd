# -*- coding: utf-8 -*-

from google.cloud import ndb


class matchingparam(ndb.Model):
    """マッチングパラメータモデル

    Migration Notes:
    - db.Model → ndb.Model
    - db.StringProperty → ndb.StringProperty（構文変更なし）
    - db.IntegerProperty → ndb.IntegerProperty（構文変更なし）
    - verbose_name, required, default, multiline は ndb では サポートされないため、
      コメントで記載のみ（アプリケーション層で検証が必要）
    """

    # 会社ID
    CorpOrg_key_name = ndb.StringProperty(name="CorpOrg_key_name")

    # 支店ID
    Branch_Key_name = ndb.StringProperty(name="Branch_Key_name")

    # サイト名
    sitename = ndb.StringProperty(name="sitename")

    # マッチング対象物件
    matchingtarget = ndb.StringProperty(name="matchingtarget")

    # マッチング対象サービス名
    service = ndb.StringProperty(default="マッチング", name="service")

    # lev1 無言日数（デフォルト: 30日）
    lev1noreactiondays = ndb.IntegerProperty(default=30, name="lev1noreactiondays")

    # lev1 最大物件送信数（デフォルト: 100件）
    lev1maxsended = ndb.IntegerProperty(default=100, name="lev1maxsended")

    # lev2 無言日数（デフォルト: 60日）
    lev2noreactiondays = ndb.IntegerProperty(default=60, name="lev2noreactiondays")

    # lev2 最大物件送信数（デフォルト: 150件）
    lev2maxsended = ndb.IntegerProperty(default=150, name="lev2maxsended")

    # 最長間隔日数（デフォルト: 100日）
    limitdistance = ndb.IntegerProperty(default=100, name="limitdistance")

    # タイトル
    subject = ndb.StringProperty(name="subject")

    # 本文（複数行）
    body = ndb.StringProperty(name="body")

    # メディア（デフォルト: "web"）
    media = ndb.StringProperty(default="web", name="media")

    # 請求
    seikyu = ndb.StringProperty(name="seikyu")

    # 送信種類
    sousinsyurui = ndb.StringProperty(name="sousinsyurui")
