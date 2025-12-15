# TODO-02: Blobstore → GCS 移行

**優先度**: 高
**作業種別**: コード実装
**参照**: `BLOBSTORE-GCS-UNIFIED-SPEC.md`（統一仕様書）

---

## 概要

GAE Python 2.7 の Blobstore API は Python 3.11 で廃止。
Cloud Storage (GCS) への移行が必須。

---

## 影響を受けるファイル

| ファイル | 変更内容 | 優先度 |
|----------|----------|--------|
| `application/blobstoreutl.py` | アップロード/ダウンロード/削除のGCS対応 | 高 |
| `application/handler.py` | FileInfo モデルとファイル操作のGCS対応 | 高 |
| `application/mapreducemapper.py` | HTML生成時のURL生成をGCS対応 | 中 |
| `application/models/blob.py` | blobKey → GCS object name 対応 | 中 |
| `templates/blobstoreutl.html` | Django→Jinja2 テンプレート修正 | 低 |

---

## ソースコード内のTODOコメント

### blobstoreutl.py

```python
# Line 13-21: SECURITY WARNING
# ⚠️ SECURITY WARNING: Blobstore → GCS migration required
# Key changes needed:
# - blobstore.create_upload_url() → GCS Signed URL
# - BlobstoreUploadHandler → Flask request.files + GCS client
# - get_serving_url() → GCS public URL / Signed URL
# - BlobReferenceProperty → String property (store GCS object name)

# Line 30-33: BlobstoreUtlHandler
# ⚠️ TODO: Complete Blobstore → GCS migration
# - Replace blobstore.create_upload_url() with GCS Signed URL generation
# - Update blob storage/retrieval to use GCS client
# - Replace get_serving_url() with GCS public/signed URLs

# Line 37-39: upload_url generation
# ⚠️ TODO: Replace with GCS Signed URL generation
upload_url = "/upload/" + keypath  # Placeholder - needs GCS implementation

# Line 69-74: get_serving_url replacement
# ⚠️ TODO: Replace get_serving_url() with GCS public/signed URL
blob.thumbnailurl = f"/gcs-serve/{blob.blobKey}?size=100"  # Placeholder
blob.bloburl = f"/gcs-serve/{blob.blobKey}"  # Placeholder

# Line 143-146: BlobstoreUploadHandler
# ⚠️ TODO: Complete Blobstore → GCS migration
# - Upload files to GCS instead of Blobstore
# - Store GCS object names instead of BlobKeys

# Line 166-175: upload処理
# ⚠️ TODO: Replace BlobstoreUploadHandler with Flask request.files + GCS upload
# ⚠️ TODO: Upload to GCS and store object name

# Line 286-300: 削除処理
# ⚠️ TODO: Update to delete from GCS instead of Blobstore
# ⚠️ TODO: Delete from GCS instead of Blobstore

# Line 314-326: ダウンロード処理
# ⚠️ TODO: Complete Blobstore → GCS migration
# - Replace BlobstoreDownloadHandler with GCS file serving
# - Use GCS signed URLs or direct streaming
return "GCS file serving not yet implemented", 501
```

### handler.py

```python
# Line 13-14: SECURITY WARNING
# ⚠️ SECURITY WARNING: Blobstore → GCS migration required

# Line 22-24: FileInfo モデル
# ⚠️ TODO: Update BlobReferenceProperty → String property (store GCS object name)
blob = ndb.StringProperty(required=True)  # Store GCS object name instead of BlobKey

# Line 46-62: アップロード処理
# ⚠️ TODO: Complete Blobstore → GCS migration
# ⚠️ TODO: Upload to GCS and get object name
blobkey = "gcs-placeholder-key"  # TODO: Replace with GCS object name

# Line 116-127: 削除処理
# ⚠️ TODO: Update to delete from GCS instead of Blobstore
# ⚠️ TODO: Delete from GCS instead of Blobstore

# Line 173-186: ダウンロード処理
# ⚠️ TODO: Complete Blobstore → GCS migration
return "GCS file download not yet implemented", 501

# Line 196-209: Signed URL生成
# ⚠️ TODO: Complete Blobstore → GCS migration
# - Replace blobstore.create_upload_url() with GCS Signed URL generation
# ⚠️ TODO: Replace with GCS Signed URL generation
```

### mapreducemapper.py

