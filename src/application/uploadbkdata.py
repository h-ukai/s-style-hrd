# -*- coding: utf-8 -*-

# https://d.hatena.ne.jp/Kmizukix/20090914/1252901315
# https://d.hatena.ne.jp/gonsuzuki/20090401/1238562547

# テスト用URL
# https://localhost:8080/csvupload/bkdata.html?source=reins

#from google.appengine.ext import webapp
import webapp2
from google.appengine.ext.webapp import template
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

class BKdataupload(webapp2.RequestHandler):

    l=0
    e=0
    message = []
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
        self.tmpl_val ['result'] = self.message 
        
        path = os.path.dirname(__file__) + '/../templates/uploadbkdata.html'
        self.response.out.write(template.render(path, self.tmpl_val))

    """
   
    def ntos(n):
        return unicode(n).translate(fulltable) if n != 0 else ''
    """
    
# アップロードしたCSVファイル内容をデータストアへ保存
    def post(self,**kwargs):
        self.message = []
        self.date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        rawfile = self.request.get('file')
        self.source = self.request.get("source")
        if not self.source:
            self.source = u"レインズ"
        csvfile = csv.reader(StringIO(rawfile))
        enc = 'cp932'
        for cont in csvfile  :
            self.l +=1
            if len(cont) > 0 :
                self.e = 0
                """
                                レインズデータをエクセルで修正した場合のデータ改変に対する修正 2011/08/10
                """
                try:
                    cont[0]=str(int(float(cont[0])))  #"1.00038E+11"の場合
                except: 
                    pass 
                clist = [1,2,3,82,83,84,87,89,132,172] #対象になるフィールドナンバー
                for i in clist:
                    if cont[i]:
                        cont[i] = ("00" + cont[i])[-2:]
                """
                                修正　ここまで
                """
                self.dtsyurilist = {u'01':u'売買',u'02':u'賃貸'}
                self.bkknShbtlist = {u'01':u'土地',u'02':u'戸建住宅等',u'03':u'マンション等',u'04':u'住宅以外の建物全部',u'05':u'住宅以外の建物一部'}
                self.bkknShmklist = {u'01':u'売地',u'02':u'借地権',u'03':u'底地権'}
                self.gnkyulist = {u'':None,u'1':u'更地',u'2':u'上物有'}
                self.mnskKisokHusklist ={u'':None,u'1':u'公簿',u'2':u'実測'}
                self.sitkYutlist ={u'':None,u'01':u'住宅用地',u'02':u'マンション用地',u'03':u'ビル用地',u'04':u'店舗用地',u'05':u'工業用地',u'06':u'配送センター用地',u'07':u'営業所用地',u'08':u'保養所用地',u'09':u'その他用地',u'10':u'事務所用地',u'11':u'別荘用地',u'12':u'倉庫用地',u'13':u'資材置場用地',u'14':u'家庭菜園用地',u'15':u'アパート用地',u'16':u'社宅社員寮用地',u'17':u'病院診療所用地',u'18':u'畑・農地用地',u'19':u'事業用地',u'20':u'駐車場用地'}
                self.sduFtnUmlist ={u'':None,u'1':u'有',u'2':u'無'}
                if cont[2] == '01':
                    self.bkknShmklist = {u'01':u'売地',u'02':u'借地権',u'03':u'底地権'}
                    self.gnkyulist = {u'1':u'更地',u'2':u'上物有'}
                    self.mnskKisokHusklist ={u'1':u'公簿',u'2':u'実測'}
                    self.sitkYutlist ={u'01':u'住宅用地',u'02':u'マンション用地',u'03':u'ビル用地',u'04':u'店舗用地',u'05':u'工業用地',u'06':u'配送センター用地',u'07':u'営業所用地',u'08':u'保養所用地',u'09':u'その他用地',u'10':u'事務所用地',u'11':u'別荘用地',u'12':u'倉庫用地',u'13':u'資材置場用地',u'14':u'家庭菜園用地',u'15':u'アパート用地',u'16':u'社宅社員寮用地',u'17':u'病院診療所用地',u'18':u'畑・農地用地',u'19':u'事業用地',u'20':u'駐車場用地'}
                    self.chushjyuZihlist ={u'1':u'有',u'2':u'無'}
                if cont[2] == '02':
                    self.bkknShmklist = {u'01':u'新築戸建',u'02':u'中古戸建',u'03':u'新築テラス',u'04':u'中古テラス'}
                    self.gnkyulist = {u'':None,u'1':u'居住中',u'2':u'空家',u'3':u'賃貸中',u'4':u'未完成'}
                    self.mnskKisokHusklist ={u'':None,u'1':u'公簿',u'2':u'実測'}
                    self.sitkYutlist ={u'':None,u'55':u'リゾート向'}
                    self.chushjyuZihlist ={u'':None,u'1':u'有',u'2':u'無',u'3':u'近隣確保'}
                elif cont[2] == '03':
                    self.bkknShmklist = {u'01':u'新築マンション',u'02':u'中古マンション',u'07':u'新築タウン',u'08':u'中古タウン',u'09':u'新築リゾート',u'10':u'中古リゾート',u'99':u'その他'}
                    self.gnkyulist = {u'':None,u'1':u'居住中',u'2':u'空家',u'3':u'賃貸中',u'4':u'未完成'}
                    self.mnskKisokHusklist ={u'':None,u'1':u'壁芯',u'2':u'内法'}
                    self.sitkYutlist ={u'':None,u'55':u'リゾート向'}
                    self.chushjyuZihlist ={u'':None,u'1':u'空有',u'2':u'空無',u'3':u'近隣確保',u'4':u'無'}
                elif cont[2] == '04':
                    self.bkknShmklist = {u'01':u'店舗',u'02':u'店舗付住宅',u'03':u'住宅付店舗',u'04':u'事務所' ,u'05':u'店舗事務所',u'06':u'ビル' ,u'07':u'工場',u'08':u'マンション' ,u'09':u'倉庫' ,u'10':u'アパート' ,u'11':u'寮',u'12':u'旅館' ,u'13':u'ホテル',u'14':u'別荘' ,u'15':u'リゾート',u'16':u'文化住宅',u'99':u'その他'}
                    self.gnkyulist = {u'':None,u'1':u'居住中',u'2':u'空家',u'3':u'賃貸中',u'4':u'未完成'}
                    self.mnskKisokHusklist ={u'':None,u'1':u'公簿',u'2':u'実測'}
                    self.sitkYutlist ={u'':None,u'55':u'リゾート向'}
                    self.chushjyuZihlist ={u'':None,u'1':u'有',u'2':u'無'}
                elif cont[2] == '05':
                    self.bkknShmklist = {u'01':u'店舗',u'02':u'事務所',u'03':u'店舗事務所',u'99':u'その他'}
                    self.gnkyulist = {u'':None,u'1':u'居住中',u'2':u'空家',u'3':u'賃貸中',u'4':u'未完成'}
                    self.mnskKisokHusklist ={u'':None,u'1':u'壁芯',u'2':u'内法'}
                    self.sitkYutlist ={u'':None,u'55':u'リゾート向'}
                    self.chushjyuZihlist ={u'':None,u'1':u'空有',u'2':u'空無',u'3':u'近隣確保',u'4':u'無'}
                self.hkwtsNyukyJklist ={u'':None,u'1':u'即時',u'2':u'相談',u'3':u'期日指定',u'4':u'予定'}
                self.hkwtsNyukyShnlist ={u'':None,u'1':u'上旬',u'2':u'中旬',u'3':u'下旬'}
                self.trhktiyulist ={u'':None,u'1':u'売主',u'2':u'代理',u'3':u'専属',u'4':u'専任',u'5':u'一般'}
                self.hushuKitilist ={u'':None,u'1':u'分かれ',u'2':u'当方不払',u'4':u'当方片手数',u'5':u'代理折半',u'9':u'相談'}
                self.stbkKbnlist ={u'':None,u'0':u'無',u'1':u'有',u'2':u'済'}
                self.kkdhuTdkdlist ={u'':None,u'1':u'要',u'2':u'中',u'3':u'不要'}
                self.tukbCmklist ={u'':None,u'1':u'宅地',u'2':u'田',u'3':u'畑',u'4':u'山林',u'5':u'雑種',u'9':u'他'}
                self.tskikklist ={u'':None,u'1':u'市街',u'2':u'調整',u'3':u'非線引き',u'4':u'域外',u'5':u'準都市'}
                self.yutCik1list ={u'':None,u'00':None,u'01':u'一低',u'02':u'二中',u'03':u'二住',u'04':u'近商',u'05':u'商業',u'06':u'準工',u'07':u'工業',u'08':u'工専',u'10':u'二低',u'11':u'一中',u'12':u'一住',u'13':u'準住',u'99':u'無指定'}
                self.cikCklist ={u'':None,u'01':u'防火',u'02':u'準防火',u'03':u'高度',u'04':u'高度利用',u'05':u'風致',u'06':u'文教',u'09':u'その他'}
                self.tcKenrlist ={u'':None,u'1':u'所有権',u'2':u'旧法地上',u'3':u'旧法賃借',u'4':u'普通地上',u'5':u'定期地上',u'6':u'普通賃借',u'7':u'定期賃借',u'8':u'他'}
                self.ftiKenrlist ={u'':None,u'01':u'抵当権',u'02':u'温泉利用権'}
                self.csilist={u'':None,u'1':u'平坦',u'2':u'高台',u'3':u'低地',u'4':u'ひな段',u'5':u'傾斜地',u'9':u'その他'}
                self.knrKitilist={u'':None,u'1':u'自主管理',u'2':u'管理会社に一部委託',u'3':u'管理会社に全部委託'}
                self.knrnnJyukyulist={u'':None,u'1':u'常駐',u'2':u'日勤',u'3':u'巡回'}
                self.stduJyukyulist={u'':None,u'1':u'一方',u'2':u'角地',u'3':u'三方',u'4':u'四方',u'5':u'二方'}
                self.stduShbt1list={u'':None,u'1':u'公道',u'2':u'私道'}
                self.stduHuku1list={u'':None,u'1':u'北',u'2':u'北東',u'3':u'東',u'4':u'南東',u'5':u'南',u'6':u'南西',u'7':u'西',u'8':u'北西'}
                self.mdrTyp1list={u'':None,u'01':u'ワンルーム',u'02':u'K',u'03':u'DK',u'04':u'LK',u'05':u'LDK',u'06':u'SK',u'07':u'SDK',u'08':u'SLK',u'09':u'SLDK'}
                self.stTyp11list={u'':None,u'1':u'和',u'2':u'洋',u'3':u'DK',u'4':u'LDK',u'5':u'L',u'6':u'D',u'7':u'K',u'8':u'S',u'9':u'その他'}
                self.chushjyuSkknGklist={u'':None,u'1':u'円',u'2':u'ヶ月'}
                self.ttmnKuzulist={u'':None,u'01':u'木造',u'02':u'ブロック',u'03':u'鉄骨造',u'04':u'RC',u'05':u'SRC',u'06':u'PC',u'07':u'HPC',u'08':u'軽量鉄骨',u'09':u'その他'}
                self.ttmnKuhulist={u'':None,u'1':u'在来',u'2':u'2×4'}
                self.shuhnAccs1list={u'':None,u'1':u'徒歩',u'2':u'車'}
                try:
