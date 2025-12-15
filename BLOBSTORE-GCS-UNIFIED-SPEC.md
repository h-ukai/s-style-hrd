# Blobstore → GCS 移行 統一仕様書

## 概要

本ドキュメントは、Blobstore から Cloud Storage への移行において、データ格納場所・エンドポイント・フィールド名などの一貫性を担保するための統一仕様を定義する。

**重要**: 本仕様に従わない実装は許可しない。既存コードのプレースホルダーも本仕様に合わせて修正すること。

---

## 1. GCS バケット仕様

### 1.1 バケット名

```
本番環境: s-style-hrd-blobs
テスト環境: s-style-hrd-blobs-test
```

### 1.2 環境変数

```yaml
# app.yaml
env_variables:
  GCS_BUCKET_NAME: "s-style-hrd-blobs"
  GCS_BUCKET_REGION: "asia-northeast1"
```

### 1.3 バケット設定

| 設定項目 | 値 |
|---------|---|
| ストレージクラス | STANDARD |
| ロケーション | asia-northeast1 |
| 公開アクセス | 非公開（Signed URL使用） |
| ライフサイクル | なし（永続保存） |

---

## 2. GCS Object Name 命名規則

### 2.1 統一フォーマット

```
{CorpOrg_key}/{Branch_Key}/{bkID}/{blobNo}.{extension}
```

### 2.2 命名ルール

| 要素 | 説明 | 例 |
|------|------|---|
| CorpOrg_key | 組織キー | `s-style` |
| Branch_Key | 支店キー | `hon` |
| bkID | 物件ID | `001`, `BK-2024-001` |
| blobNo | Blob連番（整数） | `1`, `2`, `3` |
| extension | ファイル拡張子（小文字） | `jpg`, `pdf`, `png` |

### 2.3 具体例

```
# 画像ファイル
s-style/hon/001/1.jpg
s-style/hon/001/2.png
s-style/hon/BK-2024-001/1.pdf

# 特殊文字を含む場合（URLエンコード不要、そのまま使用）
ishihara/hideki/物件A/1.jpg
```

### 2.4 禁止事項

- ファイル名（original filename）は object name に含めない
- ファイル名は Datastore の `filename` フィールドで管理
- 理由: 日本語ファイル名や長いファイル名による問題を回避

---

## 3. Datastore フィールド仕様

### 3.1 Blob モデル

| フィールド | 型 | 移行前の値 | 移行後の値 | 備考 |
|-----------|---|-----------|-----------|------|
| `blobKey` | StringProperty | Blobstore BlobKey | **GCS object name** | 役割変更 |
| `bloburl` | StringProperty | `/serve/{BlobKey}` | **統一エンドポイント** | 後述 |
| `thumbnailurl` | StringProperty | Images API URL | **統一エンドポイント** | 後述 |
| `filename` | StringProperty | 元ファイル名 | 元ファイル名（変更なし） | ダウンロード時に使用 |
| `fileextension` | StringProperty | 拡張子 | 拡張子（変更なし） | - |
| `html` | StringProperty | HTMLスニペット | 新URLで再生成 | - |

### 3.2 blobKey フィールドの移行

```
移行前: AMIfv94xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
移行後: s-style/hon/001/1.jpg
```

### 3.3 Bloblist モデル

Blob モデルと同一仕様を適用。

### 3.4 FileInfo モデル

| フィールド | 型 | 移行前の値 | 移行後の値 |
|-----------|---|-----------|-----------|
| `blob` | StringProperty | BlobKey | GCS object name |

---

## 4. エンドポイント仕様

### 4.1 統一エンドポイント

**全てのファイルアクセスは `/blob/` エンドポイントに統一する。**

| 廃止するエンドポイント | 統一後 |
|---------------------|-------|
| `/serve/{blobKey}` | `/blob/{object_name}` |
| `/gcs-serve/{blobKey}` | `/blob/{object_name}` |
| `https://storage.googleapis.com/...` | `/blob/{object_name}` |

### 4.2 エンドポイント一覧

| エンドポイント | メソッド | 機能 | 備考 |
|--------------|--------|------|------|
| `/blob/<path:object_name>` | GET | ファイルダウンロード | Signed URL リダイレクト |
| `/blob/<path:object_name>/thumbnail` | GET | サムネイル取得 | 画像のみ |
| `/blob/upload` | POST | ファイルアップロード | multipart/form-data |
| `/blob/upload-url` | GET | アップロード用Signed URL取得 | クライアント直接アップロード用 |
| `/blob/<path:object_name>` | DELETE | ファイル削除 | 管理者のみ |

