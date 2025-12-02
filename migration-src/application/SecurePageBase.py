# -*- coding: utf-8 -*-

import os
from flask import request
from application.models.member import member
from application.messageManager import messageManager
from application.bklistutl import bklistutl
import datetime
from application import timemanager
from application.chkauth import dbsession

class SecurePageBase:
    """Base class for secure page handlers"""

    def __init__(self, request=None, response=None):
        self.request = request
        self.response = response
        self.tmpl_val = {}
        self.tmpl_val['error_msg'] = ''
        self.auth = False

    def dumpdata(self):
        t = 'dumpdata:\n'
        for e in self.tmpl_val.items():
            t += str(e[0]) + ' : ' + str(e[1]) + '\n'
        return t

    def postmsg(self, sub, body, done, kindname, mailto, bkid=None):
        if self.auth:
            mes = messageManager.post(
                self.corp_name, sub, body, done, self.userID,
                kindname, combkind=u"所有", msgkey=None,
                reservation=None, reservationend=None,
                memto=None, commentto=None, mailto=mailto, htmlmail=None
            )
            if bkid:
                bklistutl.addlistbyID(
                    self.corp_name, self.branch_name, bkid,
                    mes.id(), key=None, senddate=None,
                    sended=None, memo=None
                )
            return mes

    def Secure_init(self, *status_list, **kwargs):
        """Initialize secure page"""
        # REVIEW-L2: request オブジェクトが Flask context で利用可能であることを確認
        # 推奨: request が正しく初期化されていることを確認
        self.path = request.path
        self.pathParts = self.path.split(u'/')
        self.Domain = request.url.split(u'/')[2]

        # /test プレフィックスがある場合、インデックスを +1 調整
        # /test/follow/s-style/hon/backoffice/follow.html の場合
        # pathParts = ['', 'test', 'follow', 's-style', 'hon', 'backoffice', 'follow.html']
        #              [0]  [1]    [2]      [3]        [4]    [5]          [6]
        # 本番: /follow/s-style/hon/backoffice/follow.html
        # pathParts = ['', 'follow', 's-style', 'hon', 'backoffice', 'follow.html']
        #              [0]  [1]      [2]        [3]    [4]          [5]
        self.is_test_mode = len(self.pathParts) > 1 and self.pathParts[1] == 'test'
        offset = 1 if self.is_test_mode else 0

        self.corp_name = self.pathParts[2 + offset] if len(self.pathParts) > 2 + offset else ""
        self.branch_name = self.pathParts[3 + offset] if len(self.pathParts) > 3 + offset else ""
        self.Sitename = self.pathParts[4 + offset] if len(self.pathParts) > 4 + offset else ""

        if len(self.pathParts) > 5 + offset:
            self.filename = self.pathParts[5 + offset]
        else:
            self.filename = None

        self.tmpl_val['Domain'] = self.Domain
        self.tmpl_val["CorpOrg_key_name"] = self.corp_name
        self.tmpl_val["Branch_Key_name"] = self.branch_name
        self.tmpl_val["sitename"] = self.Sitename

        self.now = datetime.datetime.now()
        self.tmpl_val["now"] = self.now

        self.tmpl_val['userpagebase'] = request.args.get('userpagebase', 'userpagebase.html')

        # Use dbsession for authentication
        ssn = dbsession(request, self.corp_name + "_" + self.branch_name + "_" + self.Sitename)
        if not ssn.chkauth(self.corp_name, self.branch_name, self.Sitename):
            self.auth = False
            self.tmpl_val['auth'] = False
        else:
            self.auth = True
            self.tmpl_val['auth'] = True
            self.userID = ssn.get_ssn_data('memberID')
            self.userkey = ssn.get_ssn_data('userkey')

            self.tmpl_val["userID"] = self.userID
            self.tmpl_val["name"] = ssn.get_ssn_data('name')
            self.tmpl_val["status"] = ssn.get_ssn_data('status')
            self.tmpl_val["phone"] = ssn.get_ssn_data('phone')
            self.tmpl_val["mobilephone"] = ssn.get_ssn_data('mobilephone')
            self.tmpl_val["usermail"] = ssn.get_ssn_data('mail')
            self.tmpl_val["userkey"] = ssn.get_ssn_data('userkey')

        # Check status list
        if status_list and self.tmpl_val.get("status") not in status_list:
            self.tmpl_val['error_msg'] = u'必要なステータスがありません'
            self.auth = False
            return False

        if kwargs.get("memberID", None) is None:
            self.memberID = request.args.get("memberID")
        else:
            self.memberID = kwargs.get("memberID", None)

        self.memdb = None
        tankey = ""
        self.tanto = None
        if self.memberID:
            key_name = self.corp_name + "/" + self.memberID
            self.memdb = member.get_by_id(key_name)
            if self.memdb:
                if self.memdb.tanto:
                    self.tanto = self.memdb.tanto
                    tankey = str(self.tanto.key.urlsafe().decode())

                self.memdb = timemanager.utc2jst_gql(self.memdb)

                self.tmpl_val["membertel"] = self.memdb.phone
                self.tmpl_val["membermail"] = self.memdb.mail
                self.tmpl_val["memberyomi"] = self.memdb.yomi
                self.tmpl_val["membername"] = self.memdb.name

        self.tmpl_val["memdb"] = self.memdb
        self.tmpl_val["tankey"] = tankey
        self.tmpl_val["memberID"] = self.memberID

        self.tmpl_val["pagepath"] = self.path
        self.tmpl_val["applicationpagebase"] = os.path.dirname(__file__) + '/../templates/' + self.tmpl_val['CorpOrg_key_name'] + u"/" + self.tmpl_val['Branch_Key_name'] + u"/" + self.tmpl_val['sitename'] + u"/" + self.tmpl_val['userpagebase']
        self.dirpath = self.pathParts[-1].split(u'?')[0] if self.pathParts else ""
        return True

    def get(self, **kwargs):
        pass

    def post(self, **kwargs):
        self.get(**kwargs)
