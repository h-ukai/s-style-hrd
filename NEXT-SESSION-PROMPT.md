# 次セッションで行うこと

最終更新: 2026-01-10

## 現在の状態

### プロジェクト概要
- **目的**: webapp2 (Python 2.7) から Flask (Python 3.11) への移行
- **環境**: Google App Engine
- **本番**: `src/` ディレクトリ（Python 2.7、変更なし）
- **テスト**: `migration-src/` ディレクトリ（Python 3.11/Flask）

### テスト環境URL
- `https://s-style-hrd.appspot.com/test/` - テスト環境
- `https://s-style-hrd.appspot.com/` - 本番（Python 2.7）

### 最新デプロイ
- バージョン: `test-20260110-mail`
- サービス: `test-service`

---

## ✅ 完了: TODO-02 Blobstore → GCS 移行（ステップ2-1〜2-3）

### 完了日時: 2026-01-10

### ステップ2-1: 前準備 ✅ 完了

| 項目 | 状態 | 詳細 |
|------|------|------|
| GCSバケット作成 | ✅ 完了 | `s-style-hrd-blobs` |
| requirements.txt | ✅ 完了 | `google-cloud-storage==2.14.0` |
| app.yaml 環境変数 | ✅ 完了 | `GCS_BUCKET_NAME: s-style-hrd-blobs` |
| CORS設定 | ✅ 完了 | 適用済み |
| IAM API有効化 | ✅ 完了 | `iamcredentials.googleapis.com` |
| IAM権限付与 | ✅ 完了 | `roles/iam.serviceAccountTokenCreator`

**CORS設定内容**:
```json
[
  {
    "origin": ["https://s-style-hrd.appspot.com"],
    "method": ["GET", "PUT", "POST", "DELETE"],
    "responseHeader": ["Content-Type"],
    "maxAgeSeconds": 3600
  }
]
```

#### ステップ2-2: コード実装 ✅ 完了

##### 2-2-1: gcs_utils.py 新規作成 ✅
- **パス**: `migration-src/application/gcs_utils.py`
- **実装済み関数**: `get_gcs_client()`, `generate_object_name()`, `upload_file()`, `download_file()`, `delete_file()`, `generate_signed_url()`, `get_blob_url()`, `get_thumbnail_url()`, `generate_html()`, `is_image_file()`

##### 2-2-2: main.py に Blob ルート追加 ✅
- **実装済みエンドポイント**:
  - `GET /test/blob/<path:object_name>` - ファイルダウンロード
  - `GET /test/blob/<path:object_name>/thumbnail` - サムネイル取得
  - `POST /test/blob/upload` - ファイルアップロード
  - `GET /test/blob/upload-url` - アップロード用Signed URL取得
  - `DELETE /test/blob/<path:object_name>` - ファイル削除

##### 2-2-3: blobstoreutl.py 修正 ✅
##### 2-2-4: handler.py 修正 ✅
##### 2-2-5: mapreducemapper.py 修正 ✅

#### ステップ2-3: テスト ✅ 完了

| テスト項目 | 結果 |
|-----------|------|
| アップロードURL生成 API | ✅ 成功 |
| ファイルアップロード | ✅ 成功 |
| ファイルダウンロード | ✅ 成功（Signed URLリダイレクト） |
| ファイル削除 | ✅ 成功 |
| 削除後のアクセス | ✅ 404（正常） |

**デプロイバージョン**: `test-20260110-gcs2`

---

## ✅ 完了: TODO-02 ステップ2-4: データ移行ツール作成

### 完了日時: 2026-01-10

### ツール概要
- **パス**: `migration-src/tools/migrate_blob_to_gcs.py`
- **機能**: 日付範囲を指定して Blob データを GCS に移行

### 使用方法

```bash
# dry-run（移行対象の確認のみ）
python tools/migrate_blob_to_gcs.py --dry-run

# 日付範囲を指定して移行（yyyy/mm/dd形式）
python tools/migrate_blob_to_gcs.py --from 2024/01/01 --to 2024/12/31

# 特定日以降のデータを移行
python tools/migrate_blob_to_gcs.py --from 2024/06/01

# 特定日以前のデータを移行
python tools/migrate_blob_to_gcs.py --to 2024/06/01

# ファイル転送も行う（Blobstore内部GCS→新GCSバケット）
python tools/migrate_blob_to_gcs.py --from 2024/01/01 --transfer-files

# 処理件数を指定
python tools/migrate_blob_to_gcs.py --from 2024/01/01 --limit 500
```

