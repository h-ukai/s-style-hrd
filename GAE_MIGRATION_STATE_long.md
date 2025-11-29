# GAE Python 2.7 → Python 3.11 マイグレーション状態

## 処理済み
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

## 未処理
- application/messageManager.py
- application/tantochange.py
- application/index.py
- models/member.py
- models/CorpOrg.py
- models/Branch.py
- session.py
- chkauth.py
- application/mapreducemapper.py
- models/bkdata.py
- models/bklist.py
- models/blob.py
- application/bklistutl.py
- application/view.py
- dataProvider/bkdataProvider.py
- application/timemanager.py
- application/wordstocker.py
- models/ziplist.py
- models/station.py
- models/message.py
- models/msgcombinator.py
- SecurePage.py
- GqlEncoder.py
- config.py
- models/bksearchaddress.py
- models/bksearchdata.py
- models/bksearchmadori.py
- dataProvider/bkdataSearchProvider.py
- application/bksearchensenutl.py
- models/address.py
- application/zipper.py
- qreki.py
- application/mailvalidation.py
- models/matchingdate.py
- models/matchingparam.py
- application/email_decoder.py
- application/CriticalSection.py
- wordstocker.py
- SecurePageBase.py

## マイグレーションルール

### プロジェクト全体の方針
- このプロジェクトは GAE Standard Python 2.7 から Python 3.11 へ移行する。
- webapp2 は Flask に置き換える。
- db.Model は google.cloud.ndb に置き換える。

