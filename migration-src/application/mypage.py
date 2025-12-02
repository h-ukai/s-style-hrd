# -*- coding: utf-8 -*-

import os
from flask import render_template, request
from application.SecurePage import SecurePage
from application.models.member import member


class MypageHandler(SecurePage):
    """Flask route handler for mypage"""

    def get(self, **kwargs):
        result = self.Secure_init(*["管理者", "担当", "顧客"], **kwargs)
        if result is not True:
            return result  # Return redirect or error template
        if self.filename == "mypagetop.html":
            # Construct the template path with subdirectories using forward slashes for Flask
            template_path = "/".join([self.corp_name, self.branch_name, self.Sitename, self.filename])
            return render_template(template_path, **self.tmpl_val)
        else:
            # Construct the template path with subdirectories for other mypage files
            template_path = "/".join([self.corp_name, self.branch_name, self.Sitename, self.dirpath])
            return render_template(template_path, **self.tmpl_val)

    def post(self, **kwargs):
        return self.get(**kwargs)


def mypage_route():
    """Flask route function for mypage"""
    handler = MypageHandler()
    if request.method == 'GET':
        return handler.get()
    elif request.method == 'POST':
        return handler.post()
