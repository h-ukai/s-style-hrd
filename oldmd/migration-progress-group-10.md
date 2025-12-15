# Migration Progress

**Start time**: 2025-11-16 13:52:49
**Total files**: 15

## Migration Progress Group 10

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


## Group 10 Specific Sections

### ✅ application/email_decoder.py
- **状態**: 完了
- **日時**: 2025-11-17 11:00:00
- **出力パス**: migration-src/application/email_decoder.py
- **依存関係**（このファイルが参照するモジュール）:
  - なし（独立したメール解析ユーティリティ）
- **⚠️ 呼び出し元**（このファイルを参照するファイル）:
  - application/email_receiver.py: IMAP受信メール解析用（未処理）
  - cron処理でのメール受信処理（未処理）
- **変更内容**:
  - `from email.Header import decode_header` → `from email.header import decode_header`（モジュール名小文字）
  - `except Exception, s:` → `except Exception as s:`（Python 3構文）
  - `unicode(s)` → `str(s)`（Python 3では全てstr）
  - `urllib.unquote()` → `urllib.parse.unquote()`
  - `msg_dic.has_key('key')` → `'key' in msg_dic`（Python 3）
  - `re.search(u'...')` → `re.search(r'...')`（raw文字列）
  - `dict.keys()` → list()への明示的変換不要（反復処理OK）
- **注意事項**: メール解析コアモジュール。IMAP受信メール処理で使用される重要なモジュール


### ✅ application/CriticalSection.py
- **状態**: 完了
- **日時**: 2025-11-17 11:05:00
- **出力パス**: migration-src/application/CriticalSection.py
- **依存関係**（このファイルが参照するモジュール）:
  - `redis`（Cloud Memorystore への接続）
- **⚠️ 呼び出し元**（このファイルを参照するファイル）:
  - application/messageManager.py（未処理）や他のロック処理が必要なモジュール
- **変更内容**:
  - `from google.appengine.api import memcache` → `import redis`（Cloud Memorystore へ移行）
  - `memcache.incr()` → `redis_client.incr()`
  - `memcache.decr()` → `redis_client.decr()`
  - `redis_client.expire()` でデッドロック防止タイムアウト（15秒）
  - Redis キー命名規則: `namespace:key` 形式
  - エラーハンドリング: Redis接続失敗時の処理追加
- **⚠️ 重要な設定項目**:
  - host と port は環境に合わせて設定必要（Cloud Memorystore インスタンスIP）
  - decode_responses=True で自動的に bytes → str 変換
- **注意事項**: Memcache API は廃止されたため Redis への完全移行が必須


### ✅ application/rotor.py
- **状態**: 完了
- **日時**: 2025-11-17 11:10:00
- **出力パス**: migration-src/application/rotor.py
- **依存関係**（このファイルが参照するモジュール）:
  - なし（独立した暗号化ユーティリティ）
- **⚠️ 呼び出し元**（このファイルを参照するファイル）:
  - application/models/member.py や他のパスワード/機密値エンコーディング処理
- **変更内容**:
  - `string.lowercase` → `string.ascii_lowercase`
  - `map(lambda c: ..., str)` → リスト内包表記 `[... for c in str]`（Python 3で map() は遅延評価）
  - rotormap の一定性（不変）確認済み
- **注意事項**: 暗号化スキーム rotor。既存データとの互換性のため、テスト推奨


### ✅ application/tantochangetasks.py
- **状態**: 完了
- **日時**: 2025-11-17 11:15:00
- **出力パス**: migration-src/application/tantochangetasks.py
- **依存関係**（このファイルが参照するモジュール）:
  - `google.cloud.tasks_v2`（Cloud Tasks API）
- **⚠️ 呼び出し元**（このファイルを参照するファイル）:
  - application/messageManager.py（未処理）
