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
| 2-1 前準備 | ✅ | GCSバケット作成済み、CORS設定必要 |
| 2-2 コード実装 | ❌ | gcs_utils.py作成、各ファイル修正 |
| 2-3 テスト | ❌ | アップロード/表示/削除テスト |
| 2-4 移行ツール | ❌ | データ移行ツール作成 |
| 2-5 本番移行 | ❌ | 既存データの移行 |

**影響ファイル**:
- `application/blobstoreutl.py` - 12箇所のTODO
- `application/handler.py` - 10箇所のTODO
- `application/mapreducemapper.py` - 5箇所のTODO

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
