# Blobstore → Cloud Storage 移行調査報告書

## 概要

本ドキュメントは、Google App Engine の Blobstore API から Cloud Storage への移行に向けた前調査結果をまとめたものです。

- **調査日**: 2025-12-15
- **対象**: `src/` (Python 2.7 本番コード) および `migration-src/` (Python 3.11 移行コード)
- **移行先**: Google Cloud Storage (GCS)

---

## 1. Blobstore使用モデル定義

### 1.1 src/application/models/ (Python 2.7 本番)

| ファイル | モデル名 | 説明 |
|---------|---------|------|
| `blob.py` | `Blob` | Blob メタデータ管理（blobKey を文字列で保存） |
| `blob.py` | `blobNo` | Blob 番号の連番管理 |
| `bloblist.py` | `Bloblist` | Blob リスト管理 |
| `bloblist.py` | `bloblistNo` | Bloblist 番号の連番管理 |
| `handler.py` | `FileInfo` | `BlobReferenceProperty` 使用（直接参照） |

### 1.2 migration-src/application/models/ (Python 3.11 移行)

| ファイル | モデル名 | 状態 | 備考 |
|---------|---------|------|------|
| `blob.py` | `Blob` | ✅ ndb移行済み | BlobKeyは文字列として保存 |
| `blob.py` | `blobNo` | ✅ ndb移行済み | トランザクション処理も対応 |
| `bloblist.py` | - | ❌ **移行漏れ** | src には存在するが migration-src に無い |

### 1.3 Blob モデルのプロパティ詳細

```python
class Blob(ndb.Model):
    blob_key_name = ndb.StringProperty()      # キー名
    CorpOrg_key = ndb.StringProperty()        # 組織キー
    Branch_Key = ndb.StringProperty()         # 支店キー
    bkID = ndb.StringProperty()               # 物件ID
    blobNo = ndb.IntegerProperty()            # Blob番号
    blobkind = ndb.StringProperty()           # Blob種別
    title = ndb.StringProperty()              # タイトル
    content = ndb.TextProperty()              # 説明文
    filename = ndb.StringProperty()           # ファイル名
    fileextension = ndb.StringProperty()      # 拡張子
    media = ndb.StringProperty()              # メディア種別
    pos = ndb.StringProperty()                # 位置情報
    thumbnailurl = ndb.StringProperty()       # サムネイルURL ← GCS移行で変更必要
    bloburl = ndb.StringProperty()            # BlobURL ← GCS移行で変更必要
    html = ndb.StringProperty()               # HTML表示用
    blobKey = ndb.StringProperty()            # BlobKey ← GCS object name に変更
    shzicmi1 = ndb.StringProperty()           # 所在地未1
    shzicmi2 = ndb.StringProperty()           # 所在地未2
    ttmnmi = ndb.StringProperty()             # 建物名
    date = ndb.DateTimeProperty(auto_now_add=True)  # 登録日時
```

---

## 2. Blobstore使用ソースコード一覧

### 2.1 migration-src（修正対象）

| ファイル | 機能 | 移行状態 | 修正必要箇所 |
|---------|------|----------|-------------|
| `application/blobstoreutl.py` | Blob管理画面、アップロード、削除 | ⚠️ 部分移行 | GCS実装未完了 |
| `application/handler.py` | ファイルアップロード/ダウンロード | ⚠️ 部分移行 | GCS実装未完了 |
| `application/mapreducemapper.py` | バッチ処理（URL変換） | ⚠️ 部分移行 | GCS URL生成未実装 |
| `dataProvider/bkdataProvider.py` | 物件データ取得（Blob含む） | ✅ ndb移行済み | 動作確認必要 |
| `main.py` | ルーティング | ⚠️ ルート未登録 | blobstoreutl関連コメントアウト |
| `templates/blobstoreutl.html` | Blob管理テンプレート | ⚠️ 要修正 | Django構文残存 |
| `templates/bkedit.html` | 物件編集テンプレート | ✅ Jinja2対応済み | - |

### 2.2 src（参考・本番）

| ファイル | 機能 | 備考 |
|---------|------|------|
| `application/blobstoreutl.py` | Blob管理（webapp2版） | migration-srcと対応 |
| `application/handler.py` | ファイル操作（webapp2版） | migration-srcと対応 |
| `application/mapreducemapper.py` | MapReduce処理 | BlobMigrationRecord使用 |
| `application/test.py` | テストコード | bloburlschange関数呼び出し |
| `dataProvider/bkdataProvider.py` | 物件データ取得 | Blobクエリ含む |
| `main.py` | ルーティング | 全ルート登録済み |

---

## 3. Blobstore API 使用パターンと移行方針

### 3.1 使用されている Blobstore API