#                    br = Branch.Branch.get_by_key_name(self.corp_name + u"/" + self.branch_name)
                    br = Branch.Branch.get_or_insert(self.corp_name + u"/" + self.branch_name)
                    bkID = str(br.getNextNum())
                    key_name = self.corp_name + u"/" + self.branch_name + u"/" + bkID
                    data = bkdata.BKdata.get_or_insert(key_name,bkID = bkID)

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
                    data.dataSource = self.source

                    #物件番号
                    if self.nunicode(cont[0], enc) == u"物件番号":
                        data.delete()
                        raise MyError, 'TitleSkip'
                        
                    #data.bknbng = self.source + '/' + self.nunicode(cont[0], enc)
                    self.e+=1
                    
                    #データ種類
                    data.bbchntikbn = self._dtsyurilist(unicode(cont[1], enc))
                    self.e+=1
                    #list = {u'01':u'売買',:u'02':u'賃貸'}

                    data.dtsyuri = u'物件'
                    
                    #物件種別
                    data.bkknShbt = self._bkknShbtlist(unicode(cont[2], enc))
                    self.e+=1
                    #list = {u'01':u'土地',u'02':u'戸建',u'03'u:'マンション',u'04':u'外全',u'05':u'外一'}
                    
                    #物件種目
                    data.bkknShmk = self._bkknShmklist(unicode(cont[3], enc))
                    self.e+=1
                    #list = {u'01':u'売地',u'02':u'借地権',u'03'u:'底地権'}
                    
                    #会員名
                    data.kiinni = self.nunicode(cont[4], enc)
                    self.e+=1
                    
                    #代表電話番号
                    data.dihyodnwbngu = self.nunicode(cont[5], enc)
                    self.e+=1
                    
                    #問合せ担当者（1）
                    data.tiawsTntush = self.nunicode(cont[6], enc)
                    self.e+=1
                    
                    #問合せ電話番号（1）
                    data.tiawsDnwBngu = self.nunicode(cont[7], enc)
                    self.e+=1
                    
                    #Eメールアドレス（1）
                    data.emlAdrs = self.nunicode(cont[8], enc)
                    self.e+=1
                    
                    #図面
                    data.zmn = self.nunicode(cont[9], enc)
                    self.e+=1
                    
                    #登録年月日
                    data.turknngp = self.getdatetime(self.nunicode(cont[10], enc))
                    self.e+=1
                    
                    #変更年月日
                    data.hnknngp = self.getdatetime(self.nunicode(cont[11], enc))
                    self.e+=1
                    
                    #取引条件の有効期限
                    data.trhkJyuknYukuKgn = self.getdatetime(unicode(cont[12], enc))
                    self.e+=1
                    
                    #新築中古区分
                    data.sntktyukkbn = self.nunicode(cont[13], enc)
                    self.e+=1
                    
                    #都道府県名
                    data.tdufknmi = self.nunicode(cont[14], enc)
                    self.e+=1
                    
                    #所在地名1
                    data.shzicmi1 = self.nunicode(cont[15], enc)
                    self.e+=1
                    
                    #所在地名2
                    data.shzicmi2 = self.nunicode(cont[16], enc)
                    self.e+=1
                    #所在地名3
                    data.shzicmi3 = self.nunicode(cont[17], enc)
                    self.e+=1
                    #建物名
                    data.ttmnmi = self.nunicode(cont[18], enc)
                    self.e+=1
                    #部屋番号
                    data.hyBngu = self.nunicode(cont[19], enc)
                    self.e+=1
                    #その他所在地表示
                    data.sntShzicHyuj = self.nunicode(cont[20], enc)
                    self.e+=1
                    #棟番号
                    data.tuBngu = self.nunicode(cont[21], enc)
                    self.e+=1
                    #沿線略称（1）
                    data.ensnmi1 = self.nunicode(cont[22], enc)
                    self.e+=1
                    #駅名（1）
                    data.ekmi1 = self.nunicode(cont[23], enc)
                    self.e+=1
                    #徒歩（分）1（1）
                    data.thHn11 = self.nfloat(self.nunicode(cont[24], enc))
                    self.e+=1
                    #徒歩（m）2（1）
                    data.thM21 = self.nfloat(self.nunicode(cont[25], enc))
                    self.e+=1
                    #バス（1）
                    data.bs1 = self.nunicode(cont[26], enc)
                    self.e+=1
                    #バス路線名（1）
                    data.bsRsnmi1 = self.nunicode(cont[27], enc)
                    self.e+=1
                    #バス停名称（1）
                    data.bstiMishu1 = self.nunicode(cont[28], enc)
                    self.e+=1
                    #停歩（分）（1）
                    data.tihHn1 = self.nfloat(self.nunicode(cont[29], enc))
                    self.e+=1
                    #停歩（m）（1）
                    data.tihM1 = self.nfloat(self.nunicode(cont[30], enc))
                    self.e+=1
                    #車（km）（1）
                    data.krmKm1 = self.nfloat(self.nunicode(cont[31], enc))
                    self.e+=1
                    #その他交通手段
                    data.sntKutuShdn = self.nunicode(cont[32], enc)
                    self.e+=1
                    
                    #交通（分）1
                    data.kutuHn = self.nfloat(self.nunicode(cont[33], enc))
                    self.e+=1
                    
                    #交通（m）2
                    data.kutuM = self.nfloat(self.nunicode(cont[34], enc))
                    self.e+=1
                    
                    #現況
                    data.gnkyu = self._gnkyulist(unicode(cont[35], enc))
                    self.e+=1
                    #list ={u'1':u'更地',u'2':u'上物有'}

                    #現況予定年月
                    data.gnkyuYtiNngt = self.getdatetime2(self.nunicode(cont[36], enc))
                    self.e+=1
                    
                    #引渡時期
                    data.hkwtsNyukyJk = self._hkwtsNyukyJklist(unicode(cont[37], enc))
                    self.e+=1
                    #list ={u'1':u'即時',u'2':u'相談',u'3':u'期日指定',u'4':u'予定'}
                    
                    #引渡年月（西暦）
                    data.hkwtsNyukyNngtSirk = self.getdatetime2(self.nunicode(cont[38], enc))
                    self.e+=1
                    
                    #引渡旬
                    data.hkwtsNyukyShn = self._hkwtsNyukyShnlist(unicode(cont[39], enc))
                    self.e+=1
                    #list ={u'1':u'上旬',u'2':u'中旬',u'3':u'下旬'}
                    
                    #入居年月（西暦）
                    data.nyukyNngtSirk = self.getdatetime2(self.nunicode(cont[40], enc))
                    self.e+=1
                    
                    #入居日