### 決定事項
- **メール送信: SMTPをユーザー名とパスワードで直接操作する（`smtplib` を使用）。**
- **MapReduce: バッチ処理スクリプト + Cron で実装する（Cloud Dataflow は使用しない）。**
- **Task Queue: Cloud Tasks API (`google.cloud.tasks_v2`) に移行する。**
- **Session管理: Flask-Session (Datastore backend) を使用する。**
- **認証・セキュリティ: 現状のSHA256ハッシュをそのまま維持する（bcrypt等への移行は行わない）。**
- **テンプレートエンジン: Jinja2（Flask標準）を使用する。**
- **Datastore クライアントライブラリ: google.cloud.ndb を使用する。**
- **ロギング・モニタリング: 標準 logging + Cloud Logging 自動統合を使用する。**
- **app.yaml の runtime を `python27` から `python311` に変更する。**
- **app.yaml の `api_version` は Python 3 では不要なため削除する。**
- **app.yaml の `threadsafe` は Python 3 では不要なため削除する。**
- **app.yaml の `builtins` セクションは Python 3 では廃止されているため削除する（remote_api, appstats, deferred など）。**
- **app.yaml の `libraries` セクション（Django 1.4など）は Python 3 では廃止されているため、requirements.txt に移行する。**
- **app.yaml の `includes` (mapreduce/include.yaml) は Python 3 では非推奨。必要であれば別の方法で実装する。**
- **app.yaml のハンドラで `script: google.appengine.ext.*` を使用している箇所は、対応する Python 3 の実装に置き換える必要がある（remote_api, deferred, appstatsなど）。**
- **webapp2.WSGIApplication は Flask アプリケーションに置き換える。ルーティングは Flask の @app.route デコレータまたは add_url_rule を使用する。**
- **webapp2.RequestHandler を継承したクラスは、Flask の view 関数または MethodView クラスに置き換える。**
- **appengine_config.py の appstats middleware は Python 3 では使用できない。Cloud Trace や OpenTelemetry などの代替ソリューションを検討する。**
- **google.appengine.ext.appstats は Python 3 では利用できないため、Cloud Trace、Cloud Profiler、または OpenTelemetry に移行する。**
- **`from google.appengine.ext.appstats import recording` は削除し、Cloud Trace SDK または OpenTelemetry に置き換える。**
- **Python 2 の `dict.iteritems()` は Python 3 では `dict.items()` に置き換える。**
- **Python 2 の `random.random() < FRACTION` による確率的な処理は Python 3 でもそのまま使用可能。**
- **`isinstance(regex, str)` のチェックは Python 3 では unicode/str の区別がなくなったため、そのまま使用可能だが、bytes との区別に注意する。**
- **正規表現マッチングでの `re.match()` は Python 3 でもそのまま使用可能。**
- **環境変数 `RECAPTCHA_SITE_KEY` や `RECAPTCHA_SECRET_KEY` などは、app.yaml の env_variables から環境変数ファイル（.env）または Cloud Secret Manager に移行することを推奨する。**
- **inbound_services の `mail` は Python 3 では直接サポートされていない。SendGrid、Mailgun、Cloud Pub/Sub などの外部サービスに移行する必要がある。**
- **`/_ah/mail/.*` のようなメール受信エンドポイントは、外部メールサービスの Webhook に置き換える必要がある。**
- **`backends.yaml` は Python 3 では廃止されている。Backend API の代わりに、Cloud Tasks、Cloud Functions、または別の App Engine サービスを使用する。**
- **`backends.yaml` で定義されていた memdb や worker などのバックエンドインスタンスは、App Engine の Manual Scaling または Cloud Run に移行することを検討する。**
- **`corpzip.yaml` (bulkloader.yaml) は Python 3 では `google.appengine.ext.bulkload` が廃止されているため使用不可。データ移行には Cloud Datastore Admin の export/import、gcloud datastore export/import、または独自の移行スクリプトを使用する。**
- **`corpzip.yaml` で使用されている `google.appengine.ext.bulkload.transform` は Python 3 では利用不可。CSV インポートには pandas や csv モジュールを使用し、Datastore への書き込みは google.cloud.ndb または google.cloud.datastore クライアントライブラリを使用する。**
- **`corpzip.yaml` の `python_preamble` で import している `google.appengine.ext.db` は `google.cloud.ndb` に置き換える。ただし bulkloader 自体が廃止されているため、全体を再実装する必要がある。**
- **`cron.yaml` は Python 3 でもそのまま使用可能。フォーマットに変更はないが、呼び出されるエンドポイントが Flask などの新しいフレームワークで実装されている必要がある。**
- **`cron.yaml` で指定する URL エンドポイント（例: `/cron/cronjobs`）は、webapp2 から Flask への移行時にルーティングを正しく設定する必要がある。**
- **`dos.yaml` は Python 3 でもそのまま使用可能。DoS 保護設定は Cloud Armor に移行することも検討できるが、App Engine の dos.yaml も引き続きサポートされている。**
- **`autolistedindex.yaml` (index.yaml の自動生成版) は Python 3 でも使用可能だが、開発時に `gcloud datastore indexes create` コマンドでインデックスを作成する。**
- **Datastore の複合インデックスは Python 3 でも必要。index.yaml は引き続き使用し、`gcloud app deploy index.yaml` でデプロイする。**
- **`index.yaml` は Python 3 でもそのまま使用可能。Datastore クエリで複数プロパティを組み合わせたフィルタやソートを行う場合は、index.yaml で複合インデックスを定義する必要がある。**
- **`index.yaml` のフォーマット（kind, properties, direction など）は Python 2 と Python 3 で変更なし。既存の index.yaml をそのまま使用できる。**
- **`mapreduce.yaml` は Python 3 では `google.appengine.ext.mapreduce` が廃止されているため使用不可。MapReduce ジョブは Cloud Dataflow (Apache Beam) または Cloud Functions + Cloud Tasks に移行する必要がある。**
- **`mapreduce.yaml` で定義されていた mapper handler（例: `application.mapreducemapper.bkdataput`）は、Cloud Dataflow の DoFn または Cloud Functions の関数として再実装する。**
- **`mapreduce.input_readers.DatastoreInputReader` は Python 3 では利用不可。Datastore エンティティの一括処理には、`google.cloud.ndb` のクエリイテレータまたは Dataflow の DatastoreIO を使用する。**
- **`queue.yaml` は Python 3 でもそのまま使用可能。ただし、Task Queue API (`google.appengine.api.taskqueue`) は廃止されており、Cloud Tasks API (`google.cloud.tasks_v2`) に移行する必要がある。**
- **`queue.yaml` の設定（rate, bucket_size, max_concurrent_requests, retry_parameters など）は Cloud Tasks のキュー設定に移行する。gcloud コマンドまたは Cloud Console で設定する。**
- **Task Queue の `task_retry_limit`, `min_backoff_seconds`, `max_backoff_seconds`, `max_doublings` は Cloud Tasks の retry_config に対応する設定項目がある。**
- **webapp2.RequestHandler のコンストラクタ `__init__(self, request, response)` は Flask では不要。Flask では `request` はグローバルコンテキストから import し、`response` は view 関数の戻り値として返す。**
- **webapp2 の `self.request.get('param_name')` は Flask では `request.args.get('param_name')` (GET) または `request.form.get('param_name')` (POST) に置き換える。両方対応するには `request.values.get('param_name')` を使用する。**
- **webapp2 の `self.response.out.write(content)` は Flask では `return content` または `return render_template('template.html', **context)` に置き換える。**
- **`google.appengine.ext.webapp.template` は Python 3 では廃止。Flask の `render_template()` を使用し、テンプレートエンジンは Jinja2 に移行する。**
- **`template.render(path, template_values)` の置き換え: Flask では `render_template('template.html', **template_values)` を使用。テンプレートファイルは `templates/` ディレクトリに配置する。**
- **`os.path.join(os.getcwd(), 'templates', 'template.html')` のような絶対パス指定は不要。Flask は自動的に `templates/` ディレクトリを探す。**
- **Python 2 の `hashlib.sha256(string).hexdigest()` は Python 3 では `hashlib.sha256(string.encode()).hexdigest()` に変更。文字列を bytes に変換する必要がある。**
- **Python 2 の `urllib.quote_plus()` / `urllib.unquote_plus()` は Python 3 では `urllib.parse.quote_plus()` / `urllib.parse.unquote_plus()` に変更。**
- **Python 2 の `types.UnicodeType` は Python 3 では存在しない。Python 3 では `str` が Unicode 文字列であり、`isinstance(obj, str)` でチェックする。**
- **Python 2 の `unicode(text, encoding)` は Python 3 では `text.decode(encoding)` または `str(text, encoding)` に変更。ただし、Python 3 では bytes から str への変換が必要な場合のみ。**
- **Python 2 の `StringIO.StringIO` は Python 3 では `io.StringIO` (文字列用) または `io.BytesIO` (バイト列用) に変更。CSV 処理では `io.StringIO` を使用することが多い。**
- **CSV ファイルの読み込み: Python 2 では `csv.reader(StringIO(rawfile))` を使用したが、Python 3 では `csv.reader(io.StringIO(rawfile.decode('cp932')))` のように bytes を文字列にデコードする必要がある。**
- **Python 2 の `str.encode('raw_unicode_escape').decode('utf8')` のようなエンコーディング変換は Python 3 では不要な場合が多い。文字列は既に Unicode であるため。**
- **webapp2 の `self.redirect(url)` は Flask では `return redirect(url)` に置き換える。`from flask import redirect` で import する。**
- **GAE Python 2.7 の session ライブラリ（カスタム実装）は Flask のセッション機能 (`flask.session`) または Flask-Session 拡張に移行することを検討する。**
- **Datastore クエリの `Model.all()` は `google.cloud.ndb` では `Model.query()` に変更。filter メソッドの構文も変更される（例: `query.filter('property =', value)` → `Model.query(Model.property == value)`）。**
- **NDB クエリの filter で `=` を使う構文（`query.filter('property = ', value)`）は Python 3 の google.cloud.ndb では使用不可。`Model.query(Model.property == value)` の形式に変更する。**
- **`user.put()` による Datastore エンティティの保存は `google.cloud.ndb` でもそのまま使用可能。ただし、非同期処理が推奨される場合は `user.put_async()` を検討する。**
- **`Model.get_by_key_name(key_name)` は `google.cloud.ndb` では `ndb.Key(Model, key_name).get()` に変更。または `Model.get_by_id(key_name)` を使用する（key_name が文字列 ID の場合）。**
- **正規表現 `re.compile()` と `re.match()` は Python 3 でもそのまま使用可能。ただし、Unicode 文字列を扱う場合は `re.UNICODE` フラグが暗黙的に有効になる。**
- **`sys.exc_info()[0]` は Python 3 でもそのまま使用可能だが、例外ハンドリングには `except Exception as e:` を使い、`str(e)` や `type(e).__name__` で情報を取得する方が推奨される。**
- **`logging.error()` は Python 3 でもそのまま使用可能。ただし、GAE Python 3 では Cloud Logging に統合されるため、`google.cloud.logging` を使用することも検討する。**
- **Python 2 の例外構文 `except Exception, e:` は Python 3 では `except Exception as e:` に変更する。**
- **`urlfetch.fetch()` は Python 3 では廃止。`requests` ライブラリまたは標準ライブラリの `urllib.request` を使用する。reCAPTCHA検証などの外部API呼び出しは `requests.post()` に置き換える。**
- **reCAPTCHA v3 の実装: `urlfetch.POST` で `https://www.google.com/recaptcha/api/siteverify` を呼び出している箇所は、`requests.post(url, data=form_fields)` に置き換える。**
- **`urllib.quote_plus()` / `urllib.unquote_plus()` は Python 3 では `urllib.parse.quote_plus()` / `urllib.parse.unquote_plus()` にインポート元が変更されている。**
- **`urllib.urlencode()` は Python 3 では `urllib.parse.urlencode()` に変更する。**

