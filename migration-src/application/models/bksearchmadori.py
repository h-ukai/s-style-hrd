# -*- coding: utf-8 -*-

from google.cloud import ndb
from .bksearchdata import bksearchdata


class bksearchmadori(ndb.Model):
    """間取（間取部屋数、タイプ）モデル

    Migration Notes:
    - db.Model → ndb.Model
    - db.ReferenceProperty → ndb.KeyProperty（参照はKeyで保存、.get()で取得）
    - db.FloatProperty → ndb.FloatProperty（構文変更なし）
    - db.IntegerProperty → ndb.IntegerProperty（構文変更なし）
    - db.StringProperty(choices=...) → ndb.StringProperty(...)（choices機能はアプリケーション層で検証）
    """

    # ref_bksearchdata: ndb.KeyProperty では collection_name は指定不可
    # bksearchdata エンティティから逆参照が必要な場合、bksearchdata 側で StructuredProperty/KeyProperty で参照すること
    ref_bksearchdata = ndb.KeyProperty(kind='bksearchdata')

    # 間取部屋数（1）
    mdrHysu = ndb.FloatProperty(name="mdrHysu")

    # 間取タイプ（1）
    # choices は ndb では機能せず、アプリケーション層で検証が必要
    mdrTyp = ndb.StringProperty(name="mdrTyp")  # 値: "ワンルーム", "K", "DK", "LK", "LDK", "SK", "SDK", "SLK", "SLDK"

    # ソート用連番
    sortkey = ndb.IntegerProperty(name="sortkey")