#####               data.          = self.nunicode(cont[41], enc)
                    self.e+=1
                    
                    #取引態様
                    data.trhktiyu = self._trhktiyulist(unicode(cont[42], enc))
                    self.e+=1
                    #list ={u'1':u'売主',u'2':u'代理',u'3':u'専属',u'4':u'専任',u'5':u'一般'}

                    #報酬形態
                    data.hushuKiti = self._hushuKitilist(unicode(cont[43], enc))
                    self.e+=1
                    #list ={u'1':u'分かれ',u'2':u'当方不払',u'3':u'当方片手数',u'4':u'代理折半',u'5':u'相談'}
                    
                    #手数料割合率
                    data.tsuryuWraiRt = self.nfloat(self.nunicode(cont[44], enc))
                    self.e+=1
                    
                    #手数料
                    data.tsuryu = self.nfloat(self.nunicode(cont[45], enc))
                    self.e+=1
                    
                    #価格
                    data.kkkuCnryu = self.nfloat(self.nunicode(cont[46], enc))
                    self.e+=1
                    
                    #価格消費税
                    data.kkkuCnryuShuhzi = self.nfloat(self.nunicode(cont[47], enc))
                    self.e+=1
                    
                    #坪単価
                    data.tbTnk = self.nfloat(self.nunicode(cont[48], enc))
                    self.e+=1
                    
                    #㎡単価
                    data.m2Tnk = self.nfloat(self.nunicode(cont[49], enc))
                    self.e+=1
                    
                    #想定利回り（％）
                    data.sutiRmwrPrcnt = self.nfloat(self.nunicode(cont[50], enc))
                    self.e+=1
                    
                    #面積計測方式
                    data.mnskKisokHusk = self._mnskKisokHusklist(unicode(cont[51], enc))
                    self.e+=1
                    #list ={u'1':u'公簿',u'2':u'実測'}
                    
                    #土地面積
                    data.tcMnsk2 = self.nfloat(self.nunicode(cont[52], enc))
                    self.e+=1
                    
                    #土地共有持分面積
                    data.tcMcbnSumnsk = self.nfloat(self.nunicode(cont[53], enc))
                    self.e+=1
                    
                    #土地共有持分（分子）
                    data.tcMcbnBns = self.nfloat(self.nunicode(cont[54], enc))
                    self.e+=1

                    #土地共有持分（分母）
                    data.tcMcbnBnb = self.nfloat(self.nunicode(cont[55], enc))
                    self.e+=1
                    
                    #建物面積1
                    data.ttmnMnsk1 = self.nfloat(self.nunicode(cont[56], enc))
                    self.e+=1
                    
                    #専有面積
                    data.snyuMnskSyuBbnMnsk2 = self.nfloat(self.nunicode(cont[57], enc))
                    self.e+=1
                    
                    #私道負担有無
                    data.sduFtnUm = self._sduFtnUmlist(unicode(cont[58], enc))
                    self.e+=1
                    #list ={u'1':u'有',u'2':u'無'}
                    
                    #私道面積
                    data.sduMnsk = self.nfloat(self.nunicode(cont[59], enc))
                    self.e+=1
                    
                    #バルコニー（テラス）面積
                    data.blcnyTrsMnsk = self.nfloat(self.nunicode(cont[60], enc))
                    self.e+=1
                    
                    #専用庭面積
                    data.snyouNwMnsk = self.nfloat(self.nunicode(cont[61], enc))
                    self.e+=1
                    
                    #セットバック区分
                    data.stbkKbn = self._stbkKbnlist(unicode(cont[62], enc))
                    self.e+=1
                    #list ={u'0':u'無',u'1':u'有',u'2':u'済'}
                    
                    #後退距離（m）
                    data.kutiKyrM = self.nfloat(self.nunicode(cont[63], enc))
                    self.e+=1
                    
                    #セットバック面積（㎡）
                    data.stbkMnskM2 = self.nfloat(self.nunicode(cont[64], enc))
                    self.e+=1
                    
                    #開発面積／総面積
                    data.kihtMnskSumnsk = self.nfloat(self.nunicode(cont[65], enc))
                    self.e+=1
                    
                    #販売総面積
                    data.hnbiSumnsk = self.nfloat(self.nunicode(cont[66], enc))
                    self.e+=1
                    
                    #販売区画数
                    data.hnbiKkksu = self.nfloat(self.nunicode(cont[67], enc))
                    self.e+=1
                    
                    #工事完了年月（西暦）
                    data.kujKnryuNngtSirk = self.getdatetime(self.nunicode(cont[68], enc))
                    self.e+=1
                    
                    #建築面積
                    data.knckMnsk = self.nfloat(self.nunicode(cont[69], enc))
                    self.e+=1
                    
                    #延べ面積
                    data.nbMnsk = self.nfloat(self.nunicode(cont[70], enc))
                    self.e+=1
                    
                    #敷地延長の有無
                    data.skcEnchuUm = self._sduFtnUmlist(unicode(cont[71], enc))
                    self.e+=1
                    #list ={u'1':u'有',u'2':u'無'}
                    
                    #敷地延長（30%以上表示）
                    data.skcEnchu30PrcntIjyuHyuj = self.nfloat(self.nunicode(cont[72], enc))
                    self.e+=1
                    
                    #借地料
                    data.shkcryu = self.nfloat(self.nunicode(cont[73], enc))
                    self.e+=1
                    
                    #借地期間
                    data.shkcKknYY = self.nfloat(self.nunicode(cont[74], enc))
                    self.e+=1
                    
                    #借地期限（西暦）
                    data.shkcKgnSirk = self.getdatetime(self.nunicode(cont[75], enc))
                    self.e+=1
                    
                    #施設費用項目（1）
                    data.sstHyuKumk1 = self.nunicode(cont[76], enc)
                    self.e+=1
                    
                    #施設費用（1）
                    data.sstHyu1 = self.nfloat(self.nunicode(cont[77], enc))
                    self.e+=1
                    
                    #国土法届出
                    data.kkdhuTdkd = self._kkdhuTdkdlist(unicode(cont[78], enc))
                    self.e+=1
                    #list ={u'1':u'要',u'2':u'中',u'3':u'不要'}
                    
                    #登記簿地目
                    data.tukbCmk = self._tukbCmklist(unicode(cont[79], enc))
                    self.e+=1
                    #list ={u'1':u'宅地',u'2':u'田',u'3':u'畑',u'4':u'山林',u'5':u'雑種',u'9':u'他'}
                    
                    #現況地目
                    data.gnkyuCmk = self._tukbCmklist(unicode(cont[80], enc))
                    self.e+=1
                    #list ={u'1':u'宅地',u'2':u'田',u'3':u'畑',u'4':u'山林',u'5':u'雑種',u'9':u'他'}
                    
                    #都市計画
                    data.tskikk = self._tskikklist(unicode(cont[81], enc))
                    self.e+=1
                    #list ={u'1':u'市街',u'2':u'調整',u'3':u'非線引き',u'4':u'域外',u'5':u'準都市'}
                    
                    #用途地域（1）
                    data.yutCik1 = self._yutCik1list(unicode(cont[82], enc))
                    self.e+=1
                    #list ={u'01':u'一低',u0'2':u'二中',u'03':u'二住',u'04':u'近商',u'05':u'商業',u'06':u'準工',u'07':u'工業',u'08':u'工専',u'10':u'二低',u'11':u'一中',u'12':u'一住',u'13':u'準住',u'99':u'無指定'}
                    
                    #用途地域（2）
                    data.yutCik2 = self._yutCik1list(unicode(cont[83], enc))
                    self.e+=1
                    #list ={u'01':u'一低',u0'2':u'二中',u'03':u'二住',u'04':u'近商',u'05':u'商業',u'06':u'準工',u'07':u'工業',u'08':u'工専',u'10':u'二低',u'11':u'一中',u'12':u'一住',u'13':u'準住',u'99':u'無指定'}
                    
                    #最適用途
                    data.sitkYut = self._sitkYutlist(unicode(cont[84], enc))
                    self.e+=1
                    #list ={u'01':u'住宅用地',u'02':u'マンション用地',u'03':u'ビル用地',u'04':u'店舗用地',u'05':u'工業用地',u'06':u'配送センター用地',u'07':u'営業所用地',u'08':u'保養所用地',u'09':u'その他用地',u'10':u'事務所用地',u'11':u'別荘用地',u'12':u'倉庫用地',u'13':u'資材置場用地',u'14':u'家庭菜園用地',u'15':u'アパート用地',u'16':u'社宅社員寮用地',u'17':u'病院診療所用地',u'18':u'畑・農地用地',u'19':u'事業用地',u'20':u'駐車場用地'}
                    
                    #建ぺい率
                    data.knpirt = self.nfloat(self.nunicode(cont[85], enc))
                    self.e+=1
                    
                    #容積率
                    data.yuskrt = self.nfloat(self.nunicode(cont[86], enc))
                    self.e+=1
                    
                    #地域地区
                    data.cikCk = self._cikCklist(unicode(cont[87], enc))
                    self.e+=1
                    #list ={u'01':u'防火',u'02':u'準防火',u'03':u'高度',u'04':u'高度利用',u'05':u'風致',u'06':u'文教',u'09':u'その他'}
                    
                    #土地権利
                    data.tcKenr = self._tcKenrlist(unicode(cont[88], enc))
                    self.e+=1
                    #list ={u'1':u'所有権',u'1':u'旧法地上',u'1':u'旧法賃借',u'1':u'普通地上',u'1':u'定期地上',u'1':u'普通賃借',u'1':u'定期賃借',u'1':u'他'}
                    
                    #付帯権利
                    data.ftiKenr = self._ftiKenrlist(unicode(cont[89], enc))
                    self.e+=1
                    #list ={u'01':u'抵当権',u'02':u'温泉利用権'}
                    
                    #造作譲渡金
                    data.zusJyutkn = self.nfloat(self.nunicode(cont[90], enc))
                    self.e+=1
                    
                    #定借権利金
                    data.tishkKenrkn = self.nfloat(self.nunicode(cont[91], enc))
                    self.e+=1
                    
                    #定借保証金
                    data.tishkHshukn = self.nfloat(self.nunicode(cont[92], enc))
                    self.e+=1
                    
                    #定借敷金
                    data.tishkSkkn = self.nfloat(self.nunicode(cont[93], enc))
                    self.e+=1
                    
                    #地勢
                    data.csi = self._csilist(unicode(cont[94], enc))
                    self.e+=1
                    #list={u'1':u'平坦',u'2':u'高台',u'3':u'低地',u'4':u'ひな段',u'5':u'傾斜地',u'9':u'その他'}
                    
                    #建築条件
                    data.knckJyukn = self._sduFtnUmlist(unicode(cont[95], enc))
                    self.e+=1
                    #list={u'1':u'有',u'2':u'無'}
                    
                    #オーナーチェンジ
                    data.ornrChng = self.nunicode(cont[96], enc)
                    self.e+=1
                    
                    #管理組合有無
                    data.knrKmaiUm = self._sduFtnUmlist(unicode(cont[97], enc))
                    self.e+=1
                    #list={u'1':u'有',u'2':u'無'}
                    
                    #管理形態
                    data.knrKiti = self._knrKitilist(unicode(cont[98], enc))
                    self.e+=1
                    #list={u'1':u'自主管理',u'2':u'管理会社に一部委託',u'3':u'管理会社に全部委託'}
                    
                    #管理会社名
                    data.knrKishmi = self.nunicode(cont[99], enc)
                    self.e+=1
                    
                    #管理人状況
                    data.knrnnJyukyu = self._knrnnJyukyulist(unicode(cont[100], enc))
                    self.e+=1
                    #list={u'1':u'常駐',u'2':u'日勤',u'3':u'巡回'}
                    
                    #管理費
                    data.knrh = self.nfloat(self.nunicode(cont[101], enc))
                    self.e+=1
                    
                    #管理費消費税
                    data.knrhShuhzi = self.nfloat(self.nunicode(cont[102], enc))
                    self.e+=1
                    
                    #修繕積立金
                    data.shznTmttkn = self.nfloat(self.nunicode(cont[103], enc))
                    self.e+=1
                    
                    #その他月額費名称1
                    data.sntGtgkhMishu1 = self.nunicode(cont[104], enc)
                    self.e+=1
                    
                    #その他月額費用金額1
                    data.sntGtgkHyuKngk1 = self.nfloat(self.nunicode(cont[105], enc))
                    self.e+=1
                    
                    #施主
                    data.ssh = self.nunicode(cont[106], enc)
                    self.e+=1
                    
                    #施工会社名
                    data.skuKishmi = self.nunicode(cont[107], enc)
                    self.e+=1
                    
                    #分譲会社名
                    data.bnjyuKishmi = self.nunicode(cont[108], enc)
                    self.e+=1
                    
                    #一括下請負人
                    data.ikktStukoinn = self.nunicode(cont[109], enc)
                    self.e+=1
                    
                    #接道状況
                    data.stduJyukyu = self._stduJyukyulist(unicode(cont[110], enc))
                    self.e+=1
                    #list={u'1':u'一方',u'2':u'角地',u'3':u'三方',u'4':u'四方',u'5':u'二方'}
                    
                    #接道種別1
                    data.stduShbt1 = self._stduShbt1list(unicode(cont[111], enc))
                    self.e+=1
                    #list={u'1':u'公道',u'2':u'私道'}
                    
                    #接道接面1
                    data.stduStmn1 = self.nunicode(cont[112], enc)
                    self.e+=1
                    
                    #接道位置指定1
                    data.stduIcSti1 = self._sduFtnUmlist(unicode(cont[113], enc))
                    self.e+=1
                    #list={u'1':u'有',u'2':u'無'}
                    
                    #接道方向1
                    data.stduHuku1 = self._stduHuku1list(unicode(cont[114], enc))
                    self.e+=1
                    #list={u'1':u'北',u'2':u'北東',u'3':u'東',u'4':u'南東',u'5':u'南',u'6':u'南西',u'7':u'西',u'8':u'北西'}
                    
                    #接道幅員1
                    data.stduFkin1 = self.nfloat(self.nunicode(cont[115], enc))
                    self.e+=1
                    
                    #接道種別2
                    data.stduShbt2 = self._stduShbt1list(unicode(cont[116], enc))
                    self.e+=1
                    #list={u'1':u'公道',u'2':u'私道'}
                    
                    #接道接面2
                    data.stduStmn2 = self.nfloat(self.nunicode(cont[117], enc))
                    self.e+=1
                    
                    #接道位置指定2
                    data.stduIcSti2 = self._sduFtnUmlist(unicode(cont[118], enc))
                    self.e+=1
                    #list={u'1':u'有',u'2':u'無'}
                    
                    #接道方向2
                    data.stduHuku2 = self._stduHuku1list(unicode(cont[119], enc))
                    self.e+=1
                    #list={u'1':u'北',u'2':u'北東',u'3':u'東',u'4':u'南東',u'5':u'南',u'6':u'南西',u'7':u'西',u'8':u'北西'}
                    
                    #接道幅員2
                    data.stduFkin2 = self.nfloat(self.nunicode(cont[120], enc))
                    self.e+=1
                    
                    #接道種別3
                    data.stduShbt3 = self._stduShbt1list(unicode(cont[121], enc))
                    self.e+=1
                    #list={u'1':u'公道',u'2':u'私道'}
                    
                    #接道接面3
                    data.stduStmn3 = self.nfloat(self.nunicode(cont[122], enc))
                    self.e+=1
                    
                    #接道位置指定3
                    data.stduIcSti3 = self._sduFtnUmlist(unicode(cont[123], enc))
                    self.e+=1
                    #list={u'1':u'有',u'2':u'無'}
                    
                    #接道方向3
                    data.stduHuku3 = self._stduHuku1list(unicode(cont[124], enc))
                    self.e+=1
                    #list={u'1':u'北',u'2':u'北東',u'3':u'東',u'4':u'南東',u'5':u'南',u'6':u'南西',u'7':u'西',u'8':u'北西'}
                    
                    #接道幅員3
                    data.stduFkin3 = self.nfloat(self.nunicode(cont[125], enc))
                    self.e+=1
                    
                    #接道種別4
                    data.stduShbt4 = self._stduShbt1list(unicode(cont[126], enc))
                    self.e+=1
                    #list={u'1':u'公道',u'2':u'私道'}
                    
                    #接道接面4
                    data.stduStmn4 = self.nfloat(self.nunicode(cont[127], enc))
                    self.e+=1
                    
                    #接道位置指定4
                    data.stduIcSti4 = self._sduFtnUmlist(unicode(cont[128], enc))
                    self.e+=1
                    #list={u'1':u'有',u'2':u'無'}
                    
                    #接道方向4
                    data.stduHuku4 = self._stduHuku1list(unicode(cont[129], enc))
                    self.e+=1
                    #list={u'1':u'北',u'2':u'北東',u'3':u'東',u'4':u'南東',u'5':u'南',u'6':u'南西',u'7':u'西',u'8':u'北西'}
                    
                    #接道幅員4
                    data.stduFkin4 = self.nfloat(self.nunicode(cont[130], enc))
                    self.e+=1
                    
                    #接道舗装
                    data.stduHsu = self._sduFtnUmlist(unicode(cont[131], enc))
                    self.e+=1
                    #list={u'1':u'有',u'2':u'無'}
                    
                    #間取タイプ（1）
                    data.mdrTyp1 = self._mdrTyp1list(unicode(cont[132], enc))
                    self.e+=1
                    #list={u'01':u'ワンルーム',u'02':u'K',u'03':u'DK',u'04':u'LK',u'05':u'LDK',u'06':u'SK',u'07':u'SDK',u'08':u'SLK',u'09':u'SLDK'}
                    
                    #間取部屋数（1）
                    data.mdrHysu1 = self.nfloat(self.nunicode(cont[133], enc))
                    self.e+=1
                    
                    #部屋位置
