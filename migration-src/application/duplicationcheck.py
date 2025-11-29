# -*- coding: utf-8 -*-

from google.cloud import ndb
from application.models import bkdata
import datetime
from datetime import date
import os
import logging
from flask import request, render_template, Response
from application import timemanager


def get_duplication_check():
    """
    GET ハンドラー: 重複チェック処理
    """
    # クエリパラメータ取得
    source = request.args.get("source", "")
    limit = 20

    # 全件数を取得（count用）
    all_list = get_my_list(999999, date, source)
    total_count = len(all_list)

    # 制限件数を取得
    limited_list = get_my_list(limit, date, source)

    if len(limited_list) < 1:
        return 'OK checked all data.'

    # 重複チェック処理を実行
    for bkdata_item in limited_list:
        do_check(bkdata_item)
        bkdata_item.duplicationcheck = None
        bkdata_item.put()

    # テンプレートに渡すデータ
    tmpl_val = {
        'count': total_count,
        'source': source,
        'limit': limit,
    }

    return render_template('duplicationcheck.html', **tmpl_val)


def get_my_list(limit, date, source):
    """
    重複チェック対象の物件リストを取得
    """
    # REVIEW-L2: ndb query efficiency - avoid query.count() + fetch() pattern
    # Original code: query[0:min(query.count(),limit)] requires 2 queries
    # Migrated code: query.fetch(limit=limit) is efficient single query
    # Recommendation: Current implementation is correct
    # Datastore クエリ（ndb 方式）
    query = bkdata.BKdata.query(
        bkdata.BKdata.nyrykkisyID == u"s-style",
        bkdata.BKdata.nyrykstnID == u"hon",
        bkdata.BKdata.duplicationcheck == True
    )

    # 件数制限
    results = query.fetch(limit=limit)
    return results


