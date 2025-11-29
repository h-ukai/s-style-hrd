# -*- coding: utf-8 -*-

from models.member import member
from models.bksearchdata import bksearchdata
from models.bkdata import BKdata
#import timemanager
from models.CorpOrg import CorpOrg  # @UnusedImport
#from models.Branch import Branch
#from models.bksearchaddress import *
#import models.blob
#import datetime
#import re
#from google.appengine.ext import webapp
import webapp2  # @UnresolvedImport
from messageManager import messageManager
from bklistutl import bklistutl
from google.appengine.api import memcache  # @UnresolvedImport
#import time
import logging
import math
from models.message import Message
import datetime

from google.appengine.ext import db
from google.appengine.api import taskqueue  # @UnresolvedImport
from application import timemanager

from application import CriticalSection

class memcachecount():
    def __init__(self, key):
        self.key = 'bksearchutl:' + str(key)
        self.cp = CriticalSection.CriticalSection(self.key)
    def add(self):
        if self.cp.lock:
            res = memcache.get(self.key)
            if res:
                res += 1
                memcache.set(self.key,res,60*90)
            else:
                res = 1
                memcache.add(self.key,res,60*90)
            self.cp.unlock()
            return res
    def sub(self):
        if self.cp.lock:
            res = memcache.get(self.key)
            if res:
                res -= 1
                memcache.set(self.key,res,60*90)
            else:
                res = 0
            self.cp.unlock()
            return res




