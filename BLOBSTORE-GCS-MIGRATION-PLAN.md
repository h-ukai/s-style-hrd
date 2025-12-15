# Blobstore → Cloud Storage 移行プラン

## 概要

本ドキュメントは、migration-src のコードを Cloud Storage (GCS) 対応に修正するための実装プランです。

- **対象**: `migration-src/` (Python 3.11)
- **前提**: 調査報告書 `BLOBSTORE-GCS-MIGRATION-RESEARCH.md` を参照

---

## フェーズ1: 前準備

### 1.1 GCS バケット作成

```bash
# バケット作成
gsutil mb -l asia-northeast1 gs://s-style-hrd-blobs

# CORS 設定（ブラウザからの直接アップロード用）
gsutil cors set cors.json gs://s-style-hrd-blobs
```

**cors.json**:
```json
[
  {
    "origin": ["https://s-style-hrd.appspot.com", "http://localhost:8080"],
    "method": ["GET", "PUT", "POST", "DELETE"],
    "responseHeader": ["Content-Type", "Content-Disposition"],
    "maxAgeSeconds": 3600
  }
]
```

### 1.2 依存パッケージ追加

**requirements.txt に追加**:
```
google-cloud-storage>=2.10.0
```

### 1.3 環境変数設定

**app.yaml に追加**:
```yaml
env_variables:
  GCS_BUCKET_NAME: "s-style-hrd-blobs"
```

---

## フェーズ2: モデル移行

### 2.1 bloblist.py の移行

**対象ファイル**: `migration-src/application/models/bloblist.py` (新規作成)

**作業内容**:
1. `src/application/models/bloblist.py` をコピー
2. `from google.appengine.ext import db` → `from google.cloud import ndb` に変更
3. `db.Model` → `ndb.Model` に変更
4. `db.StringProperty` → `ndb.StringProperty` に変更
5. `db.IntegerProperty` → `ndb.IntegerProperty` に変更
6. `db.DateTimeProperty` → `ndb.DateTimeProperty` に変更
7. `db.run_in_transaction` → `@ndb.transactional` デコレータに変更

### 2.2 blob.py への GCS 関連プロパティ追加（オプション）

**対象ファイル**: `migration-src/application/models/blob.py`

**検討事項**:
- `gcs_object_name` プロパティの追加（移行期間中の併用）
- 既存の `blobKey` を GCS object name として再利用するか検討

---

## フェーズ3: GCS ユーティリティモジュール作成

### 3.1 新規ファイル作成

**対象ファイル**: `migration-src/application/gcs_utils.py` (新規作成)

**実装機能**:

```python
# 実装予定の関数一覧
def get_gcs_client():
    """GCS クライアントを取得"""

def upload_to_gcs(file_obj, object_name, content_type=None):
    """ファイルを GCS にアップロード"""

def download_from_gcs(object_name):
    """GCS からファイルをダウンロード"""

def delete_from_gcs(object_name):
    """GCS からファイルを削除"""

def generate_signed_url(object_name, expiration=3600, method='GET'):
    """Signed URL を生成"""

def generate_upload_signed_url(object_name, expiration=3600, content_type=None):
    """アップロード用 Signed URL を生成"""

def get_public_url(object_name):
    """公開 URL を取得（公開バケットの場合）"""

def generate_thumbnail_url(object_name, size=100):
    """サムネイル URL を生成（将来的に Cloud Functions 連携）"""
```

---

## フェーズ4: ハンドラー修正

### 4.1 blobstoreutl.py の修正

**対象ファイル**: `migration-src/application/blobstoreutl.py`

#### 4.1.1 blobstore_utl_route() の修正

| 行番号 | 現在のコード | 修正後 |
|--------|------------|--------|
| 38-39 | `upload_url = "/upload/" + keypath` | `upload_url = generate_upload_signed_url(...)` |
| 72-73 | `/gcs-serve/` プレースホルダー | `get_public_url()` または `generate_signed_url()` |

#### 4.1.2 upload_route() の修正

| 行番号 | 現在のコード | 修正後 |
|--------|------------|--------|
| 169-175 | `request.files.get('file')` 後の処理 | `upload_to_gcs()` を呼び出し |
| 236-237 | `/gcs-serve/` プレースホルダー | `get_public_url()` |

#### 4.1.3 delete_blob() の修正

| 行番号 | 現在のコード | 修正後 |
|--------|------------|--------|
| 296-300 | `pass` プレースホルダー | `delete_from_gcs()` を呼び出し |

#### 4.1.4 serve_route() の修正

| 行番号 | 現在のコード | 修正後 |
|--------|------------|--------|
| 318-326 | 501 を返す | `download_from_gcs()` でストリーミング or Signed URL リダイレクト |

### 4.2 handler.py の修正

**対象ファイル**: `migration-src/application/handler.py`

#### 4.2.1 file_upload_route() の修正

| 行番号 | 現在のコード | 修正後 |
|--------|------------|--------|
| 51-62 | プレースホルダー | `upload_to_gcs()` を呼び出し |

#### 4.2.2 delete_file_route() の修正

