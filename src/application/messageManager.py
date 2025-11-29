# -*- coding: utf-8 -*-

from models.message import Message
from models.msgcombinator import msgcombinator
from models.member import member
from google.appengine.ext import db
from datetime import datetime
import re
from application import timemanager
#from google.appengine.api import mail
import config
#from google.appengine.ext import webapp
import webapp2
import logging

from sendgrid import sendgrid
from sendgrid.helpers.mail import *


"""
Message
body = db.StringProperty(verbose_name="本文")
subject = db.StringProperty(verbose_name="表題")
kindname = db.StringProperty(verbose_name="種類")
done = db.BooleanProperty(verbose_name="済")
kill = db.BooleanProperty(verbose_name="消")
timestamp = db.DateTimeProperty(auto_now_add = True,verbose_name="タイムスタンプ")
reservation = db.DateTimeProperty(auto_now_add = True,verbose_name="予定日")
reservationend = db.DateTimeProperty(auto_now_add = True,verbose_name=u"予定終了日")
"""


class messageManager:
    @classmethod
    def _send_mail(self, sender,emailto,subject,body=None,html=None):

        """
        message = mail.EmailMessage()
        message.sender = sender
        message.to = emailto
        message.subject = subject
        if body:
            message.body = body
        if html:
            message.html = html
        message.send()
        


        鵜飼　浩司様
        
        
        
        SendGridにようこそ！
        
        
        
        それでは、さっそくマイページにログインしてみましょう。
        
        https://sendgrid.kke.co.jp/app?p=login.index
        
        
        
        ---------------------------------------------------------------
        アカウント　s-style_407@s-style-hrd.appspotmail.com
        
        お客様のユーザ名：sgj419vb@kke.com
        
        パスワード　　　：pwd@0felixthecat
        
        APIkey           :[SENDGRID_API_KEY - Set in environment variables]
        
        ---------------------------------------------------------------
        
        ※Google Chrome または Firefox をご利用ください（Internet Explorer非対応）
        
        
        
        
        
        マイページのメニューから、ご利用プランの変更やパスワードの変更等ができます。
        
        メール送信状況の確認、メール送信に関する各種設定、宛先リストの管理等は、
        
        ダッシュボードから行なってください（マイページからアクセスできます）。
        
        
        
        
        
        以下も併せてご覧ください。
        
        
        
        ・チュートリアル
        
        https://sendgrid.kke.co.jp/docs/Tutorials/index.html
        
        まずはメールを送ってみたいという方は、こちらをご覧ください。
        
        他にもよく使われる設定手順や運用方法などを目的別にご紹介しています。
        
        
        
        ・利用規約に関するご注意
        
        https://support.sendgrid.kke.co.jp/hc/ja/articles/205590193
        
        SendGridでは、アカウントの譲渡・二次ライセンスが禁止されております。
        
        当てはまる項目がないか、必ずご確認ください。
        
        
        
        ・その他FAQ
        
        大量のメールを一斉配信する前に
        
        https://support.sendgrid.kke.co.jp/hc/ja/articles/206431885
        
        プラン変更方法 
        
        https://support.sendgrid.kke.co.jp/hc/ja/articles/203430615
        
        
        
        
        
        ご不明な点がございましたら、サポートページよりお問合せください。
        
        https://sendgrid.kke.co.jp/app?p=support.index
        
        
        
        
        
        ■お問合せ
        
        株式会社 構造計画研究所 SendGridサポートチーム
        
        https://sendgrid.kke.co.jp/
        
        
        From: SendGridサポートチーム &lt;support-sendgrid@kke.co.jp&gt;
        To: s-style_407@s-style-hrd.appspotmail.com &lt;s-style_407@s-style-hrd.appspotmail.com&gt;
        with 担当にメール送信


        古いやりかた
        from sendgrid import Sendgrid
        from sendgrid import Message
        # make a secure connection to SendGrid
        s = sendgrid.Sendgrid(”, ”, secure=True)
        # make a message object
        message = sendgrid.Message(“from@mydomain.com”, “message subject”, “plaintext message body”, “<strong>HTML message body</strong>”)
        # add a recipient
        message.add_to(“someone@example.com”, “John Doe”)
        # use the Web API to send your message
        s.web.send(message)

        """
        try:
            import os
            sg = sendgrid.SendGridAPIClient(apikey=os.environ.get('SENDGRID_API_KEY'))
            from_email = Email(sender)
            to_email = Email(emailto)
            if body:
                content = Content("text/plain", body)
            if html:
                content = Content("text/html", html)
    
            mail = Mail(from_email, subject, to_email, content)
            response = sg.client.mail.send.post(request_body=mail.get())
            logging.warning('送信しました')
        except:
            logging.error('送信失敗しました 失敗した送信先>>' + emailto)

    @classmethod
    def post(cls,corp,sub,body,done,memfrom,kindname,combkind=u"所有",msgkey=None,reservation=None,reservationend=None,memto=None,commentto=None,mailto=None,htmlmail=None):
        Flg = False
        memdb = None
        if not memfrom and not msgkey:
            return
        if memfrom:
            key_name = corp + "/" + memfrom
            memdb = member.get_by_key_name(key_name)
            if memdb:
                if memdb.isrequest(kindname):
                    memdb.LastRequestdatetimeset()
        if msgkey:
            msg = cls.getmesbyID(corp,msgkey)
        else:
            msg = Message()
            Flg = True
        if corp:
            msg.corp = corp
        if body:
            body2 = body
            if mailto=="tanto":
                body2 += "\n" + u"with 担当にメール送信"
            elif mailto=="member":
                body2 += "\n" + u"with メール送信"
            elif mailto=="each":
                body2 += "\n" + u"with メール送信 担当にもメール送信"
            msg.body = body2
        if sub:
            msg.subject = sub
        if kindname:
            msg.kindname = kindname
        if done == True or done == "true" or done == "True":
            msg.done = True
        else:
            msg.done = False
        if reservation:
            r = re.compile(".*:.*:.*").match(reservation, 1)
            if r == None:
                rtime = datetime.strptime(reservation, "%Y/%m/%d")
            else:
                rtime = datetime.strptime(reservation, "%Y/%m/%d %H:%M:%S")
            msg.reservation = timemanager.jst2utc_date(rtime)

        if reservationend:
            r = re.compile(".*:.*:.*").match(reservationend, 1)
            if r == None:
                rtime = datetime.strptime(reservationend, "%Y/%m/%d")
            else:
                rtime = datetime.strptime(reservationend, "%Y/%m/%d %H:%M:%S")
            msg.reservationend = timemanager.jst2utc_date(rtime)
        if commentto:
            msg.commentTo = commentto
            if not kindname:
                msg.kindname = u"コメント"
        msgkey = msg.put()

        if combkind == "":
            combkind=u"所有"
        res = None

        if msgkey and Flg:
            res = cls.combination(msgkey, corp, memdb, combkind)
            if not memto and memdb.tanto:
                res = cls.combination(msgkey, corp, memdb.tanto, u"参照")
        if memto and Flg:
            key_name = corp + "/" + memfrom
            memdbto = member.get_by_key_name(key_name)
            res = cls.combination(msgkey, corp,memdbto, u"送信")
        if mailto: #tanto member
            if mailto == "tanto" or mailto == "each":
                if memdb and memdb.tanto and memdb.tanto.mail: #左から評価されるらしい
                    sender = "sender" + config.ADMIN_EMAIL_BASE
                    if htmlmail:
                        cls._send_mail(sender, memdb.tanto.mail, subject = sub, html = body)
                    else:
                        mailbody = u""
                        if memdb.name:
                            mailbody += u"お客様：" + memdb.name + "　"
                        if memdb.yomi:
                            mailbody += memdb.yomi
                        if mailbody != u"":
                            mailbody += u"\n"
                        if memdb.address:
                            mailbody += u"住所：" + memdb.address + u"\n"
                        if memdb.phone:
                            mailbody += u"tel：" + memdb.phone + u"\n"
                        if memdb.mail:
                            mailbody += u"mail：" + memdb.mail + u"\n"
                        mailbody += body
                        cls._send_mail(sender, memdb.tanto.mail, subject = sub, body = mailbody)
                else:
                    msg.body += u"NG アドレス不明"
                    msg.put()
            elif mailto == "member" or mailto == "each":
                key_name = corp + "/" + memfrom
                memdb = member.get_by_key_name(key_name)
                if memdb and memdb.tanto and memdb.tanto.memberID: #左から評価されるらしい:
                    sender = '"' + memdb.tanto.name  + '" <' + corp + '_' + memdb.memberID + config.ADMIN_EMAIL_BASE + '>'
                    if htmlmail:
                        cls._send_mail(sender, memdb.mail, subject = sub, html = body)
                    else:
                        cls._send_mail(sender, memdb.mail, subject = sub, body = body)
                else:
                    msg.body += u"NG　 アドレス不明"
                    msg.put()
        return msgkey

    @classmethod
    def combination(cls,msgkey,corp,memdb,combkind):
        #msg = Message.get(msgkey)
        if memdb:
            comb = msgcombinator()
            comb.refmes = msgkey
            comb.refmem = memdb.key()
            comb.combkind = combkind
            comb.put()
            return True
        else:
            return False

    @classmethod
    def killmesbyID(cls,corp,ID):
        msg = cls.getmesbyID(corp,ID)
        msg.kill = True
        msg.put()

    @classmethod
    def killmes(cls,corp,key):
        msg = cls.getmesbyID(corp,key)
        msg.kill = True
        msg.put()

    @classmethod
    def getmeslistbyID(cls,corp,memberID,subject=None,kindname=None,done=None,kill=None,reservationLower=None,reservationUpper=None,order=None,combkind=None):
        mem = member.get_by_key_name(corp + "/" + memberID)
        if mem:
            return cls.getmeslist(corp,mem,subject,kindname,done,kill,reservationLower,reservationUpper,order,combkind)
        return []

    @classmethod
    def getmeslist(cls,corp,member,subject=None,kindname=None,done=None,kill=None,reservationLower=None,reservationUpper=None,order=None,combkind=None):
        if member.CorpOrg_key_name != corp:
            raise messageManagerError("BadIDError: Invalid ID　" + id)
        comblist = member.refmeslist
        if combkind:
            comblist.filter("combkind = ",combkind)
        res = []
        con = 0
        for comb in comblist:
            #https://blog.livedoor.jp/abars/archives/52045594.html
            #class MesThread(db.Model):
            #    bbs = db.ReferenceProperty(Bbs)
            #    MesThread.bbs_key.get_value_for_datastore(thread)
            try:
                sub = comb.refmes.subject
            except:
                logging.error("comb.refmes.subject ERROR 削除されました :: " + str(comb.key().id()))
                comb.delete()
                """
                2018/04/20 comb.delete()がシステムエラーを引き起こすのでコメントアウト
                """
                continue
            if subject:
                if comb.refmes.subject!=subject:
                    continue
            if kindname:
                if comb.refmes.kindname!=kindname:
                    continue
            if done != None:
                if comb.refmes.done!=done:
                    continue
            if kill == False :
                if comb.refmes:
                    if kill != comb.refmes.kill:
                        continue
            if reservationLower:
                rt = timemanager.jst2utc_date(reservationLower).replace(tzinfo=None)
                if comb.refmes.reservation < rt:
                    continue
            if reservationUpper:
                rt = timemanager.jst2utc_date(reservationUpper).replace(tzinfo=None)
                if comb.refmes.reservation >= rt:
                    continue
            res.append(comb.refmes)
        if order:
            if order == "reservation":
                res.sort(key=lambda obj: obj.reservation)
            if order == "-reservation":
                res.sort(key=lambda obj: obj.reservation)
                res.reverse()
        return res

    #メッセージを参照しているメンバーのcombinaterを集める
    @classmethod
    def getmemlist(cls,message,combkind=None):
        comblist = message.refmemlist
        if combkind:
            comblist.filter("combkind = ",combkind)
        return comblist
        """
        res = []
        for comb in comblist:
            if combkind:
                if comb.combkind!=combkind:
                    continue
            res.append(comb.refmes)
        return res
        """


    @classmethod
    def getmesbyID(cls,corp,id):
        mes = Message.get_by_id(int(id))
        if mes:
            cls.chkmes(corp,id, mes)
        return mes

    @classmethod
    def getmesbykey(cls,corp,key):
        mes = Message.get(key)
        if mes:
            cls.chkmes( corp,str(key), mes)
        return mes

    @classmethod
    def getmembymesID(cls,id):
        mes = Message.get_by_id(int(id))
        comblist = cls.getmemlist(mes)
        mems = []
        for comb in comblist:
            mems = comb.refmem
        return mems


    @classmethod
    def chkmes(cls,corp,id,message):
        comblist = message.refmemlist
        for comb in comblist:
            if comb.refmem.CorpOrg_key_name != corp:
                raise messageManagerError("BadIDError: Invalid ID　" + id)

