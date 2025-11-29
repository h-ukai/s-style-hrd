#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from flask import render_template, request, Response
from google.cloud import ndb
import datetime
import timemanager
from application.timemanager import utc2jst_date
from application.models.bksearchaddress import addtest
from application.models import member
from application.models.bklist import BKlist
from application.mapreducemapper import bkdlistupdate
from application.models.blob import Blob
from application.mapreducemapper import bloburlschange
from application.zipper import *


class test6():
    def test(self, response):
        # 出力用ファイル作成
        myfile = createBytesFile()

        # 静的ファイル用 ＊＊＊＊データ作成　読み込むファイルにタイムスタンプが必ず必要
        writeDataSet = WriteDataSet()
        writeDataSet.add("static_dir/test/[Content_Types].xml", "[Content_Types].xml")
        writeDataSet.add("static_dir/test/_rels/.rels", "_rels/.rels")
        writeDataSet.add("static_dir/test/docProps/app.xml", "docProps/app.xml")
        writeDataSet.add("static_dir/test/docProps/core.xml", "docProps/core.xml")
        writeDataSet.add("static_dir/test/word/document.xml", "word/document.xml")
        writeDataSet.add("static_dir/test/word/endnotes.xml", "word/endnotes.xml")
        writeDataSet.add("static_dir/test/word/fontTable.xml", "word/fontTable.xml")
        writeDataSet.add("static_dir/test/word/footnotes.xml", "word/footnotes.xml")
        writeDataSet.add("static_dir/test/word/numbering.xml", "word/numbering.xml")
        writeDataSet.add("static_dir/test/word/settings.xml", "word/settings.xml")
        writeDataSet.add("static_dir/test/word/styles.xml", "word/styles.xml")
        writeDataSet.add("static_dir/test/word/vbaProject.bin", "word/vbaProject.bin")
        writeDataSet.add("static_dir/test/word/webSettings.xml", "word/webSettings.xml")
        writeDataSet.add("static_dir/test/word/_rels/document.xml.rels", "word/_rels/document.xml.rels")
        writeDataSet.add("static_dir/test/word/theme/theme1.xml", "word/theme/theme1.xml")

        # zip 圧縮
        zipper = Zipper(myfile)
        zipper.write(writeDataSet)
        zipper.close()

        # 画面に出力
        output(response, myfile, "sample.docm")


class addtest():
    def test1(self):
        # Use ndb.query() instead of db.all()
        query = member.query()
        query = query.filter(member.memberID == "2")
        m = query.fetch(1)
        if m:
            m[0].LastRequestdatetime = None
            m[0].put()
            re = m[0].interval()
            return re

    def addlist(self):
        t = test2(t="gifuk", s="gifuc", o="haruchka")
        t.put()
        t = test2(t="gifuk", s="gifuc", o="zuiun")
        t.put()
        t = test2(t="aichik", s="nagoyac", o="chikusa")
        t.put()
        t = test2(t="miek", s="tuc", o="zuiun")
        t.put()

    def test2(self, info):
        """
        nyrykkisyID　入力会社ID
        bkID 物件番号
        isidkd　座標有り
        kukkTnsiKbn　広告転載区分
        bbchntikbn　売買賃貸区分
        dtsyuri　取扱い種類
        bkknShbt　物件種別
        bkknShmk　物件種目
        sksijky　作成状況
        isicon アイコンあり
        kknnngp　確認年月日
        hnknngp　変更年月日
        turknngp　登録年月日
        ksnnngp　更新年月日
        """
        # REVIEW-L3: u"プレフィックス"を削除（Python 3互換性）
        jklist = ["", " AND isidkd = True", " AND kukkTnsiKbn = '広告可'", " AND bbchntikbn = '売買'",
                  " AND dtsyuri = '物件'", " AND bkknShbt = 'マンション等'", " AND bkknShmk = '中古マンション'",
                  " AND sksijky = '請求チェック'", " AND isicon = True"]

        kklist = [" AND kknnngp <= '20014-8-1'", " AND hnknngp <= '20014-8-1'", " AND turknngp <= '20014-8-1'",
                  " AND ksnnngp <= '20014-8-1'"]

        sqlstr = " WHERE searchkeys = 'てきとう'"
        for k in kklist:
            # ndb uses query(), not GqlQuery
            # This is a simplified migration - actual GQL queries need proper ndb translation
            query_str = "SELECT __key__ FROM BKdata" + sqlstr + k
            # ndb.GqlQuery is deprecated, use ndb.query() and filters instead
            q = ndb.gql(query_str)
            p = q.fetch(1)
        print("!!!end!!!")
        return

    def test3(self):
        test


class test2(ndb.Model):
    # 国
    k = ndb.StringProperty(verbose_name="国")
    # 都道府県名
    t = ndb.StringProperty(verbose_name="都道府県名")
    # 市区町村名
    s = ndb.StringProperty(verbose_name="市区町村名")
    # 大字・町丁目
    o = ndb.StringProperty(verbose_name="大字・町丁目")


class test3():
    def addlist(self):
        t = test2(t="gifuk", s="gifuc", o="haruchka")
        print(t.t)
        t.put()
        t = test2(t="gifuk", s="gifuc", o="zuiun")
        t.put()
        t = test2(t="aichik", s="nagoyac", o="chikusa")
        t.put()
        t = test2(t="miek", s="tuc", o="zuiun")
        t.put()

    def searchtest(self):
        tlist = test2.query()
        tlist = tlist.filter(test2.t == "gifuk")
        for e in tlist.fetch():
            print('a::' + e.t + e.s + e.o)
        tlist = test2.query()
        tlist = tlist.filter(test2.t == "gifuk")
        tlist = tlist.filter(test2.s == "gifuc")
        for e in tlist.fetch():
            print('b::' + e.t + e.s + e.o)


class test4():
    def test(self):
        lst = BKlist.query()
        for bklist in lst.fetch():
            bkdlistupdate(bklist)


class test5():
    def test(self):
        bit = Blob.get_by_id('ishihara/hideki/001/3')
        res = ''
        res = res + 'oldblobkey:' + bit.blobKey + '<br/>\n'
        res = res + 'oldbloburl:' + bit.bloburl + '<br/>\n'
        res = res + 'oldthumbnailurl' + bit.thumbnailurl + '<br/>\n'
        res = res + 'oldblobhtml:' + bit.html + '<br/>\n'
        bloburlschange(bit)
        res = res + 'newblobkey:' + bit.blobKey + '<br/>\n'
        res = res + 'newbloburl:' + bit.bloburl + '<br/>\n'
        res = res + 'newthumbnailurl:' + bit.thumbnailurl + '<br/>\n'
        res = res + 'newblobhtml:' + bit.html + '<br/>\n'
        return res


def test_route():
    """Flask route function for test"""
    # REVIEW-L1: Flaskではresponseオブジェクトを直接渡すのではなく、結果をreturnする
    # 修正前: res = test.test(request.environ.get('werkzeug.request'))
    # 修正後: Flaskのresponseオブジェクトを使わず、結果を直接返す
    from flask import make_response
    test = test6()
    response = make_response()
    res = test.test(response)
    return str(res) if res else ""