### Blobstore の移行
- **`google.appengine.ext.blobstore` は Python 3 では廃止。Cloud Storage (GCS) に移行する必要がある。**
- **`blobstore.create_upload_url()` は廃止。Cloud Storage への直接アップロードまたは Signed URL を使用する。**
- **`blobstore_handlers.BlobstoreUploadHandler` は廃止。Flask の file upload 処理 (`request.files`) と Cloud Storage クライアントライブラリ (`google.cloud.storage`) を使用する。**
- **`blobstore_handlers.BlobstoreDownloadHandler` は廃止。Cloud Storage からのファイル配信は Signed URL または public URL を使用する。**
- **`blobstore.BlobInfo` は廃止。ファイルメタデータは Cloud Storage の blob metadata または独自の Datastore エンティティで管理する。**
- **`get_serving_url()` (画像サービング API) は Python 3 では廃止。Cloud Storage の公開 URL または Signed URL を使用し、画像リサイズが必要な場合は Cloud Functions や imgix などの外部サービスを検討する。**
- **Blobstore の `blob.key()` は Cloud Storage の blob name (ファイルパス) に置き換える。既存の blobKey を GCS オブジェクト名として使用することも可能。**
- **ファイルアップロード処理: `self.get_uploads('file')` は Flask の `request.files['file']` に置き換え、`blob.save(destination)` で一時保存後、Cloud Storage にアップロードする。**
- **画像のサムネイル生成: `get_serving_url(blob_key, size=100)` は廃止。Pillow (PIL) ライブラリでサムネイル生成し、GCS にアップロードするか、Cloud Functions で動的生成する。**
- **Blobstore からのファイル削除: `blobstore.delete(blob_key)` は GCS では `bucket.blob(blob_name).delete()` に置き換える。**
- **Blobstore の日本語ファイル名処理: `blobstore.BlobInfo.get(blob_key).filename` は自動的にデコードされたファイル名を返す。GCS では `blob.name` に UTF-8 エンコードされた名前を保存し、必要に応じてデコードする。**
- **ファイルアップロード時の `email.header.decode_header()` による日本語ファイル名デコード処理は、Flask の `request.files['file'].filename` が既に Unicode 文字列を返すため不要になる場合が多い。**
- **`db.Model` のプロパティとして `blobstore.BlobReferenceProperty` を使用している場合は、文字列プロパティに変更し、GCS のオブジェクト名（パス）を保存する。**

### GQL クエリの移行
- **`db.GqlQuery(query_str)` は `google.cloud.ndb` では廃止。NDB の Query API (`Model.query()`) を使用する。**
- **GQL の `SELECT * FROM Kind WHERE prop = 'value'` 構文は `Kind.query(Kind.prop == 'value')` に置き換える。**
- **GQL の `ORDER BY prop ASC` は `Kind.query().order(Kind.prop)` に置き換える。降順は `order(-Kind.prop)` を使用する。**
- **複数の WHERE 条件は複数の filter を chain するか、`query(Kind.prop1 == val1, Kind.prop2 == val2)` のように複数条件を渡す。**
- **GQL クエリの count() メソッドは NDB でも使用可能だが、大量データでは非効率。`query.count(limit=1000)` で上限を設定することを推奨する。**
- **GQL の `WHERE __key__ >= 'bookmark'` のようなキーベースのページネーションは NDB では `query.filter(Model._key >= ndb.Key(Model, 'bookmark'))` に置き換える。**
- **GQL の `DATETIME('YYYY-MM-DD HH:MM:SS')` 関数は NDB では使用不可。Python の `datetime.datetime()` オブジェクトを直接使用する。**
- **GQL での文字列結合（例: `WHERE prop = '" + value + "'`）は SQL インジェクションのリスクがある。NDB の Query API では値を直接渡すため安全。**

### メール送信の実装
- **`google.appengine.api.mail` は廃止。Python 3 では `smtplib` を使用してSMTPサーバーに直接接続する。**
- **SMTPサーバーの認証情報（ユーザー名、パスワード）は環境変数または Cloud Secret Manager で管理する。**
- **メール送信の実装例: `smtplib.SMTP()` または `smtplib.SMTP_SSL()` を使用し、`login()` と `sendmail()` メソッドで送信する。**

### MapReduce の移行
- **MapReduce ジョブはバッチ処理スクリプトとして実装し、Cron または手動実行で起動する。**
- **`mapreduce.yaml` で定義されていた処理（bkdataput, bkdlistupdate, bloburlschange, messageupdate）は、Python スクリプトとして再実装する。**
- **Datastore エンティティの一括処理は `google.cloud.ndb` のクエリイテレータ（`query.iter()`）を使用し、バッチで処理する。**
- **大量データ処理時はメモリ使用量に注意し、必要に応じてページネーション処理を実装する。**

### Task Queue / Cloud Tasks の移行
- **`google.appengine.api.taskqueue` は廃止。`google.cloud.tasks_v2.CloudTasksClient` を使用する。**
- **`taskqueue.add()` は `client.create_task()` に置き換える。タスクのペイロードは HTTP リクエスト形式で指定する。**
- **`queue.yaml` の設定は Cloud Tasks のキュー設定に移行する。`gcloud tasks queues create` または Cloud Console で設定する。**
- **Cloud Tasks の HTTP ターゲットは App Engine サービスの URL を指定する（例: `https://[PROJECT_ID].appspot.com/task-handler`）。**
- **リトライ設定は `retry_config` パラメータで指定する（`max_attempts`, `min_backoff`, `max_backoff`, `max_doublings`）。**

