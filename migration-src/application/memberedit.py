#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import render_template, request, redirect
from google.cloud import ndb
import datetime
import re
from application import timemanager
from application.SecurePage import SecurePage
from application.wordstocker import wordstocker
from application.models.member import member
from application.models.CorpOrg import CorpOrg
from application.models.Branch import Branch
import application.models.blob


class MemberEditHandler(SecurePage):
    """Flask route handler for member editing"""

    def get(self, **kwargs):
        # REVIEW-L3: u"プレフィックス"を削除（Python 3互換性）
        result = self.Secure_init(*["管理者", "担当"], **kwargs)
        if result is not True:
            return result  # Return redirect or error template
        if True:
            if kwargs.get("sitename", None) is None:
                sitename = request.args.get("sitename")
            else:
                sitename = kwargs.get("sitename")

            if sitename == 'backoffice':
                sitename = self.corp_name

            # Use ndb.query() instead of db.all()
            query = member.query()
            query = query.filter(member.CorpOrg_key_name == self.corp_name)
            query = query.filter(member.status == "担当")
            listtanto = []
            for e in query.fetch():
                e2 = {}
                e2["name"] = e.name
                e2["key"] = str(e.key.urlsafe().decode())
                listtanto.append(e2)

            query = member.query()
            query = query.filter(member.CorpOrg_key_name == self.corp_name)
            query = query.filter(member.status == "管理者")
            for e in query.fetch():
                e2 = {}
                e2["name"] = e.name
                e2["key"] = str(e.key.urlsafe().decode())
                listtanto.append(e2)

            self.tmpl_val["tanto"] = listtanto
            self.tmpl_val['servicelist'] = wordstocker.get(self.corp_name, "サービス")

            return render_template('memberedit.html', **self.tmpl_val)

    def post(self, **kwargs):
        # REVIEW-L1: ndb.Model.get_or_insertはクラスメソッド（静的メソッド）として使用
        # 修正前: memdb = member.get_or_insert(key_name)
        # 修正後: key = ndb.Key(member, key_name); memdb = key.get() or member(id=key_name)
        result = self.Secure_init(*["管理者", "担当"])
        if result is not True:
            return result  # Return redirect or error template
        if not self.memberID:
            co = CorpOrg.get_by_id(self.corp_name)
            self.memberID = str(co.getNextIDNum())

        key_name = self.corp_name + "/" + self.memberID
        key = ndb.Key(member, key_name)
        memdb = key.get()
        if not memdb:
            memdb = member(id=key_name)

        # Set member properties
        memdb.memberID = self.memberID
        status = request.form.get("status")
        memdb.status = status if status else None

        memdb.CorpOrg_key_name = self.corp_name if self.corp_name else None
        memdb.Branch_Key_name = self.branch_name if self.branch_name else None

        sitename = request.form.get("sitename")
        memdb.sitename = sitename if sitename else None

        name = request.form.get("name")
        memdb.name = name if name else None

        yomi = request.form.get("yomi")
        memdb.yomi = yomi if yomi else None

        zip_code = request.form.get("zip")
        memdb.zip = zip_code if zip_code else None

        address = request.form.get("address")
        memdb.address = address if address else None

        address1 = request.form.get("address1")
        memdb.address1 = address1 if address1 else None

        address2 = request.form.get("address2")
        memdb.address2 = address2 if address2 else None

        phone = request.form.get("phone")
        memdb.phone = phone if phone else None

        fax = request.form.get("fax")
        memdb.fax = fax if fax else None

        mobilephone = request.form.get("mobilephone")
        memdb.mobilephone = mobilephone if mobilephone else None

        mail = request.form.get("mail")
        memdb.mail = mail if mail else None

        netID = request.form.get("netID")
        memdb.netID = netID if netID else None

        netPass = request.form.get("netPass")
        memdb.netPass = netPass if netPass else None

        # REVIEW-L1: re.compile().match()の第2引数削除（Python 3では不要）
        # 修正前: r = re.compile(".*:.*:.*").match(tourokunengappi, 1)
        # 修正後: r = re.compile(".*:.*:.*").match(tourokunengappi)
        tourokunengappi = request.form.get("tourokunengappi")
        if tourokunengappi and tourokunengappi != "":
            r = re.compile(".*:.*:.*").match(tourokunengappi)
            if r is None:
                memdb.tourokunengappi = timemanager.jst2utc_date(
                    datetime.datetime.strptime(tourokunengappi, "%Y/%m/%d"))
            else:
                memdb.tourokunengappi = timemanager.jst2utc_date(
                    datetime.datetime.strptime(tourokunengappi, "%Y/%m/%d %H:%M:%S"))
        else:
            memdb.hnknngp = self.now

        tanto = request.form.get("tanto")
        if tanto and str(memdb.key) != tanto:
            memdb.tanto = ndb.Key(urlsafe=tanto.encode())
        else:
            memdb.tanto = None

        mno = request.form.get("mno")
        memdb.mno = float(mno) if mno else None

        mr = request.form.get("mr")
        memdb.mr = float(mr) if mr else None

        uri = request.form.get("uri")
        memdb.uri = bool(uri) if uri == "1" else None

        kai = request.form.get("kai")
        memdb.kai = bool(kai) if kai == "1" else None

        kashi = request.form.get("kashi")
        memdb.kashi = bool(kashi) if kashi == "1" else None

        kari = request.form.get("kari")
        memdb.kari = bool(kari) if kari == "1" else None

        baikai = request.form.get("baikai")
        memdb.baikai = baikai if baikai else None

        seiyaku = request.form.get("seiyaku")
        memdb.seiyaku = seiyaku if seiyaku else None

        # REVIEW-L1: re.compile().match()の第2引数削除（Python 3では不要）
        seiyakunengappi = request.form.get("seiyakunengappi")
        if seiyakunengappi and seiyakunengappi != "":
            r = re.compile(".*:.*:.*").match(seiyakunengappi)
            if r is None:
                memdb.seiyakunengappi = timemanager.jst2utc_date(
                    datetime.datetime.strptime(seiyakunengappi, "%Y/%m/%d"))
            else:
                memdb.seiyakunengappi = timemanager.jst2utc_date(
                    datetime.datetime.strptime(seiyakunengappi, "%Y/%m/%d %H:%M:%S"))
        else:
            memdb.hnknngp = None

        seiyakuankeito = request.form.get("seiyakuankeito")
        memdb.seiyakuankeito = bool(seiyakuankeito) if seiyakuankeito == "1" else None

        age = request.form.get("age")
        memdb.age = float(age) if age else None

        kinzoku = request.form.get("kinzoku")
        memdb.kinzoku = float(kinzoku) if kinzoku else None

        otona = request.form.get("otona")
        memdb.otona = float(otona) if otona else None

        kodomo = request.form.get("kodomo")
        memdb.kodomo = float(kodomo) if kodomo else None

        tutomesaki = request.form.get("tutomesaki")
        memdb.tutomesaki = tutomesaki if tutomesaki else None

        CorpOrg_yomi = request.form.get("CorpOrg_yomi")
        memdb.CorpOrg_yomi = CorpOrg_yomi if CorpOrg_yomi else None

        CorpOrg_yaku = request.form.get("CorpOrg_yaku")
        memdb.CorpOrg_yaku = CorpOrg_yaku if CorpOrg_yaku else None

        CorpOrg_zip = request.form.get("CorpOrg_zip")
        memdb.CorpOrg_zip = CorpOrg_zip if CorpOrg_zip else None

        CorpOrg_address = request.form.get("CorpOrg_address")
        memdb.CorpOrg_address = CorpOrg_address if CorpOrg_address else None

        CorpOrg_address1 = request.form.get("CorpOrg_address1")
        memdb.CorpOrg_address1 = CorpOrg_address1 if CorpOrg_address1 else None

        CorpOrg_address2 = request.form.get("CorpOrg_address2")
        memdb.CorpOrg_address2 = CorpOrg_address2 if CorpOrg_address2 else None

        CorpOrg_phone = request.form.get("CorpOrg_phone")
        memdb.CorpOrg_phone = CorpOrg_phone if CorpOrg_phone else None

        CorpOrg_fax = request.form.get("CorpOrg_fax")
        memdb.CorpOrg_fax = CorpOrg_fax if CorpOrg_fax else None

        access = request.form.get("access")
        memdb.access = access if access else None

        zikoshikin = request.form.get("zikoshikin")
        memdb.zikoshikin = float(zikoshikin) if zikoshikin else None

        heisaituki = request.form.get("heisaituki")
        memdb.heisaituki = float(heisaituki) if heisaituki else None

        heisaibonasu = request.form.get("heisaibonasu")
        memdb.heisaibonasu = float(heisaibonasu) if heisaibonasu else None

        kounyuziki = request.form.get("kounyuziki")
        memdb.kounyuziki = kounyuziki if kounyuziki else None

        kounyunen = request.form.get("kounyunen")
        memdb.kounyunen = float(kounyunen) if kounyunen else None

        rank = request.form.get("rank")
        memdb.rank = rank if rank else None

        service = request.form.get("service")
        if service:
            memdb.service = []
            for s in service.split(","):
                if s != "":
                    memdb.service.append(s)
        else:
            memdb.service = []

        baitai = request.form.get("baitai")
        memdb.baitai = baitai if baitai else None

        syokai = request.form.get("syokai")
        memdb.syokai = syokai if syokai else None

        gyosya = request.form.get("gyosya")
        memdb.gyosya = gyosya if gyosya else None

        bikou = request.form.get("bikou")
        memdb.bikou = bikou

        memdb.put()
        memdb.wordstock()

        kwargs = {"memberID": memdb.memberID}
        return self.get(**kwargs)


def member_edit_route():
    """Flask route function for member editing"""
    handler = MemberEditHandler()
    if request.method == 'GET':
        return handler.get()
    elif request.method == 'POST':
        return handler.post()
