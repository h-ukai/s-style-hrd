# GAE Python 2.7 → Python 3.11 マイグレーション状態

**このファイルの役割:**
- マイグレーションルールの対象範囲を記録
- 「処理済み」= マイグレーションルールでカバー済み（実際のファイル変換は未完了）
- 「未処理」= マイグレーションルールの記載が不足している可能性がある

**実際のファイル変換状況は `migration-progress.md` を参照してください。**

## マイグレーションルールでカバー済み（実際の変換は migration-progress.md を参照）
- app.yaml
- main.py
- appengine_config.py
- setting.py
- autolistedindex.yaml
- backends.yaml
- corpzip.yaml
- cron.yaml
- dos.yaml
- index.yaml
- mapreduce.yaml
- queue.yaml
- application/login.py
- application/logout.py
- application/regist.py
- application/proc.py
- application/bkedit.py
- application/blobstoreutl.py
- application/handler.py
- application/RemoveAll.py
- application/uploadbkdata.py
- application/uploadbkdataformaster.py
- application/duplicationcheck.py
- application/json.py
- application/memberedit.py
- application/test.py
- application/bksearch.py
- application/follow.py
- application/mypage.py
- application/bkjoukyoulist.py
- application/bkdchk.py
- application/addresslist.py
- application/show.py
- application/mailinglist.py
- application/SecurePageBase.py
- application/GqlEncoder.py
- application/uploadaddressset.py
- application/memberSearchandMail.py
- application/bksearchutl.py
- application/cron.py
- application/sendmsg.py
- application/email_receiver.py
- application/matching.py
- application/messageManager.py
- application/tantochange.py
- application/index.py
- application/models/member.py
- application/models/CorpOrg.py
- application/models/Branch.py
- application/session.py
- application/chkauth.py
- application/mapreducemapper.py
- application/models/bkdata.py
- application/models/bklist.py
- application/models/blob.py
- application/bklistutl.py
- application/view.py
- dataProvider/bkdataProvider.py
- application/timemanager.py
- application/wordstocker.py
- application/models/ziplist.py
- application/models/station.py
- application/models/message.py
- application/models/msgcombinator.py
- application/SecurePage.py
- application/GqlEncoder.py
- application/config.py
- application/models/bksearchaddress.py
- application/models/bksearchdata.py
- application/models/bksearchmadori.py
- dataProvider/bkdataSearchProvider.py
- application/bksearchensenutl.py
- application/models/address.py
- application/zipper.py
- application/qreki.py
- application/mailvalidation.py
- application/models/matchingparam.py
- application/models/matchingdate.py
- application/email_decoder.py
- application/CriticalSection.py
- application/rotor.py
- application/tantochangetasks.py
- geo/geomodel.py
- application/models/bksearchensen.py
- application/models/bksearcheki.py
- geo/geocell.py
- geo/geomath.py
- geo/geotypes.py
- geo/util.py

## マイグレーションルールの追加検討が必要

## マイグレーションルール

### プロジェクト全体の方針
- このプロジェクトは GAE Standard Python 2.7 から Python 3.11 へ移行する。
- webapp2 は Flask に置き換える。
- db.Model は google.cloud.ndb に置き換える。

### 決定事項（方針選択）

**アーキテクチャ選択:**
- メール送信: SMTP直接操作（`smtplib`）
  - 理由: 既存の独自SMTP実装との互換性維持、外部サービス依存回避
  - 送信元: 代表メールアドレス（全メンバー共通）
- メール受信: IMAP定期ポーリング（Cron 10分間隔）
  - 理由: サードパーティ不要、GAE無料枠内で完結、レンタルサーバー標準機能活用
  - 方式: `imaplib`で代表メールアドレスのメールボックス監視、既存`email_decoder`で解析
  - 受信先: 代表メールアドレス（全メンバー共通、キャッチオール不要）
  - メール保持: 受信メールはメールボックスから削除しない（既読フラグのみ）
  - 遅延: 最大10分（業務上許容範囲）
- MapReduce: バッチ処理スクリプト + Cron
  - 理由: Cloud Dataflowは過剰、既存処理ロジック活用可能