def do_check(bkdata1):
    """
    重複チェック処理本体
    """
    query_str = u"SELECT * FROM BKdata WHERE nyrykkisyID = 's-style' AND nyrykstnID = 'hon' AND duplicationcheck = NULL AND dtsyuri = '物件'"

    # 物件種別による重複判定
    if bkdata1.bkknShbt == u"土地" or bkdata1.bkknShbt == u"賃貸土地" or bkdata1.bkknShbt == u"戸建住宅等" or bkdata1.bkknShbt == u"住宅以外の建物全部" or bkdata1.bkknShbt == u"賃貸一戸建" or bkdata1.bkknShbt == u"賃貸外全":
        # 土地系物件: 所在地2まで一致で土地面積が一致なら重複
        query = bkdata.BKdata.query(
            bkdata.BKdata.nyrykkisyID == u"s-style",
            bkdata.BKdata.nyrykstnID == u"hon",
            bkdata.BKdata.duplicationcheck == None,
            bkdata.BKdata.dtsyuri == u"物件",
            bkdata.BKdata.bkknShbt == bkdata1.bkknShbt
        )

        if bkdata1.shzicmi1 and bkdata1.shzicmi2 and bkdata1.tcMnsk2:
            query = query.filter(
                bkdata.BKdata.shzicmi1 == bkdata1.shzicmi1,
                bkdata.BKdata.shzicmi2 == bkdata1.shzicmi2,
                bkdata.BKdata.tcMnsk2 == bkdata1.tcMnsk2
            )

            # 2年以内の物件に絞る
            cutoff_date = datetime.datetime.now() - datetime.timedelta(days=730)
            query = query.filter(bkdata.BKdata.kknnngp > cutoff_date)
            query = query.order_by(bkdata.BKdata.kknnngp)

            results = query.fetch()
            if results:
                do_set(bkdata1, results)

    elif bkdata1.bkknShbt == u"マンション等" or bkdata1.bkknShbt == u"住宅以外の建物一部" or bkdata1.bkknShbt == u"賃貸マンション" or bkdata1.bkknShbt == u"賃貸外一":
        # マンション系物件: 所在地2まで一致で所在階と部屋番号が同じなら重複
        query = bkdata.BKdata.query(
            bkdata.BKdata.nyrykkisyID == u"s-style",
            bkdata.BKdata.nyrykstnID == u"hon",
            bkdata.BKdata.duplicationcheck == None,
            bkdata.BKdata.dtsyuri == u"物件",
            bkdata.BKdata.bkknShbt == bkdata1.bkknShbt
        )

        if bkdata1.shzicmi1 and bkdata1.shzicmi2 and bkdata1.shziki and bkdata1.hyBngu:
            query = query.filter(
                bkdata.BKdata.shzicmi1 == bkdata1.shzicmi1,
                bkdata.BKdata.shzicmi2 == bkdata1.shzicmi2,
                bkdata.BKdata.shziki == bkdata1.shziki,
                bkdata.BKdata.hyBngu == bkdata1.hyBngu
            )

            # 2年以内の物件に絞る
            cutoff_date = datetime.datetime.now() - datetime.timedelta(days=730)
            query = query.filter(bkdata.BKdata.kknnngp > cutoff_date)
            query = query.order_by(bkdata.BKdata.kknnngp)

            results = query.fetch()
            if results:
                do_set(bkdata1, results)

        elif bkdata1.shzicmi1 and bkdata1.shzicmi2 and bkdata1.shziki and bkdata1.mdrTyp1 and bkdata1.mdrHysu1 and bkdata1.snyuMnskSyuBbnMnsk2:
            # 所在地2まで一致で所在階と間取りと専有面積が同じなら重複
            query = query.filter(
                bkdata.BKdata.shzicmi1 == bkdata1.shzicmi1,
                bkdata.BKdata.shzicmi2 == bkdata1.shzicmi2,
                bkdata.BKdata.shziki == bkdata1.shziki,
                bkdata.BKdata.mdrTyp1 == bkdata1.mdrTyp1,
                bkdata.BKdata.mdrHysu1 == bkdata1.mdrHysu1,
                bkdata.BKdata.snyuMnskSyuBbnMnsk2 == bkdata1.snyuMnskSyuBbnMnsk2
            )

            # 2年以内の物件に絞る
            cutoff_date = datetime.datetime.now() - datetime.timedelta(days=730)
            query = query.filter(bkdata.BKdata.kknnngp > cutoff_date)
            query = query.order_by(bkdata.BKdata.kknnngp)

            results = query.fetch()
            if results:
                do_set(bkdata1, results)


def do_set(bkdata1, bkdata2_list):
    """
    重複の場合の処理
    先にあった物件が確認1年以内で資料請求済み以降の場合、先にあった物件を生かす、あとの物件を重複
    先にあった物件が確認1年以上または資料請求していない場合、先にあった物件が重複、あとの物件を生かす
    """
    for data in bkdata2_list:
        days_diff = (datetime.datetime.now() - data.kknnngp).days

        if days_diff > 365:
            # 1年以上経過している場合
            data.kknnngp = datetime.datetime.now()
            data.dtsyuri = u"重複"
            data.jshKnrrn = str_plus(data.jshKnrrn, u"to:" + bkdata1.bkID)
        else:
            # 1年以下の場合
            if data.sksijky in [u"資料請求", u"依頼中", u"入手済み", u"分類チェック", u"未作成", u"作成済み", u"ＨＰ掲載"]:
                data.kknnngp = datetime.datetime.now()
                bkdata1.dtsyuri = u"重複"
                bkdata1.jshKnrrn = str_plus(bkdata1.jshKnrrn, u"to:" + data.bkID)
                bkdata1.put()
            else:
                data.kknnngp = datetime.datetime.now()
                data.dtsyuri = u"重複"
                data.jshKnrrn = str_plus(data.jshKnrrn, u"to:" + bkdata1.bkID)

        data.put()


def str_plus(a, b):
    """
    文字列結合ユーティリティ
    """
    if a:
        return a + b
    else:
        return b


# Flask ルート定義
def duplication_check_route():
    """
    重複チェック処理のメインエントリーポイント
    """
    if request.method == 'GET':
        return get_duplication_check()
    else:
        return get_duplication_check()
