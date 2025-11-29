#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask
import os

# Flask アプリケーション初期化
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-please-change-in-production')

# 参照元: app.yaml から参照されています

# ルートハンドラーのインポート
# webapp2 ハンドラークラスを Flask ルート関数に置き換える必要があります
# 以下のインポートは、各モジュールが Flask 対応に変更された後に有効になります

# login.py は Flask 対応済み（関数ベース）
from application.login import login_route, logout_route
# from application.regist import regist_route, confirm_route, resign_route
# from application.proc import proc_route
# from application.bkedit import bkedit_route
# from application.blobstoreutl import blobstore_utl_route, upload_route, serve_route
# from application import handler
# from application.RemoveAll import remove_all_route
# from application.uploadbkdata import bkdata_upload_route
# from application.uploadbkdataformaster import bkdata_upload_for_master_route
from application.duplicationcheck import duplication_check_route
from application.json import json_service_route
from application.memberedit import member_edit_route
from application.test import test_route
from application.bksearch import bksearch_route
from application.follow import follow_route
from application.mypage import mypage_route
from application.bkjoukyoulist import bkjoukyoulist_route
from application.bkdchk import bkdchk_route
from application.addresslist import addresslist_route
from application.show import show_route
from application.mailinglist import mailinglist_route
from application.uploadaddressset import addresssetupload_route
from application.memberSearchandMail import memberSearchandMail, memberSearchandMailback, mailsendback
from application.bksearchutl import filterWorker, filterWorker2
# from application.cron import cron_jobs_route
# from application.sendmsg import sendmsg_route
# from application.email_receiver import mail_handler_route  # /_ah/mail/* は廃止、IMAP ポーリング方式に移行
# from application.matching import (
#     matching_route, matching_worker_route, matching_task_route,
#     send_mail_task_route, send_mail_worker_route
# )
# from application.messageManager import change_tanto_worker_route, change_tanto_task_route
# from application.tantochange import tanto_change_route
from application.index import index_route

# グループ4ルートハンドラー（処理完了） - main.py更新時にコメント解除
# from application.cron import cron_jobs_route
# from application.sendmsg import sendmsg_route
# from application.matching import (
#     matching_route, matching_worker_route, matching_task_route,
#     send_mail_task_route, send_mail_worker_route
# )
# from application.messageManager import change_tanto_worker_route, change_tanto_task_route
# from application.tantochange import tanto_change_route

# Flask ルート登録（各モジュールが Flask 対応後に実装）
# webapp2.WSGIApplication のルーティングを Flask の @app.route に置き換える必要があります

# Login/Logout ルート（移行済み）
@app.route('/login', methods=['GET', 'POST'])
@app.route('/login.html', methods=['GET', 'POST'])
def login():
    """Login handler"""
    return login_route()

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    """Logout handler"""
    return logout_route()

# 以下のルートは各モジュールのマイグレーション後に実装
@app.route('/addresslist', methods=['GET', 'POST'])
def addresslist():
    """Address list handler"""
    return addresslist_route()

@app.route('/show/<path:path>', methods=['GET', 'POST'])
def show(path):
    """Property display handler"""
    return show_route()

@app.route('/mailinglist', methods=['GET', 'POST'])
def mailinglist():
    """Mailing list handler"""
    return mailinglist_route()

@app.route('/csvupload/addressset.html', methods=['GET', 'POST'])
def uploadaddressset():
    """Address set upload handler"""
    return addresssetupload_route()

@app.route('/membersearch', methods=['GET', 'POST'])
def member_search():
    """Member search and mail handler"""
    handler = memberSearchandMail()
    return handler.post()

@app.route('/membersearchback', methods=['GET', 'POST'])
def member_search_back():
    """Member search back handler"""
    handler = memberSearchandMailback()
    return handler.post()

@app.route('/mailsendback', methods=['GET', 'POST'])
def mail_send_back():
    """Mail send back handler"""
    handler = mailsendback()
    return handler.post()

@app.route('/tasks/filterWorker', methods=['POST'])
def filter_worker():
    """Filter worker task handler"""
    handler = filterWorker()
    return handler.post()