- Task Queue: Cloud Tasks API (`google.cloud.tasks_v2`)
- Session管理: Flask-Session (Datastore backend)
  - 理由: 既存のDatastoreセッションモデル活用
- 認証: SHA256ハッシュ維持（bcrypt移行なし）
- Datastore: `google.cloud.ndb`
- ロギング: 標準 `logging` + Cloud Logging 自動統合

**フレームワーク:**
- webapp2 → Flask
- テンプレート: Jinja2

**app.yaml変更:**
- `runtime: python311`
- 削除項目: `api_version`, `threadsafe`, `builtins`, `libraries`, `includes`

---

### 大幅変更箇所

**Blobstore → Cloud Storage (GCS) 完全移行:**
- `blobstore.create_upload_url()` → GCS Signed URL
- `BlobstoreUploadHandler` → Flask `request.files` + GCS client
- `get_serving_url()` → GCS public URL / Signed URL
- `BlobReferenceProperty` → 文字列プロパティ（GCSオブジェクト名保存）
- `BlobMigrationRecord.get_new_blob_key()` → GCS移行時のKey変換ロジック廃止

**StringIO → io (Python 3標準ライブラリ移行):**
- `StringIO.StringIO()` → `io.BytesIO()` (バイナリデータ用) または `io.StringIO()` (テキストデータ用)
- ZIPファイル等のバイナリストリーム処理: `io.BytesIO()` 使用

**webapp2レスポンス → Flask:**
- webapp2 `response.headers["Content-Type"]` → Flask `Response.headers["Content-Type"]`
- webapp2 `response.out.write()` → Flask `return` 文でレスポンス本体返却
- webapp2 `response.headers['Content-Disposition']` → Flask `Response.headers['Content-Disposition']`

**Memcache → Cloud Memorystore (Redis):**
- `memcache.set/get()` → `redis_client.set/get()`
- ロック処理: `memcache.add()` → Redis `SET NX EX`
- カウンター: `memcache.incr()/decr()` → Redis `INCR/DECR`
- セッションストレージ: `memcache.set(sid, session_obj)` → Redis hash構造またはFlask-Session (Datastore backend)
- クリティカルセクション実装: `CriticalSection` クラスで `memcache.incr/decr()` によるロックを使用 → Redis `INCR/DECR` またはRedis分散ロック（`SET NX EX`）に移行

**Task Queue → Cloud Tasks:**
- キューパス: `client.queue_path(project, location, queue)`
- タスク作成: `client.create_task(request={...})`
- HTTPターゲット: `https://[PROJECT_ID].appspot.com/task-handler`
- リトライヘッダー: `X-CloudTasks-TaskRetryCount`
- タスク作成（旧形式）: `taskqueue.Queue('queuename').add(taskqueue.Task(url='/path', params={...}, target='backend'))` → Cloud Tasks API

**Mail API → smtplib + IMAP:**
- **送信**: `mail.EmailMessage()` → `smtplib` + `email.message.EmailMessage`
  - 表示名: `email.utils.formataddr((name, email))`
  - SMTP送信: `smtplib.SMTP()` でSMTPサーバー接続
  - 送信元: 代表メールアドレス（全メンバー共通）
  - **件名タグ**: `[MemberID:123]` 形式でメンバーID埋め込み（返信追跡用）
  - **In-Reply-To/Referencesヘッダー**: メンバーID含む独自Message-ID形式（例: `<memberid-123-timestamp@domain>`）
- **受信**: `InboundMailHandler`（GAE固有機能）廃止 → IMAP定期ポーリング
  - 既存実装: `/_ah/mail/.*` で `corp_memberID@appspotmail.com` 形式を受信
  - 移行後: 代表メールアドレスで一括受信、メンバーID追跡で振り分け
  - **受信データ解析**: `email_decoder.py` を継続活用（標準 `email` ライブラリベース、Python 3対応必要）
  - **メンバーID追跡方式（優先順位順）**:
    1. **In-Reply-To/References ヘッダー**: メッセージIDからメンバーID抽出（`<memberid-123-...@domain>` 形式）
    2. **件名タグ**: `[MemberID:123]` 形式から抽出
    3. **送信元メールアドレス検索**: Datastoreでメールアドレス → メンバーID検索
       - 複数メンバーID発見時: **全メンバーIDの履歴に受信記録を保存**
       - 未登録メールアドレス: 保存しない（メーラーアプリが）
  - **メールボックス管理**: 受信メールは削除せず既読フラグ（`\Seen`）付与せずメーラーアプリに任せる
  - **メールパース**: `email.message_from_string()` 継続使用、`email.header.decode_header()` / `email.utils.getaddresses()` 活用
