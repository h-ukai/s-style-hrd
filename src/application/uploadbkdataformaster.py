# -*- coding: utf-8 -*-

# https://d.hatena.ne.jp/Kmizukix/20090914/1252901315
# https://d.hatena.ne.jp/gonsuzuki/20090401/1238562547

# テスト用URL
# https://localhost:8080/csvupload/bkdata.html?source=reins

#from google.appengine.ext import webapp
import webapp2
from google.appengine.ext.webapp import template
from google.appengine.ext import db
from models import bkdata
from models import CorpOrg
from models import Branch
import os
import csv
import sys
import datetime
import logging
from StringIO import StringIO
import timemanager

class BKdatauploadformaster(webapp2.RequestHandler):

    l=0
    e=0
    massage = []
    date = ''
    def __init__(self,request, response):
        self.initialize(request, response)
        self.tmpl_val = {}
        self.tmpl_val['error_msg'] = ''
        self.auth = False
        self.corp_name= u"s-style"
        self.branch_name = u"hon"
    
    def get(self,**kwargs):
        self.source = self.request.get("source")
        self.tmpl_val ['source'] = self.source
        self.tmpl_val ['result'] = self.massage 
        
        path = os.path.dirname(__file__) + '/../templates/uploadbkdata.html'
        self.response.out.write(template.render(path, self.tmpl_val))

    """
   
    def ntos(n):
        return unicode(n).translate(fulltable) if n != 0 else ''
    """
    
