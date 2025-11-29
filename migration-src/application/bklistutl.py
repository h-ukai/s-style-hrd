# -*- coding: utf-8 -*-

from google.cloud import ndb
from application.models.bklist import BKlist
from application.models.bkdata import BKdata
from application.models.message import Message
from application.models.member import member
from datetime import datetime
import re
from application import timemanager
from application.messageManager import messageManager
import logging

class bklistutl():
    @classmethod
    #refbkはbkdataエンティティもしくはkey
    def addlistbyref(cls,corp,refbk,refmesID,refmem=None, key=None,senddate=None,sended=None,memo=None):
        if not refbk:
            return
        if not isinstance(refbk, BKdata):
            refbk = ndb.Key(BKdata, refbk).get()
        if key:
            bklist = ndb.Key(BKlist, key).get()
        else:
            bklist = BKlist()
        bklist.refbk = refbk.key
        if refmesID:
            mes = messageManager.getmesbyID(corp,refmesID)
            bklist.refmes = mes.key
            bklist.kindname = mes.kindname
            #if mes.kindname in  [u"マッチング",u"自動検索",u"資料請求",u"ネット資料請求",u"送付依頼"]:
            if mes.kindname in  [u"資料請求",u"ネット資料請求",u"送付依頼"]:
                bklist.issend = True
                if refbk.sksijky in [u"請求チェック",u"一覧のみ"]:
                    refbk.sksijky = u"資料請求"
                    refbk.put()
            else:
                bklist.issend = False
            if not refmem:
                # ndb.query() with filter for reference property
                refmemlist = messageManager.getrefmembykey(corp, mes.key)
                if refmemlist:
                    refmem = refmemlist[0].refmem
        else :
            raise bklistutlError("BadKeyError: Invalid string key　" + refmesID)
        # REVIEW-L2: refmem type check - handle both entity and key cases
        # refmem が None の場合の処理が必要
        if refmem:
            bklist.refmem = refmem.key if isinstance(refmem, member) else refmem
        else:
            bklist.refmem = None

        # REVIEW-L2: Performance - 重複チェックでfetch(1000)は多い可能性
        # 推奨: 必要最低限の件数に変更、またはKeys onlyクエリで高速化
        #重複チェック
        mylst = cls.getlistbykey(corp,mes.key).fetch(1000)
        for e in mylst:
            # REVIEW-L2: N+1 query problem - refbk.get() in loop
            # 推奨: ndb.get_multi() でまとめて取得
            refbk_entity = e.refbk.get()
            if refbk.bkID == refbk_entity.bkID:
                return None

        if senddate:
            r = re.compile(".*:.*:.*").match(senddate, 1)
            if r == None:
                rtime = datetime.strptime(senddate, "%Y/%m/%d")
            else:
                rtime = datetime.strptime(senddate, "%Y/%m/%d %H:%M:%S")
            bklist.senddate = timemanager.jst2utc_date(rtime)
        if sended=="true" or sended=="True" or sended=="on" or sended==True:
            bklist.sended=True
        else:
            bklist.sended=False
            bklist.senddate = None
        if memo:
            bklist.memo=memo
        return str(bklist.put())

    @classmethod
    def extendlistbykeys(cls,corp,keys,refmes,refmem=None,senddate=None,sended=None,memo=None,flg=None):
        """
        refmesはmessageのkeyでなければならない
        """
        logging.info('extendlistbykeys::start')
        bklistA = cls.getlistbykey(corp,refmes).fetch(999999)
        bklistarray = []
        bklistC=0
        for key in keys:
            bklistC=0
            for keyA in bklistA:
                #logging.info('key=' +str(key) + '  keyA=' + str(keyA.refbk.key()))
                bklistC+=1
                if key == keyA.refbk:
                    #logging.info('bklistutl::key Hit!!')
                    break
            else:
                #logging.info('bklistutl::not Hit')
                bklist = BKlist()
                bklist.refbk = key
                bklist.refmes = refmes
                mes = ndb.Key(Message, refmes).get()
                bklist.kindname = mes.kindname
                jlist = [u"資料請求",u"ネット資料請求",u"送付依頼"]
                if flg:
                    jlist = [u"マッチング",u"自動検索",u"資料請求",u"ネット資料請求",u"送付依頼"]
                if mes.kindname in  jlist:
                    bklist.issend = True
                    refbk = ndb.Key(BKdata, key).get()
                    if refbk.sksijky in [u"請求チェック",u"一覧のみ"]:
                        refbk.sksijky = u"資料請求"
                        refbk.put()
                else:
                    bklist.issend = False
                if refmem:
                    bklist.refmem = refmem.key if isinstance(refmem, member) else refmem
                else:
                    refmemlist = messageManager.getrefmembykey(corp, refmes)
                    if refmemlist:
                        bklist.refmem = refmemlist[0].refmem.key

                if senddate:
                    r = re.compile(".*:.*:.*").match(senddate, 1)
                    if r == None:
                        rtime = datetime.strptime(senddate, "%Y/%m/%d")
                    else:
                        rtime = datetime.strptime(senddate, "%Y/%m/%d %H:%M:%S")
                    bklist.senddate = timemanager.jst2utc_date(rtime)
                if sended=="true":
                    bklist.sended=True
                else:
                    bklist.sended=False
                    bklist.senddate = None
                if memo:
                    bklist.memo=memo
                bklistarray.append(bklist)
        if len(bklistarray):
            ndb.put_multi(bklistarray)
            return len(bklistarray) + bklistC
        return bklistC

    @classmethod
    #bkid物件番号 refmesIDメッセージID
    def addlistbyID(cls,corp,branch,bkid,refmesID,refmem=None,key=None,senddate=None,sended=None,memo=None):
        key_name = corp + "/" + branch + "/" + bkid
        refbk = ndb.Key(BKdata, key_name).get()
        return cls.addlistbyref(corp,refbk,refmesID,refmem,key,senddate,sended,memo)

    @classmethod
    def remlistbykey(cls,keys):
        """
        for k in key.split(","):
            bklist = BKlist.get(k)
            bklist.delete()
        """
        ndb.delete_multi(keys)

    @classmethod
    def remlistbyID(cls,corp,branch,bkid,refmes):
        key_name = corp + "/" + branch + "/" + bkid
        bkdat = ndb.Key(BKdata, key_name).get()
        mes = messageManager.getmesbyID(corp,refmes)
        """
        refbklist = cls.getlistbyID(corp,refmes)
        for li in refbklist:
            if li.refbk.key() == bkdat.key():
                li.delete()
        """
        bkl = BKlist.query(
            BKlist.refbk == bkdat.key,
            BKlist.refmes == mes.key
        ).fetch(999999, keys_only=True)
        if bkl:
            ndb.delete_multi(bkl)

    @classmethod
    def remalllistbyID(cls,corp,branch,refmesID):
        """
        refbklist = cls.getlistbyID(corp,refmes)
        for li in refbklist:
            li.delete()
        """
        q = cls.getreflistkeysbymesID(corp,refmesID)
        # REVIEW-L1: fetch(keys_only=True) to get keys for deletion
        q = q.fetch(999999, keys_only=True)
        if q:
            ndb.delete_multi(q)


    @classmethod
    def remalllistbykey(cls,corp,branch,refmeskey):
        """
        refbklist = cls.getlistbykey(corp,refmeskey)
        for li in refbklist:
            li.delete()
        """
        q = cls.getreflistkeysbykey(corp,refmeskey)
        # REVIEW-L1: fetch(keys_only=True) to get keys for deletion
        q = q.fetch(999999, keys_only=True)
        if q:
            ndb.delete_multi(q)

    """
         時間はUTCのままなので注意！　物件の時間管理もしないといけない
    """
    @classmethod
    def getlistbykey(cls,corp,key):
        mes = messageManager.getmesbykey(corp,key)
        return BKlist.query(BKlist.refmes == mes.key)

    @classmethod
    def getreflistkeysbykey(cls,corp,key):
        mes = messageManager.getmesbykey(corp,key)
        # REVIEW-L1: Return query object, not fetched result (for consistency with fetch(999999) calls)
        return BKlist.query(BKlist.refmes == mes.key)

    """
         時間はUTCのままなので注意！　物件の時間管理もしないといけない
    """
    @classmethod
    def getlistbyID(cls,corp,ID):
        mes = messageManager.getmesbyID(corp,ID)
        if mes:
            logging.info('getlistby ID:' +str(ID) + 'subject:' + mes.subject)
            return BKlist.query(BKlist.refmes == mes.key)

    @classmethod
    def getreflistkeysbymesID(cls,corp,ID):
        mes = messageManager.getmesbyID(corp,ID)
        # REVIEW-L1: Return query object for consistency (callers will fetch(999999))
        return BKlist.query(BKlist.refmes == mes.key)
        #FilesStore.query(keys_only=True).filter(days_ref == entity.key())

    @classmethod
    def getreflistbymesID(cls,corp,ID):
        mes = messageManager.getmesbyID(corp,ID)
        return BKlist.query(BKlist.refmes == mes.key).fetch()
        #FilesStore.query(keys_only=True).filter(days_ref == entity.key())

    @classmethod
    def getreflistbyreflistkeys(cls,reflist):
        # REVIEW-L1: Incorrect usage - ndb.get_multi() for multiple keys, not ndb.Key()
        # 修正前: ndb.Key(BKlist, reflist).get() - single key only
        # 修正後: ndb.get_multi(reflist) for list of keys
        return ndb.get_multi(reflist) if isinstance(reflist, list) else ndb.Key(BKlist, reflist).get()
        #FilesStore.query(keys_only=True).filter(days_ref == entity.key())

    @classmethod
    def getmeslistbybkID(cls,corp,branch,bkID):
        key = corp + u"/" + branch + u"/" + bkID
        bkd = ndb.Key(BKdata, key).get()
        bkl = BKlist.query(BKlist.refbk == bkd.key)
        list = []
        for e in bkl:
            list.append(e.refmes)
        return list

    '''
    @classmethod
    def remlistbyref(cls,bk,mes):
        bkdb = BKdata.get(bk)
        for bke in bkdb.refmeslist:
            for me in bke.ref
    '''

class bklistutlError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