class allsearchWorker_error(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class allsearchWorker(webapp2.RequestHandler):
    def get(self):
        self.post()

    def post(self): # should run at most 1/s
        logging.debug('filterWorker')
        sddbkey = self.request.get('sddbkey')
        msgkey = self.request.get('msgkey',None)
        hnknngpL = self.request.get('hnknngpL',None)
        if msgkey:
            pass
        else:
            logging.error('allsearchWorker key error(missingmsgkey) ')





class filterWorker_error(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class filterWorker(webapp2.RequestHandler):
    def get(self):
        self.post()

    def post(self): # should run at most 1/s
        sddbkey = self.request.get('sddbkey')
        sddb = bksearchdata.get(sddbkey)
        msgkey = self.request.get('msgkey',None)
        hnknngpL = self.request.get('hnknngpL',None)
        flg = self.request.get('flg',None)
        if flg == 'True':
            flg=True
        logging.debug('filterWorker ::' + msgkey)
        if msgkey:
            msgkey = Message.get(msgkey).key()
            corp_name = sddb.member.CorpOrg_key_name
            now = timemanager.utc2jst_date(datetime.datetime.now())
            if self.request.headers.environ.get('HTTP_X_APPENGINE_TASKRETRYCOUNT'):
                if( int(self.request.headers.environ['HTTP_X_APPENGINE_TASKRETRYCOUNT']) > 5):
                    logging.error('filterWorker retry error(over 5 times) msgID:' + str(msgkey.id()))
                    sub = u"検索失敗… 　検索を処理しきれませんでした" + u" (" + now.strftime("%Y/%m/%d %H:%M:%S") + u")"
                    body = sddb.name
                    messageManager.post(corp=corp_name,sub=sub,body=body,done=False,memfrom=None,kindname=None,combkind=u"所有",msgkey=msgkey.id(),reservation=None,reservationend=None,memto=None,commentto=None,mailto=None)
                    return
            logging.info('do_searchdb start')
            flist = bksearchutl.do_searchdb(sddb,hnknngpL)
            logging.info('do_searchdb end')
            mc = memcachecount(str(msgkey))
            res = mc.sub()
            cp = CriticalSection.CriticalSection('cplockinfilterWorker'+str(msgkey))
            if cp.lock():
                rc = bklistutl.extendlistbykeys(corp_name, flist, msgkey,sddb.member,senddate=None,sended=None,memo=None,flg=flg)
                #          def extendlistbykeys(cls,corp,keys,refmes,refmem=None,senddate=None,sended=None,memo=None,flg=None):
                if res<=0:
                    sub = u"検索結果 " + str(rc) + u" (" + now.strftime("%Y/%m/%d %H:%M:%S") + u")"
                    body = sddb.name
                    messageManager.post(corp=corp_name,sub=sub,body=body,done=False,memfrom=None,kindname=None,combkind=u"所有",msgkey=msgkey.id(),reservation=None,reservationend=None,memto=None,commentto=None,mailto=None)
                else:
                    sub = u"検索中 / " + str(res ) + u" (" + now.strftime("%Y/%m/%d %H:%M:%S") + u")"
                    body = sddb.name
                    messageManager.post(corp=corp_name,sub=sub,body=body,done=False,memfrom=None,kindname=None,combkind=u"所有",msgkey=msgkey.id(),reservation=None,reservationend=None,memto=None,commentto=None,mailto=None)
                cp.unlock()
                logging.info('extendlistbykeys::end')
        else:
            logging.error('filterWorker key error(missingmsgkey) ')

        """
        """

class filterWorker2(webapp2.RequestHandler):
    def post(self): # should run at most 1/s
        sddbkey = self.request.get('sddbkey')
        sddb = bksearchdata.get(sddbkey)
        msgkey = self.request.get('msgkey',None)
        hnknngpL = self.request.get('hnknngpL',None)
        logging.debug('do_searchdb start')
        corp_name = sddb.member.CorpOrg_key_name
        if( int(self.request.headers.environ['HTTP_X_APPENGINE_TASKRETRYCOUNT']) > 5):
            logging.error('filterWorker retry error(over 5 times) msgID:' + str(msgkey.id()))
            sub = u"検索失敗… 　検索を処理しきれませんでした"
            body = sddb.name
            messageManager.post(corp=corp_name,sub=sub,body=body,done=False,memfrom=None,kindname=None,combkind=u"所有",msgkey=msgkey.id(),reservation=None,reservationend=None,memto=None,commentto=None,mailto=None)
            return
        if msgkey:
            msgkey = Message.get(msgkey).key()
            bksearchutl.do_searchdb3(sddb,msgkey,hnknngpL)
            return
        else:
            logging.error('filterWorker key error(missingmsgkey) ')

        """
        """


class autoautosearchlog(db.Model):
    corp = db.StringProperty(verbose_name=u"会社ID")
    branch = db.StringProperty(verbose_name=u"支店ID")
    sitename = db.StringProperty(verbose_name=u"サイト名")
    date = db.DateTimeProperty(auto_now_add = True,verbose_name=u"タイムスタンプ")

    def getlast(self,corp,branch=None,sitename=None):
        lastdate = db.Model.all()
        lastdate.filter("copr = ", corp)
        if branch:
            lastdate.filter("branch = ", branch)
        if sitename:
            lastdate.filter("sitename = ", sitename)
        lastdate.order('-date')
        l=lastdate.fetch(1)
        if l.count():
            return l.date

    def newadd(self,corp,branch=None,sitename=None):
        self.corp=corp
        self.branch=branch
        self.sitename=sitename
        db.Model.put()

class bksearchutl(object):

    @classmethod
    def memberProcessing(cls,corp):
        pass

    @classmethod
    def do_autosearch(cls,corp,branch=None,sitename=None,body=None):
        kindname = u"マッチング"
        query = member.all(keys_only = True)
        query.filter("CorpOrg_key_name = ",corp)
        if branch:
            query.filter("Branch_Key_name = ",branch)
        if sitename:
            query.filter("sitename = ",sitename)
        query.filter("seiyaku = ",u"未成約" )
        query.filter("service = ",u"マッチング")
        list = query.fetch(100000000)

        log =  autoautosearchlog()
        lastdate=log.getlast(corp, branch, sitename)
        log.corp=corp
        log.branch=branch
        log.sitename=sitename
        log.put()

        sub = u"自動検索  : " + timemanager.utc2jst_date(datetime.datetime.now()).strftime("%Y/%m/%d %H:%M:%S")

        for i in range(0,list.count(),500):
            cls.do_bksearchFromMamberlist(corp,db.get(list[i:i+500]),kindname,sub,body,True,None,lastdate)
        return

    @classmethod
    def do_bksearchFromMamberlist(cls,corp,memberlist,kindname,sub=None,body=None,done=None,mailto=None,hnknngpL=None):
        #現在未利用
        for member in memberlist:
            bklist = cls.do_allsearch(member,hnknngpL)
            cls.addlist(cls,corp,member,kindname,bklist,sub,body,done,mailto)

    @classmethod
    def addlist(cls,corp,mem,kindname,bklist=None,sub=None,body=None,done=None,mailto=None):
        #bkdataSearchProvider  if submit == u"検索" or submit == "search" or submit == u"新規ページへ保存して検索":で使用
        #メッセージと物件リストをセットする簡単なメソッド
        #subとbodyはあとでましなものに替えること
        if not sub:
            sub = u"検索結果 "
        if bklist :
            sub += str(len(bklist))
        if not body:
            body = u"検索結果"
        msgkey = messageManager.post(corp=corp,sub=sub,body=body,done=done,memfrom=mem.memberID,kindname=kindname,combkind=u"所有",msgkey=None,reservation=None,reservationend=None,memto=None,commentto=None,mailto=mailto)
        if bklist:
            bklistutl.extendlistbykeys(corp, bklist, msgkey,mem)
        return msgkey.id()

    @classmethod
    def do_allsearch(cls,memdb,msgkey,hnknngpL=None,flg=None):
        templist = []
        for sddb in memdb.bksearchdata_set.order("sortkey"):
            templist.append(cls.do_searchdb2(sddb,msgkey,hnknngpL,flg))
        return templist

    @classmethod
    def do_allsearch2(cls,memdb,hnknngpL=None):
        #現在未利用
        bkkeylist = []
        for sddb in memdb.bksearchdata_set.order("sortkey"):
            templist = cls.do_searchdb(sddb,hnknngpL)
            for key1 in templist:
                for key2 in bkkeylist:
                    if key1 == key2:
                        break
                else:
                    bkkeylist.append(key1)
        return bkkeylist



    @classmethod
    def do_searchdb(cls,sddb,hnknngpL=None):

        """
                   物件検索における日時はすべてUTCで行う
        　　　　与えられた日時変数はUTC変換されたものであることが前提

        https://stackoverflow.com/questions/5954846/app-engine-entity-to-dictionary
　　　　　　　エンティティを辞書に
        foo.__dict__
        dict([(x,getattr(m,x)) for x in m.dynamic_properties()])

        SELECT * FROM Hoge WHERE created >= DATETIME('2011-07-20 00:00:00')
        DATETIME(year, month, day, hour, minute, second)
        DATETIME('YYYY-MM-DD HH:MM:SS')
        DATE(year, month, day)
        DATE('YYYY-MM-DD')
        TIME(hour, minute, second)
        TIME('HH:MM:SS')
        import datetime
        t + datetime.timedelta(days=1)
        """
        cls.corp_name = sddb.member.CorpOrg_key_name
        cls.branch_name = sddb.member.Branch_Key_name

        kwargs = sddb.__dict__
        kwargs = kwargs["_entity"]
        if hnknngpL:
            #変更年月日が引数で与えられた場合検索条件の日時検索を上書きして消す
            #hnknngp = db.DateTimeProperty(verbose_name=u"変更年月日",auto_now_add = True)
            kwargs["hnknngpL"] = hnknngpL
            kwargs["hnknngpU"] = None
            #確認年月日
            #kknnngp = db.DateTimeProperty(verbose_name=u"確認年月日",auto_now_add=True)
            kwargs["kknnngpL"] = None
            kwargs["kknnngpU"] = None
            #登録年月日
            #turknngp = db.DateTimeProperty(verbose_name=u"登録年月日",auto_now_add = True)
            kwargs["turknngpL"] = None
            kwargs["turknngpU"] = None
            #更新年月日
            #ksnnngp = db.DateTimeProperty(verbose_name=u"更新年月日",auto_now=True)
            kwargs["ksnnngpL"] = None
            kwargs["ksnnngpU"] = None
        list = cls.do_search(cls.corp_name,cls.branch_name,kwargs)
        #id = str(datetime.datetime.now()) + str(random.random())
        reskey = []
        chanksize = 50
        listcount = list.count(99999)
        for i in range(0,listcount,chanksize):
            db1 = db.get(list[i:i+chanksize])
            db2 = cls.do_filter(db1, sddb)
            reskey.extend(db2)

            #reskey.extend(cls.do_filter(db.get(list[i:i+100]), sddb))

        return reskey


    @classmethod
    def do_searchdb2(cls,sddb,msgkey,hnknngpL=None,flg=None):
        if not msgkey:
            msgkey=""
        if not hnknngpL:
            hnknngpL = ""
        if flg:
            flg = 'True'
        mc = memcachecount(str(msgkey))
        mc.add()
        mytask = taskqueue.Queue('mintask')
        task = taskqueue.Task(url='/tasks/filterWorker', params={'sddbkey':str(sddb.key()),'msgkey':str(msgkey),'hnknngpL':hnknngpL,'flg':flg},target="memdb2")
        mytask.add(task)
        return sddb.name

    @classmethod
    def do_searchdb3(cls,sddb,msgkey,hnknngpL=None):
        """
                   物件検索における日時はすべてUTCで行う
        　　　　与えられた日時変数はUTC変換されたものであることが前提

        https://stackoverflow.com/questions/5954846/app-engine-entity-to-dictionary
　　　　　　　エンティティを辞書に
        foo.__dict__
        dict([(x,getattr(m,x)) for x in m.dynamic_properties()])

        SELECT * FROM Hoge WHERE created >= DATETIME('2011-07-20 00:00:00')
        DATETIME(year, month, day, hour, minute, second)
        DATETIME('YYYY-MM-DD HH:MM:SS')
        DATE(year, month, day)
        DATE('YYYY-MM-DD')
        TIME(hour, minute, second)
        TIME('HH:MM:SS')
        import datetime
        t + datetime.timedelta(days=1)
        """
        cls.corp_name = sddb.member.CorpOrg_key_name
        cls.branch_name = sddb.member.Branch_Key_name

        kwargs = sddb.__dict__
        kwargs = kwargs["_entity"]
        if hnknngpL:
            #変更年月日
            #hnknngp = db.DateTimeProperty(verbose_name=u"変更年月日",auto_now_add = True)
            kwargs["hnknngpL"] = hnknngpL
            kwargs["hnknngpU"] = None
            #確認年月日
            #kknnngp = db.DateTimeProperty(verbose_name=u"確認年月日",auto_now_add=True)
            kwargs["kknnngpL"] = None
            kwargs["kknnngpU"] = None
            #登録年月日
            #turknngp = db.DateTimeProperty(verbose_name=u"登録年月日",auto_now_add = True)
            kwargs["turknngpL"] = None
            kwargs["turknngpU"] = None
            #更新年月日
            #ksnnngp = db.DateTimeProperty(verbose_name=u"更新年月日",auto_now=True)
            kwargs["ksnnngpL"] = None
            kwargs["ksnnngpU"] = None
        list = cls.do_search(cls.corp_name,cls.branch_name,kwargs)
        #id = str(datetime.datetime.now()) + str(random.random())
        reskey = []
        chanksize = 50
        listcount = list.count(99999)
        for i in range(0,listcount,chanksize):
            db1 = db.get(list[i:i+chanksize])
            db2 = cls.do_filter(db1, sddb)
            sub = u"検索中 ： " + str(i) + '/' + str(math.ceil(listcount/chanksize))
            body = sddb.name
            messageManager.post(corp=cls.corp_name,sub=sub,body=body,done=False,memfrom=None,kindname=None,combkind=u"所有",msgkey=msgkey.id(),reservation=None,reservationend=None,memto=None,commentto=None,mailto=None)
            bklistutl.extendlistbykeys(cls.corp_name, db2, msgkey,sddb.member)
        return

    @classmethod
    def do_searchdb4(cls,sddb,msgkey=None,hnknngpL=None):
        mytask = taskqueue.Queue('mintask')
        if not msgkey:
            msgkey=""
        if not hnknngpL:
            hnknngpL = ""
        task = taskqueue.Task(url='/tasks/filterWorker2', params={'sddbkey':str(sddb.key()),'msgkey':str(msgkey),'hnknngpL':hnknngpL},target="memdb")
        mytask.add(task)
        return sddb.name


    @classmethod
    def do_search(cls,corp,branch,kwargs):

        #物件番号検索
        bkID = kwargs.get("bkID")
        if bkID:
            key_name = corp + "/" + branch + "/" + kwargs["bkID"]
            return [BKdata.get_by_key_name(key_name).key()]

        #売買賃貸区分
        #bbchntikbn = db.StringProperty(verbose_name=u"売買賃貸区分", choices=set([u"売買", u"賃貸"]))
        bbchntikbn = kwargs.get("bbchntikbn")
        bbchntikbn = str(bbchntikbn) if bbchntikbn else ""

        #取扱い種類
        #dtsyuri = db.StringProperty(verbose_name=u"データ種類", choices=set([u"物件",u"事例",u"予約",u"商談中",u"査定中",u"重複",u"停止",u"競売"]))
        dtsyuri = kwargs.get("dtsyuri")
        dtsyuri = str(dtsyuri) if dtsyuri else ""

        #物件種別
        #bkknShbt = db.StringProperty(verbose_name=u"物件種別", choices=set([u"土地", u"戸建住宅等", u"マンション等", u"住宅以外の建物全部", u"住宅以外の建物一部"]))
        bkknShbt = kwargs.get("bkknShbt")
        bkknShbt = str(bkknShbt) if bkknShbt else ""
        #物件種目
        #bkknShmk = db.StringProperty(verbose_name=u"物件種目", choices=set([u"売地", u"借地権", u"底地権",u"新築戸建",u"中古戸建",u"新築テラス",u"中古テラス", u"店舗", u"店舗付住宅", u"住宅付店舗",u"新築マンション",u"中古マンション",u"新築タウン",u"中古タウン",u"新築リゾート",u"中古リゾート",u"事務所", u"店舗事務所", u"ビル", u"工場", u"マンション", u"倉庫", u"アパート", u"寮", u"旅館", u"ホテル", u"別荘", u"リゾート", u"文化住宅", u"その他"]))
        bkknShmk = kwargs.get("bkknShmk")
        bkknShmk  = str(bkknShmk)  if bkknShmk  else ""
        #作成状況
        #sksijky = db.StringProperty(verbose_name=u"作成状況",choices=set([u"請求チェック",u"一覧のみ",u"資料請求",u"依頼中",u"入手不可",u"入手済み",u"分類チェック",u"不要",u"未作成",u"作成済み",u"ＨＰ掲載"]))
        sksijky = kwargs.get("sksijky")
        sksijky  = str(sksijky)  if sksijky else ""
        #アイコンあり
        #isicon = db.BooleanProperty(verbose_name=u"アイコンあり",default=False)
        icons = kwargs.get("icons","")
        if icons:
            isicon="True"
        else:
            isicon=""

        #座標有り
        #isidkd = db.BooleanProperty(verbose_name=u"位置情報有")
        isidkd = kwargs.get("isidkd")
        isidkd = str(isidkd) if isidkd else ""
        #広告転載区分
        kukkTnsiKbn = kwargs.get("kukkTnsiKbn")
        kukkTnsiKbn = str(kukkTnsiKbn) if kukkTnsiKbn else ""
        if kukkTnsiKbn in [u"広告可",u"一部可（インターネット）",u"一部可（チラシ・新聞広告）",u"広告可（但し要連絡）"]:
            kukkk = "True"
        else:
            kukkk = "False"

        sqlstr = " WHERE searchkeys = 'corp:" + corp
        if bbchntikbn:
            sqlstr += "/bbchntikbn:" + bbchntikbn
        if dtsyuri:
            sqlstr += "/dtsyuri:" + dtsyuri
        if bkknShbt:
            sqlstr += "/bkknShbt:"  + bkknShbt
        if bkknShmk:
            sqlstr += "/bkknShmk:" + bkknShmk
        if sksijky:
            sqlstr += "/sksijky:" + sksijky
        if isicon:
            sqlstr += "/isicon:" + isicon
        if isidkd:
            sqlstr += "/isidkd:" + isidkd
        if kukkTnsiKbn:
            sqlstr += "/kukkk:" + kukkk
        sqlstr += "'"

        """
        sqlstr = " WHERE nyrykkisyID = '" + corp + "'"

        if dtsyuri:
            sqlstr += " AND dtsyuri = '" + kwargs["dtsyuri"] + "'"
        if bkknShbt:
            sqlstr += " AND bkknShbt = '" + kwargs["bkknShbt"] + "'"
        if bkknShmk:
            sqlstr += " AND bkknShmk = '" + kwargs["bkknShmk"] + "'"
        if sksijky:
            sqlstr += " AND sksijky = '" + kwargs["sksijky"] + "'"
        if isicon :
            sqlstr += " AND isicon = True "

        if isidkd == True :
            sqlstr += " AND isidkd = True "
        #座標なし
        if isidkd == False :
            sqlstr += " AND isidkd = False "

        if bbchntikbn:
            sqlstr += " AND bbchntikbn = '" + kwargs["bbchntikbn"] + "'"
        if kukkTnsiKbn in [u"広告可",u"一部可（インターネット）",u"一部可（チラシ・新聞広告）",u"広告可（但し要連絡）"]:
            sqlstr += " AND kukkk = True "
        elif kukkTnsiKbn:
            sqlstr += " AND kukkk = False "
        """

        #確認年月日
        #kknnngp = db.DateTimeProperty(verbose_name=u"確認年月日",auto_now_add=True)
        kknnngpL = kwargs.get("kknnngpL")
        if kknnngpL:
            sqlstr += " AND kknnngp >= " + cls.timestr(kwargs["kknnngpL"])

        kknnngpU = kwargs.get("kknnngpU")
        if kknnngpU:
            sqlstr += " AND kknnngp <= " + cls.timestradd1day(kwargs["kknnngpU"])

        #変更年月日
        #hnknngp = db.DateTimeProperty(verbose_name=u"変更年月日",auto_now_add = True)
        hnknngpL = kwargs.get("hnknngpL")
        if hnknngpL:
            sqlstr += " AND hnknngp >= " + cls.timestr(kwargs["hnknngpL"])

        hnknngpU = kwargs.get("hnknngpU")
        if hnknngpU:
            sqlstr += " AND hnknngp <= " + cls.timestradd1day(kwargs["hnknngpU"])

        #登録年月日
        #turknngp = db.DateTimeProperty(verbose_name=u"登録年月日",auto_now_add = True)
        turknngpL = kwargs.get("turknngpL")
        if turknngpL:
            sqlstr += " AND turknngp >= " + cls.timestr(kwargs["turknngpL"])

        turknngpU = kwargs.get("turknngpU")
        if turknngpU:
            sqlstr += " AND turknngp <= " + cls.timestradd1day(kwargs["turknngpU"])

        #更新年月日
        #ksnnngp = db.DateTimeProperty(verbose_name=u"更新年月日",auto_now=True)
        ksnnngpL = kwargs.get("ksnnngpL")
        if ksnnngpL:
            sqlstr += " AND ksnnngp >= " + cls.timestr(kwargs["ksnnngpL"])

        ksnnngpU = kwargs.get("ksnnngpU")
        if ksnnngpU:
            sqlstr += " AND ksnnngp <= " + cls.timestradd1day(kwargs["ksnnngpU"])


        list = []
        list = memcache.get(sqlstr)
        if not list:
            list = db.GqlQuery("SELECT __key__ FROM BKdata " + sqlstr )
            """
            for e in l:
                d = BKdata.get(e).__dict__
                d = d["_entity"]
                d["key"]=str(e)
                list.append(d)
            """
            res = memcache.set(sqlstr, list,30*60) #秒数
            logging.info('memcache not hit... ::' + sqlstr + '  set::' + str(res))
            if res:
                logging.info('memcache set... ::' + sqlstr + '  set::' + str(res))
            else:
                logging.info('memcache not set... ::' + sqlstr + '  set::' + str(res))
        else:
            logging.info('memcache hit !! ::' + sqlstr)
        return list

    @classmethod
    def do_filter(cls,bklist,sddb):

        result = []
        for e in bklist:
            #e = BKdata.get(el)
            flg = True
            #都道府県名
            #tdufknmi = db.StringProperty(verbose_name=u"都道府県名")
            #所在地名1
            #shzicmi1 = db.StringProperty(verbose_name=u"所在地名1")
            #所在地名2
            #shzicmi2 = db.StringProperty(verbose_name=u"所在地名2")
            f2 = False
            for adlist in sddb.adlist:
                for ad1 in adlist.ref_bksearchaddresslist.adset:
                    if e.tdufknmi:
                        if ad1.tdufknmi == e.tdufknmi :
                            if e.shzicmi1:
                                if ad1.shzicmi1 == e.shzicmi1:
                                    if e.shzicmi2:
                                        for ad2 in ad1.address2list:
                                            if ad2.shzicmi2 == e.shzicmi2:
                                                f2 = True
                                                flg = True
                                                break
                                        else:
                                            if ad1.address2list.count() and e.shzicmi2:
                                                flg = False
                                            else:
                                                flg = True
                                                f2 = True
                                    else:
                                        if ad1.address2list.count():
                                            flg = False
                                        else:
                                            flg = True
                                            f2 = True
                                    if f2:
                                        break
                                else:
                                    flg = False
                            else:
                                flg = False
                        else:
                            flg = False
                    else:
                        flg = False
                if f2:
                    break
            if not flg:
                continue
            #沿線略称（1）
            #ensnmi1 = db.StringProperty(verbose_name=u"沿線略称（1）")
            #ensnmi2 = db.StringProperty(verbose_name=u"沿線略称（2）")
            #ensnmi3 = db.StringProperty(verbose_name=u"沿線略称（3）")
            #駅名（1）
            #ekmi1 = db.StringProperty(verbose_name=u"駅名（1）")
            #ekmi2 = db.StringProperty(verbose_name=u"駅名（2）")
            #ekmi3 = db.StringProperty(verbose_name=u"駅名（3）")
            if e.ensnmi1!=None or e.ensnmi2!=None or e.ensnmi3!=None:
                f2 = False
                for ens in sddb.ensen:
                    if ens.ensenmei == None or ens.ensenmei == "":
                        if (ens.thHnU >= e.thHn11 and ens.thHnU and e.thHn11) or (ens.thMU >= e.thM21 and ens.thMU and e.thM21) or (ens.thHnU >= e.thHn12 and ens.thHnU and e.thHn12) or (ens.thMU >= e.thM22 and ens.thMU and e.thM22) or (ens.thHnU >= e.thHn13 and ens.thHnU and e.thHn13) or (ens.thMU >= e.thM23 and ens.thMU and e.thM23):
                            f2 = True
                            break
                    elif ens.ensenmei == e.ensnmi1 or ens.ensenmei == e.ensnmi2 or ens.ensenmei == e.ensnmi3:
                        if ens.eki.count() == 0:
                            #徒歩（分）1（1）
                            #thHn11 = db.FloatProperty(verbose_name=u"徒歩（分）1（1）")
                            #thHn12 = db.FloatProperty(verbose_name=u"徒歩（分）1（2）")
                            #thHn13 = db.FloatProperty(verbose_name=u"徒歩（分）1（3）")
                            #thHnU = db.FloatProperty(verbose_name=u"徒歩（分）上限")
                            #徒歩（m）2（1）
                            #thM21 = db.FloatProperty(verbose_name=u"徒歩（m）2（1）")
                            #thM22 = db.FloatProperty(verbose_name=u"徒歩（m）2（2）")
                            #thM23 = db.FloatProperty(verbose_name=u"徒歩（m）2（3）")
                            #thMU = db.FloatProperty(verbose_name=u"徒歩（m）上限")
                            if ((ens.thHnU == None and ens.thMU == None )
                            or (ens.thHnU >= e.thHn11 and ens.thHnU and e.thHn11)
                            or (ens.thMU >= e.thM21 and ens.thMU and e.thM21)
                            or (ens.thHnU >= e.thHn12 and ens.thHnU and e.thHn12)
                            or (ens.thMU >= e.thM22 and ens.thMU and e.thM22)
                            or (ens.thHnU >= e.thHn13 and ens.thHnU and e.thHn13)
                            or (ens.thMU >= e.thM23 and ens.thMU and e.thM23)):
                                f2 = True
                                break
                        elif e.ekmi1 or e.ekmi2 or e.ekmi3:
                            for eki in ens.eki:
                                if eki.ekimei == e.ekmi1 or eki.ekimei == e.ekmi2 or eki.ekimei == e.ekmi3:
                                    #徒歩（分）1（1）
                                    #thHn11 = db.FloatProperty(verbose_name=u"徒歩（分）1（1）")
                                    #thHn12 = db.FloatProperty(verbose_name=u"徒歩（分）1（2）")
                                    #thHn13 = db.FloatProperty(verbose_name=u"徒歩（分）1（3）")
                                    #thHnU = db.FloatProperty(verbose_name=u"徒歩（分）上限")
                                    #徒歩（m）2（1）
                                    #thM21 = db.FloatProperty(verbose_name=u"徒歩（m）2（1）")
                                    #thM22 = db.FloatProperty(verbose_name=u"徒歩（m）2（2）")
                                    #thM23 = db.FloatProperty(verbose_name=u"徒歩（m）2（3）")
                                    #thMU = db.FloatProperty(verbose_name=u"徒歩（m）上限")
                                    if ((ens.ensenmei == e.ensnmi1 and eki.ekimei == e.ekmi1 and ((ens.thHnU >= e.thHn11 and ens.thHnU and e.thHn11) or (ens.thMU >= e.thM21 and ens.thMU and e.thM21) or (ens.thHnU==None and ens.thMU==None)))
                                    or (ens.ensenmei == e.ensnmi2 and eki.ekimei == e.ekmi2 and ((ens.thHnU >= e.thHn12 and ens.thHnU and e.thHn12) or (ens.thMU >= e.thM22 and ens.thMU and e.thM22) or (ens.thHnU==None and ens.thMU==None)))
                                    or (ens.ensenmei == e.ensnmi3 and eki.ekimei == e.ekmi3 and ((ens.thHnU >= e.thHn13 and ens.thHnU and e.thHn13) or (ens.thMU >= e.thM23 and ens.thMU and e.thM23) or (ens.thHnU==None and ens.thMU==None)))):
                                        f2 = True
                                        break
                            else:
                                if ens.eki.count() != 0 and f2 == False:
                                    flg = False
                else:
                    if sddb.ensen.count() != 0 and f2 == False:
                        flg = False
            else:
                if sddb.ensen.count():
                    flg = False
            if not flg:
                continue

            #間取タイプ（1）
            #mdrTyp1 = db.StringProperty(verbose_name=u"間取タイプ（1）", choices=set([u"ワンルーム",u"K",u"DK",u"LK",u"LDK",u"SK",u"SDK",u"SLK",u"SLDK"]))
            #間取部屋数（1）
            #mdrHysu1 = db.FloatProperty(verbose_name=u"間取部屋数（1）")
            if e.mdrTyp1:
                for mad in sddb.madori:
                    if mad.mdrHysu == e.mdrHysu1 and mad.mdrTyp == e.mdrTyp1:
                        flg = True
                        break
                else:
                    if sddb.madori.count() != 0:
                        flg = False

            #間取タイプ（2）
            #mdrTyp2 = db.StringProperty(verbose_name=u"間取タイプ（2）", choices=set([u"ワンルーム",u"K",u"DK",u"LK",u"LDK",u"SK",u"SDK",u"SLK",u"SLDK"]))
            #間取部屋数（2）
            #mdrHysu2 = db.FloatProperty(verbose_name=u"間取部屋数（2）")
            if e.mdrTyp2:
                for mad in sddb.madori:
                    if mad.mdrHysu == e.mdrHysu2 and mad.mdrTyp == e.mdrTyp2:
                        flg = True
                        break
                else:
                    if sddb.madori.count() != 0:
                        flg = False

            if not e.mdrTyp1 == None and not e.mdrTyp2 == None:
                if sddb.madori.count():
                    flg = True
            if not flg:
                continue
            #接道方向1
            #stduHuku1 = db.StringProperty(verbose_name=u"接道方向1", choices=set([u"北",u"北東",u"東",u"南東",u"南",u"南西",u"西",u"北西"]))
            if e.stduHuku1:
                if sddb.stduHuku ==u'北':
                    if e.stduHuku1  == u'北西' or e.stduHuku1  == u'北' or e.stduHuku1  == u'北東':
                        pass
                    else:
                        flg = False
                if sddb.stduHuku ==u'東':
                    if e.stduHuku1  == u'北東' or e.stduHuku1  == u'東' or e.stduHuku1  == u'南東':
                        pass
                    else:
                        flg = False
                if sddb.stduHuku ==u'南':
                    if e.stduHuku1  == u'南東' or e.stduHuku1  == u'南' or e.stduHuku1  == u'南西':
                        pass
                    else:
                        flg = False
                if sddb.stduHuku ==u'西':
                    if e.stduHuku1  == u'南西' or e.stduHuku1  == u'西' or e.stduHuku1  == u'北西':
                        pass
                    else:
                        flg = False
            #接道方向2
            #stduHuku2 = db.StringProperty(verbose_name=u"接道方向2", choices=set([u"北",u"北東",u"東",u"南東",u"南",u"南西",u"西",u"北西"]))
            if e.stduHuku2:
                if sddb.stduHuku ==u'北':
                    if e.stduHuku2  == u'北西' or e.stduHuku2  == u'北' or e.stduHuku2  == u'北東':
                        pass
                    else:
                        flg = False
                if sddb.stduHuku ==u'東':
                    if e.stduHuku2  == u'北東' or e.stduHuku2  == u'東' or e.stduHuku2  == u'南東':
                        pass
                    else:
                        flg = False
                if sddb.stduHuku ==u'南':
                    if e.stduHuku2  == u'南東' or e.stduHuku2  == u'南' or e.stduHuku2  == u'南西':
                        pass
                    else:
                        flg = False
                if sddb.stduHuku ==u'西':
                    if e.stduHuku2  == u'南西' or e.stduHuku2  == u'西' or e.stduHuku2  == u'北西':
                        pass
                    else:
                        flg = False

            #接道方向3
            #stduHuku3 = db.StringProperty(verbose_name=u"接道方向3", choices=set([u"北",u"北東",u"東",u"南東",u"南",u"南西",u"西",u"北西"]))

            if e.stduHuku3:
                if sddb.stduHuku ==u'北':
                    if e.stduHuku3  == u'北西' or e.stduHuku3  == u'北' or e.stduHuku3  == u'北東':
                        pass
                    else:
                        flg = False
                if sddb.stduHuku ==u'東':
                    if e.stduHuku3  == u'北東' or e.stduHuku3  == u'東' or e.stduHuku3  == u'南東':
                        pass
                    else:
                        flg = False
                if sddb.stduHuku ==u'南':
                    if e.stduHuku3  == u'南東' or e.stduHuku3  == u'南' or e.stduHuku3  == u'南西':
                        pass
                    else:
                        flg = False
                if sddb.stduHuku ==u'西':
                    if e.stduHuku3  == u'南西' or e.stduHuku3  == u'西' or e.stduHuku3  == u'北西':
                        pass
                    else:
                        flg = False

            #接道方向4
            #stduHuku4 = db.StringProperty(verbose_name=u"接道方向4", choices=set([u"北",u"北東",u"東",u"南東",u"南",u"南西",u"西",u"北西"]))
            if e.stduHuku4:
                if sddb.stduHuku ==u'北':
                    if e.stduHuku4  == u'北西' or e.stduHuku4  == u'北' or e.stduHuku4  == u'北東':
                        pass
                    else:
                        flg = False
                if sddb.stduHuku ==u'東':
                    if e.stduHuku4  == u'北東' or e.stduHuku4  == u'東' or e.stduHuku4  == u'南東':
                        pass
                    else:
                        flg = False
                if sddb.stduHuku ==u'南':
                    if e.stduHuku4  == u'南東' or e.stduHuku4  == u'南' or e.stduHuku4  == u'南西':
                        pass
                    else:
                        flg = False
                if sddb.stduHuku ==u'西':
                    if e.stduHuku4  == u'南西' or e.stduHuku4  == u'西' or e.stduHuku4  == u'北西':
                        pass
                    else:
                        flg = False
            if not e.stduHuku1 == None and not e.stduHuku2 == None and not e.stduHuku3 == None and not e.stduHuku4 == None:
                if sddb.stduHuku:
                    flg = True
            if not flg:
                continue

            #バルコニー方向（1）
            #blcnyHuku1 = db.StringProperty(verbose_name=u"バルコニー方向（1）", choices=set([u"北",u"北東",u"東",u"南東",u"南",u"南西",u"西",u"北西"]))
            if e.blcnyHuku1:
                if sddb.blcnyHuku == u'北':
                    if e.blcnyHuku1  == u'北西' or e.blcnyHuku1  == u'北' or e.blcnyHuku1  == u'北東':
                        pass
                    else:
                        flg = False
                if sddb.blcnyHuku == u'東':
                    if e.blcnyHuku1  == u'北東' or e.blcnyHuku1  == u'東' or e.blcnyHuku1  == u'南東':
                        pass
                    else:
                        flg = False
                if sddb.blcnyHuku == u'南':
                    if e.blcnyHuku1  == u'南東' or e.blcnyHuku1  == u'南' or e.blcnyHuku1  == u'南西':
                        pass
                    else:
                        flg = False
                if sddb.blcnyHuku == u'西':
                    if e.blcnyHuku1  == u'南西' or e.blcnyHuku1  == u'西' or e.blcnyHuku1  == u'北西':
                        pass
                    else:
                        flg = False

            #blcnyHuku2 = db.StringProperty(verbose_name=u"バルコニー方向(2)", choices=set([u"北",u"北東",u"東",u"南東",u"南",u"南西",u"西",u"北西"]))
            if e.blcnyHuku2:
                if sddb.blcnyHuku == u'北':
                    if e.blcnyHuku2  == u'北西' or e.blcnyHuku2  == u'北' or e.blcnyHuku2  == u'北東':
                        pass
                    else:
                        flg = False
                if sddb.blcnyHuku == u'東':
                    if e.blcnyHuku2  == u'北東' or e.blcnyHuku2  == u'東' or e.blcnyHuku2  == u'南東':
                        pass
                    else:
                        flg = False
                if sddb.blcnyHuku == u'南':
                    if e.blcnyHuku2  == u'南東' or e.blcnyHuku2  == u'南' or e.blcnyHuku2  == u'南西':
                        pass
                    else:
                        flg = False
                if sddb.blcnyHuku == u'西':
                    if e.blcnyHuku2  == u'南西' or e.blcnyHuku2  == u'西' or e.blcnyHuku2  == u'北西':
                        pass
                    else:
                        flg = False
            #blcnyHuku3 = db.StringProperty(verbose_name=u"バルコニー方向（3）", choices=set([u"北",u"北東",u"東",u"南東",u"南",u"南西",u"西",u"北西"]))
            if e.blcnyHuku2:
                if sddb.blcnyHuku == u'北':
                    if e.blcnyHuku3  == u'北西' or e.blcnyHuku3  == u'北' or e.blcnyHuku3  == u'北東':
                        pass
                    else:
                        flg = False
                if sddb.blcnyHuku == u'東':
                    if e.blcnyHuku3  == u'北東' or e.blcnyHuku3  == u'東' or e.blcnyHuku3  == u'南東':
                        pass
                    else:
                        flg = False
                if sddb.blcnyHuku == u'南':
                    if e.blcnyHuku3  == u'南東' or e.blcnyHuku3  == u'南' or e.blcnyHuku3  == u'南西':
                        pass
                    else:
                        flg = False
                if sddb.blcnyHuku == u'西':
                    if e.blcnyHuku3  == u'南西' or e.blcnyHuku3  == u'西' or e.blcnyHuku3  == u'北西':
                        pass
                    else:
                        flg = False
            if not e.blcnyHuku1 == None and not e.blcnyHuku2 == None and not e.blcnyHuku3 == None:
                if sddb.blcnyHuku:
                    flg = True
            if not flg:
                continue

            #引渡時期
            #hkwtsNyukyJk = db.StringProperty(verbose_name=u"引渡時期", choices=set([u"即時",u"相談",u"期日指定",u"予定"]))
            if not sddb.hkwtsNyukyJk == None:
                if sddb.hkwtsNyukyJk != e.hkwtsNyukyJk :
                    continue

            #ペット可
            #ptflg = db.BooleanProperty(verbose_name=u"ペット可")
            if not sddb.ptflg == None:
                if sddb.ptflg != e.ptflg :
                    continue

            #マッチング可
            #mtngflg = db.BooleanProperty(verbose_name=u"マッチング可")
            if not sddb.mtngflg == None:
                if sddb.mtngflg !=e.mtngflg :
                    continue
            #web検索許可
            #webknskflg = db.BooleanProperty(verbose_name=u"web検索許可")
            if not sddb.webknskflg == None:
                if sddb.webknskflg !=e.webknskflg :
                    continue
            #建築条件
            #knckJyukn = db.StringProperty(verbose_name=u"建築条件", choices=set([u"有",u"無"]))
            if not sddb.knckJyukn == None:
                if sddb.knckJyukn !=e.knckJyukn :
                    continue
            #オーナーチェンジ
            #ornrChng = db.StringProperty(verbose_name=u"オーナーチェンジ")
            if not sddb.ornrChng == None:
                if sddb.ornrChng !=e.ornrChng :
                    continue
            #告知事項
            #kktjkuflg = db.StringProperty(verbose_name=u"告知事項")
            if not sddb.kktjkuflg == None:
                if sddb.kktjkuflg !=e.kktjkuflg :
                    continue
            #アイコン名
            #icons = db.StringListProperty(verbose_name=u"アイコン名")
            if not sddb.icons == None:
                for s in sddb.icons.split(","):
                    for i in e.icons:
                        if s == i:
                            flg = True
                            break
                    else:
                        flg = False
                else:
                    if not flg:
                        continue
            #建物名
            #ttmnmi = db.StringProperty(verbose_name=u"建物名")
            if not sddb.ttmnmi == None:
                if sddb.ttmnmi != e.ttmnmi :
                    continue
            #データ元
            #dataSource = db.StringProperty(verbose_name=u"データ元")
            if not sddb.dataSource == None:
                if sddb.dataSource != e.dataSource :
                    continue
            #広告転載区分
            #kukkTnsiKbn = db.StringProperty(verbose_name=u"広告転載区分", choices=set([u"広告可",u"一部可（インターネット）",u"一部可（チラシ・新聞広告）",u"広告可（但し要連絡）",u"不可",u"未確認"]))
            if not sddb.kukkTnsiKbn == None:
                if sddb.kukkTnsiKbn != e.kukkTnsiKbn:
                    if sddb.kukkTnsiKbn == e.kukkTnsiKbn:
                        pass
                    elif sddb.kukkTnsiKbn == u"広告可" and (e.kukkTnsiKbn == u"一部可（インターネット）" or e.kukkTnsiKbn == u"一部可（チラシ・新聞広告）" or e.kukkTnsiKbn == u"広告可（但し要連絡）"):
                        pass
                    elif  sddb.kukkTnsiKbn == u"一部可（インターネット）" and e.kukkTnsiKbn == u"広告可":
                        pass
                    elif  sddb.kukkTnsiKbn == u"一部可（チラシ・新聞広告）" and e.kukkTnsiKbn == u"広告可":
                        pass
                    elif  sddb.kukkTnsiKbn == u"広告可（但し要連絡）" and e.kukkTnsiKbn == u"広告可":
                        pass
                    else:
                        continue
            #業者名
            #kiinni = db.StringProperty(verbose_name=u"業者名")
            if not sddb.kiinni == None:
                if sddb.kiinni != e.kiinni :
                    continue
            #交通（分）1
            #kutuHn = db.FloatProperty(verbose_name=u"交通（分）")
            #kutuHnU = db.FloatProperty(verbose_name=u"交通（分）上限")
            if not sddb.kutuHnU == None:
                if sddb.kutuHnU < e.kutuHn or not e.kutuHn:
                    continue
            #土地面積
            #tcMnsk2 = db.FloatProperty(verbose_name=u"土地面積")
            #tcMnsk2L = db.FloatProperty(verbose_name=u"土地面積下限")
            #tcMnsk2U = db.FloatProperty(verbose_name=u"土地面積上限")
            if not sddb.tcMnsk2L == None:
                if sddb.tcMnsk2L > e.tcMnsk2 or not e.tcMnsk2:
                    continue
            if not sddb.tcMnsk2U == None:
                if sddb.tcMnsk2U < e.tcMnsk2 or not e.tcMnsk2:
                    continue

            #築年月（西暦）
            #cknngtSirk = db.DateTimeProperty(verbose_name=u"築年月（西暦）")
            #cknngtSirkU = db.DateTimeProperty(verbose_name=u"築年月（西暦）上限")
            #cknngtSirkL = db.DateTimeProperty(verbose_name=u"築年月（西暦）下限")
            if not sddb.cknngtSirkL == None:
                if e.cknngtSirk:
                    if sddb.cknngtSirkL > e.cknngtSirk:
                        continue
            if not sddb.cknngtSirkU == None:
                if e.cknngtSirk:
                    if sddb.cknngtSirkU < e.cknngtSirk:
                        continue
            #地上階層
            #cjyuKisou = db.FloatProperty(verbose_name=u"地上階層")
            #cjyuKisouL = db.FloatProperty(verbose_name=u"地上階層下限")
            #cjyuKisouU = db.FloatProperty(verbose_name=u"地上階層上限")
            if not sddb.cjyuKisouL == None:
                if sddb.cjyuKisouL > e.cjyuKisou or not e.cjyuKisou:
                    continue
            if not sddb.cjyuKisouU == None:
                if sddb.cjyuKisouU < e.cjyuKisou or not e.cjyuKisou:
                    continue

            #所在階
            #shzikiU = db.FloatProperty(verbose_name=u"所在階上限")
            #shzikiL = db.FloatProperty(verbose_name=u"所在階下限")
            if not sddb.shzikiL == None:
                if sddb.shzikiL > e.shziki or not e.shziki:
                    continue
            if not sddb.shzikiU == None:
                if sddb.shzikiU < e.shziki or not e.shziki:
                    continue

            #１階
            #floor1 = db.BooleanProperty(verbose_name=u"１階")
            if not sddb.floor1 == None:
                if e.shziki != 1 :
                    continue

            #最上階
            #topfloor = db.BooleanProperty(verbose_name=u"最上階")
            if not sddb.topfloor == None:
                if sddb.topfloor :
                    if e.cjyuKisou != e.shziki or not e.shziki or not e.cjyuKisou:
                        continue

            #建物面積1
            #ttmnMnsk1 = db.FloatProperty(verbose_name=u"建物面積1")
            #ttmnMnsk1L = db.FloatProperty(verbose_name=u"建物面積下限")
            #ttmnMnsk1U = db.FloatProperty(verbose_name=u"建物面積上限")
            if not sddb.ttmnMnsk1L == None:
                if sddb.ttmnMnsk1L > e.ttmnMnsk1 or not e.ttmnMnsk1:
                    continue
            if not sddb.ttmnMnsk1U == None:
                if sddb.ttmnMnsk1U < e.ttmnMnsk1 or not e.ttmnMnsk1:
                    continue

            #専有面積
            #snyuMnskSyuBbnMnsk2 = db.FloatProperty(verbose_name=u"専有面積")
            #snyuMnskSyuBbnMnsk2L = db.FloatProperty(verbose_name=u"専有面積下限")
            #snyuMnskSyuBbnMnsk2U = db.FloatProperty(verbose_name=u"専有面積上限")
            if not sddb.snyuMnskSyuBbnMnsk2L == None:
                if sddb.snyuMnskSyuBbnMnsk2L > e.snyuMnskSyuBbnMnsk2 or not e.snyuMnskSyuBbnMnsk2:
                    continue
            if not sddb.snyuMnskSyuBbnMnsk2U == None:
                if sddb.snyuMnskSyuBbnMnsk2U < e.snyuMnskSyuBbnMnsk2 or not e.snyuMnskSyuBbnMnsk2:
                    continue

            #価格
            #kkkuCnryu = db.FloatProperty(verbose_name=u"価格")
            #kkkuCnryuL = db.FloatProperty(verbose_name=u"価格下限")
            #kkkuCnryuU = db.FloatProperty(verbose_name=u"価格上限")
            if not sddb.kkkuCnryuL == None:
                if sddb.kkkuCnryuL * 10000 > e.kkkuCnryu or not e.kkkuCnryu:
                    continue
            if not sddb.kkkuCnryuU == None:
                if sddb.kkkuCnryuU * 10000 < e.kkkuCnryu or not e.kkkuCnryu:
                    continue

            #坪単価
            #tbTnk = db.FloatProperty(verbose_name=u"坪単価")
            #tbTnkL = db.FloatProperty(verbose_name=u"坪単価下限")
            #tbTnkU = db.FloatProperty(verbose_name=u"坪単価上限")
            if not sddb.tbTnkL == None:
                if sddb.tbTnkL * 10000 > e.tbTnk or not e.tbTnk:
                    continue
            if not sddb.tbTnkU == None:
                if sddb.tbTnkU * 10000 < e.tbTnk or not e.tbTnk:
                    continue

            #㎡単価
            #m2Tnk = db.FloatProperty(verbose_name=u"㎡単価")
            #m2TnkL = db.FloatProperty(verbose_name=u"㎡単価下限")
            #m2TnkU = db.FloatProperty(verbose_name=u"㎡単価上限")
            if not sddb.m2TnkL == None:
                if sddb.m2TnkL * 10000 > e.m2Tnk or not e.m2Tnk:
                    continue
            if not sddb.m2TnkU == None:
                if sddb.m2TnkU * 10000 < e.m2Tnk or not e.m2Tnk:
                    continue

            #想定利回り（％）
            #sutiRmwrPrcnt = db.FloatProperty(verbose_name=u"想定利回り（％）")
            #sutiRmwrPrcntL = db.FloatProperty(verbose_name=u"想定利回り（％）下限")
            #sutiRmwrPrcntU = db.FloatProperty(verbose_name=u"想定利回り（％）上限")
            if not sddb.sutiRmwrPrcntL == None:
                if sddb.sutiRmwrPrcntL > e.sutiRmwrPrcnt or not e.sutiRmwrPrcnt:
                    continue
            if not sddb.sutiRmwrPrcntU == None:
                if sddb.sutiRmwrPrcntU < e.sutiRmwrPrcnt or not e.sutiRmwrPrcnt:
                    continue

            #接道接面1
            #stduStmn1 = db.StringProperty(verbose_name=u"接道接面1")
            #stduStmnL = db.StringProperty(verbose_name=u"接道接面下限")
            #stduStmnU = db.StringProperty(verbose_name=u"接道接面上限")
            if not sddb.stduStmnL == None:
                if sddb.stduStmnL > e.stduStmn1 or not e.stduStmn1:
                    flg = False
            if not sddb.stduStmnU == None:
                if sddb.stduStmnU < e.stduStmn1 or not e.stduStmn1:
                    flg = False
            #接道接面2
            #stduStmn2 = db.FloatProperty(verbose_name=u"接道接面2")
            if not sddb.stduStmnL == None:
                if sddb.stduStmnL > e.stduStmn2 or not e.stduStmn2:
                    flg = False
            if not sddb.stduStmnU == None:
                if sddb.stduStmnU < e.stduStmn2 or not e.stduStmn2:
                    flg = False
            #接道接面3
            #stduStmn3 = db.FloatProperty(verbose_name=u"接道接面3")
            if not sddb.stduStmnL == None:
                if sddb.stduStmnL > e.stduStmn3 or not e.stduStmn3:
                    flg = False
            if not sddb.stduStmnU == None:
                if sddb.stduStmnU < e.stduStmn3 or not e.stduStmn3:
                    flg = False
            #接道接面4
            #stduStmn4 = db.FloatProperty(verbose_name=u"接道接面4")
            if not sddb.stduStmnL == None:
                if sddb.stduStmnL > e.stduStmn4 or not e.stduStmn4:
                    flg = False
            if not sddb.stduStmnU == None:
                if sddb.stduStmnU < e.stduStmn4 or not e.stduStmn4:
                    flg = False
            if not flg:
                continue
            #接道幅員1
            #stduFkin1 = db.FloatProperty(verbose_name=u"接道幅員1")
            #接道幅員
            #stduFkinL = db.FloatProperty(verbose_name=u"接道幅員下限")
            if not sddb.stduFkinL == None:
                if sddb.stduFkinL > e.stduFkin1 or not e.stduFkin1:
                    flg = False
            #接道幅員2
            #stduFkin2 = db.FloatProperty(verbose_name=u"接道幅員2")
            if not sddb.stduFkinL == None:
                if sddb.stduFkinL > e.stduFkin2 or not e.stduFkin2:
                    flg = False
            #接道幅員3
            #stduFkin3 = db.FloatProperty(verbose_name=u"接道幅員3")
            if not sddb.stduFkinL == None:
                if sddb.stduFkinL > e.stduFkin3 or not e.stduFkin3:
                    flg = False
            #接道幅員4
            #stduFkin4 = db.FloatProperty(verbose_name=u"接道幅員4")
            if not sddb.stduFkinL == None:
                if sddb.stduFkinL > e.stduFkin4 or not e.stduFkin4:
                    flg = False
            if not flg:
                continue
            result.append(e.key())
        return result

    def setkey(self,reskey,mem):
        msgkey = messageManager.post(self.corp.name, "", "", True, mem, u"検索結果")
        return bklistutl.extendlistbykeys(self.corp.name,reskey,msgkey)

    @classmethod
    def timestr(cls,time):
        return " DATETIME('" + time.strftime("%Y-%m-%d %H:%M:%S") + "')"
    @classmethod
    def timestradd1day(cls,time):
        time += datetime.timedelta(days=1)
        return " DATETIME('" + time.strftime("%Y-%m-%d %H:%M:%S") + "')"


    def product(self,*args, **kwds):
        pools = map(tuple, args) * kwds.get('repeat', 1)
        result = [[]]
        for pool in pools:
            result = [x+[y] for x in result for y in pool]
        for prod in result:
            yield tuple(prod)

    # この関数で、答え返す。
    def get_seq(self,groups):
        ls = [g for g in groups if len(g)]  # からっぽのグループを除去
        return ['-'.join(elem) for elem in self.product(*ls)]

    """
# どういうデータ構造してるのか知らんが。とりあえずこんな感じ？
A = ['A']
B = ['B', 'B1', 'B2']
C = ['C','C1']
D = ['D', 'D1']

groups = [A, B, C, D]
print get_seq(groups)
    """




