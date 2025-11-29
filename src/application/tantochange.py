# -*- coding: utf-8 -*-

from SecurePage import SecurePage
from application.models.member import member
import os
from google.appengine.ext.webapp import template
from application.tantochangetasks import chagetanto


class tantochange(SecurePage):
    def get(self,**kwargs):
        self.post()

    def post(self,**kwargs):
        if self.Secure_init(*[u"管理者",u"担当"]):
            oldtanto = self.request.get("oldtanto")
            tanto = self.request.get("tanto")
            if oldtanto and tanto:
                oldtanto = member.get(oldtanto)
                tanto = member.get(tanto)
                chagetanto.tantoallchange(self.corp_name, tanto.memberID, oldtanto.memberID)
                self.tmpl_val["message"]=u"担当変更の処理を開始しました。完了まで数分かかります。ウィンドウを閉じてください"

            gql = member.all()
            gql.filter(" CorpOrg_key_name = " ,self.corp_name)
            gql.filter(" status = " ,u"担当")
            listtanto = []
            for e in gql:
                e2 = {}
                e2["name"]=e.name
                e2["key"]=str(e.key())
                listtanto.append(e2)
            gql = member.all()
            gql.filter(" CorpOrg_key_name = " ,self.corp_name)
            gql.filter(" status = " ,u"管理者")
            for e in gql:
                e2 = {}
                e2["name"]=e.name
                e2["key"]=str(e.key())
                listtanto.append(e2)

            self.tmpl_val["tanto"]=listtanto

            path = os.path.dirname(__file__) + '/../templates/tantochange.html'
            self.response.out.write(template.render(path, self.tmpl_val))
