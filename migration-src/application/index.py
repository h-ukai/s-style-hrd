# -*- coding: utf-8 -*-

from flask import Flask, request, render_template
from google.cloud import ndb
from application.GqlEncoder import GqlJsonEncoder
from application.bklistutl import bklistutl
from application.models import bkdata
from application import session
from application.SecurePageBase import SecurePageBase
from application.chkauth import dbsession
import urllib.parse
from application.models.bksearchaddress import getname

def index_route():
    """Index page handler - Flask version"""
    return get_handler()

def get_handler():
    """GET request handler"""
    tmpl_val = {}
    data = {}
    data["bkdatauri"] = "https://s-style-hrd.appspot.com/show/s-style/hon/www.s-style.ne.jp/bkdata/article.html?media=web&id="
    data["bkdatauri2"] = "https://s-style-hrd.appspot.com/show/s-style/hon/www.chikusaku-mansion.com/bkdata/article.html?media=web&id="

    tmpl_val["data"] = data

    """
    tmpl_val["tochi"] = getdatabyID(773)
    tmpl_val["mansion"] = getdatabyID(773)
    """

    # 604180 土地
    tmpl_val["tochi"] = getdatabyID(604180)
    # 593326 新築一戸建
    tmpl_val["shinchiku"] = getdatabyID(593326)
    # 599278 中古一戸建
    tmpl_val["tyuukoko"] = getdatabyID(599278)
    # 595317 中古マンション
    tmpl_val["chukoman"] = getdatabyID(595317)
    # 602284 収益物件（その他）
    tmpl_val["syueki"] = getdatabyID(602284)
    # 611083 賃貸物件
    tmpl_val["tintai"] = getdatabyID(611083)
    # 623121 売買物件
    tmpl_val["mansion"] = getdatabyID(623121)

    return render_template('index.html', **tmpl_val)

def getdatabyID(mesid):
    """Get book data by message ID"""
    # REVIEW-L1: Added explicit return [] for None/empty case (previously returned None implicitly)
    # Fixed: Ensure function always returns a list for template compatibility
    CorpOrg_key = 's-style'
    if mesid:
        bkdb = bklistutl.getlistbyID(CorpOrg_key, mesid)
        if bkdb:
            # REVIEW-L2: ndb query fetch() may need context manager (transaction/async context)
            # Recommendation: Consider using async context if bkdb is ndb Query object
            bklist = bkdb.fetch(50, 0)
            lst = []
            for bkl in bklist:
                # Cloud NDB: KeyProperty は Key オブジェクトを返すので .get() でエンティティを取得
                bk_entity = bkl.refbk.get() if bkl.refbk else None
                if bk_entity:
                    lst.append(bk_entity.makedata("web"))
            return lst
    return []  # REVIEW-L1: Return empty list instead of None
