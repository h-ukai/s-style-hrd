# 次セッションで行うこと

最終更新: 2025-12-15

## 現在の状態

### 完了済み
- ブラウザエラーチェック（8ルート）完了
- `/bkedit.html` ルート修正完了（メニューからの遷移問題解決）
- mdファイル整理完了
- **Blobstore → GCS 移行調査完了**（4つのmdファイル作成）
- **ソースコードTODO抽出完了**（6つの作業指示mdファイル作成）

### テスト環境URL
- `https://s-style-hrd.appspot.com/test/` - インデックス
- `https://s-style-hrd.appspot.com/bkedit.html` - 物件登録

---

## 本番移行に向けたTODOリスト

### TODO-01: 環境変数・シークレット設定【優先度: 最高】
**詳細**: `TODO-01-環境変数設定.md`

| 項目 | 状態 | 備考 |
|------|------|------|
| SECRET_KEY 設定 | ❌ | 本番用ランダム文字列生成必要 |
| RECAPTCHA キー | ✅ | テスト環境に設定済み |
| SMTP 認証情報 | ❌ | Xserver（sv1231.xserver.jp）をSecret Managerに登録 |
| IMAP 認証情報 | ❌ | Secret Manager への移行必要 |
| GCP_PROJECT | ❌ | app.yaml に追加必要 |
| BASE_URL | ❌ | app.yaml に追加必要 |
| GCS_BUCKET_NAME | ❌ | バケット作成後に設定 |

---

### TODO-02: Blobstore → GCS 移行【優先度: 高】
**詳細**: `TODO-02-GCS移行.md`
**統一仕様**: `BLOBSTORE-GCS-UNIFIED-SPEC.md`

| ステップ | 状態 | 内容 |
|----------|------|------|
| 2-1 前準備 | ❌ | GCSバケット作成、CORS設定 |
| 2-2 コード実装 | ❌ | gcs_utils.py作成、各ファイル修正 |
| 2-3 テスト | ❌ | アップロード/表示/削除テスト |
| 2-4 移行ツール | ❌ | データ移行ツール作成 |
| 2-5 本番移行 | ❌ | 既存データの移行 |

**影響ファイル**:
- `application/blobstoreutl.py` - 12箇所のTODO
- `application/handler.py` - 10箇所のTODO
- `application/mapreducemapper.py` - 5箇所のTODO

---

### TODO-03: メール機能移行【優先度: 高】
**詳細**: `TODO-03-メール機能移行.md`

| 項目 | 状態 | 備考 |
|------|------|------|
| IMAP/SMTP 設定 | ❌ | Xserver（sv1231.xserver.jp）共通アカウント |
| Secret Manager 移行 | ❌ | mail-server, mail-user, mail-password 登録 |
| memberSearchandMail Flask移行 | ❌ | webapp2 → Flask 変換必要 |
| main.py ルート登録 | ❌ | check-incoming-mail エンドポイント |

---

### TODO-04: 本番移行対応【優先度: 中】
**詳細**: `TODO-04-本番移行対応.md`
**チェックリスト**: `PRODUCTION-REVERT-CHECKLIST.md`

| 項目 | 状態 | 備考 |
|------|------|------|
| Blueprint URL プレフィックス変更 | ❌ | `/test` → 空 |
| app.yaml service 行削除 | ❌ | test-service → default |
| dispatch.yaml /test ルール削除 | ❌ | - |
| ログインリダイレクト先変更 | ❌ | `/test/login` → `/login` |
| 静的ファイルパス変更 | ❌ | テンプレート内の確認必要 |

---

### TODO-05: セキュリティ対応【優先度: 高】
**詳細**: `TODO-05-セキュリティ対応.md`

| 項目 | 状態 | 備考 |
|------|------|------|
| テストモードバイパス削除 | ✅ | 2025-12-01 完了 |
| 認証情報の Secret Manager 移行 | ❌ | SMTP/IMAP |
| CORS 設定制限 | ❌ | sendmsg.py |
| XSS 対策 | ❌ | mapreducemapper.py |
| 認証なしエンドポイント対策 | ❌ | uploadbkdata.py 等 |
| Flask SECRET_KEY 設定 | ❌ | 本番用生成必要 |

---

### TODO-06: コードレビュー対応【優先度: 低】
**詳細**: `TODO-06-コードレビュー対応.md`

| レベル | 件数 | 内容 |
|--------|------|------|
| REVIEW-L1 | 約15件 | ndb構文、key()→key変換、Cloud Tasks |
| REVIEW-L2 | 約20件 | パフォーマンス、例外処理 |
| REVIEW-L3 | 約10件 | コード品質（u""削除等） |

---

## 推奨作業順序

### フェーズ1: 環境準備（先に完了させる）
1. **TODO-01**: 環境変数・シークレット設定
2. **TODO-05**: セキュリティ対応（Secret Manager 移行含む）

### フェーズ2: 機能実装
3. **TODO-02**: Blobstore → GCS 移行
4. **TODO-03**: メール機能移行

### フェーズ3: 本番移行
5. **TODO-04**: 本番移行対応
6. **TODO-06**: コードレビュー対応（必要に応じて）

---

## 重要ファイル一覧

### TODO作業指示書
| ファイル名 | 概要 |
|-----------|------|
| **TODO-01-環境変数設定.md** | 環境変数とシークレットの設定手順 |
| **TODO-02-GCS移行.md** | Blobstore→GCS移行の実装手順 |
| **TODO-03-メール機能移行.md** | IMAP/SMTP移行の実装手順 |
| **TODO-04-本番移行対応.md** | 本番環境への移行手順 |
| **TODO-05-セキュリティ対応.md** | セキュリティ修正の手順 |
| **TODO-06-コードレビュー対応.md** | コードレビュー指摘事項の修正 |

### GCS移行関連
| ファイル名 | 概要 |
|-----------|------|
| **BLOBSTORE-GCS-UNIFIED-SPEC.md** | **統一仕様書（必読）** |
| BLOBSTORE-GCS-MIGRATION-PLAN.md | 実装プラン |
| BLOBSTORE-GCS-DATA-MIGRATION-TOOL-SPEC.md | データ移行ツール要件 |
| BLOBSTORE-GCS-MIGRATION-RESEARCH.md | 調査報告書 |

### その他
| ファイル名 | 概要 |
|-----------|------|
| PRODUCTION-REVERT-CHECKLIST.md | 本番移行チェックリスト |
| logs/summary-report.md | テスト結果サマリー |
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

### 主要な対象ファイル
```
# GCS移行
application/blobstoreutl.py
application/handler.py
application/mapreducemapper.py

# メール機能
application/email_receiver.py
application/messageManager.py
application/sendmsg.py

# 本番移行
main.py
app.yaml
dispatch.yaml
application/SecurePage.py
application/proc.py
```
