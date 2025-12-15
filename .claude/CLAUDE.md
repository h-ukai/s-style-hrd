# S-Style HRD プロジェクト設定

## プロジェクト概要
webapp2 から Flask への移行プロジェクト（Google App Engine）

### 現在の状態
- **フェーズ**: テスト環境でのブラウザ検証完了
- **次フェーズ**: 本番移行準備
- **テスト結果**: `logs/summary-report.md` を参照

---

## URL構造（重要）

### テスト環境
- Blueprint: `url_prefix='/test'`
- 基本URL: `https://s-style-hrd.appspot.com/test/*`

### ルーティングの注意点
```
/test/*          → test_bp (Blueprint) で定義
/bkedit.html     → app.route で定義（ドメインルート）
```
**理由**: メニューが相対パスで生成されるため、ドメインルートにもルートが必要

### 静的ファイルパス
```
テスト環境: /test/css/, /test/js/, /test/img/
本番移行時: /css/, /js/, /img/ に変更必要
```

---

## よくある修正パターン

### Django → Jinja2 テンプレート構文
| Django | Jinja2 |
|--------|--------|
| `\|default_if_none:""` | `\|default('')` |
| `{% ifequal a b %}` | `{% if a == b %}` |

### jQuery バージョン問題
`.on()` メソッドは jQuery 1.7 以降で追加
```html
修正前: jquery/1.3.2/jquery.min.js
修正後: jquery/1.7.1/jquery.min.js
```

### 静的ファイルパス（テスト環境）
```html
修正前: ../css/baselayout.css
修正後: /test/css/baselayout.css
```

---

## 重要ファイル

### 本番移行時の注意事項
- **PRODUCTION-REVERT-CHECKLIST.md** - 本番移行時に必要な変更点と戻し手順

### セッション管理
- **NEXT-SESSION-PROMPT.md** - 次のセッションで行うことのまとめを記述
- **mdcatalog.md** - 使用中のmdファイル一覧と要約
- **logs/summary-report.md** - テスト結果と修正履歴

---

## mdファイル管理ルール

### 使用中のmdファイル
- `mdcatalog.md` に要約を記述すること
- 新規作成時は必ず `mdcatalog.md` に追加

### 不要になったmdファイル
- `/oldmd/` フォルダに移動すること
- 移動時は `mdcatalog.md` から削除

### 次セッションの引き継ぎ
- セッション終了時は `NEXT-SESSION-PROMPT.md` に次にやることを記述
- 新セッション開始時はこのファイルを読むこと

---

## デプロイ

### テスト環境
```bash
cd migration-src && gcloud app deploy app.yaml --project=s-style-hrd --version=test-$(date +%Y%m%dt%H%M%S) --no-promote
```

### 本番環境
`PRODUCTION-REVERT-CHECKLIST.md` を参照のこと
