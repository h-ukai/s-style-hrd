# Blobstore → GCS 移行ツール

## 概要

Blobstore から GCS へのデータ移行を行うためのツール群です。

## ツール一覧

| ツール | 用途 | Datastore更新 | ファイル削除 |
|--------|------|---------------|--------------|
| `check_blob_count.py` | データ件数確認 | なし | なし |
| `check_blobkey_format.py` | blobKey形式の分析 | なし | なし |
| `check_file_extensions.py` | 拡張子の統計 | なし | なし |
| `download_and_upload_blob.py` | HTTP経由でコピー（推奨） | なし | なし |
| `copy_blob_to_gcs.py` | 内部GCS直接コピー（未使用） | なし | なし |
| `migrate_blob_to_gcs.py` | 移行＋Datastore更新 | **あり** | なし |

---

## 1. check_blob_count.py

### 概要
Blobデータの件数を日付で区切って確認します。

### 使用方法
```bash
python tools/check_blob_count.py
```

### 出力例
```
全体: 29,876 件
2023/01/01 より前: 29,610 件
2023/01/01 以降: 266 件
```

---

## 2. check_blobkey_format.py

### 概要
blobKeyの形式を分析し、移行済み/未移行を判定します。

### 使用方法
```bash
python tools/check_blobkey_format.py
```

### blobKey形式の種類

| 形式 | 例 | 状態 |
|------|-----|------|
| `AMIfv...` | `AMIfv94jOFK16Zx5q7Dm...` | 未移行（レガシーBlobstore） |
| `encoded_gs_file:...` | `encoded_gs_file:bucket/path` | 未移行（GCS参照） |
| `corp/branch/bkid/no.ext` | `s-style/hon/53043/1.pdf` | 移行済み |
| 空 | - | blobKeyなし |

---

## 3. check_file_extensions.py

### 概要
ファイル拡張子の分布を確認し、サイズを推定します。

### 使用方法
```bash
python tools/check_file_extensions.py
```

---

## 4. download_and_upload_blob.py（推奨）

### 概要
Python 2.7アプリの `/serve/` エンドポイント経由でファイルをダウンロードし、GCSにアップロードします。

### 特徴
- ✅ Datastoreは**更新しない**（blobKeyはそのまま）
- ✅ 元のBlobstoreファイルは**削除しない**
- ✅ レート制限対策（1秒間隔）
- ✅ 日付範囲指定可能
- ✅ ファイルサイズ統計を表示

### 使用方法

```bash
# dry-run（ダウンロードしてサイズ確認、アップロードなし）
python tools/download_and_upload_blob.py --from 2023/01/01 --dry-run

# 2023年以降のデータをコピー
python tools/download_and_upload_blob.py --from 2023/01/01

# 日付範囲を指定
python tools/download_and_upload_blob.py --from 2023/01/01 --to 2024/01/01

# 処理件数を制限
python tools/download_and_upload_blob.py --from 2023/01/01 --limit 100

# 2023年より前のデータをコピー
python tools/download_and_upload_blob.py --to 2023/01/01
```

### オプション

| オプション | 説明 | デフォルト |
|-----------|------|-----------|
| `--corp NAME` | 会社名（CorpOrg_key）でフィルタ | なし |
| `--branch NAME` | 支店名（Branch_Key）でフィルタ | なし |
| `--from DATE` | 開始日（yyyy/mm/dd、この日の00:00:00以降） | なし |
| `--to DATE` | 終了日（yyyy/mm/dd、この日の00:00:00より前） | なし |
| `--dry-run` | ドライラン（ダウンロードのみ、アップロードなし） | false |
| `--limit N` | 処理件数上限（0で無制限） | 0 |
| `--batch-size N` | 一度に取得する件数 | 100 |
| `--manual-only` | 手動入力データのみ（dataSource空） | false |

### 会社・支店指定の例

```bash
# s-style/hon のデータをすべてコピー（日付関係なく）
python tools/download_and_upload_blob.py --corp s-style --branch hon

# s-style/hon で 2020年以降のデータをコピー
python tools/download_and_upload_blob.py --corp s-style --branch hon --from 2020/01/01

# 件数確認（dry-run）
python tools/download_and_upload_blob.py --corp s-style --branch hon --dry-run --limit 10
```

