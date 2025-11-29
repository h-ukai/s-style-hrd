# Migration Progress

**Start time**: 2025-11-16 13:52:49
**Total files**: 15

## Migration Progress Group 1

### ✅ app.yaml
- **状態**: 完了
- **日時**: 2025-11-16 14:30:00
- **出力パス**: migration-src/app.yaml
- **依存関係**: なし
- **変更内容**:
  - runtime: python27 → python311
  - api_version, threadsafe, builtins, libraries, includes を削除
  - entrypoint: gunicorn 追加
  - inbound_services の mail を削除（IMAP ポーリング方式に移行）
  - remote_api, deferred, appstats ハンドラーを削除（代替実装が必要）
- **注意事項**: main.py で Flask アプリ (app) を定義する必要があります


### ✅ main.py
- **状態**: 完了
- **日時**: 2025-11-16 14:32:00
- **出力パス**: migration-src/main.py
- **依存関係**:
  - application/login.py (まだ未処理)
  - application/regist.py (まだ未処理)
  - application/proc.py (まだ未処理)
  - application/bkedit.py (まだ未処理)
  - application/blobstoreutl.py (まだ未処理)
  - application/handler.py (まだ未処理)
  - application/RemoveAll.py (まだ未処理)
  - application/uploadbkdata.py (まだ未処理)
  - application/uploadbkdataformaster.py (まだ未処理)
  - application/duplicationcheck.py (まだ未処理)
  - application/json.py (まだ未処理)
  - application/memberedit.py (まだ未処理)
  - application/test.py (まだ未処理)
  - application/bksearch.py (まだ未処理)
  - application/follow.py (まだ未処理)
  - application/mypage.py (まだ未処理)
  - application/bkjoukyoulist.py (まだ未処理)
  - application/bkdchk.py (まだ未処理)
  - application/addresslist.py (まだ未処理)
  - application/show.py (まだ未処理)
  - application/mailinglist.py (まだ未処理)
  - application/uploadaddressset.py (まだ未処理)
  - application/memberSearchandMail.py (まだ未処理)
  - application/bksearchutl.py (まだ未処理)
  - application/cron.py (まだ未処理)
  - application/sendmsg.py (まだ未処理)
  - application/email_receiver.py (まだ未処理)
  - application/matching.py (まだ未処理)
  - application/messageManager.py (まだ未処理)
  - application/tantochange.py (まだ未処理)
  - application/index.py (まだ未処理)
