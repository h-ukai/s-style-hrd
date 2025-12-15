# Python 2.7 → Python 3.11 マイグレーション修正カタログ

このドキュメントは、GAE Python 2.7 から Python 3.11 へのマイグレーション中に発見された問題と修正パターンをカタログ化したものです。

---

## 1. NDB コンテキスト管理

### 問題
Cloud NDB では、すべてのデータベース操作がコンテキスト内で実行される必要がある。Python 2.7 の App Engine NDB では自動的にコンテキストが管理されていたが、Cloud NDB では明示的なコンテキスト管理が必要。

### エラーメッセージ
```
google.cloud.ndb.exceptions.ContextError: No current context.
NDB calls must be made in context established by google.cloud.ndb.Client.context.
```

### 修正パターン（main.py）
```python
from flask import Flask, g
from google.cloud import ndb

ndb_client = ndb.Client()
app = Flask(__name__)

@app.before_request
def before_request():
    """リクエスト前に NDB コンテキストを開始"""
    g.ndb_context = ndb_client.context()
    g.ndb_context.__enter__()

@app.teardown_request
def teardown_request(exception=None):
    """リクエスト後に NDB コンテキストをクリーンアップ"""
    if hasattr(g, 'ndb_context'):
        try:
            g.ndb_context.__exit__(None, None, None)
        except:
            pass
```

### 注意点
- `ndb_client.context()` を呼び出すたびに新しいコンテキストが作成される
- `flask.g` オブジェクトを使って同じコンテキストを保持する必要がある
- `before_request` で開始したコンテキストと `teardown_request` で終了するコンテキストが同じである必要がある

---

## 2. ReferenceProperty → KeyProperty（逆参照の消失）

### 問題
Python 2.7 の `db.ReferenceProperty` は `collection_name` パラメータで逆参照プロパティを自動的に作成していたが、Cloud NDB の `ndb.KeyProperty` はこの機能をサポートしていない。

### Python 2.7（旧コード）
```python
class msgcombinator(db.Model):
    refmes = db.ReferenceProperty(reference_class=Message, collection_name="refmemlist")
# これにより Message に message.refmemlist という逆参照が自動的に作成される
```

### エラーメッセージ
```
AttributeError: 'Message' object has no attribute 'refmemlist'
```

### 修正パターン
逆参照を使用している箇所を明示的なクエリに置き換える：

**修正前：**
```python
comblist = message.refmemlist
```

**修正後：**
```python
comblist = msgcombinator.query(msgcombinator.refmes == message.key).fetch()
```

### 該当ファイル
- `application/messageManager.py` - `getmemlist()`, `chkmes()` メソッド

---

## 3. ReferenceProperty → KeyProperty（エンティティ取得）

### 問題
Python 2.7 の `db.ReferenceProperty` はプロパティにアクセスすると自動的にエンティティを取得していたが、Cloud NDB の `ndb.KeyProperty` は Key オブジェクトを返すため、明示的に `.get()` を呼び出す必要がある。

### エラーメッセージ
```
AttributeError: 'Key' object has no attribute 'makedata'
```

### 修正パターン
**修正前：**
```python
bkl.refbk.makedata("web")
```

**修正後：**
```python
bk_entity = bkl.refbk.get() if bkl.refbk else None
if bk_entity:
    bk_entity.makedata("web")
```

### 該当ファイル
- `application/index.py` - `getdatabyID()` 関数
- その他、`ReferenceProperty` を使用していたすべてのファイル

---

## 4. Django テンプレート → Jinja2 テンプレート

### 問題
Flask は Jinja2 テンプレートエンジンを使用するが、元のコードは Django テンプレート構文を使用していた。

### 4.1 default フィルター

**エラーメッセージ：**
```
jinja2.exceptions.TemplateSyntaxError: expected token 'end of print statement', got ':'
```

**修正パターン：**
| Django | Jinja2 |
|--------|--------|
| `{{value\|default:""}}` | `{{value\|default("")}}` |
| `{{value\|default:"N/A"}}` | `{{value\|default("N/A")}}` |
| `{{value\|default_if_none:""}}` | `{{value\|default("")}}` |

**注意：** Django の `default_if_none` は値が `None` の場合のみデフォルト値を使用するが、Jinja2 の `default` は falsy な値（`None`, `""`, `0`, `False`）すべてに対応。動作が若干異なるが、多くの場合問題ない。

### 4.2 floatformat フィルター

**エラーメッセージ：**
```
TypeError: type str doesn't define __round__ method
```

**修正パターン：**
| Django | Jinja2 |
|--------|--------|
| `{{value\|floatformat:"-2"}}` | `{{value\|float\|round(2)}}` |
| `{{value\|floatformat}}` | `{{value\|float\|int}}` または削除 |
| `{{value\|floatformat\|default:""}}` | `{{value\|default("")}}` |

**注意：** 値が文字列の場合は `|float` で数値に変換してから `|round(2)` を適用する

### 4.3 join フィルター

**修正パターン：**
| Django | Jinja2 |
|--------|--------|
| `{{list\|join:" "}}` | `{{list\|join(" ")}}` |

### 一括置換コマンド（sed相当）
```
|default:"" → |default("")
|default_if_none:"" → |default("")
|floatformat:"-2" → |float|round(2)
|floatformat|default("") → |default("")
|join:" " → |join(" ")
```

### 該当ファイル
- `templates/index.html` - 修正済み
- `templates/followpagebase.html` - 修正済み

### 未修正ファイル（default_if_none 変換が必要）
以下のファイルは対応するルートがアクセスされた時点でエラーになる：

