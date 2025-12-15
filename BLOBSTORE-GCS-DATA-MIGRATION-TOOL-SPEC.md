# Blobstore → GCS データ移行ツール 要件定義書

## 1. 概要

### 1.1 目的

既存の Google App Engine Blobstore に保存されているファイルデータを Google Cloud Storage (GCS) に移行し、Datastore の参照情報を更新するためのバッチ処理ツールを作成する。

### 1.2 背景

- GAE Python 2.7 → Python 3.11 移行に伴い、Blobstore API が廃止
- 既存データを GCS に移行し、アプリケーションコードと整合性を取る必要がある

### 1.3 スコープ

| 対象 | 説明 |
|------|------|
| 移行元 | GAE Blobstore |
| 移行先 | Google Cloud Storage (GCS) |
| メタデータ | Datastore: Blob, Bloblist, FileInfo モデル |

---

## 2. 機能要件

### 2.1 データ移行機能

#### 2.1.1 Blobstore → GCS ファイル転送

- Blobstore に保存されている全ファイルを GCS にコピー
- ファイル名・Content-Type を保持
- 元の BlobKey をベースに GCS object name を決定

#### 2.1.2 Datastore メタデータ更新

- `Blob` モデルの以下フィールドを更新:
  - `blobKey`: GCS object name に変更
  - `bloburl`: GCS URL に変更
  - `thumbnailurl`: GCS サムネイル URL に変更（画像の場合）
  - `html`: 新しい URL を反映した HTML に更新

- `Bloblist` モデルも同様に更新

- `FileInfo` モデルの `blob` フィールドを GCS object name に更新

### 2.2 進捗管理機能

#### 2.2.1 移行状態の記録

- 処理済み / 未処理 / エラー のステータス管理
- 再実行時に処理済みをスキップ

#### 2.2.2 ログ出力

- 処理件数
- エラー詳細
- 所要時間

### 2.3 検証機能

#### 2.3.1 移行前検証

- Blobstore データの件数確認
- 総ファイルサイズの確認
- 想定移行時間の算出

#### 2.3.2 移行後検証

- GCS ファイル件数と Datastore 件数の一致確認
- サンプリングによるファイル内容検証
- URL アクセス可否確認

---

## 3. 非機能要件

### 3.1 パフォーマンス

| 項目 | 要件 |
|------|------|
| 処理速度 | 100ファイル/分 以上 |
| 並列処理 | 最大10並列 |
| タイムアウト | 1ファイルあたり 60秒 |

### 3.2 信頼性

| 項目 | 要件 |
|------|------|
| 再開可能性 | 中断後に再開可能 |
| エラーハンドリング | 1ファイル失敗でも継続 |
| リトライ | 最大3回リトライ |

### 3.3 セキュリティ

| 項目 | 要件 |
|------|------|
| 認証 | サービスアカウント使用 |
| 権限 | Blobstore 読取、GCS 書込、Datastore 読書 |
| ログ | 機密情報をログ出力しない |

---

## 4. システム設計

### 4.1 アーキテクチャ

```
┌─────────────────────────────────────────────────────────────┐
│                     Migration Tool                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │   Scanner   │→ │  Migrator   │→ │  Validator  │        │
│  │             │  │             │  │             │        │
│  │ - List Blob │  │ - Copy File │  │ - Verify    │        │
│  │ - Count     │  │ - Update DS │  │ - Report    │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
│         │               │                │                 │
│         ▼               ▼                ▼                 │
│  ┌─────────────────────────────────────────────┐          │
│  │            Progress Tracker                  │          │
│  │  (Datastore: MigrationStatus model)          │          │
│  └─────────────────────────────────────────────┘          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
         │                │                │
         ▼                ▼                ▼
    ┌─────────┐     ┌─────────┐     ┌─────────┐
    │Blobstore│     │   GCS   │     │Datastore│
    │ (読取)  │     │ (書込)  │     │(読書)   │
    └─────────┘     └─────────┘     └─────────┘
```