### 手動入力データのみ移行

bkdataの `dataSource` が空のデータ（手動入力されたデータ）のみを移行できます。

```bash
# 手動入力データのサイズ確認（dry-run）
python tools/download_and_upload_blob.py --manual-only --dry-run --limit 10

# 手動入力データをすべてコピー
python tools/download_and_upload_blob.py --manual-only

# 手動入力データ + 日付範囲の組み合わせ
python tools/download_and_upload_blob.py --manual-only --from 2020/01/01
```

#### dataSourceの分布（2026-01-11調査）

| dataSource | 件数 | 割合 |
|------------|------|------|
| レインズ | 44,525件 | 96.9% |
| 空（手動入力） | 860件 | 1.9% |
| その他 | 575件 | 1.3% |
| **合計** | 45,960件 | 100% |

### 出力ファイルの場所
```
gs://s-style-hrd-blobs/{CorpOrg_key}/{Branch_Key}/{bkID}/{blobNo}.{ext}
```

例: `gs://s-style-hrd-blobs/s-style/hon/53043/1.pdf`

### 所要時間の目安
- 1ファイルあたり: 約2〜5秒（サイズによる）
- 266件（155MB）: 約10〜15分
- 29,610件（推定17GB）: 約15〜25時間

---

## 5. migrate_blob_to_gcs.py

### 概要
ファイルをGCSにコピーし、**DatastoreのblobKeyを更新**します。

### ⚠️ 注意
- Datastoreの `blobKey` フィールドを新しいGCS object nameに**上書き**します
- 元のBlobstore参照が失われます
- 本番移行の最終段階でのみ使用してください
- **`--transfer-files` オプションは使用しないでください**（下記参照）

### ❌ `--transfer-files` オプションについて
このオプションはBlobstoreの内部GCS（`gs://s-style-hrd.appspot.com/encoded_gs_key/...`）への直接アクセスを試みますが、**動作しません**。

理由:
- Blobstoreの内部GCSパス形式が不明
- `AMIfv...` 形式のblobKeyからGCSパスを特定できない

代わりに `download_and_upload_blob.py` でHTTP経由のコピーを先に実行してください。

### 特徴
- Datastoreを**更新する**
- 元のBlobstoreファイルは削除しない
- `--transfer-files` オプションでファイル転送も実行

### 使用方法

```bash
# dry-run（更新内容の確認のみ）
python tools/migrate_blob_to_gcs.py --from 2023/01/01 --dry-run

# メタデータのみ更新（ファイル転送なし）
python tools/migrate_blob_to_gcs.py --from 2023/01/01

# ファイル転送も行う
python tools/migrate_blob_to_gcs.py --from 2023/01/01 --transfer-files
```

### オプション

| オプション | 説明 | デフォルト |
|-----------|------|-----------|
| `--from DATE` | 開始日（yyyy/mm/dd） | なし |
| `--to DATE` | 終了日（yyyy/mm/dd） | なし |
| `--dry-run` | ドライラン | false |
| `--transfer-files` | ファイル転送も行う | false |
| `--limit N` | 処理件数上限 | 0 |
| `--batch-size N` | バッチサイズ | 100 |

---

## ハイブリッド運用（移行期間中）

### 問題
部分的に移行すると、2種類のURLが混在します：
- 移行済み: `bloburl = "/blob/s-style/hon/53043/1.pdf"`
- 未移行: `bloburl = "/serve/AMIfv94..."`

### 解決策
Flask側に `/serve/` ルートを追加し、Python 2.7アプリにリダイレクト：

```python
# main.py に追加済み
@test_bp.route('/serve/<path:blob_key>')
def serve_legacy(blob_key):
    return redirect(f"https://s-style-hrd.appspot.com/serve/{blob_key}")
```

### ルート対応表

| URL形式 | 処理 | 対象データ |
|---------|------|-----------|
| `/test/blob/<path>` | GCS Signed URL | 移行済み |
| `/test/serve/<blobKey>` | Python 2.7へリダイレクト | 未移行 |