# アップロードしたCSVファイル内容をデータストアへ保存
    def post(self,**kwargs):
        self.date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        rawfile = self.request.get('file')
        self.source = self.request.get("source")
        csvfile = csv.reader(StringIO(rawfile))
        enc = 'cp932'
        for cont in csvfile  :
            self.l +=1
            self.e = 0
            if len(cont) > 0 :
                dtsyurilist = {u'01':u'売買',u'02':u'賃貸'}
                bkknShbtlist = {u'01':u'土地',u'02':u'戸建住宅等',u'03':u'マンション等',u'04':u'住宅以外の建物全部',u'05':u'住宅以外の建物一部'}
                bkknShmklist = {u'01':u'売地',u'02':u'借地権',u'03':u'底地権'}
                gnkyulist = {u'':None,u'1':u'更地',u'2':u'上物有'}
                mnskKisokHusklist ={u'':None,u'1':u'公簿',u'2':u'実測'}
                sitkYutlist ={u'':None,u'01':u'住宅用地',u'02':u'マンション用地',u'03':u'ビル用地',u'04':u'店舗用地',u'05':u'工業用地',u'06':u'配送センター用地',u'07':u'営業所用地',u'08':u'保養所用地',u'09':u'その他用地',u'10':u'事務所用地',u'11':u'別荘用地',u'12':u'倉庫用地',u'13':u'資材置場用地',u'14':u'家庭菜園用地',u'15':u'アパート用地',u'16':u'社宅社員寮用地',u'17':u'病院診療所用地',u'18':u'畑・農地用地',u'19':u'事業用地',u'20':u'駐車場用地'}
                sduFtnUmlist ={u'':None,u'1':u'有',u'2':u'無'}
                """
                if cont[2] == '01':
                    bkknShmklist = {u'01':u'売地',u'02':u'借地権',u'03':u'底地権'}
                    gnkyulist = {u'1':u'更地',u'2':u'上物有'}
                    mnskKisokHusklist ={u'1':u'公簿',u'2':u'実測'}
                    sitkYutlist ={u'01':u'住宅用地',u'02':u'マンション用地',u'03':u'ビル用地',u'04':u'店舗用地',u'05':u'工業用地',u'06':u'配送センター用地',u'07':u'営業所用地',u'08':u'保養所用地',u'09':u'その他用地',u'10':u'事務所用地',u'11':u'別荘用地',u'12':u'倉庫用地',u'13':u'資材置場用地',u'14':u'家庭菜園用地',u'15':u'アパート用地',u'16':u'社宅社員寮用地',u'17':u'病院診療所用地',u'18':u'畑・農地用地',u'19':u'事業用地',u'20':u'駐車場用地'}
                    chushjyuZihlist ={u'1':u'有',u'2':u'無'}
                """
                if cont[2] == '02':
                    bkknShmklist = {u'01':u'新築戸建',u'02':u'中古戸建',u'03':u'新築テラス',u'04':u'中古テラス'}
                    gnkyulist = {u'':None,u'1':u'居住中',u'2':u'空家',u'3':u'賃貸中',u'4':u'未完成'}
                    mnskKisokHusklist ={u'':None,u'1':u'公簿',u'2':u'実測'}
                    sitkYutlist ={u'':None,u'55':u'リゾート向'}
                    chushjyuZihlist ={u'':None,u'1':u'有',u'2':u'無',u'3':u'近隣確保'}
                elif cont[2] == '03':
                    bkknShmklist = {u'01':u'新築マンション',u'02':u'中古マンション',u'07':u'新築タウン',u'08':u'中古タウン',u'09':u'新築リゾート',u'10':u'中古リゾート',u'99':u'その他'}
                    gnkyulist = {u'':None,u'1':u'居住中',u'2':u'空家',u'3':u'賃貸中',u'4':u'未完成'}
                    mnskKisokHusklist ={u'':None,u'1':u'壁芯',u'2':u'内法'}
                    sitkYutlist ={u'':None,u'55':u'リゾート向'}
                    chushjyuZihlist ={u'':None,u'1':u'空有',u'2':u'空無',u'3':u'近隣確保',u'4':u'無'}
                elif cont[2] == '04':
                    bkknShmklist = {u'01':u'店舗',u'02':u'店舗付住宅',u'03':u'住宅付店舗',u'04':u'事務所' ,u'05':u'店舗事務所',u'06':u'ビル' ,u'07':u'工場',u'08':u'マンション' ,u'09':u'倉庫' ,u'10':u'アパート' ,u'11':u'寮',u'12':u'旅館' ,u'13':u'ホテル',u'14':u'別荘' ,u'15':u'リゾート',u'16':u'文化住宅',u'99':u'その他'}
                    gnkyulist = {u'':None,u'1':u'居住中',u'2':u'空家',u'3':u'賃貸中',u'4':u'未完成'}
                    mnskKisokHusklist ={u'':None,u'1':u'公簿',u'2':u'実測'}
                    sitkYutlist ={u'':None,u'55':u'リゾート向'}
                    chushjyuZihlist ={u'':None,u'1':u'有',u'2':u'無'}
                elif cont[2] == '05':
                    bkknShmklist = {u'01':u'店舗',u'02':u'事務所',u'03':u'店舗事務所',u'99':u'その他'}
                    gnkyulist = {u'':None,u'1':u'居住中',u'2':u'空家',u'3':u'賃貸中',u'4':u'未完成'}
                    mnskKisokHusklist ={u'':None,u'1':u'壁芯',u'2':u'内法'}
                    sitkYutlist ={u'':None,u'55':u'リゾート向'}
                    chushjyuZihlist ={u'':None,u'1':u'空有',u'2':u'空無',u'3':u'近隣確保',u'4':u'無'}
                hkwtsNyukyJklist ={u'':None,u'1':u'即時',u'2':u'相談',u'3':u'期日指定',u'4':u'予定'}
                hkwtsNyukyShnlist ={u'':None,u'1':u'上旬',u'2':u'中旬',u'3':u'下旬'}
                trhktiyulist ={u'':None,u'1':u'売主',u'2':u'代理',u'3':u'専属',u'4':u'専任',u'5':u'一般'}
                hushuKitilist ={u'':None,u'1':u'分かれ',u'2':u'当方不払',u'4':u'当方片手数',u'5':u'代理折半',u'9':u'相談'}
                stbkKbnlist ={u'':None,u'0':u'無',u'1':u'有',u'2':u'済'}
                kkdhuTdkdlist ={u'':None,u'1':u'要',u'2':u'中',u'3':u'不要'}
                tukbCmklist ={u'':None,u'1':u'宅地',u'2':u'田',u'3':u'畑',u'4':u'山林',u'5':u'雑種',u'9':u'他'}
                tskikklist ={u'':None,u'1':u'市街',u'2':u'調整',u'3':u'非線引き',u'4':u'域外',u'5':u'準都市'}
                yutCik1list ={u'':None,u'01':u'一低',u'02':u'二中',u'03':u'二住',u'04':u'近商',u'05':u'商業',u'06':u'準工',u'07':u'工業',u'08':u'工専',u'10':u'二低',u'11':u'一中',u'12':u'一住',u'13':u'準住',u'99':u'無指定'}
                cikCklist ={u'':None,u'01':u'防火',u'02':u'準防火',u'03':u'高度',u'04':u'高度利用',u'05':u'風致',u'06':u'文教',u'09':u'その他'}
                tcKenrlist ={u'':None,u'1':u'所有権',u'2':u'旧法地上',u'3':u'旧法賃借',u'4':u'普通地上',u'5':u'定期地上',u'6':u'普通賃借',u'7':u'定期賃借',u'8':u'他'}
                ftiKenrlist ={u'':None,u'01':u'抵当権',u'02':u'温泉利用権'}
                csilist={u'':None,u'1':u'平坦',u'2':u'高台',u'3':u'低地',u'4':u'ひな段',u'5':u'傾斜地',u'9':u'その他'}
                knrKitilist={u'':None,u'1':u'自主管理',u'2':u'管理会社に一部委託',u'3':u'管理会社に全部委託'}
                knrnnJyukyulist={u'':None,u'1':u'常駐',u'2':u'日勤',u'3':u'巡回'}
                stduJyukyulist={u'':None,u'1':u'一方',u'2':u'角地',u'3':u'三方',u'4':u'四方',u'5':u'二方'}
                stduShbt1list={u'':None,u'1':u'公道',u'2':u'私道'}
                stduHuku1list={u'':None,u'1':u'北',u'2':u'北東',u'3':u'東',u'4':u'南東',u'5':u'南',u'6':u'南西',u'7':u'西',u'8':u'北西'}
                mdrTyp1list={u'':None,u'01':u'ワンルーム',u'02':u'K',u'03':u'DK',u'04':u'LK',u'05':u'LDK',u'06':u'SK',u'07':u'SDK',u'08':u'SLK',u'09':u'SLDK'}
                stTyp11list={u'':None,u'1':u'和',u'2':u'洋',u'3':u'DK',u'4':u'LDK',u'5':u'L',u'6':u'D',u'7':u'K',u'8':u'S',u'9':u'その他'}
                chushjyuSkknGklist={u'':None,u'1':u'円',u'2':u'ヶ月'}
                ttmnKuzulist={u'':None,u'01':u'木造',u'02':u'ブロック',u'03':u'鉄骨造',u'04':u'RC',u'05':u'SRC',u'06':u'PC',u'07':u'HPC',u'08':u'軽量鉄骨',u'09':u'その他'}
                ttmnKuhulist={u'':None,u'1':u'在来',u'2':u'2×4'}
                shuhnAccs1list={u'':None,u'1':u'徒歩',u'2':u'車'}
                try:
                    br = Branch.Branch.get_or_insert(u"s-style/hon")
                    bkID = self.nunicode(cont[0], enc)
                    key_name = self.corp_name + "/" + self.branch_name + "/" + bkID
                    #chzsntidkd = db.GeoPt(self.nfloat(self.nunicode(cont[10], enc)),self.nfloat(self.nunicode(cont[11], enc)))
                    #idkd = db.GeoPt(self.nfloat(self.nunicode(cont[10], enc)),self.nfloat(self.nunicode(cont[11], enc)))
                    """
                    data = bkdata.BKdata.get_or_insert(key_name,
                            dtsyuri = u"サンプル",
                            sksijky = u"作成済み",
                            bkID = self.nunicode(cont[0], enc),
                            #物件番号
                            #入力会社ID
                            nyrykkisyID = self.corp.name,
                            #入力支店ID
                            nyrykstnID = self.branch.name,
                            #入力担当
                            nyryktnt = u'import',

                            #更新会社ID
                            ksnkisID = self.corp.name,
                            #更新支店ID
                            ksnstnID = self.branch.name,
                            #更新担当
                            ksntnt = u'import',
                            #重複チェック
                            duplicationcheck = True,
                            #データ元
                            dataSource = u'マンションマスター',

                            bknbng = u'マンションマスター' + u'/' + self.nunicode(cont[1], enc),
                            

                            #地図センター緯度経度
                            chzsntidkd = db.GeoPt(self.nfloat(self.nunicode(cont[10], enc)),self.nfloat(self.nunicode(cont[11], enc))) ,
                            #chzsntidkd = chzsntidkd ,
                            #緯度経度
                            idkd = db.GeoPt(self.nfloat(self.nunicode(cont[10], enc)),self.nfloat(self.nunicode(cont[11], enc))),
                            #idkd = idkd ,
                            #地図レンジ
                            chzrnj = 18,
                            
                            #売買賃貸区分
                            bbchntikbn = u"売買",
                            #list = {u'01':u'売買',:u'02':u'賃貸'}
                            
                            #物件種別
                            bkknShbt = u'マンション等',
                            #list = {u'01':u'土地',u'02':u'戸建',u'03':u'マンション',u'04':u'外全',u'05':u'外一'}
                            
                            #物件種目
                            bkknShmk = u'中古マンション',
                            #list = {u'01':u'売地',u'02':u'借地権',u'03'u:'底地権'}
                            
                            #会員名
                            kiinni = self.corp.name,
                            
                            #登録年月日
                            turknngp = self.getdatetime('2011/06/07'),
                            
                            #都道府県名
                            tdufknmi = u'愛知県',
                            
                            #所在地名1
                            shzicmi1 = self.nunicode(cont[2], enc),
                            
                            #所在地名2
                            shzicmi2 = self.nunicode(cont[3], enc),
                            #所在地名3
                            shzicmi3 = self.nunicode(cont[4], enc),
                            #建物名
                            ttmnmi = self.nunicode(cont[0], enc),
                            
                            #建物構造
                            ttmnKuzu = self.nunicode(cont[5], enc),
                            #list={u'01':u'木造',u'02':u'ブロック',u'03':u'鉄骨造',u'04':u'RC',u'05':u'SRC',u'06':u'PC',u'07':u'HPC',u'08':u'軽量鉄骨',u'09':u'その他'}
                            
                            #地上階層
                            cjyuKisou = self.nfloat(self.nunicode(cont[6], enc)),
                            
                            #地下階層
                            ckaKisou = self.nfloat(self.nunicode(cont[7], enc)),
                            
                            #築年月（西暦）
                            cknngtSirk = self.getdatetime(self.nunicode(cont[8], enc))
                    )
                    """
                    data = bkdata.BKdata.get_or_insert(key_name,bkID = self.nunicode(cont[0], enc))
                    data.dtsyuri = u"サンプル"
                    data.sksijky = u"作成済み"
