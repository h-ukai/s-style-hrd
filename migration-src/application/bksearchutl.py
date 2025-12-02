# -*- coding: utf-8 -*-

from application.models.member import member
from application.models.bksearchdata import bksearchdata
from application.models.bkdata import BKdata
from application.models.CorpOrg import CorpOrg
from application.models.Branch import Branch
from application.models.bksearchaddress import *
from application.models.blob import Blob
import logging
import math
from application.models.message import Message
import datetime

from google.cloud import ndb
from google.cloud import tasks_v2
from application import messageManager
from application.bklistutl import bklistutl
import redis  # Redis for Memorystore replacement
import time
from application import timemanager
from application import CriticalSection

# REVIEW-L1: os がインポートされていません
# 修正前: redis_client = redis.Redis(host=os.environ.get(...))
# 修正後: os をインポート

import os

# Redis client for Memorystore
redis_client = redis.Redis(host=os.environ.get('REDIS_HOST', 'localhost'),
                           port=int(os.environ.get('REDIS_PORT', 6379)))

class memcachecount():
    """Replacement for GAE Memcache using Redis"""
    def __init__(self, key):
        self.key = 'bksearchutl:' + str(key)
        self.cp = CriticalSection.CriticalSection(self.key)

    def add(self):
        if self.cp.lock:
            try:
                res = redis_client.get(self.key)
                if res:
                    res = int(res) + 1
                    redis_client.setex(self.key, 60*90, str(res))
                else:
                    res = 1
                    redis_client.setex(self.key, 60*90, str(res))
            except Exception:
                res = 1
            self.cp.unlock()
            return res

    def sub(self):
        if self.cp.lock:
            try:
                res = redis_client.get(self.key)
                if res:
                    res = int(res) - 1
                    redis_client.setex(self.key, 60*90, str(res))
                else:
                    res = 0
            except Exception:
                res = 0
            self.cp.unlock()
            return res

