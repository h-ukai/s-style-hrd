# Migration Progress

**Start time**: 2025-11-16 13:52:49
**Total files**: 15

## Migration Progress Group 6

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


## Group 6 Specific Sections

### ✅ application/models/bkdata.py
- **状態**: 完了
- **日時**: 2025-11-17 10:50:00
- **出力パス**: migration-src/application/models/bkdata.py
- **依存関係**（このファイルが参照するモジュール）:
  - application.models.Branch (まだ未処理)
  - application.wordstocker (まだ未処理)
  - geo.geomodel (Python 3対応が必要)
  - application.GqlEncoder (まだ未処理)
  - application.models.bksearchaddress (まだ未処理)
  - application.timemanager (まだ未処理)
- **⚠️ 呼び出し元**（このファイルを参照するファイル）:
  - application/bkedit.py: 完了済み
  - application/blobstoreutl.py: 完了済み
  - application/RemoveAll.py: 完了済み
  - application/uploadbkdata.py: 完了済み
  - application/bklistutl.py: 本記録で完了
- **変更内容**:
  - `google.appengine.ext.db` → `google.cloud.ndb`
  - `db.Model` → `ndb.Model`、`db.Property` → `ndb.Property`
  - `db.GqlQuery()` → `ndb.Model.query().filter()`
  - `db.StringListProperty` → `ndb.StringProperty(repeated=True)`
  - `db.GeoPtProperty` → `ndb.GeoPtProperty` (GeoModel継承で動作)
  - `xrange()` → `range()` (Python 3)
  - `urllib.quote_plus()` → `urllib.parse.quote_plus()`
  - `db.run_in_transaction()` → `ndb.transaction()` (put()内で呼び出し)
  - `self.key()` → `self.key` (ndb.Modelではプロパティ)
  - `key.urlsafe().decode()` でバイナリKeyを文字列化
  - キー名の設定: `self.key = ndb.Key(BKdata, key_name)`
- **注意事項**:
  - GeoModel (geo/geomodel.py) が db.Model ベースなため、ndb.Model への移行が必要
  - 190+ プロパティ定義により、ファイルサイズが大きい
  - updateLocation() メソッドはGeoModel継承で動作
  - searchkeys はインデックスのために repeated=True で実装

---


### ✅ application/models/bklist.py
- **状態**: 完了
- **日時**: 2025-11-17 10:51:00
- **出力パス**: migration-src/application/models/bklist.py
- **依存関係**（このファイルが参照するモジュール）:
  - application.models.message (まだ未処理)
  - application.models.bkdata (本記録で完了)
  - application.models.member (まだ未処理)
- **⚠️ 呼び出し元**（このファイルを参照するファイル）:
  - application/bklistutl.py: 本記録で完了
- **変更内容**:
  - `google.appengine.ext.db` → `google.cloud.ndb`
  - `db.Model` → `ndb.Model`
  - `db.ReferenceProperty` → `ndb.KeyProperty` へ変更
  - KeyProperty の参照先を kind パラメータで指定
  - `db.DateTimeProperty(auto_now_add=True)` → `ndb.DateTimeProperty(auto_now_add=True)`
  - `db.BooleanProperty(default=False)` → `ndb.BooleanProperty(default=False)`
  - `db.StringProperty` → `ndb.StringProperty`
- **注意事項**:
  - ReferenceProperty → KeyProperty への移行で、関連エンティティは .get() で取得
  - メッセージフォーマットは import パスの更新のみ

---


### ✅ application/models/blob.py
- **状態**: 完了
- **日時**: 2025-11-17 10:52:00
- **出力パス**: migration-src/application/models/blob.py
- **依存関係**（このファイルが参照するモジュール）:
  - なし（独立したデータモデル）
- **⚠️ 呼び出し元**（このファイルを参照するファイル）:
  - application/blobstoreutl.py: 完了済み
  - application/handler.py: 完了済み
- **変更内容**:
  - `google.appengine.ext.db` → `google.cloud.ndb`
  - `db.Model` → `ndb.Model`
  - `db.StringProperty` → `ndb.StringProperty`
  - `db.IntegerProperty` → `ndb.IntegerProperty`
  - `db.DateTimeProperty` → `ndb.DateTimeProperty`
  - `db.run_in_transaction()` → `@ndb.transactional` デコレータ
  - トランザクション内で `self.key` (Key オブジェクト) を利用
  - getNextNum() メソッドをトランザクション対応に変更
- **注意事項**:
  - Blob ストレージ関連のメタデータモデル
  - blobNo クラスのカウンター更新は原子性が必要 (@ndb.transactional を使用)
  - ファイルデータ本体はGCS（Cloud Storage）で管理が前提

---


### ✅ application/bklistutl.py
- **状態**: 完了
- **日時**: 2025-11-17 10:53:00
- **出力パス**: migration-src/application/bklistutl.py
- **依存関係**（このファイルが参照するモジュール）:
  - application.models.bklist (本記録で完了)
  - application.models.bkdata (本記録で完了)
  - application.models.message (まだ未処理)
  - application.models.member (まだ未処理)
  - application.timemanager (まだ未処理)
  - application.messageManager (まだ未処理)
- **⚠️ 呼び出し元**（このファイルを参照するファイル）:
  - application/regist.py: 骨格のみ実装
  - application/memberedit.py: まだ未処理
  - application/matching.py: まだ未処理
- **変更内容**:
  - `google.appengine.ext.db` → `google.cloud.ndb`
  - `db.Model.all()` → `ndb.Model.query()`
  - `db.get()` → `ndb.Key().get()` (明示的にKey設定)
  - `db.ReferenceProperty` → `ndb.KeyProperty` へ対応
  - `db.run_in_transaction()` → ndb 使用時のトランザクション
  - `db.put_multi()` → `ndb.put_multi()`
  - `db.delete_multi()` → `ndb.delete_multi()`
  - クラスメソッド構造は維持 (@classmethod)
  - isinstance チェック: `isinstance(refbk, BKdata)` → `isinstance(refbk, BKdata)` (型チェック動作)
  - Key の取得: `entity.key()` → `entity.key` (プロパティアクセス)
  - query().filter() チェーンでフィルタ複数指定対応
  - fetch(keys_only=True) でキーのみ取得
- **⚠️ セキュリティ警告**:
  - メッセージID （refmesID） の検証が不足している可能性
  - 重複チェックロジックで refmemlist 取得時のエラーハンドリング不足
- **注意事項**:
  - messageManager への依存が強い（ただし未処理）
  - getrefmembykey() メソッドが messageManager に存在することを前提
  - UTC/JST の時間管理はそのまま使用（timemanager による変換）

---