### 4.3 URL生成ルール

#### 4.3.1 bloburl（ファイル表示/ダウンロード）

```python
# 統一フォーマット
bloburl = f"/blob/{gcs_object_name}"

# 例
bloburl = "/blob/s-style/hon/001/1.jpg"
```

#### 4.3.2 thumbnailurl（サムネイル）

```python
# 統一フォーマット
thumbnailurl = f"/blob/{gcs_object_name}/thumbnail"

# 例
thumbnailurl = "/blob/s-style/hon/001/1.jpg/thumbnail"
```

#### 4.3.3 html フィールド

```python
# 画像の場合
html = f'<a href="{bloburl}" target="_blank"><img src="{thumbnailurl}" title="{title}" /></a>'

# 非画像の場合
html = f'<a href="{bloburl}" download="{filename}">{filename}</a>'
```

### 4.4 テスト環境のエンドポイント

Blueprint `/test` プレフィックス付き:

```
/test/blob/s-style/hon/001/1.jpg
/test/blob/s-style/hon/001/1.jpg/thumbnail
```

---

## 5. 実装仕様

### 5.1 gcs_utils.py の関数仕様

```python
# ファイル: migration-src/application/gcs_utils.py

import os
from google.cloud import storage
from datetime import timedelta

# 環境変数から取得
BUCKET_NAME = os.environ.get('GCS_BUCKET_NAME', 's-style-hrd-blobs')

def get_gcs_client():
    """GCS クライアントを取得"""
    return storage.Client()

def generate_object_name(corp_org_key: str, branch_key: str, bk_id: str,
                         blob_no: int, extension: str) -> str:
    """
    統一フォーマットの GCS object name を生成

    Returns:
        str: "{corp_org_key}/{branch_key}/{bk_id}/{blob_no}.{extension}"
    """
    ext = extension.lower().lstrip('.')
    return f"{corp_org_key}/{branch_key}/{bk_id}/{blob_no}.{ext}"

def upload_file(file_data: bytes, object_name: str, content_type: str = None) -> str:
    """
    ファイルを GCS にアップロード

    Returns:
        str: アップロードした object_name
    """
    client = get_gcs_client()
    bucket = client.bucket(BUCKET_NAME)
    blob = bucket.blob(object_name)
    blob.upload_from_string(file_data, content_type=content_type)
    return object_name

def download_file(object_name: str) -> bytes:
    """GCS からファイルをダウンロード"""
    client = get_gcs_client()
    bucket = client.bucket(BUCKET_NAME)
    blob = bucket.blob(object_name)
    return blob.download_as_bytes()

def delete_file(object_name: str) -> bool:
    """GCS からファイルを削除"""
    client = get_gcs_client()
    bucket = client.bucket(BUCKET_NAME)
    blob = bucket.blob(object_name)
    blob.delete()
    return True

def generate_signed_url(object_name: str, expiration_minutes: int = 60,
                        method: str = 'GET') -> str:
    """
    Signed URL を生成

    Args:
        object_name: GCS object name
        expiration_minutes: 有効期限（分）
        method: HTTP メソッド ('GET' or 'PUT')
    """
    client = get_gcs_client()
    bucket = client.bucket(BUCKET_NAME)
    blob = bucket.blob(object_name)

    url = blob.generate_signed_url(
        version="v4",
        expiration=timedelta(minutes=expiration_minutes),
        method=method,
    )
    return url

def generate_upload_signed_url(object_name: str, content_type: str,
                               expiration_minutes: int = 15) -> str:
    """アップロード用 Signed URL を生成"""
    return generate_signed_url(object_name, expiration_minutes, method='PUT')

def get_blob_url(object_name: str) -> str:
    """
    統一エンドポイントの bloburl を生成

    Returns:
        str: "/blob/{object_name}"
    """
    return f"/blob/{object_name}"

def get_thumbnail_url(object_name: str) -> str:
    """
    統一エンドポイントの thumbnailurl を生成

    Returns:
        str: "/blob/{object_name}/thumbnail"
    """
    return f"/blob/{object_name}/thumbnail"

def generate_html(object_name: str, filename: str, title: str = None,
                  content: str = None, is_image: bool = False) -> str:
    """
    html フィールド用の HTML を生成
    """
    bloburl = get_blob_url(object_name)

    if is_image:
        thumbnailurl = get_thumbnail_url(object_name)
        title_attr = ""
        if title:
            title_attr = title
            if content:
                title_attr += f":{content}"
        return f'<a href="{bloburl}" target="_blank"><img src="{thumbnailurl}" title="{title_attr}" /></a>'
    else:
        return f'<a href="{bloburl}" download="{filename}">{filename}</a>'

def is_image_file(extension: str) -> bool:
    """画像ファイルかどうかを判定"""
    return extension.lower().lstrip('.') in ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp']
```

