# -*- coding: utf-8 -*-

import os
import re
from flask import request, render_template_string
from google.cloud import ndb
from application.GqlEncoder import GqlJsonEncoder
from application.bklistutl import bklistutl
from application.models import bkdata
from application import session
from application.SecurePageBase import SecurePageBase
from application.chkauth import dbsession
try:
    from urllib.parse import quote_plus
except ImportError:
    from urllib import quote_plus
from application.models.bksearchaddress import getname

def show_route(**kwargs):
    """Flask route handler for property display"""
    handler = Show(**kwargs)
    if request.method == 'POST':
        return handler.post(**kwargs)
    else:
        return handler.get(**kwargs)

class Show(SecurePageBase):

    def get(self, **kwargs):
        """
        Template name is automatically retrieved from address file name
        pathParts = path.split(u'/')
        request.path [u'', u'show', u's-style', u'hon', u'sitename',u'command',u'bkdata.html?id=59]
        request.url [u'https:', u'', u's-style-hrd.appspot.com', u'show', u's-style', u'hon', u'sitename',u'command',u'bkdata.html?id=59]
        """
        self.Secure_init(**kwargs)
        path = request.path
        pathParts = path.split(u'/')
        Domain = request.url.split(u'/')[2]
        CorpOrg_key = pathParts[2]
        Branch_Key = pathParts[3]
        Sitename = pathParts[4]
        Command = pathParts[5]
        user_agent = request.user_agent
        templ = CorpOrg_key + "/" + Branch_Key + "/" + Sitename + "/" + pathParts[6].split(u'?')[0]
        entitys = {}

        self.tmpl_val['corp_name'] = CorpOrg_key
        self.tmpl_val['branch_name'] = Branch_Key
        self.tmpl_val['sitename'] = Sitename
        media = request.args.get("media")

        if Command == "bkdata" or Command == "bkdatam" or Command == "bkdatash":
            """
            https://s-style-hrd.appspot.com/show/s-style/hon/www.chikusaku-mansion.com/bkdata/article.html?id=59&media=web
            https://localhost:8080/show/s-style/hon/www.chikusaku-mansion.com/bkdata/article.html?id=59&media=web
            """
            bkID = request.args.get("id")
            if bkID:
                key_name = CorpOrg_key + u"/" + Branch_Key + u"/" + bkID
                # REVIEW-L1-FIXED: key_name を使用して正しく取得
                # 修正前: bkdb = bkdata.BKdata.get_by_id(key_name) (文字列IDは使えない)
                # 修正後: ndb.Key(bkdata.BKdata, key_name).get() (key_name形式のキーで取得)
                bkdb = ndb.Key(bkdata.BKdata, key_name).get()
                if bkdb:
                    if (bkdb.mtngflg and bkdb.webknskflg) or True:
                        entitys = self.makedata(bkdb, media)
                        if bkdb.kukkTnsiKbn == u"広告可" or bkdb.kukkTnsiKbn == u"一部可（インターネット）" or bkdb.kukkTnsiKbn == u"広告可（但し要連絡）":
                            entitys["webkkkk"] = True
                        else:
                            entitys["webkkkk"] = False
                    else:
                        self.tmpl_val['error_msg'] = u'物件の表示が許可されませんでした。'
                        templ = CorpOrg_key + "/" + Branch_Key + "/" + Sitename + "/" + "sorry.html"
                else:
                    self.tmpl_val['error_msg'] = u'物件の情報が取得できませんでした。No data'
                    templ = CorpOrg_key + "/" + Branch_Key + "/" + Sitename + "/" + "sorry.html"
            else:
                self.tmpl_val['error_msg'] = u'物件の情報が取得できませんでした。bkID missing'
                templ = CorpOrg_key + "/" + Branch_Key + "/" + Sitename + "/" + "sorry.html"

        elif Command == "bklist" or Command == "bklistm" or Command == "bklistsp":
            listKey = request.args.get("listkey")
            offset = request.args.get("offset")
            if listKey:
                query = bkdata.BKdata.query()
                query = query.filter(bkdata.BKdata.mtngflg == True)
                query = query.filter(bkdata.BKdata.webknskflg == True)
                query = query.filter(bkdata.BKdata.nyrykkisyID == CorpOrg_key)
                query = query.filter(bkdata.BKdata.nyrykstnID == Branch_Key)

                if listKey == u"全ての販売情報":
                    query = query.filter(bkdata.BKdata.bkknShbt == u"マンション等")
                    query = query.filter(bkdata.BKdata.icons != None)
                    bklist = sorted(query.fetch(1000), key=lambda x: x.hykpint, reverse=True)
                else:
                    query = query.filter(bkdata.BKdata.icons == listKey)
                    bklist = sorted(query.fetch(1000), key=lambda x: x.hykpint, reverse=True)

                bklistlen = len(bklist)
                if offset:
                    bklist = bklist[int(offset):int(offset) + 9]
                else:
                    bklist = bklist[0:9]

                list = []
                for bkd in bklist:
                    list.append(self.makedata(bkd, media))
                entitys["bkdatalist"] = list

                if offset:
                    offsetnext = int(offset) + 10 if int(offset) + 10 <= bklistlen else 0
                    if offsetnext:
                        entitys["offsetnext"] = request.url.split(u'?')[0] + u"?offset=" + str(offsetnext) + u"&listkey=" + listKey + u"&media=" + media
                    pre = int(offset) - 10 if int(offset) >= 10 and int(offset) - 10 <= bklistlen else 0
                    if pre:
                        entitys["offsetpre"] = request.url.split(u'?')[0] + u"?offset=" + str(pre) + u"&listkey=" + listKey + u"&media=" + media

                if Command == "bklist":
                    entitys["bkdataurl"] = u"https://" + Domain + u"/show/" + CorpOrg_key + u"/" + Branch_Key + u"/" + Sitename + u"/bkdata/article.html?media=" + media + u"&id="
                elif Command == "bklistm":
                    entitys["bkdataurl"] = u"https://" + Domain + u"/show/" + CorpOrg_key + u"/" + Branch_Key + u"/" + Sitename + u"/bkdatam/articlem.html?media=" + media + u"&id="
                elif Command == "bklistsp":
                    entitys["bkdataurl"] = u"https://" + Domain + u"/show/" + CorpOrg_key + u"/" + Branch_Key + u"/" + Sitename + u"/bkdata/article-sp.html?media=" + media + u"&id="

                entitys["listKey"] = listKey
                entitys["media"] = media
                entitys["Command"] = Command
                entitys["pcsite"] = u"https://" + Domain + u"/show/" + CorpOrg_key + u"/" + Branch_Key + u"/" + Sitename + u"/bklist/bklist.html?media=" + media + u"&listkey=" + listKey
                entitys["spsite"] = u"https://" + Domain + u"/show/" + CorpOrg_key + u"/" + Branch_Key + u"/" + Sitename + u"/bklistsp/bklist-sp.html?media=" + media + u"&listkey=" + listKey
            else:
                self.tmpl_val['error_msg'] = u'リストの情報が取得できませんでした。'
                templ = CorpOrg_key + u"/" + Branch_Key + u"/" + Sitename + u"/" + u"sorry.html"

        elif Command == "bklistmesID" or Command == "bklistmesIDm" or Command == "bklistmesIDsp":
            mesid = request.args.get("mesID")
            title = request.args.get("title")
            offset = request.args.get("offset")
            if mesid:
                bkdb = bklistutl.getlistbyID(CorpOrg_key, mesid)
                bklist = bkdb.fetch(1000, 0)
                bklistlen = len(bklist)
                if bklist:
                    bklist = sorted(bklist, key=lambda x: x.refbk.hykpint, reverse=True)

                if offset:
                    bklist = bklist[int(offset):int(offset) + 10]
                else:
                    bklist = bklist[0:10]

                list = []
                for bkl in bklist:
                    list.append(self.makedata(bkl.refbk, media))
                entitys["bkdatalist"] = list

                if offset:
                    offsetnext = int(offset) + 10 if int(offset) + 10 <= bklistlen else 0
                    if offsetnext:
                        entitys["offsetnext"] = request.url.split(u'?')[0] + u"?offset=" + str(offsetnext) + u"&mesID=" + mesid + "&title=" + title + u"&media=" + media
                    pre = int(offset) - 10 if int(offset) - 10 >= 0 else -1
                    if pre >= 0:
                        entitys["offsetpre"] = request.url.split(u'?')[0] + u"?offset=" + str(pre) + u"&mesID=" + mesid + "&title=" + title + u"&media=" + media

                if Command == "bklistmesID":
                    entitys["bkdataurl"] = u"https://" + Domain + u"/show/" + CorpOrg_key + u"/" + Branch_Key + u"/" + Sitename + u"/bkdata/article.html?media=" + media + u"&id="
                elif Command == "bklistmesIDm":
                    entitys["bkdataurl"] = u"https://" + Domain + u"/show/" + CorpOrg_key + u"/" + Branch_Key + u"/" + Sitename + u"/bkdatam/articlem.html?media=" + media + u"&id="
                elif Command == "bklistmesIDsp":
                    entitys["bkdataurl"] = u"https://" + Domain + u"/show/" + CorpOrg_key + u"/" + Branch_Key + u"/" + Sitename + u"/bkdata/article-sp.html?media=" + media + u"&id="

                entitys["listKey"] = title
                entitys["media"] = media
                entitys["mesID"] = mesid
                entitys["Command"] = Command
                entitys["pcsite"] = u"https://" + Domain + u"/show/" + CorpOrg_key + u"/" + Branch_Key + u"/" + Sitename + u"/bklistmesID/bklist.html?media=" + media + u"&title=" + title + u"&mesID=" + mesid
                entitys["spsite"] = u"https://" + Domain + u"/show/" + CorpOrg_key + u"/" + Branch_Key + u"/" + Sitename + u"/bklistmesIDsp/bklist-sp.html?media=" + media + u"&title=" + title + u"&mesID=" + mesid
            else:
                self.tmpl_val['error_msg'] = u'リストの情報が取得できませんでした。'
                templ = CorpOrg_key + u"/" + Branch_Key + u"/" + Sitename + u"/" + u"sorry.html"
        else:
            self.tmpl_val['error_msg'] = u'不正なアドレスへのアクセスです。'
            templ = CorpOrg_key + "/" + Branch_Key + "/" + Sitename + "/" + "sorry.html"

        self.tmpl_val["data"] = entitys
        path = os.path.dirname(__file__) + '/../templates/' + templ
        try:
            with open(path, 'r', encoding='utf-8') as f:
                template_content = f.read()
            return render_template_string(template_content, **self.tmpl_val)
        except FileNotFoundError:
            return f"Template not found: {path}", 404

    def post(self, **kwargs):
        return self.get(**kwargs)

    def urlencode2(self, value, encoding):
        return quote_plus(value.encode(encoding).decode('utf-8'))

    def makedata(self, bkd, media):
        """Format property data for display"""
        b2 = []
        heimenzu = None

        webkkkk = False
        if bkd.kukkTnsiKbn in [u"広告可", u"一部可（インターネット）", u"広告可（但し要連絡）"]:
            webkkkk = True

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
            tknngt = bkd.cknngtSirk.year
            if int(tknngt) < 1989:
                tknngt = u"昭和" + str(tknngt - 1925) + u"年"
            elif int(tknngt) >= 1989:
                tknngt = u"平成" + str(tknngt - 1988) + u"年"
            else:
                tknngt = str(tknngt) + u"年"

        if bkd.ttmnmi:
            mailmsg = u'【' + bkd.bkID + u'】' + bkd.bkknShmk + u" " + bkd.ttmnmi + u"について"
        else:
            mailmsg = u'【' + bkd.bkID + u'】' + bkd.bkknShmk + u"について"

        gakkuS = getname(bkd.nyrykkisyID, bkd.nyrykstnID, u"小学校区", bkd.tdufknmi, bkd.shzicmi1, bkd.shzicmi2)
        bkdata_fmt = GqlJsonEncoder.GQLmoneyfmt(bkd)
        entitys = {
            "auth": self.auth,
            "mailmsg": mailmsg,
            "bkdata": bkdata_fmt,
            "picdata": b2,
            "kakakuM": kakakuM,
            "totitubo": totitubo,
            "tatemonotubo": tatemonotubo,
            "tknngtG": tknngt,
            "heimenzu": heimenzu,
            "gakkuS": gakkuS,
            "webkkkk": webkkkk
        }
        return entitys