###                 data.        = self.nunicode(cont[134], enc)
                    self.e+=1
                    
                    #納戸数
                    data.nuKsu1 = self.nfloat(self.nunicode(cont[135], enc))
                    self.e+=1
                    
                    #室所在階1（1）
                    data.stShziki11 = self.nfloat(self.nunicode(cont[136], enc))
                    self.e+=1
                    
                    #室タイプ1（1）
                    data.stTyp11 = self._stTyp11list(unicode(cont[137], enc))
                    self.e+=1
                    #list={u'1':u'和',u'2':u'洋',u'3':u'DK',u'4':u'LDK',u'5':u'L',u'6':u'D',u'7':u'K',u'8':u'S',u'9':u'その他'}
                    
                    #室広さ1（1）
                    data.stHrs11 = self.nfloat(self.nunicode(cont[138], enc))
                    self.e+=1
                    
                    #室数1（1）
                    data.stsu11 = self.nfloat(self.nunicode(cont[139], enc))
                    self.e+=1
                    
                    #室所在階2（1）
                    data.stShziki21 = self.nfloat(self.nunicode(cont[140], enc))
                    self.e+=1
                    
                    #室タイプ2（1）
                    data.stTyp21 = self._stTyp11list(unicode(cont[141], enc))
                    self.e+=1
                    #list={u'1':u'和',u'2':u'洋',u'3':u'DK',u'4':u'LDK',u'5':u'L',u'6':u'D',u'7':u'K',u'8':u'S',u'9':u'その他'}
                    
                    #室広さ2（1）
                    data.stHrs21 = self.nfloat(self.nunicode(cont[142], enc))
                    self.e+=1
                    
                    #室数2（1）
                    data.stsu21 = self.nfloat(self.nunicode(cont[143], enc))
                    self.e+=1
                    
                    #室所在階3（1）
                    data.stShziki31 = self.nfloat(self.nunicode(cont[144], enc))
                    self.e+=1
                    
                    #室タイプ3（1）
                    data.stTyp31 = self._stTyp11list(unicode(cont[145], enc))
                    self.e+=1
                    #list={u'1':u'和',u'2':u'洋',u'3':u'DK',u'4':u'LDK',u'5':u'L',u'6':u'D',u'7':u'K',u'8':u'S',u'9':u'その他'}
                    
                    #室広さ3（1）
                    data.stHrs31 = self.nfloat(self.nunicode(cont[146], enc))
                    self.e+=1
                    
                    #室数3（1）
                    data.stsu31 = self.nfloat(self.nunicode(cont[147], enc))
                    self.e+=1
                    
                    #室所在階4（1）
                    data.stShziki41 = self.nfloat(self.nunicode(cont[148], enc))
                    self.e+=1
                    
                    #室タイプ4（1）
                    data.stTyp41 = self._stTyp11list(unicode(cont[149], enc))
                    self.e+=1
                    #list={u'1':u'和',u'2':u'洋',u'3':u'DK',u'4':u'LDK',u'5':u'L',u'6':u'D',u'7':u'K',u'8':u'S',u'9':u'その他'}
                    
                    #室広さ4（1）
                    data.stHrs41 = self.nfloat(self.nunicode(cont[150], enc))
                    self.e+=1
                    
                    #室数4（1）
                    data.stsu41 = self.nfloat(self.nunicode(cont[151], enc))
                    self.e+=1
                    
                    #室所在階5（1）
                    data.stShziki51 = self.nfloat(self.nunicode(cont[152], enc))
                    self.e+=1
                    
                    #室タイプ5（1）
                    data.stTyp51 = self._stTyp11list(unicode(cont[153], enc))
                    self.e+=1
                    #list={u'1':u'和',u'2':u'洋',u'3':u'DK',u'4':u'LDK',u'5':u'L',u'6':u'D',u'7':u'K',u'8':u'S',u'9':u'その他'}
                    
                    #室広さ5（1）
                    data.stHrs51 = self.nfloat(self.nunicode(cont[154], enc))
                    self.e+=1
                    
                    #室数5（1）
                    data.stsu51 = self.nfloat(self.nunicode(cont[155], enc))
                    self.e+=1
                    
                    #室所在階6（1）
                    data.stShziki61 = self.nfloat(self.nunicode(cont[156], enc))
                    self.e+=1
                    
                    #室タイプ6（1）
                    data.stTyp61 = self._stTyp11list(unicode(cont[157], enc))
                    self.e+=1
                    #list={u'1':u'和',u'2':u'洋',u'3':u'DK',u'4':u'LDK',u'5':u'L',u'6':u'D',u'7':u'K',u'8':u'S',u'9':u'その他'}
                    
                    #室広さ6（1）
                    data.stHrs61 = self.nfloat(self.nunicode(cont[158], enc))
                    self.e+=1
                    
                    #室数6（1）
                    data.stsu61 = self.nfloat(self.nunicode(cont[159], enc))
                    self.e+=1
                    
                    #室所在階7（1）
                    data.stShziki71 = self.nfloat(self.nunicode(cont[160], enc))
                    self.e+=1
                    
                    #室タイプ7（1）
                    data.stTyp71 = self._stTyp11list(unicode(cont[161], enc))
                    self.e+=1
                    #list={u'1':u'和',u'2':u'洋',u'3':u'DK',u'4':u'LDK',u'5':u'L',u'6':u'D',u'7':u'K',u'8':u'S',u'9':u'その他'}
                    
                    #室広さ7（1）
                    data.stHrs71 = self.nfloat(self.nunicode(cont[162], enc))
                    self.e+=1
                    
                    #室数7（1）
                    data.stsu71 = self.nfloat(self.nunicode(cont[163], enc))
                    self.e+=1
                    
                    #間取りその他（1）
                    data.mdrSnt1 = self.nunicode(cont[164], enc)
                    self.e+=1
                    
                    #駐車場在否
                    data.chushjyuZih = self._chushjyuZihlist(unicode(cont[165], enc))
                    self.e+=1
                    #list={u'1':u'有',u'2':u'無',}
                    
                    #駐車場月額
                    data.chushjyuGtgk = self.nfloat(self.nunicode(cont[166], enc))
                    self.e+=1
                    
                    #駐車場月額消費税
                    data.chushjyuGtgkShuhzi = self.nfloat(self.nunicode(cont[167], enc))
                    self.e+=1
                    
                    #駐車場敷金（額）
                    data.chushjyuSkknGk = self._chushjyuSkknGklist(unicode(cont[168], enc))
                    self.e+=1
                    #list={u'1':u'円',u'2':u'ヶ月'}
                    
                    #駐車場敷金（ヶ月）
                    data.chushjyuSkknKgt = self.nfloat(self.nunicode(cont[169], enc))
                    self.e+=1
                    
                    #駐車場礼金（額）
                    data.chushjyuRiknGk = self._chushjyuSkknGklist(unicode(cont[170], enc))
                    self.e+=1
                    #list={u'1':u'円',u'2':u'ヶ月'}
                    
                    #駐車場礼金（ヶ月）
                    data.chushjyuRiknKgt = self.nfloat(self.nunicode(cont[171], enc))
                    self.e+=1
                    
                    #建物構造
                    data.ttmnKuzu = self._ttmnKuzulist(unicode(cont[172], enc))
                    self.e+=1
                    #list={u'01':u'木造',u'02':u'ブロック',u'03':u'鉄骨造',u'04':u'RC',u'05':u'SRC',u'06':u'PC',u'07':u'HPC',u'08':u'軽量鉄骨',u'09':u'その他'}
                    
                    #建物工法
                    data.ttmnKuhu = self._ttmnKuhulist(unicode(cont[173], enc))
                    self.e+=1
                    #list={u'1':u'在来',u'2':u'2×4'}
                    
                    #建物形式
                    data.ttmnKisk = self.nunicode(cont[174], enc)
                    self.e+=1
                    
                    #地上階層
                    data.cjyuKisou = self.nfloat(self.nunicode(cont[175], enc))
                    self.e+=1
                    
                    #地下階層
                    data.ckaKisou = self.nfloat(self.nunicode(cont[176], enc))
                    self.e+=1
                    
                    #所在階
                    data.shziki = self.nfloat(self.nunicode(cont[177], enc))
                    self.e+=1
                    
                    #築年月（西暦）
                    data.cknngtSirk = self.getdatetime2(self.nunicode(cont[178], enc))
                    self.e+=1
                    
                    #総戸数
                    data.suksu = self.nfloat(self.nunicode(cont[179], enc))
                    self.e+=1
                    
                    #棟総戸数
                    data.tuSuksu = self.nfloat(self.nunicode(cont[180], enc))
                    self.e+=1
                    
                    #連棟戸数
                    data.rntuKsu = self.nfloat(self.nunicode(cont[181], enc))
                    self.e+=1
                    
                    #バルコニー方向（1）
                    data.blcnyHuku1 = self._stduHuku1list(unicode(cont[182], enc))
                    self.e+=1
                    #list={u'1':u'北',u'2':u'北東',u'3':u'東',u'4':u'南東',u'5':u'南',u'6':u'南西',u'7':u'西',u'8':u'北西'}

                    #増改築年月1
                    data.zukickNngt1 = self.getdatetime2(self.nunicode(cont[183], enc))
                    self.e+=1
                    
                    #増改築履歴1
                    data.zukickRrk1 = self.nunicode(cont[184], enc)
                    self.e+=1
                    
                    #増改築年月2
                    data.zukickNngt2 = self.getdatetime2(self.nunicode(cont[185], enc))
                    self.e+=1
                    
                    #増改築履歴2
                    data.zukickRrk2 = self.nunicode(cont[186], enc)
                    self.e+=1
                    
                    #増改築年月3
                    data.zukickNngt3 = self.getdatetime2(self.nunicode(cont[187], enc))
                    self.e+=1
                    
                    #増改築履歴3
                    data.zukickRrk3 = self.nunicode(cont[188], enc)
                    self.e+=1
                    
                    #周辺環境1（フリー）
                    data.shuhnKnkyu1Fre = self.nunicode(cont[189], enc)
                    self.e+=1
                    
                    #距離1
                    data.kyr1 = self.nfloat(self.nunicode(cont[190], enc))
                    self.e+=1
                    
                    #時間1
                    data.jkn1 = self.nfloat(self.nunicode(cont[191], enc))
                    self.e+=1
                    
                    #周辺アクセス１
                    data.shuhnAccs1 = self._shuhnAccs1list(unicode(cont[192], enc))
                    self.e+=1
                    #list={u'1':u'徒歩',u'2':u'車'}
                
                    #備考1
                    data.bku1 = self.nunicode(cont[193], enc)
                    self.e+=1
                    
                    #備考2
                    data.bku2 = self.nunicode(cont[194], enc)
                    self.e+=1
                    
                    #自社管理欄
                    data.jshKnrrn = self.nunicode(cont[195], enc)
                    self.e+=1
                    
                    #再建築不可フラグ
                    data.siknckFkFlg = self.nbool(self.nunicode(cont[196], enc))
                    #早くする方法 https://hondaalfa.blogspot.com/2010/04/app-engine-datastore.html
                    data.put()
                    self.message.append("DataPutSuccess:line" + str(self.l) +"・・・・・OK")
                except Exception:
                    self.message.append("DataPutError:line" + str(self.l) + " elements" + str(self.e) + u":" + str(sys.exc_info()[0]) + u":" + str(sys.exc_info()[1]))
                    continue 
                
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
            self.message.append(u"error:line" + str(self.l) +" elements" + str(self.e) + " :" + str(sys.exc_info()[0]))
        finally:
            return result

    def getdatetime(self,text):
        result = None
        try:
            #tlist = text.split('-')
            #result = datetime.date(int(tlist[0]), int(tlist[1]), int(tlist[2])
            if text != None and text != "":
                if text[4] == '-':
                    result = timemanager.jst2utc_date(datetime.datetime.strptime(text, "%Y-%m-%d"))
                if text[4] == '/':
                    result = timemanager.jst2utc_date(datetime.datetime.strptime(text, "%Y/%m/%d"))
            #tlist = "2001-1-1".sprit('-')
        except Exception:
            self.message.append(u"error:line" + str(self.l) +u"elements" + str(self.e) + u":" + str(sys.exc_info()[0]) )
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
            self.message.append(u"error:line" + str(self.l) +u"elements" + str(self.e) + u":" + str(sys.exc_info()[0]) )
        finally:
            return result

    def nbool(self,text):
        result = None
        try:
            if text == None:
                return result
            if text != None and text != "":
                result = True
            elif text == u"0":
                result = False
        except Exception:
            self.message.append(u"error:line" + str(self.l) +u"elements" + str(self.e) + u":" + str(sys.exc_info()[0]) )
        finally:
            return result

    def nfloat(self,text):
        result = None
        try:
            if text != None and text != "":
                result = float(text)
        except Exception:
            self.message.append(u"error:line" + str(self.l) +u"elements" + str(self.e) + u":value" + text + u":" + str(sys.exc_info()[0]) )
        finally:
            return result

    def _dtsyurilist(self,data):
        result = None
        try:
            result = self.dtsyurilist[data]

        except Exception:
            self.message.append(u"error:line" + str(self.l) +u"elements" + str(self.e) + u":value" + data + u":" + str(sys.exc_info()[0]) )
        finally:
            return result

    def _bkknShbtlist(self,data):
        result = None
        try:
            result = self.bkknShbtlist[data]
        except Exception:
            self.message.append(u"error:line" + str(self.l) +u"elements" + str(self.e) + u":value" + data + u":" + str(sys.exc_info()[0]) )
        finally:
            return result

    def _bkknShmklist(self,data):
        result = None
        try:
            result = self.bkknShmklist[data]
        except Exception:
            self.message.append(u"error:line" + str(self.l) +u"elements" + str(self.e) + u":value" + data + u":" + str(sys.exc_info()[0]) )
        finally:
            return result

    def _gnkyulist(self,data):
        result = None
        try:
            result = self.gnkyulist[data]
        except Exception:
            self.message.append(u"error:line" + str(self.l) +u"elements" + str(self.e) + u":value" + data + u":" + str(sys.exc_info()[0]) )
        finally:
            return result

    def _mnskKisokHusklist(self,data):
        result = None
        try:
            result = self.mnskKisokHusklist[data]
        except Exception:
            self.message.append(u"error:line" + str(self.l) +u"elements" + str(self.e) + u":value" + data + u":" + str(sys.exc_info()[0]) )
        finally:
            return result

    def _sitkYutlist(self,data):
        result = None
        try:
            result = self.sitkYutlist[data]
        except Exception:
            self.message.append(u"error:line" + str(self.l) +u"elements" + str(self.e) + u":value" + data + u":" + str(sys.exc_info()[0]) )
        finally:
            return result

    def _sduFtnUmlist(self,data):
        result = None
        try:
            result = self.sduFtnUmlist[data]
        except Exception:
            self.message.append(u"error:line" + str(self.l) +u"elements" + str(self.e) + u":value" + data + u":" + str(sys.exc_info()[0]) )
        finally:
            return result

    def _chushjyuZihlist(self,data):
        result = None
        try:
            result = self.chushjyuZihlist[data]
        except Exception:
            self.message.append(u"error:line" + str(self.l) +u"elements" + str(self.e) + u":value" + data + u":" + str(sys.exc_info()[0]) )
        finally:
            return result

    def _hkwtsNyukyJklist(self,data):
        result = None
        try:
            result = self.hkwtsNyukyJklist[data]
        except Exception:
            self.message.append(u"error:line" + str(self.l) +u"elements" + str(self.e) + u":value" + data + u":" + str(sys.exc_info()[0]) )
        finally:
            return result

    def _hkwtsNyukyShnlist(self,data):
        result = None
        try:
            result = self.hkwtsNyukyShnlist[data]
        except Exception:
            self.message.append(u"error:line" + str(self.l) +u"elements" + str(self.e) + u":value" + data + u":" + str(sys.exc_info()[0]) )
        finally:
            return result

    def _trhktiyulist(self,data):
        result = None
        try:
            result = self.trhktiyulist[data]
        except Exception:
            self.message.append(u"error:line" + str(self.l) +u"elements" + str(self.e) + u":value" + data + u":" + str(sys.exc_info()[0]) )
        finally:
            return result

    def _hushuKitilist(self,data):
        result = None
        try:
            result = self.hushuKitilist[data]
        except Exception:
            self.message.append(u"error:line" + str(self.l) +u"elements" + str(self.e) + u":value" + data + u":" + str(sys.exc_info()[0]) )
        finally:
            return result

    def _stbkKbnlist(self,data):
        result = None
        try:
            result = self.stbkKbnlist[data]
        except Exception:
            self.message.append(u"error:line" + str(self.l) +u"elements" + str(self.e) + u":value" + data + u":" + str(sys.exc_info()[0]) )
        finally:
            return result

    def _kkdhuTdkdlist(self,data):
        result = None
        try:
            result = self.kkdhuTdkdlist[data]
        except Exception:
            self.message.append(u"error:line" + str(self.l) +u"elements" + str(self.e) + u":value" + data + u":" + str(sys.exc_info()[0]) )
        finally:
            return result

    def _tukbCmklist(self,data):
        result = None
        try:
            result = self.tukbCmklist[data]
        except Exception:
            self.message.append(u"error:line" + str(self.l) +u"elements" + str(self.e) + u":value" + data + u":" + str(sys.exc_info()[0]) )
        finally:
            return result

    def _tskikklist(self,data):
        result = None
        try:
            result = self.tskikklist[data]
        except Exception:
            self.message.append(u"error:line" + str(self.l) +u"elements" + str(self.e) + u":value" + data + u":" + str(sys.exc_info()[0]) )
        finally:
            return result

    def _yutCik1list(self,data):
        result = None
        try:
            result = self.yutCik1list[data]
        except Exception:
            self.message.append(u"error:line" + str(self.l) +u"elements" + str(self.e) + u":value" + data + u":" + str(sys.exc_info()[0]) )
        finally:
            return result

    def _cikCklist(self,data):
        result = None
        try:
            result = self.cikCklist[data]
        except Exception:
            self.message.append(u"error:line" + str(self.l) +u"elements" + str(self.e) + u":value" + data + u":" + str(sys.exc_info()[0]) )
        finally:
            return result

    def _tcKenrlist(self,data):
        result = None
        try:
            result = self.tcKenrlist[data]
        except Exception:
            self.message.append(u"error:line" + str(self.l) +u"elements" + str(self.e) + u":value" + data + u":" + str(sys.exc_info()[0]) )
        finally:
            return result

    def _ftiKenrlist(self,data):
        result = None
        try:
            result = self.ftiKenrlist[data]
        except Exception:
            self.message.append(u"error:line" + str(self.l) +u"elements" + str(self.e) + u":value" + data + u":" + str(sys.exc_info()[0]) )
        finally:
            return result

    def _csilist(self,data):
        result = None
        try:
            result = self.csilist[data]
        except Exception:
            self.message.append(u"error:line" + str(self.l) +u"elements" + str(self.e) + u":value" + data + u":" + str(sys.exc_info()[0]) )
        finally:
            return result

    def _knrKitilist(self,data):
        result = None
        try:
            result = self.knrKitilist[data]
        except Exception:
            self.message.append(u"error:line" + str(self.l) +u"elements" + str(self.e) + u":value" + data + u":" + str(sys.exc_info()[0]) )
        finally:
            return result

    def _knrnnJyukyulist(self,data):
        result = None
        try:
            result = self.knrnnJyukyulist[data]
        except Exception:
            self.message.append(u"error:line" + str(self.l) +u"elements" + str(self.e) + u":value" + data + u":" + str(sys.exc_info()[0]) )
        finally:
            return result

    def _stduJyukyulist(self,data):
        result = None
        try:
            result = self.stduJyukyulist[data]
        except Exception:
            self.message.append(u"error:line" + str(self.l) +u"elements" + str(self.e) + u":value" + data + u":" + str(sys.exc_info()[0]) )
        finally:
            return result

    def _stduShbt1list(self,data):
        result = None
        try:
            result = self.stduShbt1list[data]
        except Exception:
            self.message.append(u"error:line" + str(self.l) +u"elements" + str(self.e) + u":value" + data + u":" + str(sys.exc_info()[0]) )
        finally:
            return result

    def _stduHuku1list(self,data):
        result = None
        try:
            result = self.stduHuku1list[data]
        except Exception:
            self.message.append(u"error:line" + str(self.l) +u"elements" + str(self.e) + u":value" + data + u":" + str(sys.exc_info()[0]) )
        finally:
            return result

    def _mdrTyp1list(self,data):
        result = None
        try:
            result = self.mdrTyp1list[data]
        except Exception:
            self.message.append(u"error:line" + str(self.l) +u"elements" + str(self.e) + u":value" + data + u":" + str(sys.exc_info()[0]) )
        finally:
            return result

    def _stTyp11list(self,data):
        result = None
        try:
            result = self.stTyp11list[data]
        except Exception:
            self.message.append(u"error:line" + str(self.l) +u"elements" + str(self.e) + u":value" + data + u":" + str(sys.exc_info()[0]) )
        finally:
            return result

    def _chushjyuSkknGklist(self,data):
        result = None
        try:
            result = self.chushjyuSkknGklist[data]
        except Exception:
            self.message.append(u"error:line" + str(self.l) +u"elements" + str(self.e) + u":value" + data + u":" + str(sys.exc_info()[0]) )
        finally:
            return result

    def _ttmnKuzulist(self,data):
        result = None
        try:
            result = self.ttmnKuzulist[data]
        except Exception:
            self.message.append(u"error:line" + str(self.l) +u"elements" + str(self.e) + u":value" + data + u":" + str(sys.exc_info()[0]) )
        finally:
            return result

    def _ttmnKuhulist(self,data):
        result = None
        try:
            result = self.ttmnKuhulist[data]
        except Exception:
            self.message.append(u"error:line" + str(self.l) +u"elements" + str(self.e) + u":value" + data + u":" + str(sys.exc_info()[0]) )
        finally:
            return result

    def _shuhnAccs1list(self,data):
        result = None
        try:
            result = self.shuhnAccs1list[data]
        except Exception:
            self.message.append(u"error:line" + str(self.l) +u"elements" + str(self.e) + u":value" + data + u":" + str(sys.exc_info()[0]) )
        finally:
            return result

    
class MyError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)