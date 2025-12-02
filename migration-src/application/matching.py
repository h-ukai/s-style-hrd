#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Matching handler for property recommendations - Python 3.11 migration

Original: GAE Standard Python 2.7 + webapp2 + Task Queue
Migrated: Python 3.11 + Flask + Cloud Tasks API + Cloud NDB
"""

import os
import sys
import logging
from datetime import date, datetime, timedelta
from flask import request, Response, render_template
from google.cloud import ndb, tasks_v2
from google.protobuf.timestamp_pb2 import Timestamp

from application import config
from application.SecurePage import SecurePage
from application.models.matchingdate import matchingdate
from application.models.matchingparam import matchingparam
from application.models.bklist import BKlist
from application.models.member import member
from application import timemanager
from application.bksearchutl import bksearchutl
from application.messageManager import messageManager
from application.wordstocker import wordstocker
from application.mailvalidation import mailvalidation

BASE_URL = config.BASE_URL
ADMIN_EMAIL = config.ADMIN_EMAIL
ADMIN_SYSTEM_ID = config.TNTOID
PROJECT_ID = getattr(config, 'GCP_PROJECT_ID', 'your-project-id')
TASKS_QUEUE = 'matching-tasks'
TASKS_LOCATION = 'asia-northeast1'


def matching_route():
    """Main matching page handler"""
    handler = matching()
    if request.method == 'GET':
        return handler.get()
    elif request.method == 'POST':
        return handler.post()
    return Response("Method not allowed", status=405)


def matching_worker_route():
    """Matching worker task handler"""
    handler = matchingworker()
    if request.method == 'GET':
        return handler.get()
    elif request.method == 'POST':
        return handler.post()
    return Response("Method not allowed", status=405)


def matching_task_route():
    """Matching task (per-member) handler"""
    handler = matchingtask()
    if request.method == 'GET':
        return handler.get()
    elif request.method == 'POST':
        return handler.post()
    return Response("Method not allowed", status=405)


def send_mail_worker_route():
    """Send mail worker task handler"""
    handler = sendmailworker()
    if request.method == 'GET':
        return handler.get()
    elif request.method == 'POST':
        return handler.post()
    return Response("Method not allowed", status=405)


def send_mail_task_route():
    """Send mail task (per-member) handler"""
    handler = sendmailtask()
    if request.method == 'GET':
        return handler.get()
    elif request.method == 'POST':
        return handler.post()
    return Response("Method not allowed", status=405)


class matching(SecurePage):
    """Main matching page handler"""
    corp_name = ""
    branch_name = ""

    def get(self, **kwargs):
        return self.post()

    def post(self, **kwargs):
        if self.Secure_init("管理者", "担当"):
            mpr = {}
            com = request.values.get("com", "")
            sitename = request.values.get("sitename", "")
            matchingtarget = request.values.get("sksijky", "")
            service = request.values.get("service", "")
            seikyu = request.values.get("seikyu", "")
            lev1noreactiondays = request.values.get("lev1noreactiondays", "")
            lev1maxsended = request.values.get("lev1maxsended", "")
            lev2noreactiondays = request.values.get("lev2noreactiondays", "")
            lev2maxsended = request.values.get("lev2maxsended", "")
            limitdistance = request.values.get("limitdistance", "")
            sousinsyurui = request.values.get("sousinsyurui", "")
            media = request.values.get("media", "")
            subject = request.values.get("subject", "")
            body = request.values.get("body", "")

            key_name = self.corp_name + "/" + self.branch_name + "/" + sitename
            if com:
                mpr = matchingparam.get_or_insert(key_name, CorpOrg_key_name=self.corp_name)
                mpr.CorpOrg_key_name = self.corp_name
                mpr.Branch_Key_name = self.branch_name
                mpr.sitename = sitename
                mpr.service = service
                mpr.seikyu = seikyu
                mpr.matchingtarget = matchingtarget
                if lev1noreactiondays:
                    mpr.lev1noreactiondays = int(lev1noreactiondays)
                if lev1maxsended:
                    mpr.lev1maxsended = int(lev1maxsended)
                if lev2noreactiondays:
                    mpr.lev2noreactiondays = int(lev2noreactiondays)
                if lev2maxsended:
                    mpr.lev2maxsended = int(lev2maxsended)
                if limitdistance:
                    mpr.limitdistance = int(limitdistance)
                mpr.sousinsyurui = sousinsyurui
                mpr.media = media
                mpr.subject = subject
                mpr.body = body
                mpr.put()

            self.tmpl_val['param'] = mpr

            # Query matching dates
            mchigdatelist = matchingdate.query().filter(
                matchingdate.CorpOrg_key_name == self.corp_name,
                matchingdate.Branch_Key_name == self.branch_name
            )
            if sitename:
                mchigdatelist = mchigdatelist.filter(matchingdate.sitename == sitename)
            mchigdatelist = mchigdatelist.order(-matchingdate.matchingdate)
            mdl = mchigdatelist.fetch(1000)

            lastdate = None
            if len(mdl):
                lastdate = mdl[0].matchingdate

            if com == "履歴削除" and len(mdl):
                mdl[0].delete()
                mdl = mchigdatelist.fetch(1000)
                if len(mdl):
                    lastdate = mdl[0].matchingdate
                else:
                    lastdate = None

            datelist = []
            for e in mdl:
                datelist.append(timemanager.utc2jst_date(e.matchingdate))

            self.tmpl_val['servicelist'] = wordstocker.get(self.corp_name, "サービス")

            if com == "マッチング開始":
                if service:
                    # Create Cloud Tasks task
                    self._create_task('/matching/tasks/matchingworker', {
                        'lastdate': str(lastdate) if lastdate else '',
                        'corp_name': self.corp_name,
                        'branch_name': self.branch_name,
                        'service': service,
                        'matchingtarget': matchingtarget,
                        'sitename': sitename,
                        'seikyu': seikyu
                    })
                    datelist.append(timemanager.utc2jst_date(self.matchingdate()))
                    self.tmpl_val["message"] = "マッチングが開始されました"
                else:
                    self.tmpl_val["message"] = "マッチング対象サービスを設定してください　マッチングはキャンセルされました"

            self.tmpl_val["dateentitys"] = datelist

            if com == "メール送信":
                if not service:
                    self.tmpl_val["message"] = "対象サービスを設定してください　送信はキャンセルされました"
                elif not lev1noreactiondays:
                    self.tmpl_val["message"] = "レベル１無言日数を設定してください　送信はキャンセルされました"
                elif not lev1maxsended:
                    self.tmpl_val["message"] = "レベル１最多送信物件数を設定してください　送信はキャンセルされました"
                elif not lev2noreactiondays:
                    self.tmpl_val["message"] = "レベル２無言日数を設定してください　送信はキャンセルされました"
                elif not lev2maxsended:
                    self.tmpl_val["message"] = "レベル２最多送信物件数を設定してください　送信はキャンセルされました"
                elif not limitdistance:
                    self.tmpl_val["message"] = "最低レベルを設定してください　送信はキャンセルされました"
                else:
                    # Create Cloud Tasks task
                    self._create_task('/matching/tasks/sendmailworker', {
                        "corp_name": self.corp_name,
                        "branch_name": self.branch_name,
                        "sitename": sitename,
                        "subject": self.tmpl_val.get('subject', ''),
                        "body": self.tmpl_val.get('body', ''),
                        "media": media,
                        "service": service,
                        "lev1noreactiondays": lev1noreactiondays,
                        "lev1maxsended": lev1maxsended,
                        "lev2noreactiondays": lev2noreactiondays,
                        "lev2maxsended": lev2maxsended,
                        "limitdistance": limitdistance
                    })
                    self.tmpl_val["message"] = "送信が開始されました"

            filename = 'matching.html'
            temp1 = os.path.join(os.getcwd(), 'templates', self.corp_name, self.branch_name, self.Sitename, filename)
            temp2 = os.path.join(os.getcwd(), 'templates', self.corp_name, self.branch_name, filename)
            if os.path.isfile(temp1):
                path = temp1
            elif os.path.isfile(temp2):
                path = temp2
            else:
                path = os.path.join(os.getcwd(), 'templates', filename)
            return render_template(filename, **self.tmpl_val)

    def matchingdate(self):
        newent = matchingdate(CorpOrg_key_name=self.corp_name, Branch_Key_name=self.branch_name)
        newent.put()
        return newent.matchingdate

    def _create_task(self, url, params):
        """Create a Cloud Tasks task"""
        try:
            client = tasks_v2.CloudTasksClient()
            parent = client.queue_path(PROJECT_ID, TASKS_LOCATION, TASKS_QUEUE)

            task = {
                'http_request': {
                    'http_method': tasks_v2.HttpMethod.POST,
                    'url': BASE_URL + url,
                    'headers': {'Content-Type': 'application/x-www-form-urlencoded'},
                    'body': '&'.join([f"{k}={v}" for k, v in params.items()]).encode()
                }
            }

            response = client.create_task(request={'parent': parent, 'task': task})
            logging.info("Task created: %s", response.name)
        except Exception as e:
            logging.error("Failed to create task: %s", str(e))


class matchingworker:
    """Worker task to distribute matching to individual members"""
    def get(self, **kwargs):
        return self.post()

    def post(self, **kwargs):
        logging.info('matchingworker start')
        corp_name = request.values.get("corp_name", "")
        branch_name = request.values.get("branch_name", "")
        sitename = request.values.get("sitename", "")
        service = request.values.get("service", "")
        lastdate = request.values.get("lastdate", "")
        seikyu = request.values.get("seikyu", "")

        if service and corp_name and branch_name:
            # Query members
            memberkeylist = member.query().filter(
                member.CorpOrg_key_name == corp_name,
                member.Branch_Key_name == branch_name,
                member.seiyaku == "未成約"
            )
            if service:
                memberkeylist = memberkeylist.filter(member.service == service)
            if sitename:
                memberkeylist = memberkeylist.filter(member.sitename == sitename)

            output = ""
            for m in memberkeylist.fetch(keys_only=True):
                # REVIEW-L1: Cloud Tasksタスク作成コードが不完全
                # 問題: taskオブジェクトが定義されているが、client.create_task()の呼び出しがない
                # 修正: _create_task メソッドを呼び出すか、インラインでClient APIを使用して完成させる
                # Create individual matching task
                task = {
                    'http_request': {
                        'http_method': tasks_v2.HttpMethod.POST,
                        'url': BASE_URL + '/matching/tasks/matchingtask',
                        'headers': {'Content-Type': 'application/x-www-form-urlencoded'},
                        'body': f"key={m.urlsafe().decode()}&lastdate={lastdate}&seikyu={seikyu}".encode()
                    }
                }
                # REVIEW-L1: 修正: Cloud Tasks Client で task を作成
                try:
                    client = tasks_v2.CloudTasksClient()
                    parent = client.queue_path(PROJECT_ID, TASKS_LOCATION, TASKS_QUEUE)
                    client.create_task(request={'parent': parent, 'task': task})
                except Exception as e:
                    logging.error("Failed to create task: %s", str(e))
                # Create task using Cloud Tasks API
                output += str(m) + "<br>"

            return Response(output, content_type='text/html; charset=utf-8')
        return Response("", status=400)


class matchingtask:
    """Task to perform matching for a single member"""
    def get(self, **kwargs):
        return self.post()

    def post(self, **kwargs):
        key = request.values.get('key', '')
        lastdate = request.values.get("lastdate", "")
        seikyu = request.values.get("seikyu", "")
        flg = False
        if seikyu == "すべて資料請求する":
            flg = True

        if not key:
            return Response("Missing key", status=400)

        try:
            person = ndb.Key(urlsafe=key.encode()).get()
        except Exception as e:
            logging.error("Failed to fetch entity: %s", str(e))
            return Response("Error", status=400)

        if not person:
            return Response("Entity not found", status=404)

        if person.rank == "Z":
            return Response('rank=Z', content_type='text/plain')

        output = ""
        if person.bksearchdata_set:
            msgkey = messageManager.post(
                corp=person.CorpOrg_key_name,
                sub="一括検索中",
                body="",
                done=False,
                memfrom=person.memberID,
                kindname="マッチング",
                combkind="所有",
                reservation=None,
                reservationend=None,
                memto=None,
                commentto=None,
                mailto=None,
                htmlmail=None
            )
            mlist = bksearchutl.do_allsearch(person, msgkey, lastdate, flg)
            for m in mlist:
                output += str(m) + '<br>'
        else:
            msgkey = messageManager.post(
                corp=person.CorpOrg_key_name,
                sub="マッチングエラー",
                body="検索条件がひとつも登録されていません",
                done=False,
                memfrom=person.memberID,
                kindname="マッチング",
                combkind="所有",
                reservation=None,
                reservationend=None,
                memto=None,
                commentto=None,
                mailto="tanto",
                htmlmail=None
            )
            output = "マッチングエラー 検索条件なし"

        return Response(output, content_type='text/html; charset=utf-8')


class sendmailworker:
    """Worker task to distribute mail sending to individual members"""
    def get(self, **kwargs):
        return self.post()

    def post(self, **kwargs):
        corp_name = request.values.get("corp_name", "")
        branch_name = request.values.get("branch_name", "")
        sitename = request.values.get("sitename", "")
        service = request.values.get("service", "")
        media = request.values.get("media", "")
        subject = request.values.get("subject", "")
        body = request.values.get("body", "")
        lev1noreactiondays = int(request.values.get("lev1noreactiondays", "0"))
        lev1maxsended = int(request.values.get("lev1maxsended", "0"))
        lev2noreactiondays = int(request.values.get("lev2noreactiondays", "0"))
        lev2maxsended = int(request.values.get("lev2maxsended", "0"))
        limitdistance = int(request.values.get("limitdistance", "0"))

        if corp_name and branch_name:
            # Query members
            memberkeylist = member.query().filter(
                member.CorpOrg_key_name == corp_name,
                member.Branch_Key_name == branch_name,
                member.seiyaku == "未成約"
            )
            if sitename:
                memberkeylist = memberkeylist.filter(member.sitename == sitename)
            if service:
                memberkeylist = memberkeylist.filter(member.service == service)

            mv = mailvalidation()
            rep = ""
            output = ""

            for m in memberkeylist.fetch():
                if m.tanto:
                    if m.mail:
                        if not mv.chk(m.mail):
                            msgkey2 = messageManager.post(
                                corp=corp_name,
                                sub="メールアドレスチェック",
                                body="パターンがマッチしない警告を受けました。このユーザーのメールアドレスをチェックしてください。",
                                done=False,
                                memfrom=m.memberID,
                                kindname="アドレスチェック",
                                combkind="所有",
                                msgkey=None,
                                commentto=None,
                                mailto="tanto"
                            )
                            rep += "アドレス不正チェック:" + m.memberID + " :" + m.mail + "\n"

                        if self.spandayschk(m, lev1noreactiondays, lev1maxsended, lev2noreactiondays, lev2maxsended, limitdistance):
                            # REVIEW-L1: Cloud Tasksタスク作成コードが不完全
                            # 問題: spandayschk の判定後、タスク作成処理がない
                            # 修正: sendmailtask への Cloud Tasks タスク作成処理を追加
                            try:
                                client = tasks_v2.CloudTasksClient()
                                parent = client.queue_path(PROJECT_ID, TASKS_LOCATION, TASKS_QUEUE)
                                task = {
                                    'http_request': {
                                        'http_method': tasks_v2.HttpMethod.POST,
                                        'url': BASE_URL + '/matching/tasks/sendmailtask',
                                        'headers': {'Content-Type': 'application/x-www-form-urlencoded'},
                                        'body': f"memberkey={m.urlsafe().decode()}&corp_name={corp_name}&branch_name={branch_name}&media={media}&subject={subject}&body={body}".encode()
                                    }
                                }
                                client.create_task(request={'parent': parent, 'task': task})
                            except Exception as e:
                                logging.error("Failed to create sendmail task: %s", str(e))
                            # Create individual mail task
                            output += str(m) + '<br>'
                    else:
                        rep += "アドレス未設定チェック:" + m.memberID + "\n"
                else:
                    rep += "担当未設定チェック:" + m.memberID + "\n"

            if rep:
                msgkey = messageManager.post(
                    corp=corp_name,
                    sub="メールアドレスチェック結果",
                    body=rep,
                    done=False,
                    memfrom=ADMIN_SYSTEM_ID,
                    kindname="メールアドレスチェック",
                    combkind="所有",
                    msgkey=None,
                    mailto=None
                )

            return Response(output, content_type='text/html; charset=utf-8')
        return Response("", status=400)

    def spandayschk(self, m, lev1noreactiondays, lev1maxsended, lev2noreactiondays, lev2maxsended, limitdistance):
        return m.canSend(lev1noreactiondays, lev1maxsended, lev2noreactiondays, lev2maxsended, limitdistance)


class sendmailtask:
    """Task to send matching results email to a single member"""
    def get(self, **kwargs):
        return self.post()

    def post(self, **kwargs):
        tmpl_val = {}
        corp_name = request.values.get("corp_name", "")
        branch_name = request.values.get("branch_name", "")
        media = request.values.get("media", "")
        memberkey = request.values.get('memberkey', '')

        if not memberkey:
            return Response("Missing memberkey", status=400)

        tmpl_val['subject'] = request.values.get("subject", "")
        tmpl_val['body'] = request.values.get("body", "")
        tmpl_val["htmlmail"] = "1"

        try:
            mem = ndb.Key(urlsafe=memberkey.encode()).get()
        except Exception as e:
            logging.error("Failed to fetch member: %s", str(e))
            return Response("Error", status=400)

        if not mem:
            return Response("Member not found", status=404)

        if not tmpl_val['subject']:
            tmpl_val['subject'] = mem.name + "様のご希望条件にあった物件が見つかりました！！"
        if not tmpl_val['body']:
            tmpl_val['body'] = ''

        tmpl_val['body'] = "こんにちは！" + corp_name + "です。\n" + mem.name + "様が登録した希望条件に一致する物件が見つかりましたのでお知らせいたします。\n\n" + tmpl_val['body']

        if not mem.tanto:
            msgkey2 = messageManager.post(
                corp=corp_name,
                sub="担当者が設定されていません",
                body="顧客ID" + mem.memberID,
                done=False,
                memfrom=config.TNTOID,
                kindname="マッチング送信エラー",
                combkind="所有",
                msgkey=None,
                commentto=None,
                mailto="tanto"
            )
            return Response("", status=400)

        # REVIEW-L1: bklist.filter() の呼び出し方法が誤っている
        # 修正前: bklist.filter(bklist.model.issend == True) - bklist.model は存在しない
        # 修正後: Query API を使用して正しくフィルタを適用
        bklist = mem.refbklist
        # Assuming refbklist returns a query object or needs to be filtered properly
        # If refbklist is a query, use: bklist = bklist.filter(BKlist.issend == True)
        # For now, fetching and filtering in Python:
        bklist_results = []
        for bkl in bklist:
            if bkl.issend and not bkl.sended:
                bklist_results.append(bkl)

        nlist = []
        now = datetime.now()
        s30_days_ago = now - timedelta(30)

        for bkl in bklist_results:
            if bkl.refbk.kknnngp < s30_days_ago:
                if bkl.kindname == 'マッチング' and bkl.refbk.dtsyuri in ["事例", "重複", "停止", "予約"]:
                    bkl.issend = False
                    bkl.senddate = None
                    bkl.memo = bkl.refbk.dtsyuri + "により送信キャンセル"
                    bkl.put()
                else:
                    if (bkl.refbk.sksijky == "作成済み" or bkl.refbk.sksijky == "HP掲載") and bkl.refbk.dtsyuri != "商談中":
                        bkl.senddate = now
                        bkl.sended = True
                        bkl.put()
                        nlist.append(bkl.refbk)

        if len(nlist):
            nlist.sort(key=lambda obj: obj.kknnngp)
            try:
                body = self.makebody(mem.sitename, nlist, media, tmpl_val)
            except IOError:
                mailbody = '適切なテンプレートファイルが存在しません。顧客データのサイト名等をチェックしてください。'
                tmpl_val['subject'] += '送信時エラー 　テンプレートエラー'
                msgkey2 = messageManager.post(
                    corp=corp_name,
                    sub=tmpl_val['subject'],
                    body=mailbody,
                    done=False,
                    memfrom=mem.memberID,
                    kindname="マッチング送信エラー",
                    combkind="所有",
                    msgkey=None,
                    commentto=None,
                    mailto="tanto"
                )
                return Response("", status=400)
            except Exception as e:
                mailbody = f"未確認のエラーが発生したため送信できませんでした\n{str(e)}"
                tmpl_val['subject'] += '送信時エラー　未確認システムエラー'
                msgkey2 = messageManager.post(
                    corp=corp_name,
                    sub=tmpl_val['subject'],
                    body=mailbody,
                    done=False,
                    memfrom=mem.memberID,
                    kindname="マッチング送信エラー",
                    combkind="所有",
                    msgkey=None,
                    commentto=None,
                    mailto="tanto"
                )
                return Response("", status=400)

            msgkey2 = messageManager.post(
                corp=corp_name,
                sub=tmpl_val['subject'],
                body=body,
                done=True,
                memfrom=mem.memberID,
                kindname="マッチング送信",
                combkind="所有",
                msgkey=None,
                commentto=None,
                mailto="member",
                htmlmail=True
            )
            return Response(body, content_type='text/html; charset=utf-8')
        else:
            return Response("リストにデータがありません", content_type='text/plain; charset=utf-8')

    def makebody(self, site, bklist, media, tmpl_val, filename='bklistml.html'):
        entitys = {}
        entitys["media"] = media
        dlist = []
        if bklist:
            for bkl in bklist:
                dlist.append(bkl.makedata(media))
            entitys["bkdatalist"] = dlist
            # REVIEW-L2: bklist[0] が空リストの場合 IndexError が発生
            # 推奨: len(bklist) > 0 のチェックを追加するか、corp_name/branch_name を引数で渡す
            entitys["bkdataurl"] = BASE_URL + "/show/" + bklist[0].CorpOrg_key_name + "/" + bklist[0].Branch_Key_name + "/" + site + "/bkdata/article.html?media=" + media + "&id="
            entitys["listKey"] = ""
            tmpl_val["data"] = entitys

        templ = os.path.join(os.getcwd(), 'templates', bklist[0].CorpOrg_key_name, bklist[0].Branch_Key_name, site, filename)
        temp2 = os.path.join(os.getcwd(), 'templates', bklist[0].CorpOrg_key_name, bklist[0].Branch_Key_name, filename)
        if os.path.isfile(templ):
            path = templ
        elif os.path.isfile(temp2):
            path = temp2
        else:
            path = os.path.join(os.getcwd(), 'templates', 'bklistml.html')
        return render_template(filename, **tmpl_val)
