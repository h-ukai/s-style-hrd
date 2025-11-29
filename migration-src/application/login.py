#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Login/Logout handlers for Flask migration

IMPORTANT: This module has been migrated from webapp2 to Flask.
The Login and Logout classes have been converted to route functions.

Migration from main.py:
  OLD (webapp2):
    from application.login import Login, Logout
    app = webapp2.WSGIApplication([
        ('/login', Login),
        ('/logout', Logout),
    ])

  NEW (Flask):
    from application.login import login_route, logout_route

    @app.route('/login', methods=['GET', 'POST'])
    @app.route('/login.html', methods=['GET', 'POST'])
    def login():
        return login_route()

    @app.route('/logout', methods=['GET', 'POST'])
    def logout():
        return logout_route()
"""

import datetime
import hashlib
import re
import os
import sys
import logging
from urllib.parse import quote_plus, unquote_plus

from flask import request, render_template, redirect, session as flask_session
from google.cloud import ndb

from application.models.member import member
from application.models.CorpOrg import CorpOrg
from application.models.Branch import Branch
from application.chkauth import dbsession

def login_route():
    """
    Login route handler (Flask version)
    GET/POST /login
    """
    tmpl_val = {}
    tmpl_val['error_msg'] = ''
    auth = False

    # Get data from request
    # /login?corp_name=s-style&branch_name=hon&sitename=www.chikusaku.mansion.com
    get_login_id = request.values.get('login_id', '')
    get_login_pwd = request.values.get('login_pwd', '')
    get_login_submit = request.values.get('login_submit', '')
    get_logoff = request.values.get('logoff', '')
    get_login_togo = request.values.get('togo', '')
    get_login_style = request.values.get('style', '')
    tmpl_val['style'] = get_login_style
    tmpl_val['corp_name'] = request.values.get('corp_name', '')
    tmpl_val['branch_name'] = request.values.get('branch_name', '')
    tmpl_val['sitename'] = request.values.get('sitename', '')
    tmpl_val['togo'] = ''
    tmpl_val['userpagebase'] = request.values.get('userpagebase', 'userpagebase.html')

    if get_login_togo:
        try:
            togo = unquote_plus(get_login_togo)
            # Python 3 では全て str なので isinstance チェック不要
            tmpl_val['togo'] = quote_plus(togo)
        except Exception as e:
            logging.error(f'login_urllib_plusError: {e} togo: {get_login_togo}')

    tmpl_val["query_string"] = f"corp_name={tmpl_val['corp_name']}&branch_name={tmpl_val['branch_name']}&sitename={tmpl_val['sitename']}&togo={tmpl_val['togo']}&userpagebase={tmpl_val['userpagebase']}"
    tmpl_val["applicationpagebase"] = f"{tmpl_val['corp_name']}/{tmpl_val['branch_name']}/{tmpl_val['sitename']}/{tmpl_val['userpagebase']}"

    regx = re.compile(r'^[\s]*(.*?)[\s]*$')  # スペースを含んでいないことをチェック
    if get_login_id:
        get_login_id = regx.match(get_login_id).group(1)

    if get_logoff == "true":
        ssn_key = f"{tmpl_val['corp_name']}_{tmpl_val['branch_name']}_{tmpl_val['sitename']}"
        ssn = dbsession(request, None, ssn_key)
        ssn.destroy_ssn()
        tmpl_val['completed_msg'] = 'ログアウトしました'

    # Command processing
    if get_login_submit:
        # Python 3: hashlib.sha256 は bytes を要求
        hashed_pwd = hashlib.sha256(get_login_pwd.encode('utf-8')).hexdigest()

        # db.Model.all() → ndb.Model.query()
        query = member.query()
        query = query.filter(member.CorpOrg_key_name == tmpl_val['corp_name'])
        query = query.filter(member.sitename == tmpl_val['sitename'])
        query = query.filter(member.netID == get_login_id)
        query = query.filter(member.netPass == get_login_pwd)
        query = query.filter(member.seiyaku == "未成約")

        users = query.fetch()
        count = len(users)

        if count != 1:
            tmpl_val['error_msg'] = 'IDかパスワードが見つかりません'
        else:
            user = users[0]
            # get_by_key_name → ndb.Key(ModelName, key_name).get()
            corp = ndb.Key(CorpOrg, user.CorpOrg_key_name).get()
            if corp and corp.active:
                ssn_key = f"{tmpl_val['corp_name']}_{tmpl_val['branch_name']}_{tmpl_val['sitename']}"
                ssn = dbsession(request, None, ssn_key, user.sid)
                ssn.new_ssn()
                user.sid = ssn.getsid()
                user.put()
                auth = True
                tmpl_val['auth'] = True
                tmpl_val['sid'] = ssn.sid_value

                # Session data
                ssn.set_ssn_data('CorpOrg_key_name', user.CorpOrg_key_name)
                ssn.set_ssn_data('Branch_Key_name', user.Branch_Key_name)
                ssn.set_ssn_data('sitename', user.sitename)
                ssn.set_ssn_data('memberID', user.memberID)
                ssn.set_ssn_data('name', user.name)
                ssn.set_ssn_data('status', user.status)
                ssn.set_ssn_data('phone', user.phone)
                ssn.set_ssn_data('mobilephone', user.mobilephone)
                ssn.set_ssn_data('mail', user.mail)
                # str(user.key()) → user.key.urlsafe().decode()
                ssn.set_ssn_data('userkey', user.key.urlsafe().decode())

                if get_login_togo:
                    redirect_url = unquote_plus(get_login_togo)
                    tmpl_val['onloadsclipt'] = f"location.replace('{redirect_url}')"
                    tmpl_val['completed_msg'] = f'ログインに成功しました　<br /> <a href="{redirect_url}"> しばらく待って移動しない場合はココをクリックしてください。</a>'
                else:
                    redirect_url = f"https://{user.sitename}"
                    tmpl_val['onloadsclipt'] = f"location.replace('{redirect_url}')"
                    tmpl_val['completed_msg'] = f'ログインに成功しました　<br /> <a href="{redirect_url}"> しばらく待って移動しない場合はココをクリックしてください。</a>'
            else:
                tmpl_val['error_msg'] = 'サービスが無効となっています　管理者におたずねください'

    # View rendering
    # template.render() → render_template()
    if get_login_style:
        # Python 3: os.getcwd() → 'templates' ディレクトリパス
        return render_template(f'{get_login_style}.html', **tmpl_val)
    else:
        return render_template('login.html', **tmpl_val)


def logout_route():
    """
    Logout route handler (Flask version)
    GET/POST /logout
    """
    # session.Session → Flask session または dbsession
    # ここでは既存の session モジュールを継続使用
    from application import session as app_session
    ssn = app_session.Session(request, None)
    sid = ssn.destroy_ssn()

    # self.redirect('/') → return redirect('/')
    return redirect('/')