#                    data.bkID = self.nunicode(cont[0], enc)
                            #物件番号
                            #入力会社ID
                    data.nyrykkisyID = self.corp_name
                            #入力支店ID
                    data.nyrykstnID = self.branch_name
                            #入力担当
                    data.nyryktnt = u'import'

                            #更新会社ID
                    data.ksnkisID = self.corp_name
                            #更新支店ID
                    data.ksnstnID = self.branch_name
                            #更新担当
                    data.ksntnt = u'import'
                            #重複チェック
                    data.duplicationcheck = True
                            #データ元
                    data.dataSource = u'マンションマスター'

                    data.bknbng = u'マンションマスター' + u'/' + self.nunicode(cont[1], enc)
                            

                            #地図センター緯度経度
                    data.chzsntidkd = db.GeoPt(self.nfloat(self.nunicode(cont[10], enc)),self.nfloat(self.nunicode(cont[11], enc))) 
                            #chzsntidkd = chzsntidkd ,
                            #緯度経度
                    data.idkd = db.GeoPt(self.nfloat(self.nunicode(cont[10], enc)),self.nfloat(self.nunicode(cont[11], enc)))
                            #idkd = idkd ,
                            #地図レンジ
                    data.chzrnj = 18
                            
                            #売買賃貸区分
                    data.bbchntikbn = u"売買"
                            #list = {u'01':u'売買',:u'02':u'賃貸'}
                            
                            #物件種別
                    data.bkknShbt = u'マンション等'
                            #list = {u'01':u'土地',u'02':u'戸建',u'03':u'マンション',u'04':u'外全',u'05':u'外一'}
                            
                            #物件種目
                    data.bkknShmk = u'中古マンション'
                            #list = {u'01':u'売地',u'02':u'借地権',u'03'u:'底地権'}
                            
                            #会員名
                    data.kiinni = self.corp_name
                            
                            #登録年月日
                    data.turknngp = self.getdatetime('2011/06/07')
                            
                            #都道府県名
                    data.tdufknmi = u'愛知県'
                            
                            #所在地名1
                    data.shzicmi1 = self.nunicode(cont[2], enc)
                            
                            #所在地名2
                    data.shzicmi2 = self.nunicode(cont[3], enc)
                            #所在地名3
                    data.shzicmi3 = self.nunicode(cont[4], enc)
                            #建物名
                    data.ttmnmi = self.nunicode(cont[0], enc)
                            
                            #建物構造
                    data.ttmnKuzu = self.nunicode(cont[5], enc)
                            #list={u'01':u'木造',u'02':u'ブロック',u'03':u'鉄骨造',u'04':u'RC',u'05':u'SRC',u'06':u'PC',u'07':u'HPC',u'08':u'軽量鉄骨',u'09':u'その他'}
                            
                            #地上階層
                    data.cjyuKisou = self.nfloat(self.nunicode(cont[6], enc))
                            
                            #地下階層
                    data.ckaKisou = self.nfloat(self.nunicode(cont[7], enc))
                            
                            #築年月（西暦）
                    data.cknngtSirk = self.getdatetime(self.nunicode(cont[8], enc))
                    data.put()
                    self.massage.append("DataPutSuccess:line" + str(self.l) +"・・・・・OK")
                except Exception:
                    self.massage.append("DataPutError:line" + str(self.l) + ":" + str(sys.exc_info()[0]))
                
        self.get(**kwargs)

    def nunicode(self,text,enc):
        try:
            result = None
            if text != None and text != "":
                #text.replace(u'㈱', u'（株）')