### Session 管理の実装
- **カスタムの `session` / `dbsession` モジュールは Flask-Session に置き換える。**
- **Flask-Session のバックエンドは Datastore（NDB）を使用する。カスタム Session Interface の実装が必要。**
- **セッションデータの保存先は既存の Datastore エンティティ構造を維持するか、新しいエンティティモデルを定義する。**
- **`flask.session` を使用してセッションデータにアクセスする（例: `session['user_id'] = user.memberID`）。**
- **セッションID（SID）の生成と管理は Flask-Session が自動的に処理する。**

### テンプレートエンジン（Jinja2）の移行
- **Django テンプレート構文から Jinja2 構文への変更が必要な場合がある。**
- **主な違い: 変数は `{{ variable }}` で同じだが、タグ構文が異なる（例: Django `{% if %}` → Jinja2 `{% if %}` は同じ）。**
- **フィルタの構文は類似しているが、一部のフィルタ名が異なる場合がある。既存テンプレートの動作確認が必要。**
- **テンプレートの継承（`{% extends %}`）やインクルード（`{% include %}`）は Jinja2 でも同様に使用可能。**

### Datastore / NDB の実装
- **`google.cloud.ndb` を使用する。`from google.cloud import ndb` でインポートする。**
- **NDB クライアントの初期化: App Engine 環境では自動的に初期化されるが、ローカル開発では `ndb.Client()` を明示的に作成する。**
- **NDB のコンテキスト: `with client.context():` ブロック内で NDB 操作を実行する（App Engine では不要）。**
- **トランザクション: `@ndb.transactional` デコレータまたは `ndb.transaction()` 関数を使用する。**
- **非同期処理: `put_async()`, `get_async()`, `delete_async()` などの非同期メソッドが利用可能。`yield` または `await` で結果を取得する。**

### ロギングの実装
- **標準の `logging` モジュールをそのまま使用する（`import logging`）。**
- **GAE Python 3 環境では、`logging` の出力が自動的に Cloud Logging に転送される。**
- **ログレベル（DEBUG, INFO, WARNING, ERROR, CRITICAL）は通常通り使用可能。**
- **構造化ログが必要な場合は `google.cloud.logging` クライアントを使用することも可能。**

### Memcache の移行
- **`google.appengine.api.memcache` は Python 3 では廃止。Cloud Memorystore (Redis) または `google.cloud.memcache` に移行する。**
- **`memcache.set(key, value)` は Redis では `redis_client.set(key, value)` に置き換える。**
- **`memcache.get(key)` は Redis では `redis_client.get(key)` に置き換える。ただし、Redis は bytes を返すため、必要に応じてデコードする。**
- **簡易的なキャッシュが必要な場合は、Flask-Caching または Python の `functools.lru_cache` を検討する。**

### バッチ処理とページネーション
- **大量の Datastore エンティティを処理する場合は、`query.fetch(limit)` でバッチ処理し、カーソルを使用してページネーションする。**
- **META HTTP-EQUIV REFRESH を使用した自動リロード処理は、Cloud Tasks または Cloud Scheduler + バッチスクリプトに移行することを推奨する。**
- **`query.count()` は大量データでは非効率。可能な限り避けるか、`count(limit=N)` で上限を設定する。**
- **プログレス表示が必要な場合は、処理状況を Datastore に保存し、別のエンドポイントで確認する方式を検討する。**

### Python 2 から Python 3 への構文変更
- **Python 2 の `<>` 演算子（非等価）は Python 3 では `!=` に置き換える。`if resdata <> "":` は `if resdata != "":` に変更する。**
- **Python 2 の `except Exception, e:` は Python 3 では `except Exception as e:` に変更する（カンマではなく `as` を使用）。**
- **Python 2 の `re.compile().match(str, 1)` の第2引数（開始位置）は Python 3 では非推奨。`re.compile().match(str)` または `re.search()` を使用する。**

### Memcache の使用パターン
- **`from google.appengine.api import memcache` は Python 3 では廃止。Cloud Memorystore (Redis) に移行する。**
- **`memcache.set()`, `memcache.get()` は Redis クライアントの同等メソッドに置き換える。または Flask-Caching を使用する。**

### Mail API の使用パターン
- **`from google.appengine.api import mail` は Python 3 では廃止。`smtplib` または SendGrid などの外部メールサービスに移行する。**
- **`mail.EmailMessage()` の置き換え: `smtplib` の `MIMEText` または `EmailMessage` クラスを使用する。**
- **`message.sender`, `message.to`, `message.subject`, `message.body` の設定は `EmailMessage` オブジェクトの同等プロパティに置き換える。**
- **`message.send()` は `smtplib.SMTP.sendmail()` または `send_message()` に置き換える。**

### GQL クエリのセキュリティと移行
- **GQL での文字列結合（`"SELECT * FROM Kind WHERE prop = '" + value + "'"`）は SQL インジェクションのリスクがある。NDB の Query API (`Kind.query(Kind.prop == value)`) を使用すれば安全。**
- **`db.GqlQuery(query_str)` は `google.cloud.ndb` では廃止。NDB の Query API に移行する。**
- **GQL の `SELECT __key__` クエリは、NDB では `query.fetch(keys_only=True)` に置き換える。**

### JSON エンコーディングとレスポンス
- **Python 2 の `simplejson` は Python 3 では標準ライブラリの `json` モジュールに統合されている。`import simplejson` を `import json` に置き換える。**
- **カスタム JSON エンコーダ（`GqlJsonEncoder` など）は、Python 3 の `json.JSONEncoder` を継承して再実装する。**
- **`ensure_ascii=False` オプションは Python 3 の `json.dumps()` でもそのまま使用可能。日本語を含むデータを JSON 化する際に必須。**

### webapp2 のリクエスト・レスポンス処理
- **`self.request.arguments()` はすべてのクエリパラメータ・フォームフィールドのキーを返す。Flask では `request.values.keys()` または `request.form.keys()` + `request.args.keys()` を使用する。**
- **複数値の取得: webapp2 の `self.request.get_all('key')` は Flask では `request.form.getlist('key')` または `request.args.getlist('key')` に置き換える。**
- **`self.response.headers['Content-Type']` は Flask では `response.headers['Content-Type']` または `return jsonify(data)` で自動設定される。**