### 5.2 Flask ルート実装仕様

```python
# ファイル: migration-src/main.py に追加

from flask import send_file, redirect, Response
from application import gcs_utils
import io

@test_bp.route('/blob/<path:object_name>')
def blob_download(object_name):
    """
    ファイルダウンロード
    Signed URL にリダイレクトする方式
    """
    signed_url = gcs_utils.generate_signed_url(object_name, expiration_minutes=5)
    return redirect(signed_url)

@test_bp.route('/blob/<path:object_name>/thumbnail')
def blob_thumbnail(object_name):
    """
    サムネイル取得
    将来的に Cloud Functions でリサイズ処理を追加可能
    """
    # 現時点では元画像をそのまま返す（リサイズは将来実装）
    signed_url = gcs_utils.generate_signed_url(object_name, expiration_minutes=5)
    return redirect(signed_url)

@test_bp.route('/blob/upload', methods=['POST'])
def blob_upload():
    """
    ファイルアップロード
    """
    from flask import request

    uploaded_file = request.files.get('file')
    if not uploaded_file:
        return "No file", 400

    corp_org_key = request.form.get('CorpOrg_key')
    branch_key = request.form.get('Branch_Key')
    bk_id = request.form.get('bkID')
    blob_no = int(request.form.get('blobNo'))

    # 拡張子取得
    import os
    _, ext = os.path.splitext(uploaded_file.filename)

    # object name 生成
    object_name = gcs_utils.generate_object_name(
        corp_org_key, branch_key, bk_id, blob_no, ext
    )

    # GCS にアップロード
    gcs_utils.upload_file(
        uploaded_file.read(),
        object_name,
        content_type=uploaded_file.content_type
    )

    return {"object_name": object_name}, 200

@test_bp.route('/blob/upload-url', methods=['GET'])
def blob_upload_url():
    """
    クライアント直接アップロード用の Signed URL を生成
    """
    from flask import request

    corp_org_key = request.args.get('CorpOrg_key')
    branch_key = request.args.get('Branch_Key')
    bk_id = request.args.get('bkID')
    blob_no = int(request.args.get('blobNo'))
    ext = request.args.get('extension', 'bin')
    content_type = request.args.get('content_type', 'application/octet-stream')

    object_name = gcs_utils.generate_object_name(
        corp_org_key, branch_key, bk_id, blob_no, ext
    )

    signed_url = gcs_utils.generate_upload_signed_url(
        object_name, content_type, expiration_minutes=15
    )

    return {"upload_url": signed_url, "object_name": object_name}, 200

@test_bp.route('/blob/<path:object_name>', methods=['DELETE'])
def blob_delete(object_name):
    """
    ファイル削除（管理者のみ）
    """
    # TODO: 認証チェック追加
    gcs_utils.delete_file(object_name)
    return {"deleted": object_name}, 200
```

---

## 6. データ移行時の変換ルール

### 6.1 blobKey の変換

```python
def convert_blobkey_to_object_name(blob_entity):
    """
    既存の Blob エンティティから新しい object name を生成

    注意: 元の BlobKey は GCS object name に変換できないため、
    Datastore のメタデータから新しい object name を生成する
    """
    # 拡張子を取得
    ext = blob_entity.fileextension
    if not ext and blob_entity.filename:
        import os
        _, ext = os.path.splitext(blob_entity.filename)
        ext = ext.lower().lstrip('.')

    # 統一フォーマットで object name 生成
    return f"{blob_entity.CorpOrg_key}/{blob_entity.Branch_Key}/{blob_entity.bkID}/{blob_entity.blobNo}.{ext}"
```

### 6.2 URL フィールドの変換

