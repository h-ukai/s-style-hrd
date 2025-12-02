# -*- coding: utf-8 -*-

# Copyright 2008 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Utility classes and methods for use with json and appengine.

Provides both a specialized json encoder, GqlEncoder, designed to simplify
encoding directly from GQL results to JSON. A helper function, encode, is also
provided to further simplify usage.

  GqlEncoder: Adds support for GQL results and properties to json.
  encode(input): Direct method to encode GQL objects as JSON.

このページから呼び出されるデータは基本的にFloatが整形される ***,***,***.*****ので注意

"""

from flask import render_template, request, Response
from application import timemanager
import re
from google.cloud import ndb
import datetime
import sys
import traceback
from email.message import EmailMessage
import smtplib
import urllib.parse
import logging
import json

"""
GQLから検索するmodelkindはすべてインポートすること
"""
from application.models.bkdata import BKdata
from application.models.bksearchaddress import bksearchaddresslist
from application.models.member import member
from application.models.message import Message
from application.models.address import address1
from application.models.address import address2
from application.models.address import address3
from application.models.ziplist import ziplist
from application.models.blob import Blob
from application.models.station import Station

from application.models.bksearchaddress import getname
from copy import deepcopy
import application.messageManager
from application.GqlEncoder import GqlJsonEncoder
from application.bklistutl import bklistutl
import calendar
from calendar import monthrange
from application.qreki import Kyureki
import application.config as config
from dataProvider.bkdataSearchProvider import bkdataSearchProbider


class JsonServiceHandler:
    """JSON service handler for Flask"""

    def __init__(self):
        # REVIEW-L3: Python 3では全ての文字列がUnicode。u"プレフィックス"は不要だが、互換性のために残す
        self.code = {"北海道": "01", "青森県": "02", "岩手県": "03", "宮城県": "04", "秋田県": "05",
                    "山形県": "06", "福島県": "07", "茨城県": "08", "栃木県": "09", "群馬県": "10",
                    "埼玉県": "11", "千葉県": "12", "東京都": "13", "神奈川県": "14", "新潟県": "15",
                    "富山県": "16", "石川県": "17", "福井県": "18", "山梨県": "19", "長野県": "20",
                    "岐阜県": "21", "愛知県": "23", "三重県": "24", "滋賀県": "25", "京都府": "26",
                    "大阪府": "27", "兵庫県": "28", "奈良県": "29", "和歌山県": "30", "鳥取県": "31",
                    "島根県": "32", "岡山県": "33", "広島県": "34", "山口県": "35", "徳島県": "36",
                    "香川県": "37", "愛媛県": "38", "高知県": "39", "福岡県": "40", "佐賀県": "41",
                    "長崎県": "42", "熊本県": "43", "大分県": "44", "宮崎県": "45", "鹿児島県": "46",
                    "沖縄県": "47"}

    def gettime(self, timestr, add=None):
        # REVIEW-L1: re.compile().match()の第2引数削除（Python 3では不要）
        # 修正前: re.compile(".*/.*/.* .*:.*:.*").match(timestr, 1)
        # 修正後: re.compile(".*/.*/.* .*:.*:.*").match(timestr)
        res = None
        if timestr:
            if re.compile(".*/.*/.* .*:.*:.*").match(timestr):
                res = timemanager.jst2utc_date(datetime.datetime.strptime(timestr, "%Y/%m/%d %H:%M:%S"))
            elif re.compile(".*/.*/.*").match(timestr):
                res = timemanager.jst2utc_date(datetime.datetime.strptime(timestr, "%Y/%m/%d"))
            elif re.compile(".*/.*").match(timestr):
                res = timemanager.jst2utc_date(datetime.datetime.strptime(timestr, "%Y/%m"))
            if add:
                res += datetime.timedelta(days=add)
        return res

    def bklistGenerator(self, list_data):
        res = ""
        for i in range(0, list_data.count(1000000), 50):
            if not res == "":
                s = GqlJsonEncoder(ensure_ascii=False).encode(ndb.get_multi([k for k in list_data[i:i+50]]))
                res = res[0:-1] + ", " + s[1:]
            else:
                res += GqlJsonEncoder(ensure_ascii=False).encode(ndb.get_multi([k for k in list_data[i:i+50]]))
        return res

    def _send_mail(self, email_address):
        """Send mail using SMTP (Python 3 migration from GAE Mail API)"""
        msgbody = ''
        try:
            # Note: In production, use proper SMTP configuration
            # This is a placeholder implementation
            msg = EmailMessage()
            msg['Subject'] = 'regist confirmation'
            msg['From'] = config.ADMIN_EMAIL
            msg['To'] = email_address
            msg.set_content(msgbody)
            # TODO: Configure SMTP server
            # smtp = smtplib.SMTP(config.SMTP_SERVER, config.SMTP_PORT)
            # smtp.send_message(msg)
            # smtp.quit()
            logging.info(f"Email would be sent to {email_address}")
        except Exception as e:
            logging.error(f"Mail sending error: {str(e)}")

    def makedata(self, bkd, media):
        """Create data structure for BKdata with related information"""
        # Migrate from db.GqlQuery to ndb.query()
        query_str = (u"SELECT * FROM Blob WHERE CorpOrg_key = '" + bkd.nyrykkisyID +
                    u"' AND Branch_Key = '" + bkd.nyrykstnID + u"' AND bkID = '" + bkd.bkID +
                    u"' AND media = '" + media + u"' ORDER BY pos ASC")
        # Note: GQL is deprecated in ndb, use query filters instead
        blobs = ndb.gql(query_str).fetch()
        b2 = []
        heimenzu = None
        for c in blobs:
            if c.pos != u"平面図":
                b2.append(c)
            else:
                heimenzu = c

        totitubo = None
        if bkd.tcMnsk2:
            totitubo = float(int(bkd.tcMnsk2 * 0.3025 * 100)) / 100

        tatemonotubo = None
        if bkd.ttmnMnsk1:
            tatemonotubo = float(int(bkd.ttmnMnsk1 * 0.3025 * 100)) / 100

        kakakuM = None
        if bkd.kkkuCnryu:
            kakakuM = GqlJsonEncoder.floatfmt(float(int(bkd.kkkuCnryu / 100)) / 100)

        tknngt = None
        if bkd.cknngtSirk:
            tknngt = timemanager.utc2jst_date(bkd.cknngtSirk).year
            if int(tknngt) < 1989:
                tknngt = u"昭和" + str(tknngt - 1925) + u"年"
            elif int(tknngt) >= 1989:
                tknngt = u"平成" + str(tknngt - 1988) + u"年"
            else:
                tknngt = str(tknngt) + u"年"

        gakkuS = getname(bkd.nyrykkisyID, bkd.nyrykstnID, u"小学校区", bkd.tdufknmi, bkd.shzicmi1, bkd.shzicmi2)
        data = bkd
        entitys = {
            "bkdatakey": str(bkd.key.urlsafe().decode()) if hasattr(bkd, 'key') else "",
            "bkdata": data,
            "picdata": b2,
            "kakakuM": kakakuM,
            "totitubo": totitubo,
            "tatemonotubo": tatemonotubo,
            "tknngtG": tknngt,
            "heimenzu": heimenzu,
            "gakkuS": gakkuS
        }
        return entitys

    def senddata(self, bklist, media):
        """Send JSON response with optional JSONP callback"""
        callback = request.args.get('callback')
        if callback:
            response_type = "text/javascript"
            output = callback + "("
        else:
            response_type = "application/json"
            output = ""

        output += "["
        resdata = ""
        gqljson = GqlJsonEncoder(ensure_ascii=False)
        field = request.args.get("field")

        for bke in bklist:
            bk = bke.refbk if hasattr(bke, 'refbk') else bke
            if resdata != "":
                output += ", "

            if field == "normal":
                gqljson.fieldname = "normal"
                resdata = u'{"info":%s,"bk":%s,"key":"%s"}' % (
                    gqljson.encode(bke),
                    gqljson.encode(self.makedata(bk, media)),
                    str(bke.key.urlsafe().decode()) if hasattr(bke, 'key') else ""
                )
            else:
                resdata = u'{"情報":%s,"物件":%s,"key":"%s"}' % (
                    gqljson.encode(bke),
                    gqljson.encode(self.makedata(bk, media)),
                    str(bke.key.urlsafe().decode()) if hasattr(bke, 'key') else ""
                )
            output += resdata

        output += "]"
        if callback:
            output += ");"

        return Response(output, mimetype=response_type)

    def get(self, **kwargs):
        return self.post(**kwargs)

    def post(self, **kwargs):
        """Main POST handler for JSON service requests"""
        self.source = request.args.get("source") or request.form.get("source")
        self.com = request.args.get("com") or request.form.get("com")
        self.search_key = request.args.get("search_key") or request.form.get("search_key")
        self.callback = request.args.get("callback")
        GqlJsonEncoder.fieldname = request.args.get("fieldname") or request.form.get("fieldname")
        GqlJsonEncoder.floatformat = request.args.get("floatformat") or request.form.get("floatformat")

        gqlstr = u""
        where = u""
        entitys = []

        self.corp_name = "s-style"
        self.branch_name = "hon"

        try:
            # REVIEW-L3: u"プレフィックス"を削除（Python 3互換性）
            if self.com == "address1":
                todofukenmei = request.args.get("todofukenmei")
                query = address1.query()
                if todofukenmei:
                    query = query.filter(address1.todofukenmei == todofukenmei)
                if self.search_key:
                    query = query.filter(address1.shikutyosonmei >= self.search_key)
                    query = query.filter(address1.shikutyosonmei < self.search_key + "\uFFFD")
                query = query.order_by(address1.shikutyosonmei)
                entitys = query.fetch()

            elif self.com == "address2":
                todofukenmei = request.args.get("todofukenmei")
                shikutyosonmei = request.args.get("shikutyosonmei")
                query = address2.query()
                if todofukenmei:
                    query = query.filter(address2.todofukenmei == todofukenmei)
                if shikutyosonmei:
                    query = query.filter(address2.shikutyosonmei == shikutyosonmei)
                if self.search_key:
                    query = query.filter(address2.ooazatyotyome >= self.search_key)
                    query = query.filter(address2.ooazatyotyome < self.search_key + "\uFFFD")
                query = query.order_by(address2.ooazatyotyome)
                entitys = query.fetch()

            elif self.com == "getmemName":
                query = member.query()
                if self.search_key:
                    query = query.filter(member.yomi >= self.search_key)
                    query = query.filter(member.yomi < self.search_key + "\uFFFD")
                corp = request.args.get("corp") or "s-style"
                query = query.filter(member.CorpOrg_key_name == corp)
                query = query.order_by(member.yomi)
                query = query.order_by(member.phone)
                query = query.order_by(member.sitename)
                entitys = query.fetch(1000)

            elif self.com == "getmemID":
                query = member.query()
                memberID = request.args.get("memID")
                if memberID:
                    query = query.filter(member.memberID >= memberID)
                    query = query.filter(member.memberID < memberID + "\uFFFD")
                corp = request.args.get("corp") or "s-style"
                query = query.filter(member.CorpOrg_key_name == corp)
                query = query.order_by(member.memberID)
                query = query.order_by(member.sitename)
                entitys = query.fetch(1000)

            # JSON encode the results
            response_body = json.dumps(
                [json.loads(GqlJsonEncoder(ensure_ascii=False).encode(e)) for e in entitys],
                ensure_ascii=False
            )

            return Response(response_body, mimetype="application/json; charset=utf-8")

        except Exception as e:
            logging.error(f"JSON service error: {str(e)}")
            traceback.print_exc()
            return Response(
                json.dumps({"error": str(e)}, ensure_ascii=False),
                mimetype="application/json; charset=utf-8",
                status=500
            )


def json_service_route():
    """Flask route function for JSON service"""
    handler = JsonServiceHandler()
    if request.method == 'GET':
        return handler.get()
    elif request.method == 'POST':
        return handler.post()