| API | 使用箇所 | GCS 移行先 |
|-----|---------|-----------|
| `blobstore.create_upload_url()` | blobstoreutl.py, handler.py | GCS Signed URL (PUT) |
| `blobstore_handlers.BlobstoreUploadHandler` | blobstoreutl.py, handler.py | Flask request.files + GCS client |
| `blobstore_handlers.BlobstoreDownloadHandler` | blobstoreutl.py, handler.py | GCS streaming download / Signed URL |
| `blobstore.BlobInfo.get()` | blobstoreutl.py, handler.py | GCS Blob metadata |
| `blobstore.get()` | blobstoreutl.py | GCS client.get_blob() |
| `blobstore.delete()` | handler.py | GCS blob.delete() |
| `get_serving_url()` | blobstoreutl.py, mapreducemapper.py | GCS public URL / Signed URL |
| `BlobMigrationRecord.get_new_blob_key()` | mapreducemapper.py | 不要（新規実装では使用しない） |
| `BlobReferenceProperty` | handler.py (FileInfo) | StringProperty (GCS object name) |

### 3.2 データの流れ

```
[ブラウザ]
    │
    ├─ アップロード ─→ [Flask handler] ─→ [GCS bucket] ─→ [Datastore: Blob]
    │                    │                    │               │
    │                    │                    │               └─ blobKey = GCS object name
    │                    │                    │
    │                    │                    └─ ファイル本体保存
    │                    │
    │                    └─ request.files でファイル取得
    │
    └─ ダウンロード ←─ [Flask handler] ←─ [GCS bucket]
                         │
                         └─ Signed URL or streaming
```

---

## 4. 推定 Blob データ構造

### 4.1 Blobの階層構造（キー名パターン）

```
{CorpOrg_key}/{Branch_Key}/{bkID}/{blobNo}
例: s-style/hon/001/1
    s-style/hon/001/2
    ishihara/hideki/001/3
```

### 4.2 ファイル種別

コードから推測される保存ファイル種別:
- **画像**: JPEG, JPG, PNG, GIF, BMP
- **その他**: 任意のファイル（物件資料など）

### 4.3 media プロパティ値（推測）

物件に関連するメディア種別で分類されている模様:
- 外観写真
- 間取り図
- 内装写真
- etc.

---

## 5. 現在の問題点と課題

### 5.1 migration-src の未完了箇所

1. **GCSアップロード未実装**
   - `blobstoreutl.py:169` - `request.files` 取得後の GCS upload が未実装
   - `handler.py:51-62` - 同上

2. **GCSダウンロード未実装**
   - `blobstoreutl.py:307-326` - `serve_route()` が 501 を返す
   - `handler.py:166-186` - `file_download_route()` が 501 を返す

3. **Signed URL 生成未実装**
   - `handler.py:189-214` - `generate_upload_url_route()` がプレースホルダー

4. **テンプレート構文問題**
   - `templates/blobstoreutl.html` に Django 構文 `default_if_none` が残存

5. **移行漏れモデル**
   - `bloblist.py` が migration-src に存在しない

6. **ルート未登録**
   - `main.py` で blobstoreutl 関連ルートがコメントアウト

### 5.2 セキュリティ考慮事項

1. **XSS リスク**: `mapreducemapper.py` で HTML 生成時にエスケープなし
2. **Signed URL 有効期限**: 適切な期限設定が必要
3. **アクセス制御**: GCS bucket の IAM 設定

---

## 6. 総括と提案

### 6.1 総括

1. **移行の複雑さ**: 中程度
   - モデル定義は既に ndb 対応済み
   - Flask への移行も部分的に完了
   - 主な作業は GCS API の実装

2. **影響範囲**
   - 物件画像のアップロード/表示機能に影響
   - 既存データの移行が必要

3. **リスク**
   - 本番データの Blob 数・サイズが不明
   - 移行中のダウンタイム考慮が必要

### 6.2 提案

#### 短期（実装フェーズ）
1. `bloblist.py` を migration-src に移行
2. GCS client を使用したアップロード/ダウンロード実装
3. Signed URL 生成機能の実装
4. テンプレート構文の Jinja2 対応

#### 中期（データ移行フェーズ）
1. 既存 Blobstore データの GCS への移行ツール作成
2. Datastore の blobKey を GCS object name に更新
3. 段階的な移行（テスト環境 → 本番環境）

#### 長期（最適化フェーズ）
1. CDN 連携の検討
2. 画像リサイズ機能の Cloud Functions 化
3. バックアップ戦略の策定

### 6.3 GCS バケット構成案

```
gs://s-style-hrd-blobs/
    ├── {CorpOrg_key}/
    │   └── {Branch_Key}/
    │       └── {bkID}/
    │           ├── {blobNo}_original.{ext}
    │           └── {blobNo}_thumb.{ext}
    └── temp/  # アップロード一時領域
```

---

## 付録: 調査対象ファイル一覧

### src/ (本番 Python 2.7)
- `application/models/blob.py`
- `application/models/bloblist.py`
- `application/blobstoreutl.py`
- `application/handler.py`
- `application/mapreducemapper.py`
- `application/test.py`
- `dataProvider/bkdataProvider.py`
- `main.py`
- `templates/blobstoreutl.html`
- `templates/bkedit.html`

### migration-src/ (移行 Python 3.11)
- `application/models/blob.py`
- `application/blobstoreutl.py`
- `application/handler.py`
- `application/mapreducemapper.py`
- `dataProvider/bkdataProvider.py`
- `main.py`
- `templates/blobstoreutl.html`
- `templates/bkedit.html`
