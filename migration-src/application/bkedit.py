#!/usr/bin/env python
# -*- coding: utf-8 -*-
#

'''

 1 class JsonField(CharField):
 2     """ JSONデータをポストする場合のフィールド。AJAXに便利かも """
 3
 4     def __init__(self, *args, **kwargs):
 5         super(JsonField, self).__init__(*args, **kwargs)
 6
 7     def clean(self, value):
 8         from google.appengine.dist import use_library
use_library('django', '1.2')
from django.utils import simplejson
 9         value = super(JsonField, self).clean(value)
10         try:
11             json_data = simplejson.loads(value)
12         except Exception as e:
13             raise ValidationError(self.error_messages['invalid'])
14         return json_data

セレクトボックスや、チェックボックスで複数チェックされてリクエストされた場合に、チェックされた全ての値を読み取るには、
request.POST.getlist(キー)
とやる。キーに対応する全ての値がリストで貰える。
https://djangoproject.jp/doc/ja/1.0/ref/request-response.html

'''

import os
from flask import request, render_template
from application.models import bkdata
from application.models import Branch
import datetime

from dataProvider.bkdataProvider import bkdataProvider
from application.timemanager import utc2jst_date
from application.wordstocker import wordstocker


def bkedit_route(bkID=None):
    """
    BKEdit route handler (converted from webapp2.RequestHandler)

    Migrated from: webapp2.RequestHandler (BKEdit class)
    Original path: /bkedit.html
    """
    tmpl_val = {}
    tmpl_val['error_msg'] = ''
    auth = False

    corp_name = "s-style"
    branch_name = "hon"

    # GET request processing
    if request.method == 'GET':
        bkdp = None
        if bkID is None:
            bkID = request.args.get("bkID")
            if bkID:
                bkdp = bkdataProvider(corp_name, branch_name)
                bkdp.search(bkID)
        else:
            # REVIEW-L3: Initialize bkdp before using set() method
            bkdp = bkdataProvider(corp_name, branch_name)
            bkdp.set(bkID)

        bkdb = {}
        blobs = {}

        # 年号リスト作成
        nengolist = []
        # 昭和年号作成
        for i in range(1926, 1989):
            nengolist.insert(0, [i, "昭和", i-1925])
        # 平成年号作成
        for i in range(1989, 2019):
            nengolist.insert(0, [i, "平成", i-1988])
        # 令和年号作成
        now = utc2jst_date(datetime.datetime.now())
        for i in range(2019, now.year+2):
            nengolist.insert(0, [i, "令和", i-2018])

        cknngtSirkYY = None
        zukickNngt1YY = None
        zukickNngt2YY = None
        zukickNngt3YY = None
        kujKnryuNngtSirkYY = None
        kujKnryuNngtSirkGG = None
        gnkyuYtiNngtYY = None
        gnkyuYtiNngtGG = None
        hkwtsNyukyNngtSirkYY = None
        hkwtsNyukyNngtSirkGG = None
        nyukyNngtSirkYY = None
        nyukyNngtSirkGG = None
        trhkJyuknYukuKgnYY = None
        trhkJyuknYukuKgnGG = None
        bikiKiykNngppSirkYY = None
        bikiKiykNngppSirkGG = None
        shkcKgnSirkYY = None
        shkcKgnSirkGG = None

        if bkdp:
            bkdb = bkdp.bkdb
            blobs = bkdp.blobs
            cknngtSirkYY = bkdp.cknngtSirkYY
            zukickNngt1YY = bkdp.zukickNngt1YY
            zukickNngt2YY = bkdp.zukickNngt2YY
            zukickNngt3YY = bkdp.zukickNngt3YY
            if bkdb.kujKnryuNngtSirk and bkdb.kujKnryuNngtSirk.year > 2018:
                kujKnryuNngtSirkYY = bkdb.kujKnryuNngtSirk.year-2018
                kujKnryuNngtSirkGG = "R"
            elif bkdb.kujKnryuNngtSirk:
                kujKnryuNngtSirkYY = bkdb.kujKnryuNngtSirk.year-1988
                kujKnryuNngtSirkGG = "H"

            if bkdb.gnkyuYtiNngt and bkdb.gnkyuYtiNngt.year > 2018:
                gnkyuYtiNngtYY = bkdb.gnkyuYtiNngt.year-2018
                gnkyuYtiNngtGG = "R"
            elif bkdb.gnkyuYtiNngt:
                gnkyuYtiNngtYY = bkdb.gnkyuYtiNngt.year-1988
                gnkyuYtiNngtGG = "H"

            if bkdb.hkwtsNyukyNngtSirk and bkdb.hkwtsNyukyNngtSirk.year > 2018:
                hkwtsNyukyNngtSirkYY = bkdb.hkwtsNyukyNngtSirk.year-2018
                hkwtsNyukyNngtSirkGG = "R"
            elif bkdb.hkwtsNyukyNngtSirk:
                hkwtsNyukyNngtSirkYY = bkdb.hkwtsNyukyNngtSirk.year-1988
                hkwtsNyukyNngtSirkGG = "H"

            if bkdb.nyukyNngtSirk and bkdb.nyukyNngtSirk.year > 2018:
                nyukyNngtSirkYY = bkdb.nyukyNngtSirk.year-2018
                nyukyNngtSirkGG = "R"
            elif bkdb.nyukyNngtSirk:
                nyukyNngtSirkYY = bkdb.nyukyNngtSirk.year-1988
                nyukyNngtSirkGG = "H"

            if bkdb.trhkJyuknYukuKgn and bkdb.trhkJyuknYukuKgn.year > 2018:
                trhkJyuknYukuKgnYY = bkdb.trhkJyuknYukuKgn.year-2018
                trhkJyuknYukuKgnGG = "R"
            elif bkdb.trhkJyuknYukuKgn:
                trhkJyuknYukuKgnYY = bkdb.trhkJyuknYukuKgn.year-1988
                trhkJyuknYukuKgnGG = "H"

            if bkdb.bikiKiykNngppSirk and bkdb.bikiKiykNngppSirk.year > 2018:
                bikiKiykNngppSirkYY = bkdb.bikiKiykNngppSirk.year-2018
                bikiKiykNngppSirkGG = "R"
            elif bkdb.bikiKiykNngppSirk:
                bikiKiykNngppSirkYY = bkdb.bikiKiykNngppSirk.year-1988
                bikiKiykNngppSirkGG = "H"

            if bkdb.shkcKgnSirk and bkdb.shkcKgnSirk.year > 2018:
                shkcKgnSirkYY = bkdb.shkcKgnSirk.year-2018
                shkcKgnSirkGG = "R"
            elif bkdb.shkcKgnSirk:
                shkcKgnSirkYY = bkdb.shkcKgnSirk.year-1988
                shkcKgnSirkGG = "H"

        tmpl_val = {
            "bkID": bkID,
            "bkdb": bkdb,
            "blobs": blobs,
            "nengolist": nengolist,
            "cknngtSirkYY": cknngtSirkYY,
            "zukickNngt1YY": zukickNngt1YY,
            "zukickNngt2YY": zukickNngt2YY,
            "zukickNngt3YY": zukickNngt3YY,
            "kujKnryuNngtSirkGG": kujKnryuNngtSirkGG,
            "gnkyuYtiNngtGG": gnkyuYtiNngtGG,
            "hkwtsNyukyNngtSirkGG": hkwtsNyukyNngtSirkGG,
            "nyukyNngtSirkGG": nyukyNngtSirkGG,
            "trhkJyuknYukuKgnGG": trhkJyuknYukuKgnGG,
            "bikiKiykNngppSirkGG": bikiKiykNngppSirkGG,
            "shkcKgnSirkGG": shkcKgnSirkGG,
            "kujKnryuNngtSirkYY": kujKnryuNngtSirkYY,
            "gnkyuYtiNngtYY": gnkyuYtiNngtYY,
            "hkwtsNyukyNngtSirkYY": hkwtsNyukyNngtSirkYY,
            "nyukyNngtSirkYY": nyukyNngtSirkYY,
            "trhkJyuknYukuKgnYY": trhkJyuknYukuKgnYY,
            "bikiKiykNngppSirkYY": bikiKiykNngppSirkYY,
            "shkcKgnSirkYY": shkcKgnSirkYY,
            "iconlist": wordstocker.get(corp_name, "アイコン")
        }
        return render_template('bkedit.html', **tmpl_val)

    # POST request processing
    elif request.method == 'POST':
        # ログインユーザーを設定する
        bkdp = bkdataProvider(corp_name, branch_name)
        bkID = bkdp.put(request)

        # Recursively call GET handler
        return bkedit_route(bkID=bkID)