### フロントエンド変更
**不要** - `Blob.bloburl` フィールドの値をそのまま使用している場合、移行ツールが `bloburl` を更新するため変更不要。

### 移行完了後
`/serve/` ルートは使われなくなりますが、残しておいても無害です。

---

## 推奨ワークフロー

### ステップ1: 現状確認
```bash
# 件数確認
python tools/check_blob_count.py

# blobKey形式確認
python tools/check_blobkey_format.py
```

### ステップ2: サンプルでサイズ確認（dry-run）
```bash
python tools/download_and_upload_blob.py --from 2023/01/01 --dry-run --limit 50
```

### ステップ3: 新しいデータからコピー開始
```bash
# 2023年以降（少量）を先にコピー
python tools/download_and_upload_blob.py --from 2023/01/01
```

### ステップ4: GCSで確認
```bash
# アップロード件数とサイズ確認
gsutil ls -r gs://s-style-hrd-blobs/** | wc -l
gsutil du -sh gs://s-style-hrd-blobs/
```

### ステップ5: 古いデータをコピー
```bash
# 2023年より前（大量）をコピー
python tools/download_and_upload_blob.py --to 2023/01/01
```

### ステップ6: Datastore更新（本番移行時）
```bash
# 最終段階でDatastoreを更新
python tools/migrate_blob_to_gcs.py --from 2023/01/01
python tools/migrate_blob_to_gcs.py --to 2023/01/01
```

---

## 実行環境

### 必要条件
- Python 3.11
- Google Cloud認証（`gcloud auth application-default login`）

### 依存パッケージ
```
google-cloud-ndb
google-cloud-storage
requests
```

### 実行コマンド（Windows）
```bash
cd C:\Users\hrsuk\prj\s-style-hrd\migration-src
C:\Python311\python.exe tools/download_and_upload_blob.py --from 2023/01/01
```

---

## 実績データ（2026-01-10）

### 2023年以降のデータ移行

| 項目 | 値 |
|------|------|
| 処理対象 | 266件 |
| 成功 | 264件 |
| スキップ | 2件（blobKeyなし） |
| エラー | 0件 |
| 合計サイズ | 155.4 MB |
| 平均サイズ | 602.8 KB |
| 所要時間 | 約10分 |

### 全体推定

| 区分 | 件数 | 推定サイズ |
|------|------|------------|
| 2023/01/01 以降 | 266件 | 155.4 MB（実測） |
| 2023/01/01 より前 | 29,610件 | 約17.4 GB（推定） |
| 全体 | 29,876件 | 約17.5 GB |

---

## データ整合性について

### コピー元とコピー先の同一性

`download_and_upload_blob.py` によるコピーは以下の理由で**同一性が保証**されます：

1. **完全なバイナリ転送**: HTTP GETでファイル全体をダウンロード
2. **変換なし**: ダウンロードしたバイト列をそのままGCSにアップロード
3. **Content-Type保持**: 元のContent-Typeヘッダーを維持

### 検証方法

コピー後にファイルサイズで検証可能：
```bash
# GCS側のファイルサイズ確認
gsutil ls -l gs://s-style-hrd-blobs/s-style/hon/53043/1.pdf

# 元ファイルのサイズ確認（HTTP HEAD）
curl -I https://s-style-hrd.appspot.com/serve/{blobKey}
```

### 注意事項
- 元のBlobstoreファイルは削除されない（両方に存在する状態）
- Datastore更新前であれば、いつでもやり直し可能

---

## トラブルシューティング

### ImportError: cannot import name 'ndb'
Python 3.12ではなく3.11を使用してください：
```bash
C:\Python311\python.exe tools/check_blob_count.py
```

### HTTP 405 エラー
HEADリクエストが許可されていません。GETリクエストを使用する `download_and_upload_blob.py` を使用してください。

### Source file not found
Blobstoreの内部GCSパスにアクセスできません。`download_and_upload_blob.py`（HTTP経由）を使用してください。

### レート制限
1秒間隔で実行されます。さらに遅くする場合はソースコードの `time.sleep(1.0)` を変更してください。