class messageManagerError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

#https://localhost:8080/tasks/changetantoWorker?corp_name=s-style&tantoID=3&oldtantoID=1
class changetantoWorker(webapp2.RequestHandler):
    def get(self,**kwargs):
        self.post()
    def post(self,**kwargs):
        self.tmpl_val = {}
        corp = self.request.get("corp_name")
        tantoID = self.request.get("tantoID")
        oldtantoID =  self.request.get("oldtantoID")
        tanto = member.get_by_key_name(corp+'/'+tantoID)
        oldtanto = member.get_by_key_name(corp+'/'+oldtantoID)
        if tanto and oldtanto :
            tantomem =oldtanto.mytanto
            for mem in tantomem:
                mem.tanto=tanto
                mem.put() #putによってchangetantotaskが起動され担当の参照メッセージが変更されるので個別に変更する必要なし

#https://localhost:8080/tasks/changetantotask?corp_name=s-style&memberID=2&tantoID=3&oldtantoID=1
class changetantotask(webapp2.RequestHandler):
    def get(self,**kwargs):
        self.post()
    def post(self,**kwargs):
        self.tmpl_val = {}
        corp = self.request.get("corp_name")
        memberID = self.request.get("memberID")
        tantoID = self.request.get("tantoID")
        oldtantoID =  self.request.get("oldtantoID")
        mlist = messageManager.getmeslistbyID(corp,memberID)
        tanto = member.get_by_key_name(corp+'/'+tantoID)
        oldtanto = member.get_by_key_name(corp+'/'+oldtantoID)
        if tanto and oldtanto:
            for mes in mlist:
                comblist = messageManager.getmemlist(mes,combkind=u"参照")
                for comb in comblist:
                    if comb.refmem.key() == oldtanto.key():
                        comb.refmem = tanto
                        comb.put()

