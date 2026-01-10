#!/usr/local/bin/python
# -*- coding: utf-8 -*-

from flask import request, render_template_string
from google.cloud import ndb, tasks_v2
import smtplib
from email.message import EmailMessage
import os
import sys
from application import config
from application import messageManager
from application.models.message import Message
from application.models.member import member
from application.SecurePage import SecurePage
from application.wordstocker import wordstocker
from application.bklistutl import bklistutl
from application.GqlEncoder import GqlJsonEncoder
from application import timemanager
import datetime
import re
from application.mailvalidation import mailvalidation

BASE_URL = config.BASE_URL
ADMIN_EMAIL = config.ADMIN_EMAIL
ADMIN_SYSTEM_ID = config.TANTOID

class memberSearchandMailbase(SecurePage):
    corp_name = ""
    branch_name = ""

    def get(self, **kwargs):
        return self.post(**kwargs)

    def memberSearchandMailbase_init(self):
        if not self.corp_name:
            self.corp_name = request.args.get("corp_name")
        if not self.branch_name:
            self.branch_name = request.args.get("branch_name")

        self.bkID = request.values.get("bkID", "")
        self.tmpl_val["bkID"] = self.bkID
        self.followsubject = request.values.get("followsubject", "")
        self.tmpl_val["followsubject"] = self.followsubject
        self.rireki = request.values.get("rireki", "")
        if self.rireki:
            self.rireki = int(self.rireki)
        self.tmpl_val["rireki"] = self.rireki
        self.service = request.values.get("service", "")
        self.tmpl_val["service"] = self.service
        self.status = request.values.get("status", "")
        self.tmpl_val["status"] = self.status
        self.seiyaku = request.values.get("seiyaku", "")
        self.tmpl_val["seiyaku"] = self.seiyaku
        self.tmpl_val["tourokunengappiL"] = request.values.get("tourokunengappiL", "")
        self.tourokunengappiL = self.gettime(request.values.get("tourokunengappiL", ""))
        self.tmpl_val["tourokunengappiU"] = request.values.get("tourokunengappiU", "")
        self.tourokunengappiU = self.gettime(request.values.get("tourokunengappiU", ""), 1)
        self.filter = request.values.get("filter", "")
        self.tmpl_val["filter"] = self.filter
        self.filtervalue = request.values.get("filtervalue", "")
        self.tmpl_val["filtervalue"] = self.filtervalue
        self.htmlmail = request.values.get("htmlmail", "")
        self.tmpl_val["htmlmail"] = self.htmlmail

        self.msgkey = request.values.get("msgkey", "")
        self.memsitename = request.values.get("memsitename", "")
        self.submit = request.values.get("com", "")
        self.msg = request.values.get("msg", "")
        if self.msg:
            self.msg = int(self.msg)
        self.tmpl_val['msg'] = self.msg
        self.tmpl_val['subject'] = request.values.get("subject", "")
        self.tmpl_val['body'] = request.values.get("body", "")
        self.msID = request.values.get("msID", "")
        self.tmpl_val['msID'] = self.msID
        self.mailbody = ""
        self.media = request.values.get("media", "web")
        self.tmpl_val["media"] = self.media

    def gettime(self, timestr, add=None):
        res = None
        if timestr:
            if re.compile(r".*/.*/.* .*:.*:.*").match(timestr):
                res = timemanager.jst2utc_date(
                    datetime.datetime.strptime(timestr, "%Y/%m/%d %H:%M:%S")
                )
            elif re.compile(r".*/.*/.*").match(timestr):
                res = timemanager.jst2utc_date(
                    datetime.datetime.strptime(timestr, "%Y/%m/%d")
                )
            elif re.compile(r".*/.*").match(timestr):
                res = timemanager.jst2utc_date(
                    datetime.datetime.strptime(timestr, "%Y/%m")
                )
            if add and res:
                res += datetime.timedelta(days=add)
        return res

    def makedata(self, bkd, media):
        """Format property data for display"""
        entitys = bkd.makedata(media)
        return entitys

    def makebody(self, site, msID, media, tmpl_val, filename='bklistml.html'):
        entitys = {}
        entitys["media"] = media
        if msID:
            bkdb = bklistutl.getlistbyID(self.corp_name, msID)
            bklist = bkdb.fetch(1000, 0)
            list = []
            for bkl in bklist:
                list.append(self.makedata(bkl.refbk, media))
            entitys["bkdatalist"] = list
            entitys["bkdataurl"] = BASE_URL + u"/show/" + self.corp_name + u"/" + self.branch_name + u"/" + site + u"/bkdata/article.html?media=" + media + u"&id="
            entitys["listKey"] = msID
            tmpl_val["data"] = entitys

        templ = os.path.join(os.getcwd(), 'templates', self.corp_name, self.branch_name, site, filename)
        temp2 = os.path.join(os.getcwd(), 'templates', self.corp_name, self.branch_name, filename)
        if os.path.isfile(templ):
            path = templ
        elif os.path.isfile(temp2):
            path = temp2
        else:
            path = os.path.join(os.getcwd(), 'templates', 'bklistml.html')

        try:
            with open(path, 'r', encoding='utf-8') as f:
                return render_template_string(f.read(), **tmpl_val)
        except FileNotFoundError:
            return ""

