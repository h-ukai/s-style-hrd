# -*- coding: utf-8 -*-

import os
from flask import render_template, request
from application.SecurePage import SecurePage
from application.models.member import member


class MypageHandler(SecurePage):
    """Flask route handler for mypage"""

    def get(self, **kwargs):
        if self.Secure_init(*["管理者", "担当", "顧客"], **kwargs):
            if self.filename == "mypagetop.html":
                path = os.path.join(os.getcwd(), 'templates', self.corp_name, self.branch_name,
                                   self.Sitename, 'mypagetop.html')
                # Use render_template instead of template.render
                return render_template(self.filename, **self.tmpl_val)
            else:
                return render_template(self.dirpath, **self.tmpl_val)

    def post(self, **kwargs):
        return self.get(**kwargs)


def mypage_route():
    """Flask route function for mypage"""
    handler = MypageHandler()
    if request.method == 'GET':
        return handler.get()
    elif request.method == 'POST':
        return handler.post()