```python
def update_blob_urls(blob_entity, new_object_name):
    """
    Blob エンティティの URL フィールドを更新
    """
    from application import gcs_utils

    # blobKey を GCS object name に更新
    blob_entity.blobKey = new_object_name

    # bloburl を統一エンドポイントに更新
    blob_entity.bloburl = gcs_utils.get_blob_url(new_object_name)

    # thumbnailurl を更新（画像の場合のみ）
    if gcs_utils.is_image_file(blob_entity.fileextension):
        blob_entity.thumbnailurl = gcs_utils.get_thumbnail_url(new_object_name)
    else:
        blob_entity.thumbnailurl = None

    # html を再生成
    blob_entity.html = gcs_utils.generate_html(
        new_object_name,
        blob_entity.filename,
        title=blob_entity.title,
        content=blob_entity.content,
        is_image=gcs_utils.is_image_file(blob_entity.fileextension)
    )

    return blob_entity
```

---

## 7. 既存コード修正箇所

### 7.1 blobstoreutl.py

| 行番号 | 現在のコード | 修正後 |
|--------|------------|--------|
| 72 | `/gcs-serve/{blob.blobKey}?size=100` | `gcs_utils.get_thumbnail_url(blob.blobKey)` |
| 73 | `/gcs-serve/{blob.blobKey}` | `gcs_utils.get_blob_url(blob.blobKey)` |
| 78 | `/serve/{blobKey}/{filename}` | `gcs_utils.get_blob_url(blob.blobKey)` |
| 236-237 | 同上 | 同上 |
| 250 | 同上 | 同上 |

### 7.2 mapreducemapper.py

| 行番号 | 現在のコード | 修正後 |
|--------|------------|--------|
| 121-122 | `https://storage.googleapis.com/YOUR_BUCKET/...` | `gcs_utils.get_blob_url()` / `get_thumbnail_url()` |
| 143 | `/serve/{blobKey}/{filename}` | `gcs_utils.get_blob_url()` |

### 7.3 handler.py

| 行番号 | 現在のコード | 修正後 |
|--------|------------|--------|
| 62 | `blobkey = "gcs-placeholder-key"` | `gcs_utils.generate_object_name()` + `upload_file()` |

---

## 8. 検証チェックリスト

### 8.1 命名規則の検証

- [ ] 全ての新規アップロードが `{corp}/{branch}/{bkID}/{blobNo}.{ext}` 形式
- [ ] 拡張子が小文字で統一されている
- [ ] 日本語を含む bkID が正しく処理される

### 8.2 エンドポイントの検証

- [ ] `/blob/{object_name}` でファイルがダウンロードできる
- [ ] `/blob/{object_name}/thumbnail` でサムネイルが表示される
- [ ] 旧エンドポイント（`/serve/`, `/gcs-serve/`）が使用されていない

### 8.3 Datastore の検証

- [ ] `blobKey` フィールドが GCS object name 形式
- [ ] `bloburl` が `/blob/...` 形式
- [ ] `thumbnailurl` が `/blob/.../thumbnail` 形式（画像のみ）
- [ ] `html` が新しい URL を使用

---

## 9. データ関係図と移行対象

### 9.1 モデル間の関係

```
┌─────────────────────────────────────────────────────────────────────┐
│                        Datastore Models                              │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌─────────────┐                    ┌─────────────────────────────┐ │
│  │   BKdata    │◄───── bkID ───────│          Blob               │ │
│  │  (物件情報)  │                    │      (ファイル情報)          │ │
│  ├─────────────┤                    ├─────────────────────────────┤ │
│  │ - bkID      │                    │ - CorpOrg_key              │ │
│  │ - ttmnmi    │                    │ - Branch_Key               │ │
│  │ - shzicmi1  │                    │ - bkID        ← 紐づけキー  │ │
│  │ - shzicmi2  │                    │ - blobNo                   │ │
│  │ - ...       │                    │ - blobKey     ← 移行対象   │ │
│  │             │                    │ - bloburl     ← 移行対象   │ │
│  │ ※blob識別子 │                    │ - thumbnailurl← 移行対象   │ │
│  │   なし      │                    │ - html        ← 移行対象   │ │
│  │             │                    │ - filename                 │ │
│  └─────────────┘                    │ - fileextension            │ │
│                                      └─────────────────────────────┘ │
│                                                                      │
│  ┌─────────────────────────────────┐                                │
│  │          FileInfo               │                                │
│  │    (アップロードファイル情報)     │                                │
│  ├─────────────────────────────────┤                                │
│  │ - blob          ← 移行対象      │                                │
│  │ - uploaded_by                   │                                │
│  │ - uploaded_at                   │                                │
│  └─────────────────────────────────┘                                │
│                                                                      │
│  ┌─────────────────────────────────┐                                │
│  │          Bloblist               │                                │
│  │      (未使用の可能性)            │                                │
│  ├─────────────────────────────────┤                                │
│  │ ※参照コードなし                 │                                │
│  │ ※移行対象から除外検討           │                                │
│  └─────────────────────────────────┘                                │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
                    │
                    │ GCS 移行
                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     Google Cloud Storage                             │
├─────────────────────────────────────────────────────────────────────┤
│  gs://s-style-hrd-blobs/                                            │
│    └── {CorpOrg_key}/                                               │
│        └── {Branch_Key}/                                            │
│            └── {bkID}/                                              │
│                └── {blobNo}.{extension}                             │
└─────────────────────────────────────────────────────────────────────┘
```

