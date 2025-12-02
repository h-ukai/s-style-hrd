# -*- coding: utf-8 -*-
import os
from google.cloud import ndb
from flask import request, render_template_string
from application.models.member import member
from application.models.bksearchaddress import bksearchaddresslist

import datetime
from application import bksearchutl

def addresslist_route(**kwargs):
    """Flask route handler for address list management"""
    Message = ""
    division = request.args.get("division") if request.method == 'GET' else request.form.get("division")
    name = request.args.get("listname") if request.method == 'GET' else request.form.get("listname")
    modal = request.args.get("modal") if request.method == 'GET' else request.form.get("modal")

    if kwargs.get("Message", None):
        Message = kwargs.get("Message", None)

    if kwargs.get("memberID", None) is None:
        memberID = request.args.get("memberID") if request.method == 'GET' else request.form.get("memberID")
    else:
        memberID = kwargs.get("memberID", None)

    if not memberID:
        memberID = "testuser0001"

    key = kwargs.get("key", None)
    if not key:
        if (request.args.get(u"submit") if request.method == 'GET' else request.form.get(u"submit")) != u"削除する":
            key = request.args.get("listid") if request.method == 'GET' else request.form.get("listid")

    now = datetime.datetime.now()

    if request.method == 'POST':
        str1 = request.form.get(u"submit")
        division = request.form.get(u"division")
        name = request.form.get(u"listname")
        co = u"s-style"
        br = u"hon"

        if name and division:
            listid = request.form.get("listid")
            if listid:
                # REVIEW-L1-FIXED: ndb.Key の使用方法を修正
                # 修正前: adlist = bksearchaddresslist.get_by_id(listid)
                # 修正後: ndb.Key(urlsafe=listid).get() を使用
                adlist = ndb.Key(urlsafe=listid).get()
                if adlist:
                    adlist.division = division
                    adlist.name = name
                else:
                    adlist = bksearchaddresslist(co=co, br=br, division=division, name=name)
            else:
                adlist = bksearchaddresslist(co=co, br=br, division=division, name=name)
            adlist.put()

            if str1 == u"削除する":
                adlist.deladset()
                # REVIEW-L1-FIXED: ndb.Key.delete() を使用
                # 修正前: adlist.delete() (誤り)
                # 修正後: adlist.key.delete() (正しい)
                adlist.key.delete()
                adlist = None

            if str1 == u"保存する":
                adlist.deladset()
                i = 0
                # Handle multi-part form data
                items = request.form.items()
                for idx, (n, v) in enumerate(items):
                    if n == "address1":
                        shzicmi1 = v
                        if idx > 0:
                            # Get previous item value
                            tdufknmi = list(items)[idx-1][1]
                            if shzicmi1:
                                if idx + 2 < len(items) and list(items)[idx+2][0] == "address2":
                                    address2 = list(items)[idx+2][1]
                                    if address2:
                                        address2list = address2.split(',')
                                        for ad2 in address2list:
                                            adlist.setadset(tdufknmi, shzicmi1, ad2)
                                    else:
                                        adlist.setadset(tdufknmi, shzicmi1)

            if adlist:
                kwargs['key'] = str(adlist.key.urlsafe().decode())
        else:
            kwargs['Message'] = u"区分またはアドレスリストがありません"

    # Build template variables
    tmpl_val = {
        "memberID": memberID,
        "division": division,
        "listname": name,
        "modal": modal,
        "key": key,
        "now": now,
        "Message": Message,
        "error_msg": "",
        "data": {
            "tdufknmi": None,
            "address1": {
                "shzicmi1": None,
                "shzicmi1id": None
            }
        }
    }

    path = os.path.dirname(__file__) + '/../templates/addresslist.html'
    try:
        with open(path, 'r', encoding='utf-8') as f:
            template_content = f.read()
        return render_template_string(template_content, **tmpl_val)
    except FileNotFoundError:
        return f"Template not found: {path}", 404