class allsearchWorker_error(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class allsearchWorker:
    """Flask route handler for search worker"""
    def get(self):
        return self.post()

    def post(self):
        logging.debug('filterWorker')
        # REVIEW-L1: Flask request オブジェクトが使用されていません
        # 修正前: request.get(...)
        # 修正後: request.values.get(...) または request.args.get(...) / request.form.get(...)
        from flask import request
        sddbkey = request.values.get('sddbkey')
        msgkey = request.values.get('msgkey', None)
        hnknngpL = request.values.get('hnknngpL', None)
        if msgkey:
            pass
        else:
            logging.error('allsearchWorker key error(missingmsgkey) ')

class filterWorker_error(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class filterWorker:
    """Flask route handler for property filter worker"""
    def get(self):
        return self.post()

    def post(self):
        from flask import request
        sddbkey = request.values.get('sddbkey')
        if not sddbkey:
            logging.warning('filterWorker: missing sddbkey parameter')
            return 'OK', 200
        sddb = bksearchdata.get_by_id(sddbkey)
        msgkey = request.values.get('msgkey', None)
        hnknngpL = request.values.get('hnknngpL', None)
        flg = request.values.get('flg', None)
        if flg == 'True':
            flg = True

        logging.debug('filterWorker ::' + str(msgkey))
        if msgkey:
            msgkey_obj = Message.get_by_id(msgkey)
            msgkey = msgkey_obj.key if msgkey_obj else None
            corp_name = sddb.member.CorpOrg_key_name
            now = timemanager.utc2jst_date(datetime.datetime.now())

            retry_count = request.headers.get('X-CloudTasks-TaskRetryCount')
            if retry_count and int(retry_count) > 5:
                logging.error('filterWorker retry error(over 5 times) msgID:' + str(msgkey.id()))
                sub = u"検索失敗… 　検索を処理しきれませんでした" + u" (" + now.strftime("%Y/%m/%d %H:%M:%S") + u")"
                body = sddb.name
                messageManager.post(corp=corp_name, sub=sub, body=body, done=False,
                                  memfrom=None, kindname=None, combkind=u"所有",
                                  msgkey=msgkey.id() if msgkey else None)
                return

            logging.info('do_searchdb start')
            flist = bksearchutl.do_searchdb(sddb, hnknngpL)
            logging.info('do_searchdb end')
            mc = memcachecount(str(msgkey))
            res = mc.sub()
            cp = CriticalSection.CriticalSection('cplockinfilterWorker'+str(msgkey))
            if cp.lock():
                rc = bklistutl.extendlistbykeys(corp_name, flist, msgkey, sddb.member,
                                               senddate=None, sended=None, memo=None, flg=flg)
                if res <= 0:
                    sub = u"検索結果 " + str(rc) + u" (" + now.strftime("%Y/%m/%d %H:%M:%S") + u")"
                    body = sddb.name
                    messageManager.post(corp=corp_name, sub=sub, body=body, done=False,
                                      memfrom=None, kindname=None, combkind=u"所有",
                                      msgkey=msgkey.id() if msgkey else None)
                else:
                    sub = u"検索中 / " + str(res) + u" (" + now.strftime("%Y/%m/%d %H:%M:%S") + u")"
                    body = sddb.name
                    messageManager.post(corp=corp_name, sub=sub, body=body, done=False,
                                      memfrom=None, kindname=None, combkind=u"所有",
                                      msgkey=msgkey.id() if msgkey else None)
                cp.unlock()
                logging.info('extendlistbykeys::end')
        else:
            logging.error('filterWorker key error(missingmsgkey) ')

class filterWorker2:
    """Flask route handler for secondary filter worker"""
    def post(self):
        from flask import request
        sddbkey = request.values.get('sddbkey')
        if not sddbkey:
            logging.warning('filterWorker2: missing sddbkey parameter')
            return 'OK', 200
        sddb = bksearchdata.get_by_id(sddbkey)
        msgkey = request.values.get('msgkey', None)
        hnknngpL = request.values.get('hnknngpL', None)
        logging.debug('do_searchdb start')
        corp_name = sddb.member.CorpOrg_key_name

        retry_count = request.headers.get('X-CloudTasks-TaskRetryCount')
        if retry_count and int(retry_count) > 5:
            logging.error('filterWorker retry error(over 5 times) msgID:' + str(msgkey))
            sub = u"検索失敗… 　検索を処理しきれませんでした"
            body = sddb.name
            messageManager.post(corp=corp_name, sub=sub, body=body, done=False,
                              memfrom=None, kindname=None, combkind=u"所有",
                              msgkey=msgkey)
            return

        if msgkey:
            msgkey_obj = Message.get_by_id(msgkey)
            msgkey = msgkey_obj.key if msgkey_obj else None
            bksearchutl.do_searchdb3(sddb, msgkey, hnknngpL)
            return
        else:
            logging.error('filterWorker key error(missingmsgkey) ')

class autoautosearchlog(ndb.Model):
    """Log model for automatic searches"""
    corp = ndb.StringProperty(verbose_name=u"会社ID")
    branch = ndb.StringProperty(verbose_name=u"支店ID")
    sitename = ndb.StringProperty(verbose_name=u"サイト名")
    date = ndb.DateTimeProperty(auto_now_add=True, verbose_name=u"タイムスタンプ")

    def getlast(self, corp, branch=None, sitename=None):
        query = autoautosearchlog.query()
        query = query.filter(autoautosearchlog.corp == corp)
        if branch:
            query = query.filter(autoautosearchlog.branch == branch)
        if sitename:
            query = query.filter(autoautosearchlog.sitename == sitename)
        query = query.order(-autoautosearchlog.date)
        l = query.fetch(1)
        if l:
            return l[0].date
        return None

    def newadd(self, corp, branch=None, sitename=None):
        self.corp = corp
        self.branch = branch
        self.sitename = sitename
        self.put()

class bksearchutl(object):
    """Utility class for property search operations"""

    @classmethod
    def memberProcessing(cls, corp):
        pass

    @classmethod
    def do_autosearch(cls, corp, branch=None, sitename=None, body=None):
        kindname = u"マッチング"
        query = member.query(member.CorpOrg_key_name == corp)
        if branch:
            query = query.filter(member.Branch_Key_name == branch)
        if sitename:
            query = query.filter(member.sitename == sitename)
        query = query.filter(member.seiyaku == u"未成約")
        query = query.filter(member.service == u"マッチング")
        memberlist = query.fetch(100000000)

        log = autoautosearchlog()
        lastdate = log.getlast(corp, branch, sitename)
        log.corp = corp
        log.branch = branch
        log.sitename = sitename
        log.put()

        sub = u"自動検索  : " + timemanager.utc2jst_date(datetime.datetime.now()).strftime("%Y/%m/%d %H:%M:%S")

        for i in range(0, len(memberlist), 500):
            cls.do_bksearchFromMamberlist(corp, memberlist[i:i+500], kindname, sub, body, True, None, lastdate)
        return

    @classmethod
    def do_bksearchFromMamberlist(cls, corp, memberlist, kindname, sub=None, body=None, done=None, mailto=None, hnknngpL=None):
        for memdb in memberlist:
            bklist = cls.do_allsearch(memdb, hnknngpL)
            cls.addlist(corp, memdb, kindname, bklist, sub, body, done, mailto)

    @classmethod
    def addlist(cls, corp, mem, kindname, bklist=None, sub=None, body=None, done=None, mailto=None):
        if not sub:
            sub = u"検索結果 "
        if bklist:
            sub += str(len(bklist))
        if not body:
            body = u"検索結果"

        msgkey = messageManager.post(corp=corp, sub=sub, body=body, done=done,
                                    memfrom=mem.memberID, kindname=kindname,
                                    combkind=u"所有", msgkey=None)
        if bklist:
            bklistutl.extendlistbykeys(corp, bklist, msgkey, mem)
        return msgkey.id()

    @classmethod
    def do_allsearch(cls, memdb, msgkey, hnknngpL=None, flg=None):
        templist = []
        for sddb in memdb.bksearchdata_set:
            templist.append(cls.do_searchdb2(sddb, msgkey, hnknngpL, flg))
        return templist

    @classmethod
    def do_searchdb2(cls, sddb, msgkey, hnknngpL=None, flg=None):
        if not msgkey:
            msgkey = ""
        if not hnknngpL:
            hnknngpL = ""
        if flg:
            flg = 'True'
        mc = memcachecount(str(msgkey))
        mc.add()

        # Create Cloud Task instead of Task Queue
        try:
            project = os.environ.get('GCP_PROJECT')
            queue = 'mintask'
            location = 'us-central1'

            client = tasks_v2.CloudTasksClient()
            parent = client.queue_path(project, location, queue)

            task = {
                'http_request': {
                    'http_method': tasks_v2.HttpMethod.POST,
                    'url': f'{os.environ.get("BASE_URL")}/tasks/filterWorker',
                    'headers': {'Content-Type': 'application/x-www-form-urlencoded'},
                    'body': f'sddbkey={sddb.key.urlsafe().decode()}&msgkey={msgkey}&hnknngpL={hnknngpL}&flg={flg}'.encode()
                }
            }
            client.create_task(request={'parent': parent, 'task': task})
        except Exception as e:
            logging.error(f"Error creating task: {e}")

        return sddb.name

    @classmethod
    def do_searchdb(cls, sddb, hnknngpL=None):
        """Execute property search based on search criteria"""
        cls.corp_name = sddb.member.CorpOrg_key_name
        cls.branch_name = sddb.member.Branch_Key_name

        kwargs = sddb._properties
        if hnknngpL:
            kwargs["hnknngpL"] = hnknngpL
            kwargs["hnknngpU"] = None
            kwargs["kknnngpL"] = None
            kwargs["kknnngpU"] = None
            kwargs["turknngpL"] = None
            kwargs["turknngpU"] = None
            kwargs["ksnnngpL"] = None
            kwargs["ksnnngpU"] = None

        list = cls.do_search(cls.corp_name, cls.branch_name, kwargs)
        reskey = []
        chanksize = 50
        listcount = len(list)

        for i in range(0, listcount, chanksize):
            db1 = ndb.get_multi(list[i:i+chanksize])
            db2 = cls.do_filter(db1, sddb)
            reskey.extend(db2)

        return reskey

    @classmethod
    def do_search(cls, corp, branch, kwargs):
        """Build search query from criteria"""
        bkID = kwargs.get("bkID")
        if bkID:
            key_name = corp + "/" + branch + "/" + kwargs["bkID"]
            bkd = BKdata.get_by_id(key_name)
            return [bkd.key] if bkd else []

        # Build search string from properties
        searchkeys = "corp:" + corp
        if kwargs.get("bbchntikbn"):
            searchkeys += "/bbchntikbn:" + str(kwargs.get("bbchntikbn"))
        if kwargs.get("dtsyuri"):
            searchkeys += "/dtsyuri:" + str(kwargs.get("dtsyuri"))

        # Search using Datastore
        query = BKdata.query()
        query = query.filter(BKdata.searchkeys.contains(searchkeys))

        list = [bk.key for bk in query.fetch(1000)]
        return list

    @classmethod
    def timestr(cls, time):
        return " DATETIME('" + time.strftime("%Y-%m-%d %H:%M:%S") + "')"

    @classmethod
    def timestradd1day(cls, time):
        time += datetime.timedelta(days=1)
        return " DATETIME('" + time.strftime("%Y-%m-%d %H:%M:%S") + "')"