### 4.2 データモデル

#### 4.2.1 MigrationStatus（進捗管理用）

```python
class MigrationStatus(ndb.Model):
    """移行状態管理モデル"""
    blob_key = ndb.StringProperty(required=True)      # 元の BlobKey
    gcs_object_name = ndb.StringProperty()            # GCS object name
    status = ndb.StringProperty(choices=[
        'pending',      # 未処理
        'in_progress',  # 処理中
        'completed',    # 完了
        'failed'        # 失敗
    ])
    error_message = ndb.TextProperty()                # エラーメッセージ
    retry_count = ndb.IntegerProperty(default=0)      # リトライ回数
    file_size = ndb.IntegerProperty()                 # ファイルサイズ
    content_type = ndb.StringProperty()               # Content-Type
    created_at = ndb.DateTimeProperty(auto_now_add=True)
    updated_at = ndb.DateTimeProperty(auto_now=True)
```

#### 4.2.2 MigrationSummary（サマリー用）

```python
class MigrationSummary(ndb.Model):
    """移行サマリーモデル"""
    run_id = ndb.StringProperty(required=True)        # 実行ID
    total_count = ndb.IntegerProperty()               # 総件数
    completed_count = ndb.IntegerProperty()           # 完了件数
    failed_count = ndb.IntegerProperty()              # 失敗件数
    total_size_bytes = ndb.IntegerProperty()          # 総サイズ
    started_at = ndb.DateTimeProperty()               # 開始日時
    finished_at = ndb.DateTimeProperty()              # 終了日時
    status = ndb.StringProperty()                     # 全体ステータス
```

### 4.3 GCS オブジェクト命名規則

```
gs://{BUCKET_NAME}/{CorpOrg_key}/{Branch_Key}/{bkID}/{blobNo}_{original_filename}

例:
gs://s-style-hrd-blobs/s-style/hon/001/1_exterior.jpg
gs://s-style-hrd-blobs/s-style/hon/001/2_floor_plan.pdf
```

---

## 5. 処理フロー

### 5.1 全体フロー

```
[開始]
   │
   ▼
[1. 初期化]
   │ - MigrationSummary 作成
   │ - GCS bucket 確認
   │
   ▼
[2. スキャン]
   │ - Datastore から Blob 一覧取得
   │ - MigrationStatus レコード作成（pending）
   │ - 件数・サイズ集計
   │
   ▼
[3. 移行実行]
   │ - pending の MigrationStatus を取得
   │ - Blobstore からファイル読取
   │ - GCS にアップロード
   │ - Datastore 更新
   │ - MigrationStatus を completed に
   │ - エラー時は failed + リトライ
   │
   ▼
[4. 検証]
   │ - 完了件数確認
   │ - サンプル検証
   │ - レポート生成
   │
   ▼
[終了]
```

### 5.2 1ファイルの移行フロー

```python
def migrate_single_blob(blob_entity):
    """
    1ファイルの移行処理
    """
    # 1. 移行状態を in_progress に更新
    update_status(blob_entity.blobKey, 'in_progress')

    try:
        # 2. Blobstore からファイル取得
        blob_info = blobstore.BlobInfo.get(blob_entity.blobKey)
        blob_reader = blobstore.BlobReader(blob_entity.blobKey)
        file_data = blob_reader.read()

        # 3. GCS object name 決定
        gcs_object_name = generate_gcs_object_name(blob_entity)

        # 4. GCS にアップロード
        upload_to_gcs(
            file_data,
            gcs_object_name,
            content_type=blob_info.content_type
        )

        # 5. Datastore 更新
        update_blob_entity(blob_entity, gcs_object_name)

        # 6. 移行状態を completed に更新
        update_status(blob_entity.blobKey, 'completed', gcs_object_name)

    except Exception as e:
        # エラー時は failed に更新
        update_status(blob_entity.blobKey, 'failed', error=str(e))
        raise
```