---

### モジュール間統一仕様

**Datastoreクエリ:**
- `Model.all()` → `Model.query()`
- フィルタ: `Model.query(Model.property == value)`
- Keys取得: `query.fetch(keys_only=True)`
- 複数取得: `ndb.get_multi(key_list)`
- 位置情報検索: `geo.geomodel.GeoModel` 継承モデルで `update_location()` 使用（緯度経度検索機能）
  - `db.Model` → `ndb.Model` に変更必要（`geo/geomodel.py` は `db.Model` ベース、ndb移行が必要）
  - `db.GeoPtProperty` → `ndb.GeoPtProperty`
  - `db.StringListProperty` → `ndb.StringProperty(repeated=True)`
- `db.ReferenceProperty` → `ndb.KeyProperty(kind='ModelName')`（関連エンティティはKeyで参照、`.get()`で取得）
- `db.SelfReferenceProperty` → `ndb.KeyProperty(kind='ModelName')`（自己参照も同様にKeyで保存）
- `db.GqlQuery("SELECT * FROM Model WHERE ...")` → `Model.query().filter(Model.property == value)`

**Key操作:**
- 文字列化: `entity.key.urlsafe().decode()`
- 復元: `ndb.Key(urlsafe=key_string)`
- 取得: `ndb.Key(Model, key_name).get()`

**Flask移行:**
- リクエスト: `request.args.get()` (GET) / `request.form.get()` (POST) / `request.values.get()` (両方)
- レスポンス: `return content` / `return redirect(url)` / `return render_template()`
- セッション: `flask.session['key']`
- Cookie設定: `response.set_cookie(key, value, expires=..., secure=...)` (webapp2の `headers.add_header('Set-Cookie', ...)` から移行)
- P3Pヘッダー: `response.headers['P3P'] = 'CP=CAO PSA OUR'`
- テンプレート: webapp2 `template.render(path, dict)` → Flask `render_template(filename, **dict)`
- ハンドラー出力: webapp2 `self.response.out.write()` → Flask `return` 文

**Cloud Tasks統一:**
- キュー作成: `gcloud tasks queues create QUEUE_NAME --location=REGION`
- `queue.yaml`設定 → Cloud Tasksキュー設定に移行
- 認証: `service_account_email` 指定

**GCS統一:**
- Blob名: 既存blobKey互換または新規命名規則
- メタデータ: Datastore独自エンティティで管理
- 日本語ファイル名: UTF-8エンコード保存

**セキュリティ:**
- Cronエンドポイント: `X-Appengine-Cron: true` ヘッダーチェック
- CORS: Flask-CORS使用または `@app.after_request` で設定
- 本番環境: `Access-Control-Allow-Origin` はワイルドカード禁止

**datetime/timezone:**
- カスタム`timemanager`継続使用 または `pytz`/`zoneinfo`
- Datastore保存: UTC
- 表示: JST変換

**環境変数:**
- 機密情報: Cloud Secret Manager
- 一般設定: `.env` または `app.config`
- `os.environ['REMOTE_ADDR']`: Flask `request.remote_addr`
- `os.environ['HTTP_ACCEPT_LANGUAGE']`: Flask `request.headers.get('Accept-Language')`

**JSON処理統一:**
- ライブラリ: 標準 `json` 使用（`simplejson`からの完全移行）
- 日本語データ: `json.dumps(data, ensure_ascii=False)` 必須
- カスタムエンコーダ: `json.JSONEncoder` 継承で統一実装
- 型変換ルール:
  - `datetime` → ISO 8601文字列 (`isoformat()`)
  - `ndb.Key` → urlsafe文字列 (`key.urlsafe().decode()`)
  - `float` → 文字列化が必要な場合は明示的に変換