@app.route('/tasks/filterWorker2', methods=['POST'])
def filter_worker2():
    """Filter worker2 task handler"""
    handler = filterWorker2()
    return handler.post()

@app.route('/duplicationcheck', methods=['GET', 'POST'])
def duplicationcheck():
    """Duplication check handler"""
    return duplication_check_route()

# Group 2 routes (json, memberedit, test, bksearch, follow, mypage, bkjoukyoulist, bkdchk)
@app.route('/jsonservice', methods=['GET', 'POST'])
def jsonservice():
    """JSON service handler"""
    return json_service_route()

@app.route('/memberedit', methods=['GET', 'POST'])
def memberedit():
    """Member edit handler"""
    return member_edit_route()

@app.route('/test', methods=['GET', 'POST'])
def test():
    """Test handler"""
    return test_route()

@app.route('/bksearch', methods=['GET', 'POST'])
def bksearch():
    """Book search handler"""
    return bksearch_route()

@app.route('/follow', methods=['GET', 'POST'])
def follow():
    """Follow handler"""
    return follow_route()

@app.route('/mypage', methods=['GET', 'POST'])
def mypage():
    """My page handler"""
    return mypage_route()

@app.route('/bkjoukyoulist', methods=['GET', 'POST'])
def bkjoukyoulist():
    """Book situation list handler"""
    return bkjoukyoulist_route()

@app.route('/bkdchk', methods=['GET', 'POST'])
def bkdchk():
    """Book data check handler"""
    return bkdchk_route()

# Index route (moved to Group 5)
@app.route('/', methods=['GET', 'POST'])
@app.route('/index.html', methods=['GET', 'POST'])
def index():
    """Index page handler"""
    return index_route()

# グループ4ルート（処理完了） - コメント解除時に実装
# @app.route('/cron/cronjobs', methods=['GET'])
# def cron_jobs():
#     """Cron jobs handler"""
#     return cron_jobs_route()
#
# @app.route('/sendmsg', methods=['GET', 'POST'])
# def sendmsg():
#     """Send message handler"""
#     return sendmsg_route()
#
# @app.route('/matching', methods=['GET', 'POST'])
# def matching():
#     """Matching page handler"""
#     return matching_route()
#
# @app.route('/matching/tasks/matchingworker', methods=['GET', 'POST'])
# def matching_worker():
#     """Matching worker task handler"""
#     return matching_worker_route()
#
# @app.route('/matching/tasks/matchingtask', methods=['GET', 'POST'])
# def matching_task():
#     """Matching task handler"""
#     return matching_task_route()
#
# @app.route('/matching/tasks/sendmailworker', methods=['GET', 'POST'])
# def send_mail_worker():
#     """Send mail worker task handler"""
#     return send_mail_worker_route()
#
# @app.route('/matching/tasks/sendmailtask', methods=['GET', 'POST'])
# def send_mail_task():
#     """Send mail task handler"""
#     return send_mail_task_route()
#
# @app.route('/tasks/changetantoWorker', methods=['GET', 'POST'])
# def change_tanto_worker():
#     """Change tanto worker task handler"""
#     return change_tanto_worker_route()
#
# @app.route('/tasks/changetantotask', methods=['GET', 'POST'])
# def change_tanto_task():
#     """Change tanto task handler"""
#     return change_tanto_task_route()
#
# @app.route('/tantochange', methods=['GET', 'POST'])
# def tantochange():
#     """Tanto change handler"""
#     return tanto_change_route()

# ... (以下、全ルート定義)

# 注意:
# - webapp2 ハンドラークラス (Login, Logout, etc.) を Flask ルート関数に変更する必要があります
# - webapp2.RequestHandler.get(), .post() → Flask の request.method チェックまたは @app.route の methods パラメータ
# - self.response.out.write() → return 文
# - self.redirect() → return redirect()
# - /_ah/mail/* ルートは廃止されました（IMAP ポーリング方式に移行）
# - 各モジュールのマイグレーション完了後、ここにルート登録を追加してください

if __name__ == '__main__':
    # 開発サーバー起動（本番環境では gunicorn が使用されます）
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)), debug=True)