| ファイル | 出現数 |
|---------|--------|
| bkedit.html | 342 |
| address2.html | 50 |
| bksearch.html | 50 |
| memberedit.html | 43 |
| s-style/hon/backoffice/bksearch.html | 41 |
| bkdchk.html | 35 |
| s-style/hon/www.chikusaku-mansion.com/mypagemydata.html | 22 |
| blobstoreutl.html | 14 |
| s-style/hon/www.chikusaku-mansion.com/mypagesearch.html | 14 |
| memberSearchandMail.html | 11 |
| addresslist.html | 9 |
| matching.html | 7 |
| その他 16 ファイル | 51 |
| **合計** | **689** |

---

## 5. dispatch.yaml ルーティング

### 問題
`*/test/*` パターンは `/test/xxx` にマッチするが、`/test` 単体にはマッチしない。

### 修正パターン
```yaml
dispatch:
  # /test 単体（末尾スラッシュなし）
  - url: "*/test"
    service: test-service
  # /test/ 以下のすべてのパス
  - url: "*/test/*"
    service: test-service
```

### Flask 側の対応
```python
@app.route('/test', methods=['GET', 'POST'])
@app.route('/test/', methods=['GET', 'POST'])
def test():
    return test_route()
```

---

## 6. Flask Blueprint による URL プレフィックス

### 問題
dispatch.yaml で `/test/*` を test-service にルーティングしているが、Flask のルート定義には `/test` プレフィックスがないため、`/test/login` などのパスが 404 になる。

### エラーメッセージ
```
HTTP 404 Not Found
```

### 原因
dispatch.yaml はリクエストを正しいサービスにルーティングするが、Flask アプリケーションは元のパス（`/test/login`）でリクエストを受け取る。Flask ルートが `/login` のみで定義されている場合、マッチしない。

### 修正パターン（main.py）
Blueprint を使用して URL プレフィックスを追加：

**修正前：**
```python
from flask import Flask
app = Flask(__name__)

@app.route('/login', methods=['GET', 'POST'])
def login():
    return login_route()
```

**修正後：**
```python
from flask import Flask, Blueprint
app = Flask(__name__)

# Blueprint で /test プレフィックスを設定
test_bp = Blueprint('test', __name__, url_prefix='/test')

@test_bp.route('/login', methods=['GET', 'POST'])
def login():
    return login_route()

# Blueprint をアプリに登録
app.register_blueprint(test_bp)
```

### 注意点
- すべての `@app.route` を `@test_bp.route` に変更する
- ルートパスは `/test` を含めない（Blueprint が自動的に追加する）
- `app.register_blueprint(test_bp)` を忘れずに追加する
- `before_request` と `teardown_request` は `app` に残す（グローバルミドルウェア）

### 該当ファイル
- `main.py` - すべてのルート定義

---

## 7. 今後発生する可能性のある問題

### 7.1 その他のテンプレートフィルター
| Django | Jinja2 |
|--------|--------|
| `{{value\|date:"Y-m-d"}}` | `{{value.strftime("%Y-%m-%d")}}` |
| `{{value\|time:"H:i"}}` | `{{value.strftime("%H:%M")}}` |
| `{{value\|truncatewords:30}}` | `{{value\|truncate(150, True)}}` |
| `{{value\|linebreaks}}` | カスタムフィルターまたは `|replace("\n", "<br>")` |
| `{{value\|safe}}` | `{{value\|safe}}` （同じ） |
| `{% url 'name' %}` | `{{url_for('name')}}` |

### 7.2 モデル関連
- `db.SelfReference` → `ndb.KeyProperty(kind='SameModel')`
- `db.ListProperty` → `ndb.StringProperty(repeated=True)` など
- `db.BlobProperty` → `ndb.BlobProperty()` または Cloud Storage

### 7.3 その他の逆参照パターン
`collection_name` を使用している他のモデルを検索：
```bash
grep -rn "collection_name" src/application/models/
```

---

## チェックリスト

新しいエンドポイントを移行する際のチェックリスト：

- [ ] NDB コンテキストミドルウェアが設定されているか
- [ ] `ReferenceProperty` の逆参照を使用していないか
- [ ] `KeyProperty` でエンティティ取得時に `.get()` を呼んでいるか
- [ ] テンプレートの Django 構文が Jinja2 に変換されているか
- [ ] dispatch.yaml で末尾スラッシュあり/なし両方がルーティングされているか

---

## 修正履歴

| 日付 | バージョン | 修正内容 |
|------|-----------|----------|
| 2025-11-30 | 20251130t134300 | followpagebase.html default_if_none→default()変換 |
| 2025-11-30 | 20251130t133025 | SecurePageBase.py /testプレフィックス対応、follow pathルート追加 |
| 2025-11-30 | 20251130t132149 | login.py dbsession引数修正（余分なNone削除） |
| 2025-11-30 | 20251130t124932 | SecurePage.py, proc.py 認証リダイレクト先を /test/login に変更 |
| 2025-11-30 | 20251130t122144 | login.html テンプレート変数形式に修正 |
| 2025-11-30 | 20251130t120901 | main.py Blueprint追加（/test/*ルート対応） |
| 2025-11-30 | 20251130t115551 | index.html Jinja2対応（floatformat修正） |
| 2025-11-30 | 20251130t115201 | index.html Django→Jinja2変換 |
| 2025-11-30 | 20251130t114656 | index.py refbk.get()修正 |
| 2025-11-30 | 20251130t114237 | messageManager.py refmemlist修正 |
| 2025-11-30 | 20251130t113641 | main.py NDBコンテキストをg使用に修正 |
| 2025-11-30 | 20251130t113229 | main.py /test→index_route() |
| 2025-11-30 | 20251130t112545 | dispatch.yaml /testルール追加 |
| 2025-11-29 | 20251129t145226 | NDBコンテキストミドルウェア追加 |