### 9.2 BKdata と Blob の紐づけ方式

```python
# BKdata から Blob を取得する方法（既存コード）
# BKdata 自体には blob 識別子は保存されていない

from application.models.blob import Blob

def get_blobs_for_bkdata(bkdata):
    """BKdata に紐づく Blob 一覧を取得"""
    return Blob.query(
        Blob.CorpOrg_key == bkdata.nyrykkisyID,
        Blob.Branch_Key == bkdata.nyrykstnID,
        Blob.bkID == bkdata.bkID
    ).order(Blob.media, Blob.pos).fetch()
```

### 9.3 移行対象モデル一覧

| モデル | 移行対象 | 理由 |
|-------|---------|------|
| **Blob** | ✅ 対象 | `blobKey`, `bloburl`, `thumbnailurl`, `html` を更新 |
| **FileInfo** | ✅ 対象 | `blob` フィールドを GCS object name に更新 |
| **BKdata** | ❌ 対象外 | blob 識別子を保存していない。Blob 側で紐づけ |
| **Bloblist** | ⚠️ 除外検討 | 参照コードなし。未使用の可能性が高い |
| **blobNo** | ❌ 対象外 | 連番管理のみ。URL/識別子なし |
| **bloblistNo** | ⚠️ 除外検討 | Bloblist と同様 |

### 9.4 移行対象フィールド詳細

#### Blob モデル（移行必須）

| フィールド | 移行前 | 移行後 | 移行処理 |
|-----------|-------|-------|---------|
| `blobKey` | `AMIfv94xxx...` | `s-style/hon/001/1.jpg` | メタデータから生成 |
| `bloburl` | `/serve/AMIfv94xxx...` | `/blob/s-style/hon/001/1.jpg` | `gcs_utils.get_blob_url()` |
| `thumbnailurl` | Images API URL | `/blob/.../thumbnail` | `gcs_utils.get_thumbnail_url()` |
| `html` | 旧URL含むHTML | 新URL含むHTML | `gcs_utils.generate_html()` |
| `filename` | 変更なし | 変更なし | - |
| `fileextension` | 変更なし | 変更なし | - |

#### FileInfo モデル（移行必須）

| フィールド | 移行前 | 移行後 |
|-----------|-------|-------|
| `blob` | BlobKey 文字列 | GCS object name |

### 9.5 Bloblist モデルの扱い

**調査結果**: `src/application/models/bloblist.py` に定義されているが、他のコードからの参照なし。

**判断**:
- コードベースで `Bloblist` を import/使用している箇所が見つからない
- 過去に使用されていた可能性があるが、現在は未使用
- **移行対象から除外**を推奨

**除外する場合の対応**:
1. `migration-src` への移行は不要
2. 既存データが存在する場合は別途確認
3. 将来の使用予定があれば計画を見直し

---

## 10. バッチ移行戦略

### 10.1 タイムスタンプフィールド

各モデルは自身のタイムスタンプを持っており、BKdataに依存せずバッチ分割が可能。

| モデル | タイムスタンプ | 型 | 備考 |
|--------|--------------|---|------|
| **Blob** | `date` | DateTimeProperty(auto_now_add=True) | Blob作成日時 |
| **FileInfo** | `uploaded_at` | DateTimeProperty(auto_now_add=True) | アップロード日時 |

### 10.2 BKdataとの紐づけ状況

