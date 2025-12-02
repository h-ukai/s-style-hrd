# -*- coding: utf-8 -*-

import os
from flask import render_template, request
from application.SecurePage import SecurePage
from application.models.member import member


class FollowHandler(SecurePage):
    """Flask route handler for follow"""

    def get(self, **kwargs):
        result = self.Secure_init(*["管理者", "担当"], **kwargs)
        if result is not True:
            return result  # Return redirect or error template
        if self.memberID == "" or not self.memberID:
            self.memberID = self.userID
            key_name = self.corp_name + "/" + self.memberID
            self.memdb = member.get_by_id(key_name)
            if self.memdb:
                self.tmpl_val["membertel"] = self.memdb.phone
                self.tmpl_val["membermail"] = self.memdb.mail
                self.tmpl_val["memberyomi"] = self.memdb.yomi
                self.tmpl_val["membername"] = self.memdb.name
                self.tmpl_val["memberID"] = self.memberID
        # Use render_template instead of template.render
        return render_template(self.dirpath, **self.tmpl_val)

    def post(self, **kwargs):
        return self.get(**kwargs)


def follow_route():
    """Flask route function for follow"""
    handler = FollowHandler()
    if request.method == 'GET':
        return handler.get()
    elif request.method == 'POST':
        return handler.post()