#                text2 = ""
#                text2 = text.replace(u'\u3231', u'（株）')
#                if text2 != None and text2 != "":
                result = unicode(text, enc,errors='replace')
        except Exception:
            self.massage.append("error:line" + str(self.l) +"elements" + str(self.e) + ":" + sys.exc_info()[0])
            logging.debug("error:line" + str(self.l) +"elements" + str(self.e) + ":" + sys.exc_info()[0])
        finally:
            self.e += 1     #要注意！！この場所でインクリメントせざるを得なかった　他の演算関数のエラーメッセージではeの値がずれるので注意
            return result

    def getdatetime(self,text):
        result = None
        try:
            #tlist = text.split('-')
            #result = datetime.date(int(tlist[0]), int(tlist[1]), int(tlist[2])
            if text != None and text != "":
                result = timemanager.jst2utc_date(datetime.datetime.strptime(text, "%Y/%m/%d"))
            #tlist = "2001-1-1".sprit('-')
        except Exception:
            self.massage.append("error:line" + str(self.l) +"elements" + str(self.e) + ":" + sys.exc_info()[0] )
        finally:
            return result


    def getdatetime2(self,text):
        result = None
        try:
            if text != None and text != "":
                if text[0] != '0' and text[4] == '0' and text[5] == '0':
                    result = timemanager.jst2utc_date(datetime.datetime.strptime(text, "%Y00"))
                elif text[0] != '0' :
                    result = timemanager.jst2utc_date(datetime.datetime.strptime(text, "%Y%m"))
        except Exception:
            self.massage.append("error:line" + str(self.l) +"elements" + str(self.e) + ":" + sys.exc_info()[0] )
        finally:
            return result

    def nbool(self,text):
        result = None
        try:
            if text != None and text != "":
                result = True
            elif text == u"0":
                result = False
        except Exception:
            self.massage.append("error:line" + str(self.l) +"elements" + str(self.e) + ":" + sys.exc_info()[0] )
        finally:
            return result

    def nfloat(self,text):
        result = None
        try:
            if text != None and text != "":
                result = float(text)
        except Exception:
            self.massage.append("error:line" + str(self.l) +"elements" + str(self.e) + ":value" + text + ":" + sys.exc_info()[0] )
        finally:
            return result