- デコード: `json.loads(data)` でUnicode文字列として扱う

**文字エンコーディング統一:**
- CSV入力: `cp932` (Shift-JIS)
- CSV処理: `io.StringIO(rawfile.decode('cp932'))`
- メール本文: `utf-8` (SMTPヘッダーは必要に応じて `ISO-2022-JP`)
- URL: `urllib.parse.quote_plus/unquote_plus` (UTF-8)
- ハッシュ化: `string.encode('utf-8')` → `hashlib.sha256()`

**datetime文字列フォーマット統一:**
- 保存形式: ISO 8601 (`datetime.isoformat()`)
- 表示形式: 既存フォーマット維持 or 統一ルール決定
- パース: `datetime.fromisoformat()` or `strptime()`

**Datastore Key文字列化統一:**
- 統一形式: `key.urlsafe().decode()` (bytes → str)
- 復元: `ndb.Key(urlsafe=key_string)`
- レガシーキー: 変換処理を別途実装
- Key名パターン: `{corp_name}/{branch_name}/{id}` 形式継続使用

**MIME/Content-Type統一:**
- JSON API: `application/json; charset=utf-8`
- HTML: `text/html; charset=utf-8`
- CSV: `text/csv; charset=utf-8`
- JSONP: `application/javascript; charset=utf-8`

**国際化(i18n):**
- `gettext` ライブラリ継続使用（標準Python機能）
- テンプレート内メッセージ: Jinja2の `_()` 関数で翻訳
- 言語リソース: `locale/` ディレクトリ配下にPOファイル配置

**CSVデータ処理統一:**
- 入力エンコーディング: `cp932`
- 出力エンコーディング: `utf-8` (または `cp932` 継続)
- 区切り文字: カンマ `,` 継続
- 改行: LF `\n` (Pythonデフォルト)

**トランザクション処理統一:**
- `db.run_in_transaction(func)` → `ndb.transaction(func)` または `@ndb.transactional` デコレータ
- 連番生成等のアトミック操作に使用
- 例: `memberID_max_num` カウンタインクリメント

**Python 2→3 互換性（geoライブラリ）:**
- `cmp()` 関数: Python 3で削除 → `functools.cmp_to_key()` または比較演算子 (`<`, `>`, `==`) で代替
- `reduce()`: Python 3で組み込み関数から削除 → `functools.reduce()` をインポート

**メール送受信統一仕様:**
- **送信アドレス体系**: 代表メールアドレス1つで全メンバー対応（メンバーごとの個別アドレス廃止）
- **受信アドレス体系**: 代表メールアドレス1つで全受信を集約
- **メンバーID識別方法（3段階優先順位）**:
  1. **In-Reply-To/References ヘッダー**: Message-IDからメンバーID抽出（`<memberid-123-timestamp@domain>` 形式）
  2. **件名タグ**: `[MemberID:123]` 形式から抽出
  3. **送信元メールアドレス**: Datastoreでメールアドレス → メンバーID検索
- **メールアドレス→メンバーID検索ルール**:
  - 1対1対応: 該当メンバーIDに受信履歴保存
  - 1対多対応（複数メンバーIDが同じメールアドレス登録）: **全メンバーIDの履歴に受信記録を保存**
  - 未登録: デフォルトメンバーID（例: `corp/test222`）に保存
- **送信メール記録**:
  - Message-ID にメンバーID埋め込み（`<memberid-123-timestamp@domain>` 形式）
  - 件名に `[MemberID:123]` 自動付与（ヘッダー追跡失敗時の保険）
  - Datastoreへの記録不要（Message-ID自体にメンバーID含む）
- **受信メール処理**:
  - IMAP `UNSEEN` フラグで未処理メール取得
  - 処理後は `\Seen` フラグ付与（削除しない）
  - Message-ID で重複チェック（同一メールの再処理防止）
- **Cron設定**: 10分間隔で `/tasks/check-incoming-mail` 実行