| 行番号 | 現在のコード | 修正後 |
|--------|------------|--------|
| 125-127 | `pass` プレースホルダー | `delete_from_gcs()` を呼び出し |

#### 4.2.3 file_download_route() の修正

| 行番号 | 現在のコード | 修正後 |
|--------|------------|--------|
| 181-186 | 501 を返す | `download_from_gcs()` or Signed URL |

#### 4.2.4 generate_upload_url_route() の修正

| 行番号 | 現在のコード | 修正後 |
|--------|------------|--------|
| 207-210 | プレースホルダー | `generate_upload_signed_url()` を呼び出し |

### 4.3 mapreducemapper.py の修正

**対象ファイル**: `migration-src/application/mapreducemapper.py`

#### 4.3.1 bloburlschange() の修正

| 行番号 | 現在のコード | 修正後 |
|--------|------------|--------|
| 121-122 | `YOUR_BUCKET` プレースホルダー | `get_public_url()` を使用 |
| 143 | `/serve/` URL | `generate_signed_url()` を使用 |

---

## フェーズ5: ルーティング登録

### 5.1 main.py の修正

**対象ファイル**: `migration-src/main.py`

**作業内容**:

1. インポートのコメント解除:
```python
from application.blobstoreutl import blobstore_utl_route, upload_route, serve_route
from application import handler
```

2. ルート登録の追加:
```python
# Blobstore/GCS routes
@test_bp.route('/BlobstoreUtl/<corp_org_key>/<branch_key>/<bk_id>')
def blobstore_utl(corp_org_key, branch_key, bk_id):
    return blobstore_utl_route(corp_org_key, branch_key, bk_id)

@test_bp.route('/upload/<corp_org_key>/<branch_key>/<bk_id>', methods=['POST'])
@test_bp.route('/upload/<corp_org_key>/<branch_key>/<bk_id>/<blob_no>', methods=['POST'])
def upload(corp_org_key, branch_key, bk_id, blob_no=None):
    return upload_route(corp_org_key, branch_key, bk_id, blob_no)

@test_bp.route('/serve/<path:blob_key>')
def serve(blob_key):
    return serve_route(blob_key)

# FileUploadFormHandler routes
@test_bp.route('/FileUploadFormHandler')
def file_upload_form():
    return handler.file_upload_form_route()

@test_bp.route('/FileUploadFormHandler/upload', methods=['POST'])
def file_upload():
    return handler.file_upload_route()

# ... 他のルート
```

---

## フェーズ6: テンプレート修正

### 6.1 blobstoreutl.html の修正

**対象ファイル**: `migration-src/templates/blobstoreutl.html`

**修正箇所**:

| 行番号 | 現在のコード | 修正後 |
|--------|------------|--------|
| 54 | `default_if_none:""` | `default('')` |
| 57 | `default_if_none:""` | `default('')` |
| 59 | `default_if_none:""` | `default('')` |
| 61 | `default_if_none:""` | `default('')` |
| 81-95 | `default_if_none:""` | `default('')` |

---

## フェーズ7: テストと検証

### 7.1 単体テスト

1. `gcs_utils.py` の各関数のテスト
2. アップロード → Datastore保存 → 表示 の流れ
3. 削除機能のテスト

### 7.2 統合テスト

1. テスト環境へのデプロイ
2. ブラウザからのアップロードテスト
3. 画像表示テスト
4. ファイルダウンロードテスト

### 7.3 検証項目チェックリスト

- [ ] 画像アップロードが成功する
- [ ] アップロード後にサムネイルが表示される
- [ ] 画像クリックで元画像が表示される
- [ ] 非画像ファイルがダウンロードできる
- [ ] ファイル削除が成功する
- [ ] 削除後に GCS からもファイルが消える
- [ ] Datastore の blobKey/bloburl が正しく更新される
- [ ] 複数ファイルの一括アップロードが動作する

---

## 実装順序（推奨）

```
1. フェーズ1: 前準備（GCS バケット、依存パッケージ）
   ↓
2. フェーズ3: gcs_utils.py 作成（基盤）
   ↓
3. フェーズ2: bloblist.py 移行（モデル完成）
   ↓
4. フェーズ6: テンプレート修正（構文エラー解消）
   ↓
5. フェーズ4: ハンドラー修正（機能実装）
   ↓
6. フェーズ5: ルーティング登録（統合）
   ↓
7. フェーズ7: テストと検証
```

---

## リスクと対策

| リスク | 影響度 | 対策 |
|-------|-------|------|
| Signed URL の有効期限切れ | 中 | 適切な有効期限設定（1時間推奨） |
| 大容量ファイルのタイムアウト | 中 | resumable upload の検討 |
| 移行中の既存データアクセス | 高 | 旧 Blobstore と GCS の並行運用期間設定 |
| CORS エラー | 低 | 事前の CORS 設定確認 |

---

## 参考資料

- [Google Cloud Storage Python Client](https://cloud.google.com/storage/docs/reference/libraries#client-libraries-install-python)
- [Signed URLs](https://cloud.google.com/storage/docs/access-control/signed-urls)
- [Flask File Uploads](https://flask.palletsprojects.com/en/2.0.x/patterns/fileuploads/)
