# mdファイルカタログ

使用中のmdファイル一覧。不要になったファイルは `/oldmd/` に移動すること。

## アクティブなmdファイル

### プロジェクト管理
| ファイル名 | 概要 | 最終更新 |
|-----------|------|----------|
| NEXT-SESSION-PROMPT.md | 次セッションで行う作業のまとめ（TODOリスト含む） | 2025-12-15 |
| PRODUCTION-REVERT-CHECKLIST.md | 本番移行時の変更点と戻し手順 | 2025-12-05 |
| mdcatalog.md | このファイル。使用中mdの一覧 | 2025-12-15 |
| .claude/CLAUDE.md | プロジェクト固有のClaude設定（自動読込） | 2025-12-05 |
| logs/summary-report.md | ブラウザテスト結果サマリー | 2025-12-05 |

### TODO作業指示書（2025-12-15 新規作成）
| ファイル名 | 概要 | 優先度 |
|-----------|------|--------|
| TODO-01-環境変数設定.md | 環境変数・シークレットの設定手順 | 最高 |
| TODO-02-GCS移行.md | Blobstore→GCS移行の実装手順 | 高 |
| TODO-03-メール機能移行.md | IMAP/SMTP移行の実装手順 | 高 |
| TODO-04-本番移行対応.md | 本番環境への移行手順 | 中 |
| TODO-05-セキュリティ対応.md | セキュリティ修正の手順 | 高 |
| TODO-06-コードレビュー対応.md | コードレビュー指摘事項の修正 | 低 |

### GCS移行関連
| ファイル名 | 概要 | 最終更新 |
|-----------|------|----------|
| BLOBSTORE-GCS-UNIFIED-SPEC.md | **統一仕様書**（命名規則・エンドポイント・実装仕様） | 2025-12-15 |
| BLOBSTORE-GCS-MIGRATION-PLAN.md | Blobstore→GCS移行の実装プラン | 2025-12-15 |
| BLOBSTORE-GCS-DATA-MIGRATION-TOOL-SPEC.md | データ移行ツールの要件定義書 | 2025-12-15 |
| BLOBSTORE-GCS-MIGRATION-RESEARCH.md | Blobstore→GCS移行の調査報告書 | 2025-12-15 |

## サブフォルダ内

| ファイル名 | 概要 |
|-----------|------|
| migration-src/application/login_REVIEW_FIXES.md | login.py のレビュー修正記録 |

## アーカイブ済み

`/oldmd/` フォルダに移動済み。必要時に参照可能。

- migration-progress-group-*.md (グループ別移行進捗)
- CODE_REVIEW_LOG_GROUP_*.md (グループ別コードレビュー)
- TEMPLATE_MIGRATION_*.md (テンプレート移行関連)
- GAE_MIGRATION_STATE*.md (移行状態)
- その他プロンプト/ログファイル
