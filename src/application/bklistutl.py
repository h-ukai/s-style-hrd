# -*- coding: utf-8 -*-

from google.appengine.ext import db
from models.bklist import BKlist
from models.bkdata import BKdata
from models.message import Message
from models.member import member
from datetime import datetime
import re
from application import timemanager
from messageManager import messageManager
import logging

class bklistutl():
    @classmethod
    #refbkはbkdataエンティティもしくはkey
    def addlistbyref(cls,corp,refbk,refmesID,refmem=None, key=None,senddate=None,sended=None,memo=None):
        if not refbk:
            return
        if not isinstance(refbk, BKdata):
            refbk = BKdata.get(refbk)
        if key:
            bklist = BKlist.get(key)
        else:
            bklist = BKlist()
        bklist.refbk = refbk
        if refmesID:
            mes = messageManager.getmesbyID(corp,refmesID)
            bklist.refmes = mes
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
                refmem = mes.refmemlist.filter("combkind = ", "所有").fetch(1)[0].refmem
        else :
            raise bklistutlError("BadKeyError: Invalid string key　" + refmesID)
        bklist.refmem =refmem

        #重複チェック
        mylst = cls.getlistbykey(corp,mes.key()).fetch(1000)
        for e in mylst:
            if refbk.bkID == e.refbk.bkID:
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
        bklistA = cls.getlistbykey(corp,refmes)
        bklistarray = []
        bklistC=0
        for key in keys:
            bklistC=0
            for keyA in bklistA:
                #logging.info('key=' +str(key) + '  keyA=' + str(keyA.refbk.key()))
                bklistC+=1
                if key == keyA.refbk.key():
                    #logging.info('bklistutl::key Hit!!')
                    break
            else:
                #logging.info('bklistutl::not Hit')
                bklist = BKlist()
                bklist.refbk = key
                bklist.refmes = refmes
                mes = db.get(refmes)
                bklist.kindname = mes.kindname
                jlist = [u"資料請求",u"ネット資料請求",u"送付依頼"]
                if flg:
                    jlist = [u"マッチング",u"自動検索",u"資料請求",u"ネット資料請求",u"送付依頼"]
                if mes.kindname in  jlist:
                    bklist.issend = True
                    refbk = BKdata.get(key)
                    if refbk.sksijky in [u"請求チェック",u"一覧のみ"]:
                        refbk.sksijky = u"資料請求"
                        refbk.put()
                else:
                    bklist.issend = False
                if refmem:
                    bklist.refmem = refmem
                else:
                    bklist.refmem = db.get(refmes).refmemlist.filter("combkind = ", "所有").fetch(1)[0].refmem

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
            db.put(bklistarray)
            return len(bklistarray) + bklistC
        return bklistC

    @classmethod
    #ｂｋid物件番号 refmesIDメッセージID
    def addlistbyID(cls,corp,branch,bkid,refmesID,refmem=None,key=None,senddate=None,sended=None,memo=None):
        key_name = corp + "/" + branch + "/" + bkid
        refbk = BKdata.get_by_key_name(key_name)
        return cls.addlistbyref(corp,refbk,refmesID,refmem,key,senddate,sended,memo)

    @classmethod
    def remlistbykey(cls,keys):
        """
        for k in key.split(","):
            bklist = BKlist.get(k)
            bklist.delete()
        """
        db.delete(keys)

    @classmethod
    def remlistbyID(cls,corp,branch,bkid,refmes):
        key_name = corp + "/" + branch + "/" + bkid
        bkdat = BKdata.get_by_key_name(key_name)
        mes = messageManager.getmesbyID(corp,refmes)
        """
        refbklist = cls.getlistbyID(corp,refmes)
        for li in refbklist:
            if li.refbk.key() == bkdat.key():
                li.delete()
        """
        bkl = BKlist.all(keys_only=True).filter("refbk = ", bkdat.key()).filter("refmes = ", mes.key()).fetch(999999)
        if bkl:
            db.delete(bkl)

    @classmethod
    def remalllistbyID(cls,corp,branch,refmesID):
        """
        refbklist = cls.getlistbyID(corp,refmes)
        for li in refbklist:
            li.delete()
        """
        q = cls.getreflistkeysbymesID(corp,refmesID)
        q = q.fetch(999999)
        if q:
            db.delete(q)


    @classmethod
    def remalllistbykey(cls,corp,branch,refmeskey):
        """
        refbklist = cls.getlistbykey(corp,refmeskey)
        for li in refbklist:
            li.delete()
        """
        q = cls.getreflistkeysbykey(corp,refmeskey)
        q = q.fetch(999999)
        if q:
            db.delete(q)

    """
         時間はUTCのままなので注意！　物件の時間管理もしないといけない
    """
    @classmethod
    def getlistbykey(cls,corp,key):
        mes = messageManager.getmesbykey(corp,key)
        return mes.refbklist

    @classmethod
    def getreflistkeysbykey(cls,corp,key):
        mes = messageManager.getmesbykey(corp,key)
        return  BKlist.all(keys_only=True).filter("refmes = ", mes.key())

    """
         時間はUTCのままなので注意！　物件の時間管理もしないといけない
    """
    @classmethod
    def getlistbyID(cls,corp,ID):
        mes = messageManager.getmesbyID(corp,ID)
        if mes:
            logging.info('getlistby ID:' +str(ID) + 'subject:' + mes.subject)
            return mes.refbklist

    @classmethod
    def getreflistkeysbymesID(cls,corp,ID):
        mes = messageManager.getmesbyID(corp,ID)
        return BKlist.all(keys_only=True).filter("refmes = ", mes.key())
        #FilesStore.all(keys_only=True).filter("days_ref =", entity.key())

    @classmethod
    def getreflistbymesID(cls,corp,ID):
        mes = messageManager.getmesbyID(corp,ID)
        return BKlist.all().filter("refmes = ", mes.key())
        #FilesStore.all(keys_only=True).filter("days_ref =", entity.key())

    @classmethod
    def getreflistbyreflistkeys(cls,reflist):
        return BKlist.get(reflist)
        #FilesStore.all(keys_only=True).filter("days_ref =", entity.key())

    @classmethod
    def getmeslistbybkID(cls,corp,branch,bkID):
        key = corp + u"/" + branch + u"/" + bkID
        bkd = BKdata.get_by_key_name(key)
        bkl = BKlist.all()
        bkl.filter("refbk = ", bkd)
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
