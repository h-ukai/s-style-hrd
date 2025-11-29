# -*- coding: utf-8 -*-

# Test URL: https://localhost:8080/csvupload/addressset.html

from flask import request, render_template_string
import os
import csv
import sys
import datetime
from io import StringIO
from models.bksearchaddress import bksearchaddresslist
from models.bksearchaddress import *

def addresssetupload_route(**kwargs):
    """Flask route handler for address set upload"""
    handler = addresssetupload(**kwargs)
    if request.method == 'POST':
        return handler.post(**kwargs)
    else:
        return handler.get(**kwargs)

class addresssetupload:

    def __init__(self, request=None, response=None):
        self.request = request
        self.response = response
        self.tmpl_val = {}
        self.tmpl_val['error_msg'] = ''
        self.auth = False
        self.corp_name = u"s-style"
        self.branch_name = u"hon"
        self.l = 0
        self.e = 0
        self.message = []
        self.date = ''

    def get(self, **kwargs):
        self.source = request.args.get("source", "")
        self.tmpl_val['source'] = self.source
        self.tmpl_val['result'] = self.message

        path = os.path.dirname(__file__) + '/../templates/uploadadresslist.html'
        try:
            with open(path, 'r', encoding='utf-8') as f:
                template_content = f.read()
            return render_template_string(template_content, **self.tmpl_val)
        except FileNotFoundError:
            return f"Template not found: {path}", 404

    def post(self, **kwargs):
        """Upload and parse CSV file"""
        self.message = []
        self.date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Get file from request
        if 'file' not in request.files:
            self.message.append("Error: No file provided")
            return self.get(**kwargs)

        rawfile = request.files['file'].read()
        enc = 'cp932'  # Shift-JIS encoding for Japanese

        # Decode bytes to string
        if isinstance(rawfile, bytes):
            rawfile = rawfile.decode(enc)

        csvfile = csv.reader(StringIO(rawfile))
        name = None
        list = None

        for cont in csvfile:
            self.l += 1
            if self.l == 1:
                continue  # Skip first row (header)

            if len(cont) > 0:
                self.e = 0
                try:
                    cont_name = self.nunicode(cont[1], enc)
                    if name != cont_name:
                        division = self.nunicode(cont[0], enc)
                        name = cont_name
                        list = bksearchaddresslist(
                            division=division,
                            name=name,
                            co=self.corp_name,
                            br=self.branch_name
                        )
                        list.put()

                    list.setadset(
                        self.nunicode(cont[2], enc),
                        self.nunicode(cont[3], enc),
                        self.nunicode(cont[4], enc) if len(cont) > 4 else ""
                    )
                    self.e += 1
                    self.message.append("DataPutSuccess:line" + str(self.l) + "・・・・・OK")
                except Exception as e:
                    self.message.append(
                        "DataPutError:line" + str(self.l) + " elements" +
                        str(self.e) + u":" + str(type(e).__name__)
                    )
                    continue

        return self.get(**kwargs)

    def nunicode(self, text, enc):
        try:
            result = None
            if text is not None and text != "":
                # REVIEW-L1: text の型チェックが不適切
                # 修正前: result = text if isinstance(text, str) else text.decode(enc, errors='replace')
                # 修正後: text が既に str 型の場合とバイト列の場合を正しく処理
                if isinstance(text, bytes):
                    result = text.decode(enc, errors='replace')
                else:
                    result = str(text)
        except Exception as e:
            self.message.append(
                u"error:line" + str(self.l) + " elements" +
                str(self.e) + " :" + str(type(e).__name__)
            )
        finally:
            return result

class MyError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)