### datetime とタイムゾーン処理
- **JST から UTC への変換（`timemanager.jst2utc_date()`）は、Python 3 では `datetime.timezone` または `pytz` ライブラリを使用して実装する。**
- **UTC から JST への変換（`timemanager.utc2jst_date()`）も同様に `pytz` または `zoneinfo` (Python 3.9+) を使用する。**
- **`datetime.datetime.strptime()` は Python 3 でもそのまま使用可能。日付文字列のパース処理は変更不要。**

### JSONP サポート
- **JSONP レスポンス（`callback(...)` 形式）は、Flask では `jsonify()` の代わりに手動で文字列を組み立てるか、Flask-JSONPIFY 拡張を使用する。**
- **`self.request.get("callback")` でコールバック関数名を取得し、レスポンスを `callback_name(json_data)` の形式で返す処理は、Flask でも同様に実装可能。**

### db.Model から google.cloud.ndb への移行（補足）
- **`Model.get_or_insert(key_name)` は `google.cloud.ndb` でもそのまま使用可能。指定されたキー名のエンティティが存在しない場合は新規作成する。**
- **`db.Key(key_string)` は `ndb.Key(urlsafe=key_string)` に置き換える。ただし、`key_string` が urlsafe 形式の場合。レガシー形式の場合は変換が必要。**
- **`str(entity.key())` は `entity.key.urlsafe().decode()` に置き換える（NDB では `key` がプロパティであり、メソッドではない）。**
- **`db.get(key_list)` による複数エンティティの一括取得は、NDB では `ndb.get_multi(key_list)` に置き換える。**

### SelfReferenceProperty の扱い
- **`db.SelfReferenceProperty` は同じモデル内の別エンティティへの参照。NDB では `ndb.KeyProperty(kind='ModelName')` として定義する。**
- **参照の設定: `entity.tanto = db.Key(key_string)` は `entity.tanto = ndb.Key(urlsafe=key_string)` に置き換える。**
- **循環参照のチェック（`str(memdb.key()) != tanto`）は、NDB でも同様に `memdb.key.urlsafe() != tanto_key.urlsafe()` で実装する。**

### StringListProperty の扱い
- **`db.StringListProperty` は NDB でも `ndb.StringProperty(repeated=True)` として定義する。**
- **リストの初期化: `entity.service = []` のように空リストを代入する処理は NDB でもそのまま使用可能。**
- **カンマ区切り文字列の分割（`service.split(",")`）と StringListProperty への保存は、Python 3 でもそのまま動作する。**

### カスタムベースクラス（SecurePage）の移行
- **`SecurePage` などのカスタム RequestHandler 基底クラスは、Flask の `before_request` フック、デコレータ、またはカスタム View クラスに置き換える。**
- **`Secure_init()` メソッドでの認証チェックは、Flask のデコレータ関数（例: `@login_required`）として実装し直すことを推奨する。**
- **`self.tmpl_val` のようなテンプレート変数ディクショナリは、Flask では view 関数内でローカル変数として管理し、`render_template()` に渡す。**

### Memcache のクリティカルセクション（ロック処理）
- **`memcache.get()` と `memcache.set()` を使った排他制御は、Redis の `SETNX` や `GETSET` コマンドを使用したロック機構に移行する。**
- **カスタムの `CriticalSection` クラスは、Redis の分散ロック（例: `redis.lock()` または `redlock` パターン）に置き換える。**
- **`memcache.add(key, value, time)` は Redis の `SET key value EX seconds NX` に対応する。**
- **ロックの解放忘れを防ぐため、`try-finally` ブロックまたは Python の `with` 文を使用してロック解放を保証する。**

### Memcache のカウンター処理
- **`memcache.incr(key)` / `memcache.decr(key)` は Redis の `INCR` / `DECR` コマンドに置き換える。**
- **カウンターの初期化処理（`memcache.add(key, initial_value)`）は Redis の `SETNX` または `SET key value NX` で実装する。**
- **タイムアウト付きカウンター（例: `memcache.set(key, value, 60*90)`）は Redis の `SETEX` コマンドを使用する。**

### GQL クエリでの `__key__` の取得
- **`db.GqlQuery("SELECT __key__ FROM Model WHERE ...")` は NDB では `Model.query(...).fetch(keys_only=True)` に置き換える。**
- **`keys_only=True` を指定することで、エンティティの Key のみを取得でき、パフォーマンスが向上する。**
- **取得した Key から実際のエンティティを取得する場合は `ndb.get_multi(key_list)` を使用する。**

### Task Queue のターゲット指定（Backend / Module）
- **Python 2.7 の `taskqueue.Task(..., target="memdb2")` の `target` パラメータは、App Engine のバックエンドまたはモジュールを指定している。**
- **Python 3 では App Engine のバックエンドは廃止されており、Cloud Tasks の `http_request.url` で適切なサービス URL を指定する必要がある。**
- **マルチサービス構成の場合は、`https://[SERVICE]-dot-[PROJECT_ID].appspot.com/task-endpoint` のように URL を構築する。**
- **Cloud Tasks では `service_account_email` を指定して認証を行う。App Engine のデフォルトサービスアカウントまたはカスタムサービスアカウントを使用する。**

### InboundMailHandler の移行
- **`google.appengine.ext.webapp.mail_handlers.InboundMailHandler` は Python 3 では廃止。受信メールの処理は外部メールサービス（SendGrid、Mailgun、Cloud Pub/Sub）の Webhook に移行する。**
- **`InboundMailHandler.post()` メソッドは、Flask の POST エンドポイントとして再実装し、Webhook からのリクエストを処理する。**
- **`self.request.body` で取得した MIME エンコードメールは、Python 3 の `email` モジュール（`email.parser.BytesParser`）でパースする。**
- **受信メールのルーティング（`/_ah/mail/[address]`）は、外部サービスの Webhook 設定で代替する。メールアドレスごとの振り分けはアプリケーション側で実装する。**

### CORS (Cross-Origin Resource Sharing) の設定
- **webapp2 の `self.response.headers['Access-Control-Allow-Origin'] = '*'` は Flask では `@app.after_request` デコレータまたは Flask-CORS 拡張を使用して設定する。**
- **OPTIONS メソッドのハンドリング: webapp2 の `options()` メソッドは Flask では `@app.route(..., methods=['OPTIONS'])` で実装する。**
- **Flask-CORS を使用する場合: `from flask_cors import CORS; CORS(app)` で簡単に CORS を有効化できる。**
- **セキュリティのため、本番環境では `Access-Control-Allow-Origin` にワイルドカード `*` ではなく、信頼できるオリジンを明示的に指定することを推奨する。**