- **変更内容**:
  - webapp2.WSGIApplication → Flask app
  - インポート文をコメントアウト（各モジュールのマイグレーション後に有効化）
  - ルート定義をコメントで記載（実装は各モジュールのマイグレーション後）
  - /_ah/mail/* ルートを削除（IMAP ポーリング方式に移行）
- **注意事項**: 各application配下のモジュールをマイグレーション後、ルート登録を実装する必要があります


### ✅ appengine_config.py
- **状態**: 完了
- **日時**: 2025-11-16 14:35:00
- **出力パス**: migration-src/appengine_config.py
- **依存関係**: なし
- **変更内容**:
  - appstats 関連コードを全削除
  - Cloud Trace / Cloud Profiler / Cloud Monitoring への移行案内コメント追加
  - webapp_add_wsgi_middleware() を廃止
- **注意事項**: Python 3.11ではこのファイルは実質不要ですが、互換性のため残しています


### ✅ setting.py
- **状態**: 完了
- **日時**: 2025-11-16 14:37:00
- **出力パス**: migration-src/setting.py
- **依存関係**: なし
- **変更内容**:
  - AppStatsDjangoMiddleware を削除
  - Cloud Trace / Cloud Profiler への移行コメント追加
- **注意事項**: Flask に移行するため、Django ミドルウェアは不要


### ✅ autolistedindex.yaml
- **状態**: 完了
- **日時**: 2025-11-16 14:39:00
- **出力パス**: migration-src/autolistedindex.yaml
- **依存関係**: なし
- **変更内容**: なし（Python 3.11 でもそのまま使用可能）
- **注意事項**: Datastore インデックス定義ファイルは変更不要


### ✅ backends.yaml
- **状態**: 完了
- **日時**: 2025-11-16 14:41:00
- **出力パス**: migration-src/backends.yaml
- **依存関係**: なし
- **変更内容**:
  - backends は廃止
  - サービス分割方法のコメント追加
  - Task Queue のターゲット指定を 'service' に変更する必要がある旨を記載
- **注意事項**: memdb, memdb2 を別サービスとして定義する必要があります


### ✅ corpzip.yaml
- **状態**: 完了
- **日時**: 2025-11-16 14:43:00
- **出力パス**: migration-src/corpzip.yaml
- **依存関係**: なし
- **変更内容**:
  - bulkloader は廃止
  - Cloud Datastore Admin または Python スクリプトでのインポート方法をコメント追加
- **注意事項**: データインポートには別途スクリプトを作成する必要があります


### ✅ cron.yaml
- **状態**: 完了
- **日時**: 2025-11-16 14:45:00
- **出力パス**: migration-src/cron.yaml
- **依存関係**: なし
- **変更内容**:
  - 既存の cronjobs ジョブを維持
  - IMAP メール受信ジョブ追加（10分間隔）
  - /_ah/mail/* の代替として /tasks/check-incoming-mail を追加
- **注意事項**: IMAP ポーリング用のハンドラー実装が必要


### ✅ dos.yaml
- **状態**: 完了
- **日時**: 2025-11-16 14:47:00
- **出力パス**: migration-src/dos.yaml
- **依存関係**: なし
- **変更内容**: なし（Python 3.11 でもそのまま使用可能）
- **注意事項**: DoS攻撃対策として必要に応じてIPブラックリスト追加


### ✅ index.yaml
- **状態**: 完了
- **日時**: 2025-11-16 14:47:00
- **出力パス**: migration-src/index.yaml
- **依存関係**: なし
- **変更内容**: なし（Python 3.11 でもそのまま使用可能）
- **注意事項**: Datastore インデックス定義ファイルは変更不要


### ✅ mapreduce.yaml
- **状態**: 完了
- **日時**: 2025-11-16 14:48:00
- **出力パス**: migration-src/mapreduce.yaml
- **依存関係**: なし
- **変更内容**:
  - MapReduce は廃止
  - Cron + Python スクリプトでのバッチ処理方法をコメント追加
  - 既存タスク（bkdataput, bklist, bloburlschange, message）の移行方法を記載
- **注意事項**: 各MapReduceタスクをCronジョブに変換する必要があります


### ✅ queue.yaml
- **状態**: 完了
- **日時**: 2025-11-16 14:49:00
- **出力パス**: migration-src/queue.yaml
- **依存関係**: なし
- **変更内容**:
  - queue.yaml は廃止
  - Cloud Tasks API の使用方法をコメント追加
  - gcloud コマンドでのキュー作成方法を記載
- **注意事項**: Cloud Tasks API (`google.cloud.tasks_v2`) を使用する必要があります


### ✅ application/login.py
- **状態**: 完了
- **日時**: 2025-11-16 14:55:00
- **出力パス**: migration-src/application/login.py
- **依存関係**（このファイルが参照するモジュール）:
  - application/models/member.py (まだ未処理)
  - application/models/CorpOrg.py (まだ未処理)
  - application/models/Branch.py (まだ未処理)
  - application/chkauth.py (まだ未処理)
  - application/session.py (まだ未処理)
- **⚠️ 呼び出し元**（このファイルを参照するファイル）:
  - main.py: webapp2.WSGIApplication のルート定義を Flask の @app.route に変更が必要
    - ✅ 修正完了（2025-11-16 15:30:00）
    - インポート文: `from application.login import Login, Logout` → `from application.login import login_route, logout_route`
    - ルート登録: webapp2 クラス渡し → Flask @app.route デコレータ
    - ファイルパス: [migration-src/main.py:18](migration-src/main.py#L18), [migration-src/main.py:53-62](migration-src/main.py#L53-L62)
- **変更内容**:
  - webapp2.RequestHandler → Flask ルート関数（login_route, logout_route）
  - urllib.quote_plus/unquote_plus → urllib.parse.quote_plus/unquote_plus
  - types.UnicodeType チェック削除（Python 3 では全て str）
  - hashlib.sha256 に bytes 引数（.encode('utf-8')）
  - db.Model.all() → ndb.Model.query()
  - get_by_key_name() → ndb.Key().get()
  - str(key()) → key.urlsafe().decode()
  - template.render() → render_template()
  - self.redirect() → return redirect()
- **注意事項**: 依存モジュールのマイグレーションが必要


### ✅ application/logout.py
- **状態**: 完了（ファイル不存在）
- **日時**: 2025-11-16 14:57:00
- **出力パス**: なし
- **依存関係**: なし
- **変更内容**: logout.py は存在せず、login.py の Logout クラスとして実装されています
- **注意事項**: login.py の logout_route() 関数として移行済み


### ✅ application/regist.py
- **状態**: 完了（骨格のみ）
- **日時**: 2025-11-16 15:00:00
- **出力パス**: migration-src/application/regist.py
- **依存関係**（このファイルが参照するモジュール）:
  - application/config.py (まだ未処理)
  - application/users.py (まだ未処理)
  - application/view.py (まだ未処理)
  - application/models/member.py (まだ未処理)
  - application/models/CorpOrg.py (まだ未処理)
  - application/models/Branch.py (まだ未処理)
  - application/messageManager.py (まだ未処理)
  - application/bklistutl.py (まだ未処理)
  - application/session.py (まだ未処理)
  - application/lib/json.py (まだ未処理)
  - cs (CipherSaber library)
- **⚠️ 呼び出し元**（このファイルを参照するファイル）:
  - main.py: webapp2 クラス (Regist, Confirm, Resign) を Flask 関数 (regist_route, confirm_route, resign_route) に変更が必要
    - ⏳ 未修正（骨格のみ実装のため、完全実装後に main.py を更新する必要があります）
    - 予定: インポート文コメントアウト解除 [migration-src/main.py:19](migration-src/main.py#L19)
    - 予定: ルート登録の有効化（/regist, /confirm, /resign）
- **変更内容**:
  - プレースホルダー実装（regist_route, confirm_route, resign_route）
  - 移行タスクをコメントで記載
  - webapp2 → Flask の骨格のみ実装
- **注意事項**:
  - 完全な実装は次セッションで実施する必要があります
  - セキュリティ警告: ユーザー登録ロジックのため、入力検証・CSRF保護・安全なパスワード処理が必要
  - Mail API → smtplib, urlfetch → requests への変換が必要

---

## ⚠️ main.py ルート登録チェックリスト

webapp2からFlaskへのルート登録移行状況（各モジュールのマイグレーション完了時に更新）：


## Group 1 Specific Sections

### ✅ application/proc.py
- **状態**: 完了
- **日時**: 2025-11-17 00:00:00
- **出力パス**: migration-src/application/proc.py
- **依存関係**（このファイルが参照するモジュール）:
  - `application/view.py` (まだ未処理)
  - `application/session.py` (まだ未処理)
- **⚠️ 呼び出し元**（このファイルを参照するファイル）:
  - main.py: コメントアウト解除が必要
    - ⏳ 未修正（実装完了後に main.py を更新する必要があります）
    - 予定: インポート文 `from application.proc import proc_route`
    - 予定: ルート登録 `@app.route('/proc', methods=['GET', 'POST'])`
- **変更内容**:
  - webapp2.RequestHandler (Proc クラス) → Flask ルート関数 (proc_route)
  - `self.request.get()` → `request.values.get()`（GET/POST両対応）
  - `self.response.out.write()` → return文に変換
  - `self.redirect()` → `return redirect()`
  - `template.render()` → `render_template()`
  - セッション管理: `session.Session(self.request, self.response)` → `session.Session(request)`
- **注意事項**:
  - 依存モジュール（view.py, session.py）のマイグレーションが必要
  - レスポンス出力が2箇所（"proc" + テンプレート）あり、意図を確認が必要かもしれません

---


### ✅ application/bkedit.py
- **状態**: 完了
- **日時**: 2025-11-17 00:01:00
- **出力パス**: migration-src/application/bkedit.py
- **依存関係**（このファイルが参照するモジュール）:
  - `application/models/bkdata.py` (まだ未処理)
  - `application/models/Branch.py` (まだ未処理)
  - `dataProvider/bkdataProvider.py` (まだ未処理)
  - `application/timemanager.py` (まだ未処理)
  - `application/wordstocker.py` (まだ未処理)
- **⚠️ 呼び出し元**（このファイルを参照するファイル）:
  - main.py: コメントアウト解除が必要
    - ⏳ 未修正（実装完了後に main.py を更新する必要があります）
    - 予定: インポート文 `from application.bkedit import bkedit_route`
    - 予定: ルート登録 `@app.route('/bkedit.html', methods=['GET', 'POST'])`
- **変更内容**:
  - webapp2.RequestHandler (BKEdit クラス) → Flask ルート関数 (bkedit_route)
  - `Exception, e` → `Exception as e` (Python 3構文)
  - `self.request.get()` → `request.args.get()` / `request.form.get()`
  - `self.response.out.write()` → `return render_template()`
  - `u"文字列"` → `"文字列"` (Python 3ではstr型がUnicode)
  - `template.render()` → `render_template()`
  - GET/POSTを if request.method で分岐
  - kwargs引数を廃止し、bkIDを直接引数で受け取る形式に変更
- **注意事項**:
  - 依存モジュール（bkdata, Branch, bkdataProvider, timemanager, wordstocker）のマイグレーションが必要
  - 年号処理ロジックは複雑なので、テスト実施が推奨されます

---


### ✅ application/blobstoreutl.py
- **状態**: 完了（骨格のみ、GCS移行保留）
- **日時**: 2025-11-17 00:02:00
- **出力パス**: migration-src/application/blobstoreutl.py
- **依存関係**（このファイルが参照するモジュール）:
  - `application/models/bkdata.py` (まだ未処理)
  - `application/models/blob.py` (まだ未処理)
- **⚠️ 呼び出し元**（このファイルを参照するファイル）:
  - main.py: 複数ルート登録が必要
    - ⏳ 未修正（GCS移行完了後に main.py を更新する必要があります）
    - 予定: インポート文 `from application.blobstoreutl import blobstore_utl_route, upload_route, serve_route`
    - 予定: ルート登録 `/BlobstoreUtl/<corp>/<branch>/<bkid>`, `/upload/...`, `/serve/...`
- **変更内容**:
  - webapp2.RequestHandler → Flask ルート関数 (blobstore_utl_route, upload_route, serve_route)
  - BlobstoreUploadHandler/BlobstoreDownloadHandler → Flask request.files (骨格のみ)
  - `urllib.quote/unquote` → `urllib.parse.quote/unquote`
  - `Exception, e` → `Exception as e` (Python 3構文)
  - `db.GqlQuery` → `ndb.Model.query().filter()` (コメント付きプレースホルダー)
  - `u"文字列"` → `"文字列"` (Python 3ではstr型がUnicode)
- **⚠️ 重大な変更保留**:
  - **Blobstore → GCS 完全移行が未完了**（マイグレーションルールに記載あり）
  - `blobstore.create_upload_url()` → GCS Signed URL（未実装）
  - `get_serving_url()` → GCS public/signed URL（未実装）
  - BlobstoreUploadHandler → Flask request.files + GCS client（未実装）
  - ファイルアップロード/ダウンロード処理はプレースホルダーのみ
- **注意事項**:
  - **このファイルは完全な実装ではありません。GCS移行作業が別途必要です。**
  - 依存モジュール（bkdata, blob）のマイグレーションが必要
  - セキュリティ警告: ファイルアップロード処理のため、入力検証・ファイルタイプチェックが必要

---


### ✅ application/handler.py
- **状態**: 完了（骨格のみ、GCS移行保留）
- **日時**: 2025-11-17 00:03:00
- **出力パス**: migration-src/application/handler.py
- **依存関係**（このファイルが参照するモジュール）:
  - `application/models/blob.py` (まだ未処理)
  - `application/models/bkdata.py` (まだ未処理)
- **⚠️ 呼び出し元**（このファイルを参照するファイル）:
  - main.py: 複数ルート登録が必要
    - ⏳ 未修正（GCS移行完了後に main.py を更新する必要があります）
    - 予定: インポート文 `from application.handler import file_upload_form_route, file_upload_route, ...`
    - 予定: ルート登録 `/FileUploadFormHandler`, `/FileUploadFormHandler/upload`, ...
- **変更内容**:
  - webapp2.RequestHandler → Flask ルート関数 (file_upload_form_route, file_upload_route, ...)
  - BlobstoreUploadHandler/BlobstoreDownloadHandler → Flask request.files (骨格のみ)
  - `db.Model` → `ndb.Model` (FileInfo クラス)
  - `db.UserProperty` → `ndb.StringProperty` (ユーザーID/メールを文字列で保存)
  - `blobstore.BlobReferenceProperty` → `ndb.StringProperty` (GCSオブジェクト名保存)
  - `urllib.unquote_plus` → `urllib.parse.unquote_plus`
  - `long()` → `int()` (Python 3ではlongが廃止)
  - `db.GqlQuery` → `ndb.Model.query().filter()` (コメント付きプレースホルダー)
- **⚠️ 重大な変更保留**:
  - **Blobstore → GCS 完全移行が未完了**
  - `blobstore.create_upload_url()` → GCS Signed URL（未実装）
  - BlobstoreUploadHandler → Flask request.files + GCS client（未実装）
  - BlobstoreDownloadHandler → GCS file serving（未実装）
- **注意事項**:
  - **このファイルは完全な実装ではありません。GCS移行作業が別途必要です。**
  - 依存モジュール（blob, bkdata）のマイグレーションが必要
  - セキュリティ警告: ファイルアップロード処理のため、入力検証・ファイルタイプチェックが必要

---


### ✅ application/RemoveAll.py
- **状態**: 完了
- **日時**: 2025-11-17 00:04:00
- **出力パス**: migration-src/application/RemoveAll.py
- **依存関係**（このファイルが参照するモジュール）:
  - `application/models/ziplist.py` (まだ未処理)
  - `application/models/station.py` (まだ未処理)
  - `application/models/bkdata.py` (まだ未処理)
  - `application/models/member.py` (まだ未処理)
  - `application/models/message.py` (まだ未処理)
  - `application/models/msgcombinator.py` (まだ未処理)
  - `application/timemanager.py` (まだ未処理)
- **⚠️ 呼び出し元**（このファイルを参照するファイル）:
  - main.py: コメントアウト解除が必要
    - ⏳ 未修正（実装完了後に main.py を更新する必要があります）
    - 予定: インポート文 `from application.RemoveAll import remove_all_route`
    - 予定: ルート登録 `@app.route('/RemoveAll', methods=['GET'])`
- **変更内容**:
  - webapp2.RequestHandler (RemoveAll クラス) → Flask ルート関数 (remove_all_route)
  - `self.request.get()` → `request.args.get()`
  - `self.response.out.write()` → `return Response()`
  - `db.gql()` → `ndb.Model.query().filter().order()` (コメント付きプレースホルダー)
  - `query.count()` → `len(query.fetch())`
  - webapp2.WSGIApplication → Flask ルート登録（main.py で実施）
- **⚠️ セキュリティ警告**:
  - **認証なしでデータの一括操作が可能（重大な脆弱性）**
  - 本番環境では管理者のみアクセス可能にする必要があります
  - CSRF保護の実装が必要
  - レート制限の実装が推奨されます
  - 元のGQL実装にはSQLインジェクションリスクあり（ndb.query()移行で軽減）
- **⚠️ 変更保留**:
  - **Memcache → Redis 移行が未完了**
  - `memcache.set()` → `redis_client.set()`（コメントのみ）
- **注意事項**:
  - 依存モジュール（ziplist, station, bkdata, member, message, msgcombinator, timemanager）のマイグレーションが必要
  - 元の実装は `c.put()` を実行（削除ではなく保存）

---


### ✅ application/uploadbkdata.py
- **状態**: 完了（骨格のみ、フィールドマッピング190+項目は未実装）
- **日時**: 2025-11-17 00:05:00
- **出力パス**: migration-src/application/uploadbkdata.py
- **依存関係**（このファイルが参照するモジュール）:
  - `application/models/bkdata.py` (まだ未処理)
  - `application/models/CorpOrg.py` (まだ未処理)
  - `application/models/Branch.py` (まだ未処理)
  - `application/timemanager.py` (まだ未処理)
- **⚠️ 呼び出し元**（このファイルを参照するファイル）:
  - main.py: コメントアウト解除が必要
    - ⏳ 未修正（完全実装後に main.py を更新する必要があります）
    - 予定: インポート文 `from application.uploadbkdata import uploadbkdata_route`
    - 予定: ルート登録 `@app.route('/csvupload/bkdata.html', methods=['GET', 'POST'])`
- **変更内容**:
  - webapp2.RequestHandler (BKdataupload クラス) → Flask ルート関数 (uploadbkdata_route)
  - `from StringIO import StringIO` → `import io` (Python 3標準ライブラリ)
  - `StringIO(rawfile)` → `io.StringIO(rawfile.decode('cp932'))`
  - `unicode(text, enc)` → `text.decode(enc)` (bytes) or `text` (str)
  - `Exception, e` → `Exception as e` (Python 3構文)
  - `u"文字列"` → `"文字列"` (Python 3ではstr型がUnicode)
  - `raise MyError, 'msg'` → `raise MyError('msg')` (Python 3構文)
  - `Branch.get_by_key_name()` → `ndb.Key(Branch, key_name).get()`
- **⚠️ 重大な未完了項目**:
  - **CSV フィールドマッピング 190+ 項目が未実装**
  - 元のファイルは1300行以上で、190個以上のCSVフィールドをBKdataモデルにマッピング
  - 骨格のみ実装、全フィールドマッピングロジックの完全移行が必要
  - 30+ 個のルックアップ辞書メソッド（_dtsyurilist, _bkknShbtlist等）の実装が必要
- **⚠️ セキュリティ警告**:
  - **認証なしでCSVアップロード可能（重大な脆弱性）**
  - 本番環境では認証・認可チェックが必須
  - CSRF保護の実装が必要
  - ファイルサイズ制限、CSV構造検証、レート制限の実装が推奨
- **注意事項**:
  - **このファイルは完全な実装ではありません。190+フィールドマッピングの完全移行が別途必要です。**
  - 依存モジュール（bkdata, CorpOrg, Branch, timemanager）のマイグレーションが必要
  - CSV エンコーディング (cp932) の適切な処理が必要

---

## グループ 9 マイグレーション（2025-11-17 実施）


### ✅ application/duplicationcheck.py
- **状態**: 完了
- **日時**: 2025-11-17 11:01:00
- **出力パス**: migration-src/application/duplicationcheck.py
- **依存関係**（このファイルが参照するモジュール）:
  - `application.models.bkdata` (グループ6で処理済み)
  - `application.timemanager` (まだ未処理)
- **⚠️ 呼び出し元**（このファイルを参照するファイル）:
  - main.py: ✅ 修正完了（2025-11-17 11:01:00）
    - インポート文: `from application.duplicationcheck import duplication_check_route`（コメント解除）
    - ルート登録: `@app.route('/duplicationcheck', methods=['GET', 'POST'])`（追加）
    - ファイルパス: [migration-src/main.py:27](migration-src/main.py#L27), [migration-src/main.py:116-119](migration-src/main.py#L116-L119)
- **変更内容**:
  - webapp2.RequestHandler (DuplicationCheck クラス) → Flask ルート関数 (duplication_check_route, get_duplication_check)
  - `google.appengine.ext.db` → `google.cloud.ndb`
  - `db.GqlQuery()` → `ndb.Model.query().filter()`（複数のフィルタに対応）
  - `self.request.get()` → `request.args.get()`（GETパラメータ）
  - `self.response.out.write()` → `return` 文に変換
  - `self.response.headers['Content-Type']` → Flask Response オブジェクトで対応予定
  - `template.render()` → `render_template()`
  - `query.count()` → `len(query.fetch())`（ndbではcountメソッドの代わり）
  - `self.strplus()` → `str_plus()` (module-level function へ移行)
- **主な機能**:
  - 重複物件チェック処理（土地系、マンション系で異なる判定条件）
  - 2年以内の物件に限定したクエリ処理
  - 物件の所在地・面積・階数・間取りなどの組み合わせで重複判定
  - 重複判定時に履歴情報（jshKnrrn）を自動更新
- **セキュリティ警告**:
  - 認証なしでデータ更新が可能（管理者のみアクセス可能にする必要あり）
  - CSRF保護の実装が推奨される
- **注意事項**:
  - テンプレート出力（duplicationcheck.html）の path 処理は Flask `render_template()` に移行
  - GQL クエリ（複雑な文字列結合）を ndb query API に変換
  - 時間計算（2年前まで）を datetime.timedelta で実装

---

---

## グループ 10 マイグレーション（2025-11-17 実施）


