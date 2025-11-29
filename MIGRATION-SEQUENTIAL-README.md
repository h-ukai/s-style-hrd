# GAE Migration Sequential Processing（推奨版）

ファイルを1件ずつ順次処理し、各エージェント間で情報を引き継ぐバッチシステムです。

## 🎯 この方式の特徴

### ✅ メリット
1. **情報の引き継ぎ**: 前のファイルの処理結果を次のエージェントが参照可能
2. **依存関係の管理**: 未処理の依存モジュールを自動記録
3. **元ファイル保護**: `src/` は読み込み専用、`migration-src/` に出力
4. **進捗の可視化**: `migration-progress.md` で全体の進捗を一元管理
5. **トレーサビリティ**: どのファイルがどのファイルを参照しているか明確

### 📁 ファイル構成

```
s-style-hrd/
├── src/                              # 元のソースコード（読み込み専用）
│   ├── main.py
│   ├── application/
│   │   ├── login.py
│   │   └── ...
│   └── ...
│
├── migration-src/                    # マイグレーション結果（新規作成）
│   ├── main.py                       # マイグレーション後
│   ├── application/
│   │   ├── login.py                  # マイグレーション後
│   │   └── ...
│   └── ...
│
├── migrate-sequential.ps1            # ⭐ 順次処理スクリプト（推奨）
├── migration-prompt-template-v2.txt  # ⭐ 新バージョンテンプレート
├── migration-progress.md             # ⭐ 進捗管理ファイル（共有）
├── migration-progress-template.md    # 進捗ファイルのテンプレート
│
├── file-list.txt                     # 処理対象ファイルリスト
├── GAE_MIGRATION_STATE.md            # マイグレーションルール（参照用）
│
└── migration-logs/                   # ログ保存先
    └── [日時]/
        ├── prompt-1-main.py.txt
        ├── log-1-main.py.txt
        └── ...
```

## 🚀 使い方

### ステップ1: 進捗ファイルの初期化

```powershell
# テンプレートから進捗ファイルを作成
Copy-Item migration-progress-template.md migration-progress.md
```

### ステップ2: ファイルリストの編集

`file-list.txt` を編集して、処理したいファイルを**依存関係順**に記載:

```text
# 基盤モジュール（依存される側）から先に処理
setting.py
appengine_config.py

# モデル定義
application/models/member.py
application/models/bkdata.py

# ユーティリティ
application/session.py
application/chkauth.py

# ハンドラー（依存する側）
application/handler.py
application/login.py

# メインエントリーポイント（最後）
main.py
```

### ステップ3: バッチ実行

```powershell
# デフォルト設定で実行
.\migrate-sequential.ps1

# カスタム設定で実行
.\migrate-sequential.ps1 `
  -FileListPath ".\my-files.txt" `
  -PromptTemplatePath ".\migration-prompt-template-v2.txt" `
  -OutputDir ".\migration-output"
```

### ステップ4: 進捗確認

```powershell
# 進捗ファイルを確認
Get-Content .\migration-progress.md

# または
notepad .\migration-progress.md
```

## 📊 進捗管理ファイルの構造

`migration-progress.md` の内容例:

```markdown
# マイグレーション進捗状態

**開始日時**: 2024-01-15 14:00:00
**総ファイル数**: 10

---

## 処理済みファイル

### ✅ setting.py
- **状態**: 完了
- **日時**: 2024-01-15 14:05:00
- **出力パス**: migration-src/setting.py
- **依存関係**: なし（基盤モジュール）
- **注意事項**: 環境変数の読み込み方法を os.environ から app.config に変更

### ✅ application/models/member.py
- **状態**: 完了
- **日時**: 2024-01-15 14:10:00
- **出力パス**: migration-src/application/models/member.py
- **依存関係**: なし（モデル定義）
- **注意事項**:
  - db.ReferenceProperty を 3箇所で使用 → ndb.KeyProperty に変更
  - パスワードハッシュは SHA256 維持

### ✅ application/session.py
- **状態**: 完了
- **日時**: 2024-01-15 14:15:00
- **出力パス**: migration-src/application/session.py
- **依存関係**:
  - `application/models/member.py` (処理済み)
- **注意事項**:
  - Flask-Session (Datastore backend) に移行
  - session['member_id'] でメンバーID管理

---

## 未処理の依存関係

### application/handler.py
- **参照元**: application/login.py, application/logout.py
- **優先度**: 高（複数ファイルから参照）
- **メモ**: webapp2 ハンドラーの基底クラス、Flaskに移行必要

---

## 次に処理すべきファイル（推奨順）

