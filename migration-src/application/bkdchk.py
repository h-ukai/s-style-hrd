#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from flask import render_template, request
from google.cloud import ndb
from application.models import bkdata
from application.models import CorpOrg
from application.models import Branch


class Bkdchk:
    """Handler for book data check"""

    def get(self):
        shzicmi1 = request.args.get("shzicmi1")
        shzicmi2 = request.args.get("shzicmi2")
        bkID = request.args.get("bkID")
        self.corp = "s-style"
        self.branch = "hon"
        bkdb = None
        if bkID:
            # REVIEW-L3: u"プレフィックス"を削除（Python 3互換性）
            key_name = self.corp + "/" + self.branch + "/" + bkID
            # Use ndb.Key for getting entities
            key = ndb.Key(bkdata.BKdata, key_name)
            bkdb = key.get()
            if not bkdb:
                # If entity doesn't exist, create new one
                bkdb = bkdata.BKdata(id=key_name, bkID=bkID)

        Default = {"tdufknmi": "愛知県"}
        tmpl_val = {
            "current": bkdb,
            "def": Default,
            "shzicmi1": shzicmi1,
            "shzicmi2": shzicmi2
        }
        if bkdb:
            if hasattr(bkdb, 'snyuMnskSyuBbnMnsk2') and bkdb.snyuMnskSyuBbnMnsk2:
                tmpl_val["snyuMnskSyuBbnMnsk2"] = bkdb.snyuMnskSyuBbnMnsk2
            elif hasattr(bkdb, 'tcMnsk2') and bkdb.tcMnsk2:
                tmpl_val["tcMnsk2"] = bkdb.tcMnsk2

        # Use render_template instead of template.render
        return render_template('bkdchk.html', **tmpl_val)

    def post(self):
        return self.get()


def bkdchk_route():
    """Flask route function for book data check"""
    handler = Bkdchk()
    if request.method == 'GET':
        return handler.get()
    elif request.method == 'POST':
        return handler.post()
