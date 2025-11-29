# -*- coding: utf-8 -*-

from application.models.bksearchensen import bksearchensen
from application.models.bksearcheki import bksearcheki


class bksearchensenutl(object):
    """検索駅/路線ユーティリティ

    Migration Notes:
    - db.Model → ndb.Model
    - ReferenceProperty の子エンティティ（.eki）は StructuredProperty で対応
    - .put() → .put()（構文同じ）
    - .delete() → .delete()（構文同じ）
    """

    ensen = None

    def newensen(self, ref_bksearchdata, ensenmei, tdufknmi=None, thHnU=None, thMU=None):
        """新規駅/路線エンティティを作成

        Args:
            ref_bksearchdata: 参照する bksearchdata キーまたはエンティティ
            ensenmei: 駅/路線名
            tdufknmi: 都道府県名（オプション）
            thHnU: 徒歩分上限（オプション）
            thMU: 徒歩m上限（オプション）
        """
        if thHnU:
            thHnU = float(thHnU)
        else:
            thHnU = None
        if thMU:
            thMU = float(thMU)
        else:
            thMU = None

        # ref_bksearchdata はキーで保存（ndb.KeyProperty）
        if hasattr(ref_bksearchdata, 'key'):
            # エンティティが渡された場合、key を取得
            ref_key = ref_bksearchdata.key
        else:
            # キーが渡された場合、そのまま使用
            ref_key = ref_bksearchdata

        # REVIEW-L1: ref_bksearchdata がキーの場合、メソッド呼び出し不可
        # 修正前: sortkey=ref_bksearchdata.getNextlinelistNum()
        # 修正後: エンティティを取得してからメソッド呼び出し
        if hasattr(ref_bksearchdata, 'getNextlinelistNum'):
            # エンティティが渡された場合
            sortkey = ref_bksearchdata.getNextlinelistNum()
        else:
            # キーが渡された場合、エンティティを取得
            entity = ref_bksearchdata.get()
            sortkey = entity.getNextlinelistNum() if entity else 0

        self.ensen = bksearchensen(
            ref_bksearchdata=ref_key,
            tdufknmi=tdufknmi,
            ensenmei=ensenmei,
            thHnU=thHnU,
            thMU=thMU,
            sortkey=sortkey
        )
        self.ensen.put()

    def delete(self):
        """駅/路線エンティティと子の駅エンティティを全削除"""
        if hasattr(self.ensen, 'eki'):
            for eki in self.ensen.eki:
                eki.delete()
        self.ensen.delete()

    def addeki(self, ekistr):
        """駅を追加（重複チェック付き）

        Args:
            ekistr: 駅名

        Returns:
            生成された駅キー、または None（既存の場合）
        """
        if hasattr(self.ensen, 'eki'):
            for eki in self.ensen.eki:
                if eki.ekimei == ekistr:
                    return None

        # ref_ensen: ndb.KeyProperty で親エンティティへの参照を保存
        return bksearcheki(ref_ensen=self.ensen.key, ekimei=ekistr).put()

    def deleki(self, ekistr):
        """駅を削除

        Args:
            ekistr: 駅名
        """
        if hasattr(self.ensen, 'eki'):
            for eki in self.ensen.eki:
                if eki.ekimei == ekistr:
                    eki.delete()
                    break
