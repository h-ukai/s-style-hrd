あなたは Google App Engine Python 2.7 から Python 3.11 へのマイグレーションを実行するエキスパートです。

---

# 🎯 あなたへの実行指示（必ず最初に読むこと）

## 実行フロー

このプロンプトを受け取ったら、以下の手順を**自動的に**実行してください：

### ステップ1: 進捗確認

1. **Read** `C:\Users\hrsuk\prj\s-style-hrd\migration-progress.md`
2. 各グループの完了状態を確認

### ステップ2: 並列タスク起動

**Task ツールを使用して、未完了のグループを並列に処理します。**

- **重要**: すべてのタスクを**同じメッセージ内で一度に**起動してください
- 各タスクには下記の「グループ別タスクプロンプト」を使用
- `subagent_type: "general-purpose"` を指定
- `model: "haiku"` を使用（コスト削減のため）

**例**:
```
未完了グループが 2, 3, 5 の場合:
→ 1つのメッセージで Task ツールを3回呼び出し（グループ2, 3, 5用）
```

### ステップ3: タスク完了待機と報告

すべてのタスクが完了したら、以下を報告：

```
🎉 全タスク完了

完了グループ: {グループ番号リスト}
処理ファイル数: {合計数}
成功: {数}
失敗: {数}（ある場合）

次の手順:
「すべてのファイルが完了しました。コードレビューが必要な場合は別途指示してください。」
```

---

# 📋 グループ別タスクプロンプト

各グループのタスクには、以下のプロンプトテンプレートを使用してください：

```
あなたは Google App Engine Python 2.7 から Python 3.11 へのマイグレーションタスクを実行します。

## タスク概要
グループ {番号} の全ファイルをマイグレーションし、migration-progress.md に記録してください。

## 必須手順

### 1. 事前準備
- Read: C:\Users\hrsuk\prj\s-style-hrd\GAE_MIGRATION_STATE.md（マイグレーションルール確認）
- Read: C:\Users\hrsuk\prj\s-style-hrd\migration-src\main.py（main.py の現在の状態確認）

### 2. 処理対象ファイル
{グループ内ファイルリスト}

### 3. 各ファイルの処理手順

for ファイル in 処理対象ファイル:
    1. Read: C:\Users\hrsuk\prj\s-style-hrd\src\{ファイルパス}
    2. マイグレーション実行（下記「詳細なマイグレーションルール」参照）
    3. Write: C:\Users\hrsuk\prj\s-style-hrd\migration-src\{ファイルパス}
    4. main.py 更新（webapp2ハンドラーの場合のみ）
    5. migration-progress.md に記録（競合時はリトライ）

---

## 詳細なマイグレーションルール

### ソースファイルの読み込み
```
Read: C:\Users\hrsuk\prj\s-style-hrd\src\{ファイルパス}
```

### マイグレーション実行

GAE_MIGRATION_STATE.md のマイグレーションルールに従って変換。以下の順序で適用：

1. **インポート文の修正**
   - `google.appengine.ext` → `google.cloud.ndb`
   - `from StringIO import StringIO` → `import io`
   - など

2. **モデル定義の修正**
   - `db.Model` → `ndb.Model`
   - `db.StringProperty` → `ndb.StringProperty`
   - など

3. **webapp2 → Flask の変更**
   - `webapp2.RequestHandler` クラス → Flask ルート関数
   - `self.request.get()` → `request.args.get()` / `request.form.get()`
   - `self.response.out.write()` → `return` 文
   - など

4. **リクエスト/レスポンス処理の変更**
   - `self.redirect()` → `return redirect()`
   - `template.render()` → `render_template()`
   - など

5. **Python 2→3 構文の修正**
   - `print` 文 → `print()` 関数
   - `except Exception, e:` → `except Exception as e:`
   - `.iteritems()` → `.items()`
   - `unicode(text, enc)` → `text.decode(enc)` または `text`
   - `u"文字列"` → `"文字列"`
   - など

### 出力ファイルの保存

```
Write: C:\Users\hrsuk\prj\s-style-hrd\migration-src\{ファイルパス}
```

**注意**: ディレクトリ構造を維持
- 例: `src/application/login.py` → `migration-src/application/login.py`

### 依存関係の分析

対象ファイルがインポートしている**プロジェクト内モジュール**を特定：

**プロジェクト内モジュールの判定基準:**
- ✅ `from application.xxx import ...` → プロジェクト内
- ✅ `from geo.xxx import ...` → プロジェクト内
- ✅ `import application.xxx` → プロジェクト内
- ✅ `from dataProvider.xxx import ...` → プロジェクト内
- ❌ `from google.cloud import ...` → 外部ライブラリ（記録不要）
- ❌ `from flask import ...` → 外部ライブラリ（記録不要）

### セキュリティチェック

以下の脆弱性がないか確認：
- XSS (クロスサイトスクリプティング)
- SQLインジェクション
- コマンドインジェクション
- 認証なしアクセス
- CSRF脆弱性

**脆弱性を発見した場合:**
- ❌ 修正しない（既存システムの動作を変えない）
- ✅ コメントで警告を追加
- ✅ migration-progress.md に記録

---

### 4. main.py の更新ルール（webapp2ハンドラーの場合）

**main.py が期待する動作：**
- webapp2.RequestHandler クラスを Flask 関数に変換済みであること
- 各ハンドラーに対応する Flask ルート関数が存在すること
- インポート文とルート登録がコメントアウトされていること

**更新手順：**
1. 処理したファイルが webapp2.RequestHandler クラスの場合
2. migration-src/main.py を Edit ツールで更新：
   - インポート文のコメント解除
   - @app.route デコレータのコメント解除
   - ルート関数定義のコメント解除

**例:**
```python
# 変更前（コメントアウトされている）
# from application.login import login_route, logout_route
# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     return login_route()

