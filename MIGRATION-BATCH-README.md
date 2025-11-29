# GAE Migration Batch Processing

複数のClaude Codeエージェントを使用してファイルを並列または順次処理するためのバッチスクリプト集です。

## ファイル構成

```
s-style-hrd/
├── migrate-batch.ps1              # 並列実行スクリプト（推奨）
├── generate-batch-commands.ps1    # 個別コマンド生成スクリプト
├── file-list.txt                  # 処理対象ファイルリスト
├── migration-prompt-template.txt  # プロンプトテンプレート
└── MIGRATION-BATCH-README.md      # このファイル
```

## 使用方法

### 方法1: 並列実行（推奨）

複数のClaude Codeエージェントを同時に起動して並列処理します。

```powershell
# デフォルト設定で実行（最大3並列）
.\migrate-batch.ps1

# 並列数を指定して実行
.\migrate-batch.ps1 -MaxParallel 5

# ファイルリストとプロンプトを指定
.\migrate-batch.ps1 -FileListPath ".\my-files.txt" -PromptTemplatePath ".\my-prompt.txt"
```

**パラメータ:**
- `-FileListPath`: 処理対象ファイルリストのパス（デフォルト: `.\file-list.txt`）
- `-PromptTemplatePath`: プロンプトテンプレートのパス（デフォルト: `.\migration-prompt-template.txt`）
- `-MaxParallel`: 最大同時実行数（デフォルト: 3）

**出力:**
- `migration-logs/[日時]/` ディレクトリにログファイルとプロンプトファイルが保存されます
- `migration-logs/[日時]/results.csv` に処理結果のCSVが保存されます

### 方法2: 個別コマンド生成

ファイルリストから個別のバッチコマンドを生成します。生成されたコマンドを手動で実行できます。

```powershell
# バッチコマンドを生成
.\generate-batch-commands.ps1

# 生成されたバッチファイルを実行
.\run-migrations.bat
```

**パラメータ:**
- `-FileListPath`: 処理対象ファイルリストのパス（デフォルト: `.\file-list.txt`）
- `-PromptTemplatePath`: プロンプトテンプレートのパス（デフォルト: `.\migration-prompt-template.txt`）
- `-OutputBatchPath`: 出力バッチファイルのパス（デフォルト: `.\run-migrations.bat`）

**出力:**
- `run-migrations.bat`: 実行可能なバッチファイル
- `migration-prompts/`: 各ファイル用のプロンプトファイル

## ファイルリストの編集

`file-list.txt` を編集して処理対象ファイルを指定します。

```text
# コメント行（#で始まる行は無視されます）
# 空行も無視されます

# メインファイル
main.py

# 設定ファイル
setting.py
appengine_config.py

# アプリケーションファイル
application/handler.py
application/login.py
```

**フォーマット:**
- 1行に1ファイル
- パスは `src/` を含めない相対パス
- `#` で始まる行はコメント
- 空行は無視される

## プロンプトテンプレートのカスタマイズ

`migration-prompt-template.txt` を編集してプロンプトをカスタマイズできます。

```text
あなたは GAE Python 2.7 から Python 3.11 へのマイグレーションを実行するエキスパートです。

[あなたの指示内容]

あなたが処理するファイルは:
```

**重要:**
- プロンプトの末尾は「あなたが処理するファイルは:」で終わる必要はありません
- スクリプトが自動的に `\n\nあなたが処理するファイルは: [ファイル名]` を追加します

## ワークフロー例

### ステップ1: main.pyと関連ファイルの処理

```powershell
# file-list.txt を編集して main.py 関連ファイルのみを記載
# 例: main.py, setting.py, application/handler.py など

# 並列実行
.\migrate-batch.ps1 -MaxParallel 3

# ログを確認
Get-Content .\migration-logs\[日時]\results.csv
```

### ステップ2: 結果を確認してプロンプトを改善

```powershell
# ログファイルを確認
Get-Content .\migration-logs\[日時]\log-1-main.py.txt

# プロンプトを修正
notepad .\migration-prompt-template.txt

# 失敗したファイルのみを file-list.txt に記載して再実行
.\migrate-batch.ps1 -MaxParallel 3
```

### ステップ3: 次のファイルグループを処理

```powershell
# file-list.txt を更新して次のファイルグループを記載

# 並列実行
.\migrate-batch.ps1 -MaxParallel 3
```

## トラブルシューティング

### Claude Codeが見つからない

```powershell
# Claude Code がインストールされているか確認
claude-code --version

# パスが通っていない場合は、フルパスを指定してスクリプトを修正
```

### 並列実行でエラーが多発する

同時実行数を減らしてください:

```powershell
.\migrate-batch.ps1 -MaxParallel 1
```

### プロンプトが長すぎる

プロンプトテンプレートを簡潔にするか、ファイルリストを分割してください。

### 特定のファイルだけ再実行したい

```powershell
# file-list-retry.txt を作成して失敗したファイルのみを記載
# 例:
# application/login.py
# application/handler.py

# 再実行
.\migrate-batch.ps1 -FileListPath ".\file-list-retry.txt"
```

## 注意事項

1. **バックアップ**: 実行前に必ずソースコードのバックアップを取ってください
2. **Git管理**: Git でコミットしてから実行することを推奨
3. **段階的実行**: 一度に全ファイルを処理せず、段階的に実行してください
4. **並列数の調整**: システムリソースに応じて `-MaxParallel` を調整してください
5. **ログの確認**: 各処理のログを必ず確認してください

## ベストプラクティス

1. **小さいグループから開始**: main.py + 直接依存ファイル（5-10ファイル）から始める
2. **結果を確認**: 各グループの処理結果を確認してから次へ進む
3. **プロンプト改善**: 失敗パターンを分析してプロンプトを改善する
4. **依存関係順**: 依存されるファイル（モデル、ユーティリティ）を先に処理
5. **テスト**: 処理後は必ず構文チェックとテストを実行

## サンプル file-list.txt

### フェーズ1: 基盤ファイル
```text
setting.py
appengine_config.py
application/config.py
```

### フェーズ2: モデル
```text
application/models/member.py
application/models/bkdata.py
application/models/bklist.py
```

### フェーズ3: ユーティリティ
```text
application/session.py
application/chkauth.py
application/timemanager.py
```

### フェーズ4: ハンドラー
```text
main.py
application/handler.py
application/login.py
application/logout.py
```