### 日付指定の仕様
- `--from`: 指定日の 00:00:00 **以降**のデータが対象
- `--to`: 指定日の 00:00:00 **より前**のデータが対象（指定日は含まない）
- 片方のみの指定も可能

### オプション一覧

| オプション | 説明 |
|-----------|------|
| `--from DATE` | 開始日（yyyy/mm/dd形式） |
| `--to DATE` | 終了日（yyyy/mm/dd形式） |
| `--dry-run` | ドライランモード（実際の更新なし） |
| `--transfer-files` | ファイル転送も行う |
| `--limit N` | 処理件数上限（0で無制限） |
| `--batch-size N` | 一度に取得する件数（デフォルト: 100） |

### 注意事項
- GAE 上で実行する必要あり（NDB が必要）
- `--transfer-files` なしの場合はメタデータのみ更新
- 既に移行済みのデータはスキップされる

---

## 完了済みTODO

### TODO-01: 環境変数・シークレット設定 ✅ 完了
- Cloud Secret Manager API 有効化済み
- 登録済みシークレット:
  - `smtp-server`: sv1231.xserver.jp
  - `smtp-port`: 465
  - `smtp-user`: info@s-style.ne.jp
  - `smtp-password`: 登録済み
  - `imap-server`: sv1231.xserver.jp
  - `imap-port`: 993
  - `imap-user`: info@s-style.ne.jp
- app.yaml 環境変数:
  - `SECRET_KEY`: 設定済み
  - `GCP_PROJECT`: s-style-hrd
  - `BASE_URL`: https://s-style-hrd.appspot.com
  - `GCS_BUCKET_NAME`: s-style-hrd-blobs
- GCSバケット `s-style-hrd-blobs` 作成済み

### TODO-03: メール機能移行 ✅ コード実装完了
- `secret_manager.py` 新規作成（シークレット取得ユーティリティ）
- `messageManager.py` Secret Manager対応 + SSL/TLS
- `email_receiver.py` Secret Manager対応
- `sendmsg.py` Secret Manager対応 + SSL/TLS
- `memberSearchandMail.py` Flask移行完了（mailsendback, memberSearchandMailback追加）
- main.py ルート登録完了
- **ローカルSMTPテスト**: 成功（warao.shikyo@gmail.com受信確認）
- **GAE上テスト**: 未実施

---

## 残りTODO

### TODO-02: Blobstore → GCS 移行【優先度: 高】
**詳細**: `TODO-02-GCS移行.md`
**統一仕様**: `BLOBSTORE-GCS-UNIFIED-SPEC.md`

| ステップ | 状態 | 内容 |
|----------|------|------|
| 2-1 前準備 | ✅ 完了 | GCSバケット、CORS、IAM設定 |
| 2-2 コード実装 | ✅ 完了 | gcs_utils.py作成、各ファイル修正 |
| 2-3 テスト | ✅ 完了 | アップロード/表示/削除テスト |
| 2-4 移行ツール | ✅ 完了 | `tools/migrate_blob_to_gcs.py` |
| 2-5 本番移行 | ❌ 未実施 | 既存データの移行実行 |

#### Blobデータ ボリューム確認結果（2026-01-10）

| 区分 | 件数 | 割合 |
|------|------|------|
| **全体** | 29,876 件 | 100% |
| 2023/01/01 より前 | 29,610 件 | 99.1% |
| 2023/01/01 以降 | 266 件 | 0.9% |

#### ✅ 2023年以降のデータ GCSコピー完了（2026-01-11）

| 項目 | 結果 |
|------|------|
| 処理対象 | 266件 |
| 成功 | 264件 |
| スキップ | 2件（blobKeyなし） |
| エラー | 0件 |
| **合計サイズ** | **155.4 MB** |
| 平均サイズ | 602.8 KB |

