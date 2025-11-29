# -*- coding: utf-8 -*-

import os
from flask import render_template, redirect, request
from application.SecurePageBase import SecurePageBase

class SecurePage(SecurePageBase):

    # REVIEW-L2: webapp2 クラスベースハンドラーから Flask 関数ベースへの移行が不完全
    # 推奨: Flask では @app.route デコレータを使用し、クラスではなく関数として実装すべき
    # このクラスは SecurePageBase を継承しているが、Flask 移行では使用できない可能性がある
    def Secure_init(self, *status, **kwargs):
        SecurePageBase.Secure_init(self, **kwargs)
        if self.auth == False:
            urlstr = "corp_name=" + self.corp_name
            urlstr = urlstr + "&branch_name=" + self.branch_name
            urlstr = urlstr + "&sitename=" + self.Sitename
            urlstr = urlstr + "&togo=" + request.path
            urlstr = urlstr + "&userpagebase=" + self.tmpl_val['userpagebase']
            # ssn.set_ssn_data("togo", urllib.parse.quote_plus(request.path))
            return redirect('/login?' + urlstr)
        if not self.tmpl_val["status"] in status:
            self.tmpl_val['error_msg'] = '必要なステータスがありません'
            templ = self.corp_name + "/" + self.branch_name + "/" + self.Sitename + "/" + "sorry.html"
            return render_template(templ, **self.tmpl_val)
        return True

    def get(self, **kwargs):
        pass

    def post(self, **kwargs):
        self.get(**kwargs)