1. ✅ setting.py - 完了
2. ✅ application/models/member.py - 完了
3. ✅ application/session.py - 完了
4. ⏳ application/handler.py - 次に処理
5. ⏳ application/login.py - handler.py の後
```

## 🔍 各エージェントの動作

### エージェントが実行する処理

1. **マイグレーションルール読み込み**
   - `GAE_MIGRATION_STATE.md` を読み込んでルールを理解

2. **進捗状況の確認**
   - `migration-progress.md` を読み込んで既処理ファイルを確認

3. **ソースファイルの読み込み**
   - `src/[ファイルパス]` を読み込み

4. **マイグレーション実行**
   - ルールに従ってコード変換

5. **出力ファイルの保存**
   - `migration-src/[ファイルパス]` に Write ツールで保存

6. **依存関係の分析**
   - インポート文から依存モジュールを抽出

7. **依存モジュールへのコメント追記**
   - すでに処理済みの依存モジュールに「参照元」コメントを追記

8. **進捗ファイルへの記録**
   - `migration-progress.md` に処理結果を Edit ツールで追記

## 🎨 ワークフロー例

### フェーズ1: 基盤モジュール

```powershell
# file-list.txt を編集
setting.py
appengine_config.py
application/config.py

# 実行
.\migrate-sequential.ps1

# 結果確認
notepad .\migration-progress.md
```

### フェーズ2: モデル定義

```powershell
# file-list.txt を編集
application/models/member.py
application/models/bkdata.py
application/models/bklist.py

# 実行
.\migrate-sequential.ps1

# 依存関係を確認
notepad .\migration-progress.md
```

### フェーズ3: ユーティリティ

```powershell
# 進捗ファイルから「次に処理すべきファイル」を確認
notepad .\migration-progress.md

# file-list.txt に推奨順で記載
application/session.py
application/chkauth.py
application/timemanager.py

# 実行
.\migrate-sequential.ps1
```

## 🔧 トラブルシューティング

### エラー: ファイルが見つからない

```powershell
# src/ ディレクトリ内のファイルを確認
Get-ChildItem -Recurse -Path .\src -Filter "*.py"

# file-list.txt のパスを修正
# 正しい例: application/login.py
# 間違い: src/application/login.py
```

### 依存関係のエラー

進捗ファイルの「未処理の依存関係」を確認して、依存されるファイルを先に処理:

```powershell
# 依存関係を確認
notepad .\migration-progress.md

# 依存されるファイルを file-list.txt の先頭に移動
# 例: session.py が login.py から参照される場合
#     session.py を login.py より先に記載
```

### 処理の途中で中断した場合

```powershell
# 進捗ファイルで最後に処理したファイルを確認
notepad .\migration-progress.md

# file-list.txt から処理済みファイルを削除または コメントアウト
# 未処理ファイルのみ残して再実行
.\migrate-sequential.ps1
```

## 💡 ベストプラクティス

1. **依存関係順に処理**
   - 依存される側（モデル、ユーティリティ）→ 依存する側（ハンドラー）

2. **小さいグループで実行**
   - 一度に 5-10 ファイル程度を処理
   - 結果を確認してから次へ進む

3. **進捗ファイルを活用**
   - `migration-progress.md` の「次に処理すべきファイル」を参考

4. **ログを必ず確認**
   - 各ファイルのログで詳細なエラー内容を確認
   - 問題があればプロンプトテンプレートを改善

5. **バックアップ**
   - 元の `src/` は変更されないが、念のため Git commit してから実行

## 📋 パラメータ一覧

| パラメータ | デフォルト値 | 説明 |
|----------|------------|------|
| `-FileListPath` | `.\file-list.txt` | 処理対象ファイルリスト |
| `-PromptTemplatePath` | `.\migration-prompt-template.txt` | プロンプトテンプレート |
| `-MigrationStateFile` | `.\GAE_MIGRATION_STATE.md` | マイグレーションルール |
| `-ProgressStateFile` | `.\migration-progress.md` | 進捗管理ファイル |
| `-SourceDir` | `.\src` | ソースディレクトリ |
| `-OutputDir` | `.\migration-src` | 出力ディレクトリ |

## 🆚 旧バージョンとの比較

| 機能 | 並列版 (migrate-batch.ps1) | 順次版 (migrate-sequential.ps1) ⭐推奨 |
|------|---------------------------|----------------------------------|
| 実行速度 | 高速（並列処理） | やや遅い（順次処理） |
| 情報引き継ぎ | なし | あり（進捗ファイル経由） |
| 依存関係管理 | なし | あり |
| 元ファイル保護 | なし（直接編集） | あり（読み込み専用） |
| トレーサビリティ | 低 | 高 |
| 推奨用途 | 独立したファイル群 | 依存関係があるファイル群 |

## ✨ まとめ

この順次処理方式は、**依存関係が複雑なプロジェクト**に最適です。

- ✅ 各エージェントが前の処理結果を参照
- ✅ 依存関係を自動追跡
- ✅ 元ファイルを保護
- ✅ 進捗を一元管理

まずは小規模なファイルグループで試してみてください！