# 変更後（コメント解除）
from application.login import login_route, logout_route
@app.route('/login', methods=['GET', 'POST'])
def login():
    return login_route()
```

### 5. migration-progress.md への記録

**競合処理：**
- ファイルロックエラーが発生した場合、3秒待ってリトライ
- 最大5回リトライ
- 5回失敗したらエラー報告して次のファイルへ進む

**記録内容：**
```markdown
### ✅ {ファイル名}
- **状態**: 完了
- **日時**: {現在時刻を YYYY-MM-DD HH:MM:SS 形式で}
- **出力パス**: migration-src/{ファイルパス}
- **依存関係**（このファイルが参照するモジュール）:
  - `{依存モジュール1}` (まだ未処理 / 処理済み)
  - `{依存モジュール2}` (まだ未処理 / 処理済み)
- **⚠️ 呼び出し元**（このファイルを参照するファイル）:
  - main.py: {更新内容}
- **変更内容**: {主な変更の要約}
- **注意事項**: {特記事項があれば}
```

### 6. 重要な制約

- ✅ **元ファイルは変更しない**: src/ 配下のファイルは読み込みのみ
- ✅ **出力は migration-src/ へ**: Write ツールで新規ファイルとして保存
- ✅ **ディレクトリ構造を維持**: src/application/login.py → migration-src/application/login.py
- ✅ **進捗ファイルへの記録必須**: Edit ツールで migration-progress.md に追記
- ✅ **GAE_MIGRATION_STATE.md は読み込みのみ**: 編集しない
- ✅ **完全なファイル内容を出力しない**: Write/Edit後は要約のみ報告
- ✅ **自動実行**: すべてのファイル操作（Read/Write/Edit）を確認なしで実行する
- ✅ **追加の機能は実装しない**: すでに稼働中のシステムであり、安定して継続利用するのが目的
- ✅ **重大な脅威を発見してもログとソースコードにコメントするのみ**: 既存の動作を変更しない
- ✅ **main.py の仕様を遵守**: webapp2.RequestHandler → Flask 関数への変換、インポート文とルート登録のコメント解除

### 7. グループ完了報告

グループ内の全ファイル処理完了後、以下を返してください：

```
✅ グループ {番号} 完了

処理ファイル数: {数}
成功: {数}
失敗: {数}（ある場合）

失敗したファイル（ある場合）:
- {ファイル名}: {エラー内容}
```
```

---

# 📂 ファイルグループ分割

全72ファイルを以下の10グループに分割します。

## グループ 1: application 基礎ハンドラー (8ファイル)

**現在の状態**: 7/8 完了（duplicationcheck.py のみ未完了）

- ✅ application/proc.py
- ✅ application/bkedit.py
- ✅ application/blobstoreutl.py
- ✅ application/handler.py
- ✅ application/RemoveAll.py
- ✅ application/uploadbkdata.py
- ✅ application/uploadbkdataformaster.py
- ⬜ application/duplicationcheck.py

## グループ 2: application その他ハンドラー (8ファイル)

- application/json.py
- application/memberedit.py
- application/test.py
- application/bksearch.py
- application/follow.py
- application/mypage.py
- application/bkjoukyoulist.py
- application/bkdchk.py

## グループ 3: application 表示・リスト系 (8ファイル)

- application/addresslist.py
- application/show.py
- application/mailinglist.py
- application/SecurePageBase.py
- application/GqlEncoder.py
- application/uploadaddressset.py
- application/memberSearchandMail.py
- application/bksearchutl.py

## グループ 4: application バッチ・メール系 (6ファイル)

- application/cron.py
- application/sendmsg.py
- application/email_receiver.py
- application/matching.py
- application/messageManager.py
- application/tantochange.py