class memberSearchandMail(memberSearchandMailbase):
    def get(self, **kwargs):
        return self.post(**kwargs)

    def post(self, **kwargs):
        # REVIEW-L2: Secure_init() の引数形式確認
        # 推奨: Secure_init(*status_list) の形式に合わせる
        if self.Secure_init(u"管理者", u"担当"):
            self.memberSearchandMailbase_init()
            if self.submit == u"プレビュー":
                if self.htmlmail == "1":
                    self.tmpl_val["htmlmail"] = self.htmlmail
                    self.mailbody = self.makebody(self.Sitename, self.msID, self.media, self.tmpl_val)
                else:
                    self.mailbody = self.tmpl_val['body']
                self.tmpl_val['preview'] = self.mailbody

            if self.submit == u"メール送信" or self.submit == u"リスト保存" or self.submit == u"メール保存":
                if not self.tmpl_val['subject'] and (self.submit == u"メール送信" or self.submit == u"メール保存"):
                    self.tmpl_val['error_msg'] += u"表題がありません　　"
                if not self.tmpl_val['body'] and (self.submit == u"メール送信" or self.submit == u"メール保存"):
                    self.tmpl_val['error_msg'] += u"本文がありません　"

                if self.tmpl_val['error_msg'] == "" and self.submit == u"メール保存":
                    msgkey = messageManager.messageManager.post(
                        corp=self.corp_name,
                        sub=self.tmpl_val['subject'],
                        body=self.tmpl_val['body'],
                        done=False,
                        memfrom=ADMIN_SYSTEM_ID,
                        kindname=u"保存したメール",
                        combkind=u"所有",
                        msgkey=self.msg
                    )

                elif (self.tmpl_val['error_msg'] == "" and self.submit == u"メール送信") or self.submit == u"リスト保存":
                    if self.submit == u"メール送信":
                        msgkey = messageManager.messageManager.post(
                            corp=self.corp_name,
                            sub=self.tmpl_val['subject'],
                            body=self.tmpl_val['body'],
                            done=True,
                            memfrom=ADMIN_SYSTEM_ID,
                            kindname=u"送信したメール",
                            combkind=u"所有",
                            msgkey=self.msg
                        )
                    elif self.submit == u"リスト保存":
                        msgkey = messageManager.messageManager.post(
                            corp=self.corp_name,
                            sub=self.tmpl_val['subject'],
                            body=self.tmpl_val['body'],
                            done=False,
                            memfrom=ADMIN_SYSTEM_ID,
                            kindname=u"保存したリスト",
                            combkind=u"所有",
                            msgkey=self.msg
                        )

                    if msgkey:
                        # Use Cloud Tasks instead of Task Queue
                        self.create_cloud_task(
                            '/tasks/mailinglistsend',
                            {
                                "corp_name": self.corp_name,
                                "branch_name": self.branch_name,
                                "bkID": self.bkID,
                                "followsubject": self.followsubject,
                                "rireki": str(self.rireki),
                                "service": self.service,
                                "status": self.status,
                                "seiyaku": self.seiyaku,
                                "tourokunengappiL": self.tmpl_val["tourokunengappiL"],
                                "tourokunengappiU": self.tmpl_val["tourokunengappiU"],
                                "filter": self.filter,
                                "filtervalue": self.filtervalue,
                                "htmlmail": self.htmlmail,
                                "com": self.submit,
                                "msg": self.msg,
                                "subject": self.tmpl_val['subject'],
                                "body": self.tmpl_val['body'],
                                "msID": self.msID,
                                "media": self.media,
                                "msgkey": str(msgkey),
                                "memsitename": self.memsitename
                            }
                        )
                else:
                    self.tmpl_val['error_msg'] += u"\nキャンセルされました"

            msglist = messageManager.messageManager.getmeslistbyID(
                corp=self.corp_name,
                memberID=ADMIN_SYSTEM_ID,
                order='-reservation',
                combkind=u'所有'
            )
            self.tmpl_val['msglist'] = msglist
            self.tmpl_val['servicelist'] = wordstocker.get(self.corp_name, u"サービス")
            path = 'templates/memberSearchandMail.html'
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    return render_template_string(f.read(), **self.tmpl_val)
            except FileNotFoundError:
                return f"Template not found: {path}", 404

    def create_cloud_task(self, url, params):
        """Create a Cloud Tasks task"""
        try:
            project = config.PROJECT_ID
            queue = config.TASK_QUEUE
            location = config.TASK_LOCATION

            client = tasks_v2.CloudTasksClient()
            parent = client.queue_path(project, location, queue)

            task = {
                'http_request': {
                    'http_method': tasks_v2.HttpMethod.POST,
                    'url': BASE_URL + url,
                    'headers': {'Content-Type': 'application/x-www-form-urlencoded'},
                }
            }

            # Add parameters as body
            import urllib.parse
            task['http_request']['body'] = urllib.parse.urlencode(params).encode()

            response = client.create_task(request={'parent': parent, 'task': task})
        except Exception as e:
            print(f"Error creating cloud task: {e}")


