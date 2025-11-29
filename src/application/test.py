#!/usr/local/bin/python
# -*- coding: utf-8 -*-
#from google.appengine.dist import use_library
#use_library('django', '1.2')

import os
#from google.appengine.ext import webapp
import webapp2
from google.appengine.ext.webapp import template

from application.models.bksearchaddress import addtest



#os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
#from google.appengine.dist import use_library
#use_library('django', '1.2')

import datetime
import timemanager
from application.timemanager import utc2jst_date
# from google.storage.speckle.proto.jdbc_type import BIT


class test(webapp2.RequestHandler):
    def get(self):

        test = test6()
        res = test.test(self.response)
        self.response.out.write(str(res))
        """
        test = test6(self.response)
        res = test.test()
        self.response.out.write(str(res))
        self.tmpl_val = {"res":res}
        path = os.path.dirname(__file__) + '/../templates/test.html'
        self.response.out.write(template.render(path, self.tmpl_val))
        """

    def post(self):
        self.get()

from application.models import member

class addtest():
    def test1(self):
        mem = member.member.all()
        mem.filter("memberID", "2")
        m=mem.fetch(1)
        m[0].LastRequestdatetime=None
        m[0].put()
        re = m[0].interval()
        return re



    def addlist(self):
        t = test2(t=u"gifuk",s=u"gifuc",o=u"haruchka")
        t.put()
        t = test2(t=u"gifuk",s=u"gifuc",o=u"zuiun")
        t.put()
        t = test2(t=u"aichik",s=u"nagoyac",o=u"chikusa")
        t.put()
        t = test2(t=u"miek",s=u"tuc",o=u"zuiun")
        t.put()

    def test2(self,info):
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
        jklist = [u"",u" AND isidkd = True",u" AND kukkTnsiKbn = '広告可'",u" AND bbchntikbn = '売買'",u" AND dtsyuri = '物件'",u" AND bkknShbt = 'マンション等'",u" AND bkknShmk = '中古マンション'",u" AND sksijky = '請求チェック'",u" AND isicon = True"]

        kklist = [" AND kknnngp <= '20014-8-1'", " AND hnknngp <= '20014-8-1' "," AND turknngp <= '20014-8-1'"," AND ksnnngp <= '20014-8-1'"]

        sqlstr = " WHERE searchkeys = 'てきとう'"
        for k in kklist:
            q = db.GqlQuery("SELECT __key__ FROM BKdata " + sqlstr + k )
            p = q.get()
        print("!!!end!!!")
        return



        '''
        コンソールでテストするとき
        コードを書き換えるたびにコンソールを開き直す必要があってめんどいぞ
        import os
        import sys
        import tempfile

        DIR_PATH = r"C:\Program Files (x86)\Google\google_appengine"
        APP_ID = "amanedb"

        sys.path += [
          DIR_PATH,
          os.path.join(DIR_PATH, 'lib', 'antlr3'),
          os.path.join(DIR_PATH, 'lib', 'django'),
          os.path.join(DIR_PATH, 'lib', 'fancy_urllib'),
          os.path.join(DIR_PATH, 'lib', 'ipaddr'),
          os.path.join(DIR_PATH, 'lib', 'webob'),
          os.path.join(DIR_PATH, 'lib', 'yaml', 'lib'),
        ]

        from google.appengine.api import apiproxy_stub_map,datastore_file_stub

        os.environ['APPLICATION_ID'] = APP_ID

        datastore_path = os.path.join(tempfile.gettempdir(), 'dev_appserver.datastore')
        apiproxy_stub_map.apiproxy = apiproxy_stub_map.APIProxyStubMap()
        datastore = datastore_file_stub.DatastoreFileStub(APP_ID, datastore_path)
        apiproxy_stub_map.apiproxy.RegisterStub('datastore_v3', datastore)

        from application.test import test3
        '''

    def test3(self):
        test


from google.appengine.ext import db
class test2(db.Model):
    #国
    k = db.StringProperty(verbose_name=u"国")
    #都道府県名
    t = db.StringProperty(verbose_name=u"都道府県名")
    #市区町村名
    s = db.StringProperty(verbose_name=u"市区町村名")
    #大字・町丁目
    o = db.StringProperty(verbose_name=u"大字・町丁目")

class test3():
    def addlist(self):
        t = test2(t=u"gifuk",s=u"gifuc",o=u"haruchka")
        print t.t
        t.put()
        t = test2(t=u"gifuk",s=u"gifuc",o=u"zuiun")
        t.put()
        t = test2(t=u"aichik",s=u"nagoyac",o=u"chikusa")
        t.put()
        t = test2(t=u"miek",s=u"tuc",o=u"zuiun")
        t.put()
    def searchtest(self):
        tlist = test2.all()
        tlist.filter("t =", u"gifuk")
        for e in tlist:
            print 'a::' + e.t + e.s + e.o
        tlist = test2.all()
        tlist.filter("t =", u"gifuk")
        tlist.filter("s=",u"gifuc")
        for e in tlist:
            print 'b::' + e.t + e.s + e.o


from application.models.bklist import BKlist
from application.mapreducemapper import bkdlistupdate
class test4():
    def test(self):
        lst = BKlist.all()
        for bklist in lst:
            bkdlistupdate(bklist)


from application.models.blob import Blob
from application.mapreducemapper import  bloburlschange
class test5():
    def test(self):
        bit = Blob.get_by_key_name('ishihara/hideki/001/3')
        #bit = Blob.get_by_key_name('s-style/hon/1/1')
        res = ''
        res = res + 'oldblobkey:' + bit.blobKey + '<br/>\n'
        res = res +  'oldbloburl:' + bit.bloburl + '<br/>\n'
        res = res +  'oldthumbnailurl' + bit.thumbnailurl  + '<br/>\n'
        res =  res + 'oldblobhtml:' + bit.html + '<br/>\n'
        bloburlschange(bit)
        res = res + 'newblobkey:' + bit.blobKey + '<br/>\n'
        res = res +  'newbloburl:' + bit.bloburl + '<br/>\n'
        res = res +  'newthumbnailurl:' + bit.thumbnailurl  + '<br/>\n'
        res =  res + 'newblobhtml:' + bit.html + '<br/>\n'
        return res

from application.zipper import *
class test6():
    def test(self,response):
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
        """
        # バイトストリーム用 データ作成
        writeStrDataSet = WriteStrDataSet()
        writeStrDataSet.add(bytesA, createZipInfoOfNowTime("test.swf"))
        writeStrDataSet.add(bytesB, createZipInfoOfNowTime("test/aaa.swf"))
        """

        # zip 圧縮
        zipper = Zipper(myfile)
        #zipper.write(writeDataSet, writeStrDataSet)
        zipper.write(writeDataSet)
        zipper.close()

        # 画面に出力
        output(response, myfile, "sample.docm")
