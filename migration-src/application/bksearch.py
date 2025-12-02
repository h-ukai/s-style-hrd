# -*- coding: utf-8 -*-

import os
from flask import render_template, request, redirect
from google.cloud import ndb

from application.models.member import member
from application.models.bksearchdata import bksearchdata
from application.models.bkdata import BKdata
from application.models.CorpOrg import CorpOrg
from application.models.Branch import Branch
from application.models.bksearchaddress import *
from application.models.bksearchmadori import bksearchmadori
from dataProvider.bkdataSearchProvider import bkdataSearchProbider
from application.bksearchensenutl import bksearchensenutl

import datetime
import re
from application.bksearchutl import bksearchutl
from application import timemanager
from application.SecurePage import SecurePage
from application.wordstocker import wordstocker


class BksearchHandler(SecurePage):
    """Flask route handler for book search"""

    def get(self, **kwargs):
        result = self.Secure_init(*["管理者", "担当"], **kwargs)
        if result is not True:
            return result  # Return redirect or error template
        bksp = bkdataSearchProbider(self.corp_name, self.branch_name, self.memberID, self.userID, self.userkey,
                                   self.memdb, self.tmpl_val, request)
        self.tmpl_val = bksp.get(**kwargs)
        # Construct the template path - check if dirpath has extension, if not add .html
        template_name = self.dirpath if self.dirpath.endswith('.html') else self.dirpath + '.html'
        # Use render_template instead of template.render
        return render_template(template_name, **self.tmpl_val)

    def post(self, **kwargs):
        result = self.Secure_init(*["管理者", "担当"], **kwargs)
        if result is not True:
            return result  # Return redirect or error template
        submit = request.form.get("submit")
        bksp = bkdataSearchProbider(self.corp_name, self.branch_name, self.memberID, self.userID, self.userkey,
                                   self.memdb, self.tmpl_val, request)
        kwargs = bksp.post(**kwargs)

        if submit in ["検索", "search", "新規ページへ保存して検索", "検索2", "search2",
                      "新規ページへ保存して検索2", "検索3", "search3", "新規ページへ保存して検索3",
                      "全ページ一括検索", "allpagesearch", "全ページ一括検索2", "allpagesearch2"]:
            redirect_url = str("/follow/" + self.corp_name + "/" + self.branch_name + "/" + self.Sitename +
                               "/follow.html?memberID=" + self.memberID)
            return redirect(redirect_url)

        return self.get(**kwargs)


def bksearch_route():
    """Flask route function for book search"""
    handler = BksearchHandler()
    if request.method == 'GET':
        return handler.get()
    elif request.method == 'POST':
        return handler.post()
