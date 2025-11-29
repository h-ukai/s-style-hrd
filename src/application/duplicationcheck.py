# -*- coding: utf-8 -*-

from google.appengine.ext import db
from models import bkdata
import datetime
from datetime import date
import os
import timemanager
import logging
#from google.appengine.ext import webapp
import webapp2
from google.appengine.ext.webapp import template


class DuplicationCheck(webapp2.RequestHandler):

    corp = u"s-style"
    branch = u"hon"
    tmpl_val = {}

    def get(self) :

        limit = 20
#        DATE('YYYY-MM-DD')
        source = self.request.get("source")
        list=self.getMyList(999999,date,source)
        self.tmpl_val['count']=len(list)
        list=self.getMyList(limit,date,source)

        if len(list)<1:
            self.response.headers['Content-Type'] = 'text/plain'
            self.response.out.write( 'OK checked all data.' )
            return 
        for c in list:
            self.docheck(c)
            c.duplicationcheck = None
            c.put()
        self.tmpl_val['source']=source
        self.tmpl_val['limit']=limit
        path = os.path.dirname(__file__) + '/../templates/duplicationcheck.html'
        self.response.out.write(template.render(path, self.tmpl_val))


    def getMyList(self,limit,date,source):
#        query = ziplist.Ziplist.gql('LIMIT '+str(limit))
#        DATE('YYYY-MM-DD')
        query = bkdata.BKdata.gql(u"WHERE nyrykkisyID = '" + self.corp + u"' AND nyrykstnID = '" + self.branch + u"' AND duplicationcheck = True LIMIT " + str(limit))
        return query[0:min(query.count(),limit)]

    def docheck(self,bkdata1):
        """
        #ここはコメントアウト→            物件番号が同じなら重複
        "土地" "賃貸土地" "戸建住宅等" "住宅以外の建物全部" "賃貸一戸建" "賃貸外全"　の場合
                    所在地２まで一致で土地面積が一致なら重複        
        "マンション等" "住宅以外の建物一部" "賃貸マンション" "賃貸外一"　の場合
                    所在地２まで一致で所在階と部屋番号が同じなら重複
                   所在地２まで一致で所在階と間取りと専有面積が同じなら重複
        """
        query_str = u"SELECT * FROM BKdata WHERE nyrykkisyID = '" + self.corp + u"' AND nyrykstnID = '" + self.branch + u"' AND duplicationcheck = NULL AND dtsyuri = '物件'"


        """
        2018/09/08 確認する対象物件を二年前までに絞る
        
        """
        """
        if bkdata1.bknbng:
            query_str += u" AND bknbng = '" + bkdata1.bknbng + "'"
            query_str += u" AND kknnngp >  DATETIME( '" + datetime.datetime.strftime(timemanager.jst2utc_date(datetime.datetime.today()+datetime.timedelta(days=-730)), "%Y-%m-%d %H:%M:%S") + u"' )  ORDER BY kknnngp ASC"
            logging.debug('docheck query_str ::' + query_str)        
            bkdata2 = db.GqlQuery(query_str)
            if bkdata2.count():
                self.doset(bkdata1,bkdata2)
        """
        #物件種別
        #bkknShbt = db.StringProperty(verbose_name=u"物件種別", choices=set([u"土地", u"戸建住宅等", u"マンション等", u"住宅以外の建物全部", u"住宅以外の建物一部",u"賃貸一戸建",u"賃貸マンション",u"賃貸土地",u"賃貸外全",u"賃貸外一", u"その他"]))
        if bkdata1.bkknShbt == u"土地" or bkdata1.bkknShbt == u"賃貸土地" or bkdata1.bkknShbt == u"戸建住宅等" or bkdata1.bkknShbt == u"住宅以外の建物全部" or bkdata1.bkknShbt == u"賃貸一戸建" or bkdata1.bkknShbt == u"賃貸外全":
            query_str += u" AND bkknShbt = '" + bkdata1.bkknShbt
            if bkdata1.shzicmi1 and bkdata1.shzicmi2 and bkdata1.tcMnsk2:
                query_str += u"' AND shzicmi1 = '" + bkdata1.shzicmi1 + u"' AND shzicmi2 = '" + bkdata1.shzicmi2 + u"' AND tcMnsk2 = " + str(bkdata1.tcMnsk2)
                query_str += u" AND kknnngp >  DATETIME( '" + datetime.datetime.strftime(timemanager.jst2utc_date(datetime.datetime.today()+datetime.timedelta(days=-730)), "%Y-%m-%d %H:%M:%S") + u"' )  ORDER BY kknnngp ASC"
                logging.debug('docheck query_str ::' + query_str)        
                bkdata2 = db.GqlQuery(query_str)
                if bkdata2.count():
                    self.doset(bkdata1,bkdata2)
        elif bkdata1.bkknShbt == u"マンション等" or bkdata1.bkknShbt == u"住宅以外の建物一部" or bkdata1.bkknShbt == u"賃貸マンション" or bkdata1.bkknShbt == u"賃貸外一":
            query_str += u" AND bkknShbt = '" + bkdata1.bkknShbt
            if bkdata1.shzicmi1 and bkdata1.shzicmi2 and bkdata1.shziki and bkdata1.hyBngu:
                query_str += u"' AND shzicmi1 = '" + bkdata1.shzicmi1 + u"' AND shzicmi2 = '" + bkdata1.shzicmi2 + "' AND shziki = " + str(bkdata1.shziki) + u" AND hyBngu = '" + bkdata1.hyBngu + "'"
                query_str += u" AND kknnngp >  DATETIME( '" + datetime.datetime.strftime(timemanager.jst2utc_date(datetime.datetime.today()+datetime.timedelta(days=-730)), "%Y-%m-%d %H:%M:%S") + u"' )  ORDER BY kknnngp ASC"
                logging.debug('docheck query_str ::' + query_str)        
                bkdata2 = db.GqlQuery(query_str)
                if bkdata2.count():
                    self.doset(bkdata1,bkdata2)
            elif bkdata1.shzicmi1 and bkdata1.shzicmi2 and bkdata1.shziki and bkdata1.mdrTyp1 and bkdata1.mdrHysu1 and bkdata1.snyuMnskSyuBbnMnsk2:
                query_str += u"' AND shzicmi1 = '" 
                query_str + bkdata1.shzicmi1 + u"' AND shzicmi2 = '" 
                query_str += bkdata1.shzicmi2 + u"' AND shziki = " 
                query_str += str(bkdata1.shziki) + u" AND mdrTyp1 = '" 
                query_str += bkdata1.mdrTyp1 + u"' AND mdrHysu1 = " 
                query_str += str(bkdata1.mdrHysu1) + u" AND snyuMnskSyuBbnMnsk2 = "
                query_str += str(bkdata1.snyuMnskSyuBbnMnsk2)
                query_str += u" AND kknnngp >  DATETIME( '" + datetime.datetime.strftime(timemanager.jst2utc_date(datetime.datetime.today()+datetime.timedelta(days=-730)), "%Y-%m-%d %H:%M:%S") + u"' )  ORDER BY kknnngp ASC"
                logging.debug('docheck query_str ::' + query_str)        
                bkdata2 = db.GqlQuery(query_str)
                if bkdata2.count():
                    self.doset(bkdata1,bkdata2)

    def doset(self,bkdata1,bkdata2):
        """
        重複の場合
        先にあった物件が確認１年以内で資料請求済み以降の場合、先にあった物件を生かす　あとの物件を重複
        先にあった物件が確認１年以上または資料請求していない場合、先にあった物件が重複　あとの物件を生かす
        """
        for data in bkdata2:
            if (datetime.datetime.now() - data.kknnngp).days > 365:
                #一年以上 sksijky [u"請求チェック",u"一覧のみ",u"資料請求",u"入手不可",u"請求済み",u"分類チェック",u"不要",u"未作成",u"作成済み"]
                data.kknnngp = datetime.datetime.now()
                data.dtsyuri = u"重複"
                data.jshKnrrn = self.strplus(data.jshKnrrn , u"to:" + bkdata1.bkID)
            else:
                #一年以下
                if data.sksijky == u"資料請求" or data.sksijky == u"依頼中" or data.sksijky == u"入手済み" or data.sksijky == u"分類チェック" or data.sksijky == u"未作成" or data.sksijky == u"作成済み" or data.sksijky == u"ＨＰ掲載":
                    data.kknnngp = datetime.datetime.now()
                    bkdata1.dtsyuri = u"重複"
                    bkdata1.jshKnrrn = self.strplus(bkdata1.jshKnrrn , u"to:" + data.bkID)
                    bkdata1.put()
                else:                    
                    data.kknnngp = datetime.datetime.now()
                    data.dtsyuri = u"重複"
                    data.jshKnrrn = self.strplus(data.jshKnrrn , u"to:" + bkdata1.bkID)
            data.put()
    def strplus(self,a,b):
        if a:
            a += b
        else:
            a = b
        return a

    def timestr(self,time):
        return " DATETIME('" + time.strftime("%Y-%m-%d") + " 00:00:00')"