```
┌─────────────────────────────────────────────────────────────┐
│                    Blob の紐づけパターン                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  パターン1: BKdataに紐づいているBlob（通常ケース）            │
│  ┌─────────────┐          ┌─────────────┐                  │
│  │   BKdata    │◄─ bkID ──│    Blob     │                  │
│  │ (物件情報)   │          │ bkID="001" │                  │
│  └─────────────┘          │ date=...   │ ← 自身のタイムスタンプ│
│                           └─────────────┘                  │
│                                                             │
│  パターン2: BKdataに紐づいていないBlob（孤立Blob）            │
│                            ┌─────────────┐                  │
│         紐づけなし          │    Blob     │                  │
│                            │ bkID=""    │                  │
│                            │ date=...   │ ← 自身のタイムスタンプ│
│                            └─────────────┘                  │
│                                                             │
│  ※ bkID は必須フィールドではないため、空の可能性あり          │
│  ※ 孤立Blobも date フィールドでバッチ分割可能                │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 10.3 バッチ移行クエリ例

```python
from datetime import datetime
from application.models.blob import Blob
from application.handler import FileInfo

def get_blob_batch(start_date: datetime, end_date: datetime, limit: int = 100):
    """
    タイムスタンプでBlob をバッチ取得
    BKdataへの紐づけ有無に関わらず取得可能
    """
    return Blob.query(
        Blob.date >= start_date,
        Blob.date < end_date
    ).order(Blob.date).fetch(limit=limit)

def get_fileinfo_batch(start_date: datetime, end_date: datetime, limit: int = 100):
    """
    タイムスタンプでFileInfo をバッチ取得
    """
    return FileInfo.query(
        FileInfo.uploaded_at >= start_date,
        FileInfo.uploaded_at < end_date
    ).order(FileInfo.uploaded_at).fetch(limit=limit)
```

### 10.4 バッチ移行の実行方針

| 方針 | 説明 |
|------|------|
| **ツール** | Cloud Run Jobs（シンプル、長時間実行可） |
| **分割単位** | タイムスタンプ（日単位 or 週単位） |
| **並行運用** | 本番環境は稼働継続、移行は段階的に実行 |
| **再実行** | MigrationStatus で進捗管理、失敗時は再実行可能 |

### 10.5 移行バッチの流れ

```
┌─────────────────────────────────────────────────────────────┐
│                     バッチ移行フロー                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  [1. バッチ開始]                                             │
│       │                                                     │
│       ▼                                                     │
│  [2. 期間指定でデータ取得]                                    │
│       │  例: 2024-01-01 ～ 2024-01-31                       │
│       │  Blob.query(Blob.date >= start, Blob.date < end)   │
│       │                                                     │
│       ▼                                                     │
│  [3. 各レコードを処理]                                        │
│       │  - Blobstore からファイル読取                        │
│       │  - GCS にアップロード                                │
│       │  - Datastore フィールド更新                          │
│       │  - MigrationStatus に記録                           │
│       │                                                     │
│       ▼                                                     │
│  [4. バッチ完了]                                             │
│       │                                                     │
│       ▼                                                     │
│  [5. 次の期間へ]                                             │
│       例: 2024-02-01 ～ 2024-02-28                          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 10.6 孤立Blobの扱い

| 状況 | 対応 |
|------|------|
| `bkID` が空 | **移行対象**（date フィールドでバッチ分割） |
| `CorpOrg_key` が空 | object name 生成時にデフォルト値を使用 |
| 全メタデータが空 | 警告ログを出力し、スキップまたは手動対応 |

**孤立Blobの object name 生成ルール**:

```python
def generate_object_name_for_orphan(blob_entity):
    """
    メタデータが不完全なBlobの object name を生成
    """
    corp = blob_entity.CorpOrg_key or "_orphan"
    branch = blob_entity.Branch_Key or "_unknown"
    bk_id = blob_entity.bkID or f"_no-bkid-{blob_entity.key.id()}"
    blob_no = blob_entity.blobNo or 0
    ext = blob_entity.fileextension or "bin"

    return f"{corp}/{branch}/{bk_id}/{blob_no}.{ext}"
```

---

## 11. 変更履歴

| 日付 | 変更内容 |
|------|---------|
| 2025-12-15 | 初版作成 |
| 2025-12-15 | データ関係図、移行対象/対象外の明示を追加 |
| 2025-12-15 | バッチ移行戦略（タイムスタンプ、孤立Blob対応）を追加 |