---

## 6. 実行方法

### 6.1 コマンドライン インターフェース

```bash
# スキャンのみ（件数確認）
python migration_tool.py scan

# ドライラン（実際の移行なし）
python migration_tool.py migrate --dry-run

# 移行実行
python migration_tool.py migrate

# 移行実行（並列数指定）
python migration_tool.py migrate --workers=10

# 特定の CorpOrg のみ移行
python migration_tool.py migrate --corp-org=s-style

# 検証のみ
python migration_tool.py verify

# レポート出力
python migration_tool.py report
```

### 6.2 Cloud Tasks / Cloud Run での実行

大量データの場合、Cloud Tasks または Cloud Run Jobs での実行を推奨:

```yaml
# cloud_run_job.yaml
apiVersion: run.googleapis.com/v1
kind: Job
metadata:
  name: blobstore-migration
spec:
  template:
    spec:
      containers:
        - image: gcr.io/s-style-hrd/migration-tool
          command: ["python", "migration_tool.py", "migrate"]
          resources:
            limits:
              memory: "2Gi"
              cpu: "2"
```

---

## 7. エラーハンドリング

### 7.1 エラー種別と対処

| エラー種別 | 原因 | 対処 |
|-----------|------|------|
| BlobNotFoundError | Blobstore にファイルなし | スキップ、警告ログ |
| GCSUploadError | GCS アップロード失敗 | リトライ（最大3回） |
| DatastoreError | Datastore 更新失敗 | トランザクションロールバック、リトライ |
| TimeoutError | 処理タイムアウト | リトライ |
| QuotaExceededError | API クォータ超過 | 待機後リトライ |

### 7.2 リトライ戦略

```python
RETRY_CONFIG = {
    'max_retries': 3,
    'initial_delay': 1,      # 秒
    'max_delay': 60,         # 秒
    'exponential_base': 2,   # 指数バックオフ
}
```

---

## 8. ファイル構成

```
migration-src/
├── tools/
│   └── blobstore_migration/
│       ├── __init__.py
│       ├── migration_tool.py      # メインスクリプト
│       ├── scanner.py             # スキャン処理
│       ├── migrator.py            # 移行処理
│       ├── validator.py           # 検証処理
│       ├── models.py              # MigrationStatus 等
│       ├── gcs_client.py          # GCS 操作
│       ├── blobstore_client.py    # Blobstore 操作
│       ├── config.py              # 設定
│       └── utils.py               # ユーティリティ
└── requirements-migration.txt     # 移行ツール用依存パッケージ
```

---

## 9. テスト計画

### 9.1 単体テスト

- `scanner.py`: Datastore クエリのモック
- `migrator.py`: Blobstore/GCS のモック
- `validator.py`: 検証ロジック

### 9.2 統合テスト

- テスト用バケットでの E2E テスト
- 少量データ（10件）での動作確認

### 9.3 本番移行前テスト

- ステージング環境での全量移行テスト
- パフォーマンス計測
- ロールバック手順確認

---

## 10. 移行スケジュール案

```
Day 1: ツール開発・単体テスト
Day 2: 統合テスト・ステージング移行
Day 3: 本番移行（メンテナンス時間帯）
Day 4: 検証・問題対応
```

---

## 11. ロールバック計画

### 11.1 移行中断時

- MigrationStatus で pending/in_progress のレコードを確認
- 中断前の状態に戻す必要なし（Blobstore は変更されない）

### 11.2 移行完了後のロールバック

- Datastore のバックアップから復元
- GCS のバケットを削除

---

## 12. 成果物

| 成果物 | 説明 |
|-------|------|
| migration_tool.py | 移行ツール本体 |
| MigrationStatus | 進捗管理用 Datastore モデル |
| 移行レポート | CSV/JSON 形式のレポート |
| 実行ログ | Cloud Logging に出力 |