class mailsendback(memberSearchandMailbase):
    """メール送信バックエンドタスク"""

    def get(self, **kwargs):
        return self.post(**kwargs)

    def post(self, **kwargs):
        self.memberSearchandMailbase_init()
        memberID = request.values.get("memberID", "")
        mailbody = ""

        if self.submit == u"メール送信":
            if self.htmlmail == "1":
                htmlml = True
                try:
                    mailbody = self.makebody(self.memsitename, self.msID, self.media, self.tmpl_val)
                except IOError:
                    mailbody = u'適切なテンプレートファイルが存在しません。顧客データのサイト名等をチェックしてください。'
                    self.tmpl_val['subject'] += u'送信時エラー 　テンプレートエラー'
                    msgkey2 = messageManager.messageManager.post(
                        corp=self.corp_name, sub=self.tmpl_val['subject'], body=mailbody,
                        done=False, memfrom=memberID, kindname=u"顧客リストエラー",
                        combkind=u"所有", msgkey=None,
                        commentto=self._get_message(self.msgkey), mailto=None
                    )
                    return "Template error", 400
                except Exception as e:
                    mailbody = u"未確認のエラーが発生したため送信できませんでした\n%s" % str(e)
                    self.tmpl_val['subject'] += u'送信時エラー　未確認システムエラー'
                    msgkey2 = messageManager.messageManager.post(
                        corp=self.corp_name, sub=self.tmpl_val['subject'], body=mailbody,
                        done=False, memfrom=memberID, kindname=u"顧客リストエラー",
                        combkind=u"所有", msgkey=None,
                        commentto=self._get_message(self.msgkey), mailto=None
                    )
                    return "System error", 500
            else:
                htmlml = False
                try:
                    mailbody = self.makebody(self.memsitename, self.msID, self.media, self.tmpl_val, 'bklistml.txt')
                except IOError:
                    mailbody = u'適切なテンプレートファイルが存在しません。顧客データのサイト名等をチェックしてください。'
                    self.tmpl_val['subject'] += u'送信時エラー 　テンプレートエラー'
                    msgkey2 = messageManager.messageManager.post(
                        corp=self.corp_name, sub=self.tmpl_val['subject'], body=mailbody,
                        done=False, memfrom=memberID, kindname=u"顧客リストエラー",
                        combkind=u"所有", msgkey=None,
                        commentto=self._get_message(self.msgkey), mailto=None
                    )
                    return "Template error", 400
                except Exception as e:
                    mailbody = u"未確認のエラーが発生したため送信できませんでした\n%s" % str(e)
                    self.tmpl_val['subject'] += u'送信時エラー　未確認システムエラー'
                    msgkey2 = messageManager.messageManager.post(
                        corp=self.corp_name, sub=self.tmpl_val['subject'], body=mailbody,
                        done=False, memfrom=memberID, kindname=u"顧客リストエラー",
                        combkind=u"所有", msgkey=None,
                        commentto=self._get_message(self.msgkey), mailto=None
                    )
                    return "System error", 500

            msgkey2 = messageManager.messageManager.post(
                corp=self.corp_name, sub=self.tmpl_val['subject'], body=mailbody,
                done=True, memfrom=memberID, kindname=u"メーリングリスト",
                combkind=u"所有", msgkey=None,
                commentto=self._get_message(self.msgkey), mailto="member", htmlmail=htmlml
            )
        elif self.submit == u"リスト保存":
            msgkey2 = messageManager.messageManager.post(
                corp=self.corp_name, sub=self.tmpl_val['subject'], body=mailbody,
                done=False, memfrom=memberID, kindname=u"顧客リスト",
                combkind=u"所有", msgkey=None,
                commentto=self._get_message(self.msgkey), mailto=None
            )

        return "OK", 200

    def _get_message(self, msgkey):
        """メッセージキーからMessageオブジェクトを取得"""
        if not msgkey:
            return None
        try:
            return ndb.Key(Message, int(msgkey)).get()
        except:
            return None


