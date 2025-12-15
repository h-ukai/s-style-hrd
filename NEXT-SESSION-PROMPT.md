# 次セッションで行うこと

最終更新: 2025-12-15

## 現在の状態

### 完了済み
- ブラウザエラーチェック（8ルート）完了
- `/bkedit.html` ルート修正完了（メニューからの遷移問題解決）
- mdファイル整理完了
- **Blobstore → GCS 移行調査完了**（4つのmdファイル作成）

### テスト環境URL
- `https://s-style-hrd.appspot.com/test/` - インデックス
- `https://s-style-hrd.appspot.com/bkedit.html` - 物件登録

---

## 次にやること

### フェーズ1: テスト環境の機能検証（優先度: 高）

1. **残りのルート機能テスト**
   - 物件登録（保存・変更・確認ボタン）
   - 物件検索
   - その他の未テストルート

2. **コンソールエラーの調査（任意）**
   - bkedit.html: ローカルファイルパス参照（レガシー問題）
   - bkedit.html: JavaScript null reference エラー
   - Google Maps API 非推奨警告

---

### フェーズ2: Blobstore → GCS 移行（優先度: 高）

**参照ドキュメント**:
- `BLOBSTORE-GCS-UNIFIED-SPEC.md` - **統一仕様書（最初に参照）**
- `BLOBSTORE-GCS-MIGRATION-PLAN.md` - 実装プラン
- `BLOBSTORE-GCS-DATA-MIGRATION-TOOL-SPEC.md` - データ移行ツール要件
- `BLOBSTORE-GCS-MIGRATION-RESEARCH.md` - 調査報告書

#### ステップ2-1: 前準備
- [ ] GCS バケット作成: `s-style-hrd-blobs`
- [ ] CORS 設定
- [ ] `requirements.txt` に `google-cloud-storage>=2.10.0` 追加
- [ ] `app.yaml` に環境変数追加

#### ステップ2-2: コード実装
- [ ] `gcs_utils.py` 新規作成（統一仕様書 セクション5.1）
- [ ] `blobstoreutl.py` 修正（統一仕様書 セクション7.1）
- [ ] `handler.py` 修正（統一仕様書 セクション7.3）
- [ ] `mapreducemapper.py` 修正（統一仕様書 セクション7.2）
- [ ] `main.py` にルート登録（統一仕様書 セクション5.2）
- [ ] `templates/blobstoreutl.html` Django構文修正

#### ステップ2-3: テスト環境検証
- [ ] 画像アップロードテスト
- [ ] 画像表示テスト（サムネイル・元画像）
- [ ] ファイルダウンロードテスト
- [ ] 削除テスト

#### ステップ2-4: データ移行ツール作成
- [ ] `tools/blobstore_migration/` ディレクトリ作成
- [ ] スキャン機能実装
- [ ] 移行処理実装
- [ ] 検証機能実装

#### ステップ2-5: 本番データ移行
- [ ] ステージング環境でテスト移行
- [ ] 本番移行実行（メンテナンス時間帯）
- [ ] 移行後検証

---

### フェーズ3: 本番移行準備（優先度: 中）

1. **本番移行チェックリスト確認**
   - `PRODUCTION-REVERT-CHECKLIST.md` の確認
   - 静的ファイルパス変更箇所の洗い出し
   - Blueprintプレフィックス削除の準備

2. **移行後の確認事項**
   - 全ルートの動作確認
   - 画像表示の確認
   - パフォーマンス確認

---

## 重要ファイル

| ファイル | 用途 |
|----------|------|
| **BLOBSTORE-GCS-UNIFIED-SPEC.md** | **Blob移行の統一仕様（必読）** |
| BLOBSTORE-GCS-MIGRATION-PLAN.md | Blob移行の実装プラン |
| BLOBSTORE-GCS-DATA-MIGRATION-TOOL-SPEC.md | データ移行ツール要件 |
| BLOBSTORE-GCS-MIGRATION-RESEARCH.md | Blob移行の調査報告 |
| PRODUCTION-REVERT-CHECKLIST.md | 本番移行手順 |
| logs/summary-report.md | テスト結果サマリー |
| mdcatalog.md | 使用中mdファイル一覧 |
| .claude/CLAUDE.md | プロジェクト設定（自動読込） |

---

## Blob移行の要点

### 移行対象
| モデル | 対象 |
|-------|-----|
| Blob | ✅ `blobKey`, `bloburl`, `thumbnailurl`, `html` を更新 |
| FileInfo | ✅ `blob` フィールドを更新 |
| BKdata | ❌ 対象外（blob識別子なし） |
| Bloblist | ❌ 除外（未使用） |

### 統一エンドポイント
```
旧: /serve/{blobKey}, /gcs-serve/{blobKey}
新: /blob/{object_name}
    /blob/{object_name}/thumbnail
```

### GCS Object Name 形式
```
{CorpOrg_key}/{Branch_Key}/{bkID}/{blobNo}.{extension}
例: s-style/hon/001/1.jpg
```

---

## 作業ディレクトリ
`C:\Users\hrsuk\prj\s-style-hrd\migration-src\`

## デプロイコマンド
```bash
cd migration-src && gcloud app deploy app.yaml --project=s-style-hrd --version=test-$(date +%Y%m%dt%H%M%S) --no-promote
```
