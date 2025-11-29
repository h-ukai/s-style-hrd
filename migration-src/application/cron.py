#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask, request, Response
from google.cloud import ndb
from application.models.member import member
from application.bksearchutl import bksearchutl
from application.messageManager import messageManager
from application.bklistutl import bklistutl
from application import timemanager

import datetime
import logging

def cron_jobs_route():
    """Cron jobs handler for periodic task execution"""
    # REVIEW-L2: member.get_by_key_name() は ndb.Model の互換性メソッド
    # 推奨: ndb.Model に直接実装するか、互換性ラッパーの確認が必要
    try:
        key_name = "s-style/systemwebsearch@s-style"
        mmdb = member.get_by_key_name(key_name)
        if not mmdb:
            logging.warning("System member not found: %s", key_name)
            return Response("System member not found", status=404)

        corp = mmdb.CorpOrg_key_name
        branch = mmdb.Branch_Key_name
        dat = ""

        # REVIEW-L2: bksearchdata_set の実装確認が必要
        # 推奨: member.py の bksearchdata_set プロパティが ndb.query() を返すか、
        #       または bksearchdata.query().filter() でクエリを実行する
        # ndb query for search data
        sddblist = mmdb.bksearchdata_set  # Relationship query (if using query API)
        # If bksearchdata_set is not available, use:
        # from application.models.bksearchdata import bksearchdata
        # sddblist = bksearchdata.query().filter(
        #     bksearchdata.modified == ndb.Key(member, key_name)
        # ).order(bksearchdata.name)

        meslist = messageManager.getmeslist("s-style", mmdb, order="reservation")
        kknnngp = datetime.datetime.now()
        kknnngp = timemanager.utc2jst_date(kknnngp)
        kknnngp = timemanager.add_months(kknnngp, -1)
        kknnngp = kknnngp.strftime("%Y/%m/%d")

        i = 0
        for sddb in sddblist:
            if dat:
                dat += ","
            # REVIEW-L3: インデックス範囲チェックが追加されているが、
            # meslist が sddblist より少ない場合、処理が途中で止まる
            # 提案: sddb と meslist の対応関係を確認し、適切なロジックに修正
            # Skip completed messages
            while i < len(meslist) and meslist[i].done:
                i += 1

            # REVIEW-L1: meslist[i].key() → meslist[i].key (ndb では key プロパティ)
            # 修正前: bklistutl.remalllistbykey(corp, branch, meslist[i].key())
            # 修正後: bklistutl.remalllistbykey(corp, branch, meslist[i].key)
            if i < len(meslist):
                bklistutl.remalllistbykey(corp, branch, meslist[i].key)
                # Legacy: do_searchdb2 may need refactoring
                # dat += bksearchutl.do_searchdb2(sddb, msgkey=meslist[i].key, hnknngp=kknnngp)
                dat += bksearchutl.do_searchdb2(sddb, msgkey=meslist[i].key)
                i += 1

        return Response(dat, content_type='text/plain; charset=utf-8')

    except Exception as e:
        logging.error("Cron job error: %s", str(e))
        return Response("Error: " + str(e), status=500)