- **変更内容**:
  - `from google.appengine.api import taskqueue` → `from google.cloud import tasks_v2`（Cloud Tasks API移行）
  - `taskqueue.Queue('mintask')` → `client.queue_path(project, location, queue)`
  - HTTP メソッド: POST で固定
  - パラメータ: URL エンコード形式で body に指定
  - プロジェクトID: `os.environ.get('GCP_PROJECT')` から取得
- **⚠️ 設定項目**:
  - location: 'asia-northeast1'（リージョン要確認）
  - queue: 'mintask'（Cloud Tasks キュー事前作成必須）
- **注意事項**: Task Queue → Cloud Tasks への重要な移行


### ✅ geo/geomodel.py
- **状態**: 完了
- **日時**: 2025-11-17 11:20:00
- **出力パス**: migration-src/geo/geomodel.py
- **依存関係**（このファイルが参照するモジュール）:
  - `geo.geocell`, `geo.geomath`, `geo.geotypes`, `geo.util`（同グループで処理済み）
- **⚠️ 呼び出し元**（このファイルを参照するファイル）:
  - application/models/bkdata.py（グループ6で処理済み）
- **変更内容**:
  - `#!/usr/bin/python2.5` → `#!/usr/bin/env python3`
  - `from google.appengine.ext import db` → `from google.cloud import ndb`
  - `db.Model` → `ndb.Model`
  - `db.GeoPtProperty` → `ndb.GeoPtProperty`
  - `db.StringListProperty` → `ndb.StringProperty(repeated=True)`
  - `cmp()` 関数廃止 → `functools.cmp_to_key()` でラップ
  - `query._Query__orderings` → `query._query_order`（ndb内部属性）
  - `query.filter(...) IN [...]` → `query.filter(Property.IN_(...))`（ndb構文）
- **注意事項**: 地理的位置検索の中核モジュール。テスト推奨


### ✅ application/models/bksearchensen.py
- **状態**: 完了
- **日時**: 2025-11-17 11:25:00
- **出力パス**: migration-src/application/models/bksearchensen.py
- **依存関係**（このファイルが参照するモジュール）:
  - `application.models.bksearchdata`（グループ9で処理済み）
- **⚠️ 呼び出し元**（このファイルを参照するファイル）:
  - application/models/bksearcheki.py（同グループで処理済み）
  - application/bksearchensenutl.py（グループ9で処理済み）
- **変更内容**:
  - `from google.appengine.ext import db` → `from google.cloud import ndb`
  - `db.Model` → `ndb.Model`
  - `db.ReferenceProperty` → `ndb.KeyProperty`
  - `db.StringProperty` → `ndb.StringProperty`
  - `db.FloatProperty` → `ndb.FloatProperty`
  - `db.IntegerProperty` → `ndb.IntegerProperty`
  - 相対インポート → 絶対インポート
- **注意事項**: 駅名検索用の沿線情報モデル


### ✅ application/models/bksearcheki.py
- **状態**: 完了
- **日時**: 2025-11-17 11:30:00
- **出力パス**: migration-src/application/models/bksearcheki.py
- **依存関係**（このファイルが参照するモジュール）:
  - `application.models.bksearchensen`（同グループで処理済み）
- **⚠️ 呼び出し元**（このファイルを参照するファイル）:
  - application/bksearchensenutl.py（グループ9で処理済み）
- **変更内容**:
  - `from google.appengine.ext import db` → `from google.cloud import ndb`
  - `db.Model` → `ndb.Model`
  - `db.ReferenceProperty` → `ndb.KeyProperty`
  - `db.StringProperty` → `ndb.StringProperty`
  - 相対インポート → 絶対インポート
- **注意事項**: 駅名情報モデル


### ✅ geo/geocell.py
- **状態**: 完了
- **日時**: 2025-11-17 11:35:00
- **出力パス**: migration-src/geo/geocell.py
- **依存関係**（このファイルが参照するモジュール）:
  - `geo.geomath`, `geo.geotypes`（同グループで処理済み）
- **⚠️ 呼び出し元**（このファイルを参照するファイル）:
  - geo/geomodel.py（同グループで処理済み）