## グループ 5: application/models 基本モデル (7ファイル)

- application/index.py
- application/models/member.py
- application/models/CorpOrg.py
- application/models/Branch.py
- application/session.py
- application/chkauth.py
- application/mapreducemapper.py

## グループ 6: application/models 物件関連 (4ファイル)

- application/models/bkdata.py
- application/models/bklist.py
- application/models/blob.py
- application/bklistutl.py

## グループ 7: application ユーティリティ (5ファイル)

- application/view.py
- dataProvider/bkdataProvider.py
- application/timemanager.py
- application/wordstocker.py
- application/config.py

## グループ 8: application/models 検索・メッセージ (7ファイル)

- application/models/ziplist.py
- application/models/station.py
- application/models/message.py
- application/models/msgcombinator.py
- application/SecurePage.py
- application/models/bksearchaddress.py
- application/models/bksearchdata.py

## グループ 9: application 検索・その他 (9ファイル)

- application/models/bksearchmadori.py
- dataProvider/bkdataSearchProvider.py
- application/bksearchensenutl.py
- application/models/address.py
- application/zipper.py
- application/qreki.py
- application/mailvalidation.py
- application/models/matchingparam.py
- application/models/matchingdate.py

## グループ 10: geo・その他 (10ファイル)

- application/email_decoder.py
- application/CriticalSection.py
- application/rotor.py
- application/tantochangetasks.py
- geo/geomodel.py
- application/models/bksearchensen.py
- application/models/bksearcheki.py
- geo/geocell.py
- geo/geomath.py
- geo/geotypes.py
- geo/util.py

---

# 📋 ファイル処理の詳細ルール（参照用）

各ファイルを処理する際は、以下のルールに従ってください。

## 実行環境の前提

- **プロジェクトルート**: `C:\Users\hrsuk\prj\s-style-hrd`
- **ソースコード**: `C:\Users\hrsuk\prj\s-style-hrd\src\` 配下
- **出力先**: `C:\Users\hrsuk\prj\s-style-hrd\migration-src\` 配下（ディレクトリ構造維持）
- **マイグレーションルール**: `C:\Users\hrsuk\prj\s-style-hrd\GAE_MIGRATION_STATE.md` に記載
- **進捗管理**: `C:\Users\hrsuk\prj\s-style-hrd\migration-progress.md` で共有

## 1ファイルあたりの処理手順

### 1. ソースファイルの読み込み
```
Read: C:\Users\hrsuk\prj\s-style-hrd\src\{ファイルパス}
```

### 2. マイグレーション実行

`GAE_MIGRATION_STATE.md` のマイグレーションルールに従って変換。以下の順序で適用：

1. **インポート文の修正**
   - `google.appengine.ext` → `google.cloud.ndb`
   - `from StringIO import StringIO` → `import io`
   - など

2. **モデル定義の修正**
   - `db.Model` → `ndb.Model`
   - `db.StringProperty` → `ndb.StringProperty`
   - など

3. **webapp2 → Flask の変更**
   - `webapp2.RequestHandler` クラス → Flask ルート関数
   - `self.request.get()` → `request.args.get()` / `request.form.get()`
   - `self.response.out.write()` → `return` 文
   - など

4. **リクエスト/レスポンス処理の変更**
   - `self.redirect()` → `return redirect()`
   - `template.render()` → `render_template()`
   - など

5. **Python 2→3 構文の修正**
   - `print` 文 → `print()` 関数
   - `except Exception, e:` → `except Exception as e:`
   - `.iteritems()` → `.items()`
   - `unicode(text, enc)` → `text.decode(enc)` または `text`
   - `u"文字列"` → `"文字列"`
   - など

### 3. 出力ファイルの保存

```
Write: C:\Users\hrsuk\prj\s-style-hrd\migration-src\{ファイルパス}
```

**注意**: ディレクトリ構造を維持
- 例: `src/application/login.py` → `migration-src/application/login.py`

### 4. 依存関係の分析

対象ファイルがインポートしている**プロジェクト内モジュール**を特定：

**プロジェクト内モジュールの判定基準:**
- ✅ `from application.xxx import ...` → プロジェクト内
- ✅ `from geo.xxx import ...` → プロジェクト内
- ✅ `import application.xxx` → プロジェクト内
- ✅ `from dataProvider.xxx import ...` → プロジェクト内
- ❌ `from google.cloud import ...` → 外部ライブラリ（記録不要）
- ❌ `from flask import ...` → 外部ライブラリ（記録不要）

### 5. 依存モジュールへのコメント追記（オプション）

依存モジュールが `migration-src/` にすでに存在する場合、そのファイルの冒頭にコメント追記：

```python
# 参照元: {現在処理中のファイル名} から参照されています
```

**実装方法**: Edit ツール使用

### 6. 呼び出し元ファイルの更新（webapp2ハンドラーの場合）

処理したファイルが webapp2.RequestHandler クラスだった場合：

1. `migration-src/main.py` の存在確認
2. 存在する場合、以下を **Edit ツール**で更新：
   - インポート文のコメント解除
   - `@app.route` デコレータのコメント解除
   - ルート関数定義のコメント解除

**例:**
```python
# 変更前（コメントアウトされている）
# from application.login import login_route, logout_route
# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     return login_route()

