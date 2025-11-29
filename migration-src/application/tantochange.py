# -*- coding: utf-8 -*-

"""
Tanto (assigned person) change handler - Python 3.11 migration

Original: GAE Standard Python 2.7 + webapp2
Migrated: Python 3.11 + Flask + Cloud NDB
"""

from flask import request, Response, render_template
from google.cloud import ndb
import os
import logging

from application.SecurePage import SecurePage
from application.models.member import member
from application.tantochangetasks import chagetanto


def tanto_change_route():
    """Tanto change page handler - Flask version"""
    handler = tantochange()
    if request.method == 'GET':
        return handler.get()
    elif request.method == 'POST':
        return handler.post()
    return Response("Method not allowed", status=405)


class tantochange(SecurePage):
    """Handler for changing assigned persons (tanto)"""

    def get(self, **kwargs):
        return self.post()

    def post(self, **kwargs):
        if self.Secure_init("管理者", "担当"):
            oldtanto = request.values.get("oldtanto", "")
            tanto = request.values.get("tanto", "")

            if oldtanto and tanto:
                try:
                    oldtanto_mem = ndb.Key(urlsafe=oldtanto.encode()).get()
                    tanto_mem = ndb.Key(urlsafe=tanto.encode()).get()

                    if oldtanto_mem and tanto_mem:
                        chagetanto.tantoallchange(
                            self.corp_name,
                            tanto_mem.memberID,
                            oldtanto_mem.memberID
                        )
                        self.tmpl_val["message"] = "担当変更の処理を開始しました。完了まで数分かかります。ウィンドウを閉じてください"
                    else:
                        logging.error("Tanto member not found: %s or %s", oldtanto, tanto)
                        self.tmpl_val["message"] = "エラー：担当者が見つかりません"

                except Exception as e:
                    logging.error("Error in tanto change: %s", str(e))
                    self.tmpl_val["message"] = f"エラー：{str(e)}"

            # REVIEW-L2: メンバーキーがurlsafe().decode()で文字列化されている
            # 推奨: キーはバイナリのままで扱うか、一貫した形式を使用
            # Query both tanto and admin members
            tanto_query = member.query().filter(
                member.CorpOrg_key_name == self.corp_name,
                member.status == "担当"
            )

            admin_query = member.query().filter(
                member.CorpOrg_key_name == self.corp_name,
                member.status == "管理者"
            )

            listtanto = []

            # Add tanto members
            for e in tanto_query.fetch():
                e2 = {}
                e2["name"] = e.name
                e2["key"] = e.key.urlsafe().decode()
                listtanto.append(e2)

            # Add admin members
            for e in admin_query.fetch():
                e2 = {}
                e2["name"] = e.name
                e2["key"] = e.key.urlsafe().decode()
                listtanto.append(e2)

            self.tmpl_val["tanto"] = listtanto

            # Render template
            path = os.path.join(os.path.dirname(__file__), '../templates/tantochange.html')
            return render_template('tantochange.html', **self.tmpl_val)

        else:
            return Response("Unauthorized", status=403)