- **変更内容**:
  - `#!/usr/bin/python2.5` → `#!/usr/bin/env python3`
  - `from functools import reduce` でインポート追加
  - `sorted(..., lambda ...)` で cmp 引数廃止 → 直接比較で実装
  - クラス定義・メソッド定義は変更なし（互換性あり）
- **注意事項**: Geocell 計算の中核。テスト推奨


### ✅ geo/geomath.py
- **状態**: 完了
- **日時**: 2025-11-17 11:40:00
- **出力パス**: migration-src/geo/geomath.py
- **依存関係**（このファイルが参照するモジュール）:
  - `geo.geotypes`（同グループで処理済み）
- **⚠️ 呼び出し元**（このファイルを参照するファイル）:
  - geo/geomodel.py, geo/geocell.py, geo/util.py（同グループで処理済み）
- **変更内容**:
  - `#!/usr/bin/python2.5` → `#!/usr/bin/env python3`
  - コメント内での db.GeoPt → ndb.GeoPt 記載に変更
  - 関数実装は変更なし（互換性あり）
- **注意事項**: 地理的距離計算。単純な数学計算のため低リスク


### ✅ geo/geotypes.py
- **状態**: 完了
- **日時**: 2025-11-17 11:45:00
- **出力パス**: migration-src/geo/geotypes.py
- **依存関係**（このファイルが参照するモジュール）:
  - なし（基本型定義のみ）
- **⚠️ 呼び出し元**（このファイルを参照するファイル）:
  - geo/geomath.py, geo/geocell.py, geo/util.py, geo/geomodel.py（全て同グループで処理済み）
- **変更内容**:
  - `#!/usr/bin/python2.5` → `#!/usr/bin/env python3`
  - クラス定義（Point, Box）は変更なし（互換性あり）
  - Python 3 互換性あり
- **注意事項**: 地理座標・矩形領域の基本型。低リスク


### ✅ geo/util.py
- **状態**: 完了
- **日時**: 2025-11-17 11:50:00
- **出力パス**: migration-src/geo/util.py
- **依存関係**（このファイルが参照するモジュール）:
  - `geo.geocell`, `geo.geomath`, `geo.geotypes`（同グループで処理済み）
- **⚠️ 呼び出し元**（このファイルを参照するファイル）:
  - geo/geomodel.py（同グループで処理済み）
- **変更内容**:
  - `#!/usr/bin/python2.5` → `#!/usr/bin/env python3`
  - `cmp()` 関数廃止 → `default_cmp()` 関数を内部に定義
  - `sorted(..., key=...)` で キー関数に変更
  - 関数シグネチャ変更なし（互換性あり）
- **注意事項**: Geocell ユーティリティ関数

---

## グループ 10 完了サマリー

処理ファイル数: 11
成功: 11
失敗: 0

**処理対象ファイル:**
1. application/email_decoder.py - メール解析ユーティリティ
2. application/CriticalSection.py - Memcache → Redis 移行
3. application/rotor.py - 暗号化ユーティリティ
4. application/tantochangetasks.py - Task Queue → Cloud Tasks API移行
5. geo/geomodel.py - db → ndb 移行
6. application/models/bksearchensen.py - db → ndb 移行
7. application/models/bksearcheki.py - db → ndb 移行
8. geo/geocell.py - Python 3構文対応
9. geo/geomath.py - Python 3 移行
10. geo/geotypes.py - Python 3 移行
11. geo/util.py - Python 3 移行

**主な変更内容:**
1. db.* → ndb.* への置き換え
2. memcache → redis への移行
3. Task Queue → Cloud Tasks API への移行
4. Python 2 → 3 構文対応
5. cmp() 廃止対応
6. urllib.* → urllib.parse.*

---

## Group 7 Completion (Application Utilities)

グループ7の5ファイル（view.py, timemanager.py, wordstocker.py, config.py, bkdataProvider.py）のマイグレーション完了


