# -*- coding: utf-8 -*-

from flask import request, render_template
from google.cloud import ndb
from application.models import bkdata
from application.models import CorpOrg
from application.models import Branch
import os
import csv
import sys
import datetime
import logging
import io
import application.timemanager as timemanager


# ⚠️ SECURITY WARNING: CSV upload for master data without authentication


def uploadbkdataformaster_route():
    """BKdatauploadformaster route (migrated from webapp2)"""

    l = 0
    e = 0
    message = []  # Note: Original has typo 'massage' → 'message'
    date = ''
    tmpl_val = {}
    tmpl_val['error_msg'] = ''
    auth = False
    corp_name = "s-style"
    branch_name = "hon"

    if request.method == 'GET':
        source = request.args.get("source")
        tmpl_val['source'] = source
        tmpl_val['result'] = message
        return render_template('uploadbkdata.html', **tmpl_val)

    # POST
    elif request.method == 'POST':
        date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        uploaded_file = request.files.get('file')
        rawfile = uploaded_file.read() if uploaded_file else b''
        source = request.form.get("source")

        try:
            csvfile = csv.reader(io.StringIO(rawfile.decode('cp932')))
        except (AttributeError, TypeError):
            if isinstance(rawfile, str):
                csvfile = csv.reader(io.StringIO(rawfile))
            else:
                csvfile = csv.reader(io.StringIO(''))

        enc = 'cp932'

        for cont in csvfile:
            l += 1
            e = 0
            if len(cont) > 0:
                # ⚠️ TODO: Lookup dictionaries (same as uploadbkdata.py)
                # Abbreviated for brevity

                try:
                    br = Branch.Branch.get_or_insert("s-style/hon")
                    bkID = nunicode(cont[0], enc)
                    key_name = corp_name + "/" + branch_name + "/" + bkID

                    # Old: db.GeoPt → ndb.GeoPt
                    # Note: GeoPt remains same in ndb
                    lat = nfloat(nunicode(cont[10], enc))
                    lon = nfloat(nunicode(cont[11], enc))

                    data = bkdata.BKdata.get_or_insert(key_name, bkID=nunicode(cont[0], enc))
                    data.dtsyuri = "サンプル"
                    data.sksijky = "作成済み"
                    data.nyrykkisyID = corp_name
                    data.nyrykstnID = branch_name
                    data.nyryktnt = 'import'
                    data.ksnkisID = corp_name
                    data.ksnstnID = branch_name
                    data.ksntnt = 'import'
                    data.duplicationcheck = True
                    data.dataSource = 'マンションマスター'
                    data.bknbng = 'マンションマスター' + '/' + nunicode(cont[1], enc)

                    # GeoPt remains same in ndb
                    if lat is not None and lon is not None:
                        data.chzsntidkd = ndb.GeoPt(lat, lon)
                        data.idkd = ndb.GeoPt(lat, lon)
                    data.chzrnj = 18

                    data.bbchntikbn = "売買"
                    data.bkknShbt = 'マンション等'
                    data.bkknShmk = '中古マンション'
                    data.kiinni = corp_name
                    data.turknngp = getdatetime('2011/06/07')
                    data.tdufknmi = '愛知県'
                    data.shzicmi1 = nunicode(cont[2], enc)
                    data.shzicmi2 = nunicode(cont[3], enc)
                    data.shzicmi3 = nunicode(cont[4], enc)
                    data.ttmnmi = nunicode(cont[0], enc)
                    data.ttmnKuzu = nunicode(cont[5], enc)
                    data.cjyuKisou = nfloat(nunicode(cont[6], enc))
                    data.ckaKisou = nfloat(nunicode(cont[7], enc))
                    data.cknngtSirk = getdatetime(nunicode(cont[8], enc))

                    data.put()
                    message.append("DataPutSuccess:line" + str(l) + "・・・・・OK")

                except Exception as ex:
                    message.append("DataPutError:line" + str(l) + ":" + str(sys.exc_info()[0]))

        tmpl_val['source'] = source
        tmpl_val['result'] = message
        return render_template('uploadbkdata.html', **tmpl_val)


# Helper functions (same as uploadbkdata.py)

def nunicode(text, enc):
    try:
        result = None
        if text is not None and text != "":
            if isinstance(text, bytes):
                result = text.decode(enc, errors='replace')
            else:
                result = text
    except Exception:
        pass
    finally:
        return result


def getdatetime(text):
    result = None
    try:
        if text is not None and text != "":
            result = timemanager.jst2utc_date(datetime.datetime.strptime(text, "%Y/%m/%d"))
    except Exception:
        pass
    finally:
        return result


def nfloat(text):
    result = None
    try:
        if text is not None and text != "":
            result = float(text)
    except Exception:
        pass
    finally:
        return result