### POST データの内部構造への直接アクセス
- **webapp2 の `self.request.POST.multi._items` による内部データ構造への直接アクセスは非推奨。Flask では `request.form.items()` を使用する。**
- **`for n, v in self.request.POST.multi._items:` は Flask では `for key, value in request.form.items():` に置き換える。**
- **複数値フィールドの取得は `request.form.getlist('key')` を使用する。**
- **フォームデータとクエリパラメータの両方を取得する場合は `request.values.items()` を使用する。**

### Cron ジョブのエンドポイント実装
- **`cron.yaml` で指定されたエンドポイント（例: `/cron/cronjobs`）は、Flask のルーティングで実装する。**
- **Cron ハンドラは通常の GET/POST リクエストとして実装し、`@app.route('/cron/cronjobs', methods=['GET'])` のように定義する。**
- **Cron ジョブの認証: App Engine の Cron サービスからのリクエストは `X-Appengine-Cron: true` ヘッダーが付与される。このヘッダーをチェックして不正アクセスを防ぐ。**
- **Cron ハンドラ内で長時間処理を行う場合は、Cloud Tasks を使用してバックグラウンドタスクに委譲することを推奨する。**

### 大量データ処理のページネーション
- **`query.fetch(100000000)` のような極端に大きな limit 指定は非効率。カーソルベースのページネーションを使用する。**
- **NDB のカーソル: `query.fetch_page(page_size, start_cursor=cursor)` を使用して段階的にデータを取得する。**
- **処理を複数のタスクに分割する場合は、Cloud Tasks でタスクを順次実行し、各タスクで一部のデータを処理する。**
- **バッチサイズ（例: 500件ずつ処理）は、メモリ使用量とレイテンシのバランスを考慮して適切に設定する。**

### Task Queue の複数キュー管理
- **`taskqueue.Queue('queue_name')` で特定のキューにタスクを追加する処理は、Cloud Tasks の `client.queue_path(project, location, queue_name)` で同様に実装する。**
- **`queue.yaml` で定義した複数のキュー（例: `mintask`, `oneshotmintask`）は、Cloud Tasks でも同じ名前のキューを作成して使用できる。**
- **Cloud Tasks のキュー作成: `gcloud tasks queues create queue_name --location=region` コマンドで作成する。**
- **キューごとの rate limit や retry パラメータは Cloud Tasks のキュー設定で管理する。**

### リダイレクト処理
- **webapp2 の `self.redirect(url)` は Flask では `return redirect(url)` に置き換える。`from flask import redirect` が必要。**
- **リダイレクト後の処理を停止するため、`return` を明示的に記述することが重要（Flask では `redirect()` を return しないと処理が継続される）。**

### テストコードとデバッグ処理
- **`print` 文によるデバッグ出力は、Python 3 では `print()` 関数に変更する。ただし、本番コードでは `logging` モジュールの使用を推奨する。**
- **開発用のテストハンドラ（`application/test.py` など）は、本番デプロイ時に無効化するか、適切なアクセス制御を設定する。**

### テンプレートパスの構築方法
- **`os.path.dirname(__file__) + '/../templates/xxx.html'` のような相対パス指定は、Flask では `render_template('xxx.html')` に置き換え、テンプレートは `templates/` ディレクトリに配置する。**
- **`os.path.join(os.getcwd(), 'templates', corp_name, branch_name, sitename, 'xxx.html')` のような動的パス生成は、Flask の `render_template()` でサブディレクトリを指定する形式（`'corp_name/branch_name/sitename/xxx.html'`）に置き換える。**

### POSTデータの取得方法
- **webapp2 の `self.request.POST.multi._items` による内部データ構造への直接アクセスは非推奨。Flask では `request.form.items()` または `request.form.getlist()` を使用する。**
- **複数値の取得: `self.request.POST.multi._items` でインデックスアクセスしている箇所は、Flask の `request.form` 辞書を使用して安全にアクセスする。または `request.form.to_dict(flat=False)` で全データを取得する。**
- **`for n, v in self.request.POST.multi._items:` のようなループは、`for key in request.form.keys():` + `request.form.get(key)` または `request.form.items()` に置き換える。**

### URL パスパラメータの解析
- **`self.request.path.split('/')` による手動パス解析は、Flask のルーティング機能（`@app.route('/show/<corp>/<branch>/<sitename>/<command>/<filename>')`）を使用して自動的にパラメータを取得することを推奨する。**
- **`pathParts[2]`, `pathParts[3]` のようなインデックスアクセスは、Flask の URL パラメータ（`<corp>`、`<branch>` など）として定義し、view 関数の引数で受け取る方が安全。**
- **URL クエリパラメータと組み合わせる場合は、`request.args.get('id')` などで取得する（webapp2 と同様）。**

### Datastore クエリの filter と all() の移行
- **`db.Model.all()` は `google.cloud.ndb` では `Model.query()` に変更する。**
- **`query.filter('property', value)` の形式は NDB では `query.filter(Model.property == value)` に変更する。**
- **複数の filter を連続で呼び出す場合（`query.filter('prop1', val1).filter('prop2', val2)`）は、NDB でも同様にメソッドチェーンが可能（`query.filter(Model.prop1 == val1).filter(Model.prop2 == val2)`）。**
- **`filter('property !=', value)` は NDB では `filter(Model.property != value)` に変更する。**
- **`filter('property =', value)` の `=` 演算子（等号と空白）は NDB では使用不可。`==` を使用する。**

### Datastore の fetch() と count() の移行
- **`query.fetch(limit, offset)` は NDB でもそのまま使用可能。ただし、offset は非推奨でカーソルベースのページネーションが推奨される。**
- **大量データの fetch: `fetch(1000, 0)` のように大きな limit を指定している場合は、カーソルを使った段階的な取得に移行することを推奨する。**
- **`query.count()` は NDB でもそのまま使用可能だが、大量データでは非効率。`count(limit=1000)` で上限を設定することを推奨する。**

