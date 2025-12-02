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