**コピー先**: `gs://s-style-hrd-blobs/`

**注意**: Datastoreは未更新（blobKeyは元のまま）。ファイルコピーのみ完了。

#### 残り作業: 2023年より前のデータ

| 項目 | 値 |
|------|------|
| 件数 | 29,610件 |
| 推定サイズ | 約17.4 GB |
| 推定所要時間 | 15〜25時間（HTTP経由） |

**高速化オプション**: Python 2.7側に移行ハンドラを追加すればGAE内部で処理可能

#### 移行ツールドキュメント
- **パス**: `migration-src/tools/README.md`

**修正済みファイル**:
- `application/gcs_utils.py` - 新規作成（GCSユーティリティ）
- `application/blobstoreutl.py` - GCS対応完了
- `application/handler.py` - GCS対応完了
- `application/mapreducemapper.py` - GCS対応完了
- `main.py` - Blobルート追加
- `tools/migrate_blob_to_gcs.py` - データ移行ツール

---

### TODO-04: 本番移行対応【優先度: 中】
**詳細**: `TODO-04-本番移行対応.md`
**チェックリスト**: `PRODUCTION-REVERT-CHECKLIST.md`

| 項目 | 状態 |
|------|------|
| Blueprint URL プレフィックス変更 (`/test` → 空) | ❌ |
| app.yaml service 行削除 | ❌ |
| dispatch.yaml /test ルール削除 | ❌ |
| ログインリダイレクト先変更 | ❌ |
| 静的ファイルパス変更 | ❌ |

---

### TODO-05: セキュリティ対応【優先度: 高】
**詳細**: `TODO-05-セキュリティ対応.md`

| 項目 | 状態 |
|------|------|
| テストモードバイパス削除 | ✅ |
| 認証情報の Secret Manager 移行 | ✅ |
| CORS 設定制限 (sendmsg.py) | ❌ |
| XSS 対策 (mapreducemapper.py) | ❌ |
| 認証なしエンドポイント対策 | ❌ |
| Flask SECRET_KEY 設定 | ✅ |

---

### TODO-06: コードレビュー対応【優先度: 低】
**詳細**: `TODO-06-コードレビュー対応.md`

---

## 推奨作業順序

1. **TODO-02**: Blobstore → GCS 移行（次の主要タスク）
2. **TODO-05**: セキュリティ対応（残り項目）
3. **TODO-04**: 本番移行対応
4. **TODO-06**: コードレビュー対応

---

## 重要ファイル

### 作業履歴
- `作業履歴.md` - 今日の作業内容の詳細記録

### TODO作業指示書
| ファイル名 | 概要 |
|-----------|------|
| TODO-02-GCS移行.md | Blobstore→GCS移行の実装手順 |
| TODO-04-本番移行対応.md | 本番環境への移行手順 |
| TODO-05-セキュリティ対応.md | セキュリティ修正の手順 |
| TODO-06-コードレビュー対応.md | コードレビュー指摘事項 |

### GCS移行関連
| ファイル名 | 概要 |
|-----------|------|
| **BLOBSTORE-GCS-UNIFIED-SPEC.md** | **統一仕様書（必読）** |
| BLOBSTORE-GCS-MIGRATION-PLAN.md | 実装プラン |

### その他
| ファイル名 | 概要 |
|-----------|------|
| PRODUCTION-REVERT-CHECKLIST.md | 本番移行チェックリスト |
| mdcatalog.md | 使用中mdファイル一覧 |
| .claude/CLAUDE.md | プロジェクト設定 |

---

## クイックリファレンス

### デプロイコマンド（テスト環境）
```bash
cd migration-src && gcloud app deploy app.yaml --project=s-style-hrd --version=test-$(date +%Y%m%dt%H%M%S) --no-promote
```

### 作業ディレクトリ
```
C:\Users\hrsuk\prj\s-style-hrd\migration-src\
```

### Secret Manager シークレット一覧
```
smtp-server, smtp-port, smtp-user, smtp-password
imap-server, imap-port, imap-user
```

### 主要な対象ファイル（次タスク: GCS移行）
```
application/blobstoreutl.py
application/handler.py
application/mapreducemapper.py
```