### リストのソート処理
- **Python リストの `sort(key=lambda x: x.property, reverse=True)` は Python 3 でもそのまま使用可能。**
- **Datastore クエリの `order()` とリストの `sort()` を組み合わせている場合（例: クエリで一次ソート後、Python でカスタムソート）は、NDB でも同様の手法が使用可能。**
- **複数プロパティでのソート: Datastore では複合インデックスが必要。または、fetch 後に Python の `sort()` で複数キーを指定する（`sort(key=lambda x: (x.prop1, x.prop2))`）。**

### Unicode 文字列リテラル (u"...")
- **Python 2 の `u"..."` リテラルは Python 3 では不要（すべての文字列がデフォルトで Unicode）。ただし、Python 3 でも `u"..."` 構文は互換性のために許容されている。**
- **マイグレーション時は `u"..."` をそのまま残しても動作するが、クリーンアップ時に `"..."` に置き換えることを推奨する。**

### 条件式での `in` 演算子
- **`if value in [val1, val2, val3]:` の構文は Python 3 でもそのまま使用可能。**
- **Datastore クエリの IN 演算子（`filter('property IN', [val1, val2])`）は、NDB では `filter(Model.property.IN([val1, val2]))` に変更する。**

### datetime 操作とタイムゾーン
- **`datetime.datetime.now()` は Python 3 でもそのまま使用可能。ただし、タイムゾーンを考慮する場合は `datetime.now(tz=timezone.utc)` を使用する。**
- **Datastore に保存される datetime プロパティは、NDB でも UTC で保存される。表示時に JST に変換する処理が必要な場合は `pytz` または `zoneinfo` を使用する。**

### URL エンコーディング
- **`urllib.quote_plus()` は Python 3 では `urllib.parse.quote_plus()` に変更する。**
- **`urllib.unquote_plus()` は Python 3 では `urllib.parse.unquote_plus()` に変更する。**
- **`self.request.query_string` は Flask では `request.query_string` でアクセス可能（bytes 型で返される）。文字列として扱う場合は `.decode()` が必要。**

### カスタム JSON エンコーダの移行
- **`GqlEncoder` のようなカスタム JSON エンコーダは、Python 3 の `json.JSONEncoder` を継承して再実装する。**
- **`GQLmoneyfmt()` や `floatfmt()` のような独自のフォーマット関数は、NDB エンティティを JSON シリアライズ可能な形式に変換する処理として再実装する。**
- **NDB の `DateTimeProperty`, `KeyProperty`, `FloatProperty` などは、JSON 化時に適切な型に変換する処理が必要（例: `datetime` → ISO 8601 文字列、`Key` → urlsafe 文字列）。**

### ユーザーエージェントの取得
- **`self.request.user_agent` は Flask では `request.user_agent` または `request.headers.get('User-Agent')` でアクセスする。**
- **Flask の `request.user_agent` はオブジェクトを返し、`request.user_agent.string` で文字列を取得する。**

### GQL クエリでの SQL インジェクション対策
- **GQL クエリで文字列結合を使用している箇所（例: `"SELECT * FROM member WHERE service = '" + service + "'"`）は SQL インジェクションのリスクがある。NDB の Query API を使用すれば安全（`member.query(member.service == service)`）。**
- **`WHERE` 句の動的構築で `where += " WHERE" if where == "" else " AND"` のような処理は、NDB では複数の `filter()` 呼び出しをチェーンすることで実現する。**
- **GQL の `u"CorpOrg_key_name = '" + CorpOrg_key_name + u"'"` は NDB では `Model.query(Model.CorpOrg_key_name == CorpOrg_key_name)` に置き換える。**

### Mail API の複数受信者への送信
- **GAE Python 2 の `mail.EmailMessage()` で `message.to = email` を設定し、ループ内で `message.send()` を繰り返し呼び出す処理は、Python 3 では `smtplib` で同様に実装する。**
- **`message.sender`, `message.reply_to`, `message.subject`, `message.body` の設定は、`smtplib` の `EmailMessage` クラスの `['From']`, `['Reply-To']`, `['Subject']`, `set_content()` に対応する。**
- **`message.sender = '"' + name + '" <' + email + '>'` の形式（表示名付き）は、Python 3 の `email.utils.formataddr()` を使用して `formataddr((name, email))` として構築する。**

### Django simplejson から標準 json への移行
- **`from django.utils import simplejson` は Python 3 では `import json` に置き換える。simplejson は標準ライブラリに統合されている。**
- **`simplejson.JSONEncoder` を継承したカスタムエンコーダは、`json.JSONEncoder` を継承して再実装する。`default()` メソッドのオーバーライド方法は同じ。**
- **`simplejson.JSONEncoder.default(self, obj)` の呼び出しは `json.JSONEncoder.default(self, obj)` に置き換える。**

### Python 2 の unicode() 関数の移行
- **`unicode(text, encoding)` は Python 3 では `text.decode(encoding)` に置き換える（text が bytes の場合）。または `str(text, encoding)` を使用する。**
- **`unicode(text, encoding, errors='replace')` は Python 3 では `text.decode(encoding, errors='replace')` に置き換える。**
- **CSV ファイルの Shift-JIS エンコーディング処理: `unicode(text, 'cp932')` は `text.decode('cp932')` に変更する。**

### StringIO の移行
- **`from StringIO import StringIO` は Python 3 では `from io import StringIO` に変更する。**
- **CSV 処理での `csv.reader(StringIO(rawfile))` は、Python 3 では rawfile が bytes の場合、`csv.reader(io.StringIO(rawfile.decode('cp932')))` のようにデコードが必要。**
- **`StringIO` は文字列用、`BytesIO` はバイト列用。CSV ファイルのアップロード処理では通常 `StringIO` を使用する。**

### Task Queue から Cloud Tasks への移行（具体例）
- **`taskqueue.Queue('queue_name')` は Cloud Tasks では `CloudTasksClient()` を使用してキューを指定する。**
- **`taskqueue.Task(url='/tasks/handler', params={...})` は Cloud Tasks では `create_task()` メソッドで HTTP リクエストとして構築する。**
- **Task の params は Cloud Tasks では `http_request.body` に URL エンコードされた形式またはJSON形式で設定する。**
- **`queue.add(task)` は `client.create_task(request={"parent": queue_path, "task": task})` に置き換える。**
- **Cloud Tasks のキューパスは `client.queue_path(project, location, queue)` で構築する（例: `projects/my-project/locations/us-central1/queues/oneshotmintask`）。**