# 変更後（コメント解除）
from application.login import login_route, logout_route
@app.route('/login', methods=['GET', 'POST'])
def login():
    return login_route()
```

### 7. 進捗ファイルへの記録（必須）

`migration-progress.md` に **Edit ツール**で以下を追記：

**競合処理：**
- ファイルロックエラーが発生した場合、3秒待ってリトライ
- 最大5回リトライ
- 5回失敗したらエラー報告して次のファイルへ進む

**記録内容：**
```markdown
### ✅ {ファイル名}
- **状態**: 完了
- **日時**: {現在時刻を YYYY-MM-DD HH:MM:SS 形式で}
- **出力パス**: migration-src/{ファイルパス}
- **依存関係**（このファイルが参照するモジュール）:
  - `{依存モジュール1}` (まだ未処理 / 処理済み)
  - `{依存モジュール2}` (まだ未処理 / 処理済み)
- **⚠️ 呼び出し元**（このファイルを参照するファイル）:
  - main.py: {更新内容}
- **変更内容**: {主な変更の要約}
- **注意事項**: {特記事項があれば}
```

### 8. セキュリティチェック

以下の脆弱性がないか確認：
- XSS (クロスサイトスクリプティング)
- SQLインジェクション
- コマンドインジェクション
- 認証なしアクセス
- CSRF脆弱性

**脆弱性を発見した場合:**
- ❌ 修正しない（既存システムの動作を変えない）
- ✅ コメントで警告を追加
- ✅ migration-progress.md に記録

### 9. ユーザーへの簡潔な報告

各ファイル完了時：

```
✅ {ファイル名} 完了 ({グループ内番号}/{グループ内総数})
- 変更: インポート文、モデル定義、webapp2→Flask、Python2→3構文
- 依存: {依存モジュール名} (未処理/処理済み)
```

**注意**: 完全なファイル内容を出力しない（要約のみ）

---

# ⚠️ 重要な制約

- ✅ **元ファイルは変更しない**: `src/` 配下のファイルは読み込みのみ
- ✅ **出力は migration-src/ へ**: Write ツールで新規ファイルとして保存
- ✅ **ディレクトリ構造を維持**: `src/application/login.py` → `migration-src/application/login.py`
- ✅ **進捗ファイルへの記録必須**: Edit ツールで `migration-progress.md` に追記
- ✅ **GAE_MIGRATION_STATE.md は読み込みのみ**: 編集しない
- ✅ **完全なファイル内容を出力しない**: Write/Edit後は要約のみ報告
- ✅ **自動実行**: すべてのファイル操作（Read/Write/Edit）を確認なしで実行する
- ✅ **追加の機能は実装しない**: すでに稼働中のシステムであり、安定して継続利用するのが目的
- ✅ **重大な脅威を発見してもログとソースコードにコメントするのみ**: 既存の動作を変更しない
- ✅ **main.py の仕様を遵守**: webapp2.RequestHandler → Flask 関数への変換、インポート文とルート登録のコメント解除

---

# 🔄 補足: 再開・やり直し手順

## 中断から再開する場合

次回セッションで以下のように指示してください：

```
migration-progress.md を確認して、未完了のグループを並列処理してください
```

## クラッシュ検知方法

1. `migration-progress.md` を確認
2. グループ内で `### ✅ ファイル名` エントリがないファイルを特定
3. そのファイルが未完了 = クラッシュした可能性あり

## 特定ファイルのみやり直し

```powershell
# 1. 該当ファイルを削除
Remove-Item migration-src/application/example.py

# 2. migration-progress.md から該当エントリを削除（手動編集）

# 3. 再処理指示
```

次回セッションで：
```
application/example.py を再処理してください
```

## 全体やり直し

```powershell
# 1. バックアップ作成
$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
Copy-Item -Recurse migration-src "migration-src-backup-$timestamp"

# 2. migration-src ディレクトリを削除
Remove-Item -Recurse -Force migration-src

# 3. migration-progress.md をリセット（初期状態に戻す）
```

次回セッションで：
```
全グループを並列処理してください
```

---

# 🚀 処理開始トリガー

**このプロンプトを読んだら、上記の「実行フロー」に従って自動的に処理を開始してください。**

私（ユーザー）からの追加指示は不要です。