class memberSearchandMailback(memberSearchandMailbase):
    """メンバー検索バックエンドタスク"""

    def get(self, **kwargs):
        return self.post(**kwargs)

    def post(self, **kwargs):
        try:
            rep = ''
            self.memberSearchandMailbase_init()
            self.tmpl_val['msgkey'] = str(self.msgkey)
            memlist = []

            # followsubject でメッセージ検索
            if self.followsubject:
                meslist = Message.query(
                    Message.subject >= self.followsubject,
                    Message.subject < self.followsubject + u"\uFFFD",
                    Message.corp == self.corp_name,
                    Message.kill == False
                )
                for mes in meslist:
                    comblist = mes.refmemlist
                    for e in comblist:
                        if e.combkind == u"所有":
                            e2 = e.refmem.key
                            if e2 not in memlist:
                                memlist.append(e2)

            # bkID で物件検索
            if self.bkID:
                meslist = bklistutl.getmeslistbybkID(self.corp_name, self.branch_name, self.bkID)
                if len(memlist):
                    reslist = []
                    for mes in meslist:
                        m = messageManager.messageManager.getmemlist(mes, u"所有")
                        for e in m:
                            e2 = e.refmem.key
                            if e2 in memlist:
                                if e2 not in reslist:
                                    reslist.append(e2)
                    memlist = reslist
                else:
                    for mes in meslist:
                        m = messageManager.messageManager.getmemlist(mes, u"所有")
                        for e in m:
                            e2 = e.refmem.key
                            if e2 not in memlist:
                                memlist.append(e2)

            # rireki で履歴検索
            if self.rireki:
                mes = messageManager.messageManager.getmesbyID(self.corp_name, self.rireki)
                if mes:
                    meslist = mes.refmes
                    if len(memlist):
                        reslist = []
                        for mes in meslist:
                            m = messageManager.messageManager.getmemlist(mes, u"所有")
                            for e in m:
                                e2 = e.refmem.key
                                if e2 in memlist:
                                    if e2 not in reslist:
                                        reslist.append(e2)
                        memlist = reslist
                    else:
                        for mes in meslist:
                            m = messageManager.messageManager.getmemlist(mes, u"所有")
                            for e in m:
                                e2 = e.refmem.key
                                if e2 not in memlist:
                                    memlist.append(e2)

            # フィルター条件でメンバー検索
            if (self.service or self.status or self.seiyaku or
                self.tourokunengappiL or self.tourokunengappiU or
                (self.filter and self.filtervalue)):
                query = member.query(member.CorpOrg_key_name == self.corp_name)
                if self.service:
                    query = query.filter(member.service == self.service)
                if self.status:
                    query = query.filter(member.status == self.status)
                if self.seiyaku:
                    query = query.filter(member.seiyaku == self.seiyaku)
                if self.tourokunengappiL:
                    query = query.filter(member.tourokunengappi >= self.tourokunengappiL)
                if self.tourokunengappiU:
                    query = query.filter(member.tourokunengappi <= self.tourokunengappiU)
                if self.filter and self.filtervalue:
                    filtervalue1 = self._parse_filter_value(self.filtervalue)
                    # 動的フィルターは NDB では直接サポートされないため、後処理が必要

                if len(memlist):
                    reslist = []
                    for e in query.iter(keys_only=True):
                        if e in memlist:
                            if e not in reslist:
                                reslist.append(e)
                    memlist = reslist
                else:
                    for e in query.iter(keys_only=True):
                        if e not in memlist:
                            memlist.append(e)

            # キーからメンバーオブジェクトを取得
            memlist = ndb.get_multi(memlist)
            memlist = [m for m in memlist if m is not None]

            if self.submit == u"メール送信" or self.submit == u"リスト保存":
                mv = mailvalidation()
                for mem in memlist:
                    if mem.tanto:
                        if mem.mail:
                            if not mv.chk(mem.mail):
                                msgkey2 = messageManager.messageManager.post(
                                    corp=self.corp_name, sub=u"メールアドレスチェック",
                                    body=u"パターンがマッチしない警告を受けました。このユーザーのメールアドレスをチェックしてください。",
                                    done=False, memfrom=mem.memberID, kindname=u"アドレスチェック",
                                    combkind=u"所有", msgkey=None,
                                    commentto=self._get_message(self.msgkey), mailto=None
                                )
                                rep += u"アドレス不正チェック:" + mem.memberID + " :" + mem.mail + u"\n"

                            # Cloud Tasks でメール送信タスクを作成
                            self.create_cloud_task(
                                '/tasks/mailsendback',
                                {
                                    "corp_name": self.corp_name,
                                    "branch_name": self.branch_name,
                                    "bkID": self.bkID,
                                    "followsubject": self.followsubject,
                                    "rireki": str(self.rireki) if self.rireki else "",
                                    "service": self.service,
                                    "status": self.status,
                                    "seiyaku": self.seiyaku,
                                    "tourokunengappiL": self.tmpl_val["tourokunengappiL"],
                                    "tourokunengappiU": self.tmpl_val["tourokunengappiU"],
                                    "filter": self.filter,
                                    "filtervalue": self.filtervalue,
                                    "htmlmail": self.htmlmail,
                                    "com": self.submit,
                                    "msg": str(self.msg) if self.msg else "",
                                    "subject": self.tmpl_val['subject'],
                                    "body": self.tmpl_val['body'],
                                    "msID": self.msID,
                                    "media": self.media,
                                    "msgkey": str(self.msgkey),
                                    "memberID": mem.memberID,
                                    "memsitename": mem.sitename or ""
                                }
                            )
                        else:
                            rep += u"アドレス未設定チェック:" + mem.memberID + u"\n"
                    else:
                        rep += u"担当未設定チェック:" + mem.memberID + u"\n"

                if rep:
                    msgkey = messageManager.messageManager.post(
                        corp=self.corp_name, sub=u"メールアドレスチェック結果", body=rep,
                        done=False, memfrom=ADMIN_SYSTEM_ID, kindname=u"メールアドレスチェック",
                        combkind=u"所有", msgkey=None, mailto=None
                    )

            if self.submit == u"はがき" or self.submit == u"タックシール":
                self.tmpl_val["memlist"] = memlist
                if self.submit == u"はがき":
                    path = 'templates/HAGAKI.html'
                elif self.submit == u"タックシール":
                    path = 'templates/ATENA.html'
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        return render_template_string(f.read(), **self.tmpl_val)
                except FileNotFoundError:
                    return f"Template not found: {path}", 404

            return "OK", 200

        except Exception as e:
            import traceback
            mailbody = u"エラーが発生したため一部のメールが送信できませんでした\n%s\nその他のエラー\n%s" % (str(e), rep)
            sub = u'タスクキューエラー　未確認システムエラー'
            msgkey2 = messageManager.messageManager.post(
                corp=self.corp_name, sub=sub, body=mailbody,
                done=False, memfrom=ADMIN_SYSTEM_ID, kindname=u"顧客リストエラー",
                combkind=u"所有", msgkey=None, mailto=None
            )
            raise

    def _get_message(self, msgkey):
        """メッセージキーからMessageオブジェクトを取得"""
        if not msgkey:
            return None
        try:
            return ndb.Key(Message, int(msgkey)).get()
        except:
            return None

    def _parse_filter_value(self, filtervalue):
        """フィルター値をパース"""
        if filtervalue == "true":
            return True
        elif filtervalue == "false":
            return False
        elif filtervalue == "none":
            return None
        elif filtervalue.isdigit():
            return float(filtervalue)
        elif self.gettime(filtervalue):
            return self.gettime(filtervalue)
        return filtervalue

    def create_cloud_task(self, url, params):
        """Create a Cloud Tasks task"""
        try:
            project = config.PROJECT_ID
            queue = config.TASK_QUEUE
            location = config.TASK_LOCATION

            client = tasks_v2.CloudTasksClient()
            parent = client.queue_path(project, location, queue)

            task = {
                'http_request': {
                    'http_method': tasks_v2.HttpMethod.POST,
                    'url': BASE_URL + url,
                    'headers': {'Content-Type': 'application/x-www-form-urlencoded'},
                }
            }

            import urllib.parse
            task['http_request']['body'] = urllib.parse.urlencode(params).encode()

            response = client.create_task(request={'parent': parent, 'task': task})
        except Exception as e:
            print(f"Error creating cloud task: {e}")