### 正規表現の match() メソッドの第2引数
- **`re.compile().match(str, 1)` の第2引数（開始位置）は Python 3 では非推奨。代わりに `re.compile().match(str[1:])` のようにスライスするか、`re.search()` を使用する。**
- **日付パターンマッチング（`re.compile(".*/.*/.* .*:.*:.*").match(timestr, 1)`）は、`match(timestr)` に変更し、必要に応じて文字列の先頭から検証する。**

### db.Key() と ndb.Key() の変換
- **`db.Key(key_string)` は `ndb.Key(urlsafe=key_string)` に置き換える（urlsafe 形式の場合）。**
- **`db.get(key_string)` は `ndb.Key(urlsafe=key_string).get()` に置き換える。**
- **`str(entity.key())` は `entity.key.urlsafe().decode()` に置き換える（NDB では `key` がプロパティで、urlsafe() は bytes を返す）。**

### カスタム RequestHandler の初期化メソッド
- **webapp2 の `__init__(self, request, response)` と `initialize(request, response)` は Flask では不要。Flask では view 関数またはクラスベースビュー（`MethodView`）を使用する。**
- **`self.tmpl_val = {}` のようなテンプレート変数の初期化は、Flask では view 関数内で行う。**
- **カスタムベースクラス（`SecurePageBase` など）の初期化処理は、Flask のデコレータまたは `before_request` フックに移行する。**

### URL パスからのパラメータ抽出
- **`self.request.path.split('/')` による手動のパス解析は、Flask の URL ルーティング（`@app.route('/<corp_name>/<branch_name>/<sitename>')`）を使用して自動的にパラメータを取得することを推奨する。**
- **`pathParts[2]`, `pathParts[3]` のようなインデックスアクセスは、Flask の URL 変数として定義し、view 関数の引数で受け取る方が安全で保守性が高い。**

### セッション管理のカスタム実装
- **`dbsession(request, response, session_name)` のようなカスタム session クラスは、Flask-Session に移行することを検討する。**
- **`chkauth()` メソッドによる認証チェックは、Flask のデコレータ（`@login_required` など）として実装し直すことを推奨する。**
- **`get_ssn_data()`, `set_ssn_data()` のような session データアクセスは、Flask では `session['key']` で直接アクセスする。**

### Task Queue のリトライ処理
- **`self.request.headers.environ.get('HTTP_X_APPENGINE_TASKRETRYCOUNT')` でリトライ回数を取得する処理は、Cloud Tasks では `request.headers.get('X-CloudTasks-TaskRetryCount')` に置き換える。**
- **リトライ回数の上限チェック（例: `> 5`）は、Cloud Tasks の `retry_config.max_attempts` で設定することを推奨する。ただし、ハンドラ内でのチェックも可能。**
- **リトライ失敗時のエラーハンドリング（例: エラーメッセージの保存）は、Flask のエンドポイント内で同様に実装する。**

### db.Model.all() の keys_only オプション
- **`member.all(keys_only=True)` は NDB では `member.query().fetch(keys_only=True)` に置き換える。**
- **`keys_only=True` を指定することで、Key のみを取得し、ネットワーク転送量とコストを削減できる。**
- **取得した Key から実際のエンティティを取得する場合は `db.get(key_list)` → `ndb.get_multi(key_list)` を使用する。**

### Query の run() メソッド
- **`query.run()` はクエリの結果をイテレータとして返す。NDB でもそのまま使用可能だが、`query.iter()` または `query.fetch()` の使用を推奨する。**
- **`for entity in query.run():` は NDB では `for entity in query.iter():` に置き換えることを推奨する。**
- **大量データの処理では `iter()` を使用することでメモリ効率が向上する。**

### datetime.timedelta() を使った日付計算
- **`datetime.timedelta(days=N)` による日付計算は Python 3 でもそのまま使用可能。**
- **`now - timedelta(30)` のような過去の日付計算は、フィルタ条件（例: `kknnngp < s30_days_ago`）と組み合わせて使用できる。**
- **UTC/JST の変換が必要な場合は、カスタムの `timemanager` モジュールまたは `pytz` ライブラリを使用する。**

### os.path.isfile() によるテンプレートファイルの存在チェック
- **`os.path.isfile(template_path)` は Python 3 でもそのまま使用可能。**
- **複数のテンプレートパスを優先順位付きでチェックする処理（例: 会社別→支店別→デフォルト）は、Flask でも同様に実装できる。**
- **テンプレートファイルが見つからない場合のエラーハンドリング（例: IOError のキャッチ）は、Python 3 では `FileNotFoundError` を使用することを推奨する。**

### BKlist クエリのフィルタリング
- **`bklist.filter("issend = ", True)` の構文は NDB では `bklist.filter(BKlist.issend == True)` に置き換える。**
- **複数の filter を連続で適用する処理（例: `filter("issend = ", True).filter("sended = ", False)`）は、NDB でもメソッドチェーンで同様に実装できる。**
- **`filter("prop = ", value)` の `=` 演算子（等号と空白）は NDB では使用不可。`==` を使用する。**

### リストのソート（lambda 式）
- **`list.sort(key=lambda obj: obj.property)` は Python 3 でもそのまま使用可能。**
- **降順ソートの場合は `list.sort(key=lambda obj: obj.property, reverse=True)` を使用する。**
- **複数プロパティでのソートは `sort(key=lambda obj: (obj.prop1, obj.prop2))` のようにタプルを使用する。**

### sys.exc_info() によるエラー情報の取得
- **`sys.exc_info()[0]`, `sys.exc_info()[1]` は Python 3 でもそのまま使用可能だが、`except Exception as e:` で例外をキャッチし、`type(e).__name__`, `str(e)` で情報を取得する方が推奨される。**
- **ログ出力時は `logging.exception()` を使用することで、スタックトレースも含めて自動的に記録できる。**

### config モジュールの環境変数管理
- **`config.ADMIN_EMAIL`, `config.BASE_URL` などの設定値は、環境変数（`.env` ファイル）または Cloud Secret Manager に移行することを推奨する。**
- **Flask では `os.environ.get('ADMIN_EMAIL')` または `app.config['ADMIN_EMAIL']` で環境変数を取得する。**
- **機密情報（メールパスワード、API キーなど）は Cloud Secret Manager で管理し、`google.cloud.secretmanager` ライブラリで取得する。**