```python
# Line 69-100: Migration Note
# Migration Note: BLOBSTORE → GCS MIGRATION IN PROGRESS
# - GCS migration implementation is deferred
# - Implement GCS signed URL generation using google.cloud.storage
# - Update thumbnail generation for GCS objects

# Line 115-122: URL生成
# TODO: Replace with GCS signed URL generation
# REVIEW-L2: Placeholder URLs contain hardcoded 'YOUR_BUCKET' - needs environment config
entity.thumbnailurl = f"https://storage.googleapis.com/YOUR_BUCKET/{entity.blobKey}"
entity.bloburl = f"https://storage.googleapis.com/YOUR_BUCKET/{entity.blobKey}"
```

---

## 実装手順

### ステップ1: 前準備

1. **GCS バケット作成**
   ```bash
   gsutil mb -p s-style-hrd -l asia-northeast1 gs://s-style-hrd-blobs
   ```

2. **CORS 設定**
   ```json
   // cors.json
   [
     {
       "origin": ["https://s-style-hrd.appspot.com"],
       "method": ["GET", "PUT", "POST", "DELETE"],
       "responseHeader": ["Content-Type"],
       "maxAgeSeconds": 3600
     }
   ]
   ```
   ```bash
   gsutil cors set cors.json gs://s-style-hrd-blobs
   ```

3. **requirements.txt 確認**
   ```
   google-cloud-storage==2.14.0  # 既に追加済み
   ```

4. **app.yaml に環境変数追加**
   ```yaml
   env_variables:
     GCS_BUCKET_NAME: 's-style-hrd-blobs'
   ```

### ステップ2: gcs_utils.py 新規作成

```python
# application/gcs_utils.py
"""GCS ユーティリティ関数"""
import os
from google.cloud import storage
from datetime import timedelta

BUCKET_NAME = os.environ.get('GCS_BUCKET_NAME', 's-style-hrd-blobs')

def get_storage_client():
    """GCS クライアントを取得"""
    return storage.Client()

def upload_file(file_obj, object_name, content_type=None):
    """ファイルをGCSにアップロード"""
    client = get_storage_client()
    bucket = client.bucket(BUCKET_NAME)
    blob = bucket.blob(object_name)
    blob.upload_from_file(file_obj, content_type=content_type)
    return object_name

def generate_signed_url(object_name, expiration_minutes=60):
    """署名付きURLを生成"""
    client = get_storage_client()
    bucket = client.bucket(BUCKET_NAME)
    blob = bucket.blob(object_name)
    url = blob.generate_signed_url(
        version="v4",
        expiration=timedelta(minutes=expiration_minutes),
        method="GET"
    )
    return url

def delete_file(object_name):
    """ファイルをGCSから削除"""
    client = get_storage_client()
    bucket = client.bucket(BUCKET_NAME)
    blob = bucket.blob(object_name)
    blob.delete()

def download_file(object_name):
    """ファイルをGCSからダウンロード"""
    client = get_storage_client()
    bucket = client.bucket(BUCKET_NAME)
    blob = bucket.blob(object_name)
    return blob.download_as_bytes()
```

### ステップ3: 各ファイルの修正

詳細は `BLOBSTORE-GCS-UNIFIED-SPEC.md` セクション7を参照

---

## 作業チェックリスト

- [ ] GCSバケット `s-style-hrd-blobs` を作成
- [ ] CORS設定を適用
- [ ] app.yaml に `GCS_BUCKET_NAME` 環境変数を追加
- [ ] `application/gcs_utils.py` を新規作成
- [ ] `application/blobstoreutl.py` を修正
- [ ] `application/handler.py` を修正
- [ ] `application/mapreducemapper.py` を修正（YOUR_BUCKET を環境変数に）
- [ ] `main.py` に GCS 関連ルートを登録
- [ ] `templates/blobstoreutl.html` の Django 構文を Jinja2 に修正
- [ ] 画像アップロードテスト
- [ ] 画像表示テスト
- [ ] ファイルダウンロードテスト
- [ ] 削除テスト

---

## GCS Object Name 命名規則

```
{CorpOrg_key}/{Branch_Key}/{bkID}/{blobNo}.{extension}
例: s-style/hon/001/1.jpg
```

---

## 統一エンドポイント

```
旧: /serve/{blobKey}, /gcs-serve/{blobKey}
新: /blob/{object_name}
    /blob/{object_name}/thumbnail
```

---

## 関連ドキュメント

- **BLOBSTORE-GCS-UNIFIED-SPEC.md** - 統一仕様書（必読）
- **BLOBSTORE-GCS-MIGRATION-PLAN.md** - 実装プラン
- **BLOBSTORE-GCS-DATA-MIGRATION-TOOL-SPEC.md** - データ移行ツール要件
