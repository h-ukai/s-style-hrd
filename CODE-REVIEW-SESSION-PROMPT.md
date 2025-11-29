あなたは Google App Engine Python 2.7 から Python 3.11 へのマイグレーションコードレビュータスクを発行・管理するマスターエージェントです。

**あなたの役割**:
- レビュー作業自体は行いません
- 10個のグループに対してレビュータスクを並列に発行します
- 各タスクの完了を待機し、全体の結果をまとめて報告します

---

# 🎯 あなたへの実行指示（必ず最初に読むこと）

## 実行フロー

このプロンプトを受け取ったら、以下の手順を**自動的に**実行してください：

### ステップ1: 並列タスク起動

**Task ツールを使用して、全10グループを並列にレビューします。**

- **重要**: すべてのタスクを**同じメッセージ内で一度に**起動してください
- 各タスクには下記の「グループ別レビュープロンプト」を使用
- `subagent_type: "general-purpose"` を指定
- `model: "sonnet"` を使用（精度重視のため）

**例**:
```
グループ 1-10 すべてを対象に:
→ 1つのメッセージで Task ツールを10回呼び出し（グループ1-10用）
```

### ステップ2: タスク完了待機と報告

すべてのタスクが完了したら、以下を報告：

```
🎉 全レビュー完了

レビューファイル数: {合計数}
レベル1問題: {数}（自動修正済み）
レベル2問題: {数}
レベル3問題: {数}
問題なし: {数}

```

---

# 📋 グループ別レビュープロンプト

各グループのレビュータスクには、以下のプロンプトテンプレートを使用してください：

**重要**: 以下のテンプレート内のプレースホルダーは、マスタープロンプト（このプロンプトを実行するエージェント）が各タスク発行時に以下のように展開する必要があります：
- `{番号}` → 実際のグループ番号 (1-10)
- `{グループ番号}` → 実際のグループ番号 (1-10)
- `{グループ内ファイルリスト}` → そのグループに属するファイルの具体的なリスト（下記「ファイルグループ分割」セクションから取得）

```
あなたは Google App Engine Python 2.7 から Python 3.11 へのマイグレーションコードレビューを実行します。

## タスク概要
グループ {番号} の全ファイルをレビューし、CODE_REVIEW_LOG_{グループ番号}.md に記録してください。

## 必須手順

### 1. 事前準備
- Read: C:\Users\hrsuk\prj\s-style-hrd\GAE_MIGRATION_STATE.md(マイグレーションルール確認)
- Read: C:\Users\hrsuk\prj\s-style-hrd\migration-progress-group-{グループ番号}.md(このグループの依存関係確認)

### 2. レビュー対象ファイル
{グループ内ファイルリスト}

### 3. 各ファイルのレビュー手順

for ファイル in レビュー対象ファイル:
    1. Read: C:\Users\hrsuk\prj\s-style-hrd\src\{ファイルパス}（旧ファイル）
    2. Read: C:\Users\hrsuk\prj\s-style-hrd\migration-src\{ファイルパス}（新ファイル）
    3. 10項目チェックリストに基づいてレビュー実施
    4. 問題発見時:
       a. レベル1問題: 新ファイルにコメント追記 + 即座に自動修正 + Edit で更新
       b. レベル2/3問題: 新ファイルにコメント追記のみ + Edit で更新
    5. CODE_REVIEW_LOG_GROUP_{グループ番号}.md に記録（グループ専用のログファイル）

---

## レビューチェックリスト（10項目）

各ファイルについて、以下の項目を確認してください：

### 1. 基本的な構文とスペルのミス
- Python 3 構文エラーの有無
- 変数名・関数名のタイポ
- インデントの問題
- 括弧の不一致

### 2. 旧ファイルで動作していたすべての機能の継承
- すべてのクラス・メソッド・関数が新ファイルに存在するか
- ロジックの欠落がないか
- 条件分岐・ループが正しく移行されているか

### 3. 新たに書き換えられた代替コードの有効性
- webapp2 → Flask の変換が正しいか
- db → ndb の変換が正しいか
- Mail API → SMTP の実装が正しいか
- Task Queue → Cloud Tasks の実装が正しいか

### 4. マイグレーションルールの適用漏れ
- GAE_MIGRATION_STATE.md の全ルールが適用されているか
- `db.Model` → `ndb.Model` の変換漏れ
- `u"文字列"` の削除漏れ
- `google.appengine.*` インポートの残存

### 5. 依存関係の整合性
- インポート文が正しく更新されているか
- 相対インポート → 絶対インポートへの変換
- 循環インポートの有無
- 未マイグレーション依存モジュールの適切な扱い
- **マイグレーション済み依存モジュールとの整合性**:
  - migration-progress-group-{グループ番号}.md で依存関係を確認
  - マイグレーション済みの依存モジュールがある場合:
    - 呼び出し時の引数の型・数が正しいか
    - 戻り値の型・構造が想定通りか
    - 関数名・メソッド名の変更が反映されているか
  - マイグレーション未完了の依存モジュールの場合:
    - コメントで依存関係を明記（migration-progress-group-{グループ番号}.md に記載があることを確認）

### 6. Python 2/3 互換性の問題
- `xrange()` → `range()` の変換漏れ
- `dict.iteritems()` / `.iterkeys()` / `.itervalues()` の変換漏れ
- `long()` 型の使用
- `print` 文の残存
- `unicode()` / `str()` の適切な使用
- `except E, e:` → `except E as e:` の変換

### 7. セキュリティ問題の悪化
- 旧ファイルのセキュリティ警告が記録されているか
- 新しいコードで新たなリスクが追加されていないか
- XSS、SQLインジェクション、認証バイパスの確認
- ユーザー入力の適切なエスケープ・検証

### 8. API の破壊的変更
- `self.request.get()` → `request.args.get()` / `request.form.get()` の適切な使い分け
- `self.response.out.write()` → `return` 文への変換
- `self.redirect()` → `return redirect()` への変換
- セッション管理の互換性

### 9. エラーハンドリングの保持
- try-except ブロックが維持されているか
- エラーメッセージが適切か
- ログ出力が維持されているか
- 例外の再スロー処理

### 10. main.py との統合確認
- webapp2ハンドラーの場合、main.py のルート登録が正しいか
- インポート文が正しいか
- URL パス・HTTPメソッドが元の仕様と一致しているか

---

## 問題レベル定義

### 🔴 レベル1: 重要（絶対修正が必要 - 動作に影響）
- 構文エラー
- インポートエラー
- マイグレーションルールの重大な適用漏れ（`db.Model` 残存など）
- 機能の欠落
- API の誤った使用

**対応**: 即座に自動修正 + ログ記録（修正前後のコード含む）

### 🟡 レベル2: 推奨（セキュリティ・品質改善）
- セキュリティ脆弱性
- エラーハンドリングの不足
- 非推奨 API の使用
- パフォーマンス問題

**対応**: コメント追記のみ + ログ記録

### 🔵 レベル3: 提案（軽微な改善）
- 変数名の可読性
- コメントの不足
- コードスタイル
- リファクタリング提案

**対応**: コメント追記のみ + ログ記録

---

## レビュー結果の記録方法

### A. 新ファイルへのコメント追記

問題を発見した場合、新ファイルの該当行に以下のコメントを追記：

```python
# REVIEW-L1: [問題の説明]
# 修正前: [元のコード]
# 修正後: [修正されたコード]（レベル1の場合のみ）
問題のあるコード行
```

```python
# REVIEW-L2: [問題の説明]
# 推奨: [修正方法]
問題のあるコード行
```

```python
# REVIEW-L3: [提案内容]
問題のあるコード行
```

**レベル1の場合の特別処理**:
1. コメント追記
2. 問題のコード行を修正
3. Edit ツールで新ファイルを更新

**レベル2/3の場合**:
1. コメント追記のみ
2. Edit ツールで新ファイルを更新

### B. CODE_REVIEW_LOG_GROUP_{グループ番号}.md への記録

**重要**: 各グループは専用のログファイルに記録します：
- グループ1 → `C:\Users\hrsuk\prj\s-style-hrd\CODE_REVIEW_LOG_GROUP_1.md`
- グループ2 → `C:\Users\hrsuk\prj\s-style-hrd\CODE_REVIEW_LOG_GROUP_2.md`
- ...
- グループ10 → `C:\Users\hrsuk\prj\s-style-hrd\CODE_REVIEW_LOG_GROUP_10.md`

**ファイル作成：**
- ログファイルが存在しない場合は新規作成
- 既存ファイルがある場合は追記モードで書き込み

**競合処理：**
- グループ専用ファイルのため、競合は発生しません

**記録フォーマット:**

```markdown
## モジュール名: {ファイルパス}

### 🔴 レベル1: 重要（絶対修正が必要 - 動作に影響）

#### 問題 1
- **行番号**: {行番号}
- **問題**: {問題の説明}
- **影響**: {動作への影響}
- **修正前**:
  ```python
  {修正前のコード}
  ```
- **修正後**:
  ```python
  {修正後のコード}
  ```
- **自動修正**: ✅ 完了

#### 問題 2
...

### 🟡 レベル2: 推奨（セキュリティ・品質改善）

#### 問題 1
- **行番号**: {行番号}
- **問題**: {問題の説明}
- **影響**: {セキュリティ/品質への影響}
- **推奨修正方法**: {修正方法の説明}
- **自動修正**: ❌ 手動対応が必要

### 🔵 レベル3: 提案（軽微な改善）

#### 提案 1
- **行番号**: {行番号}
- **提案**: {提案内容}
- **効果**: {改善効果}
- **自動修正**: ❌ 手動対応が必要

### ✅ レビュー結果サマリー
- **レベル1問題**: {数}件（すべて自動修正済み）
- **レベル2問題**: {数}件
- **レベル3問題**: {数}件
- **総評**: {全体的な評価}

---
```

---

## 重要な制約

- ✅ **旧ファイルは変更しない**: `src/` 配下のファイルは読み込みのみ
- ✅ **新ファイルのみ更新**: `migration-src/` 配下のファイルに対してのみ Edit を実行
- ✅ **レベル1問題は必ず自動修正**: 構文エラーなど動作に影響する問題は即座に修正
- ✅ **レベル2/3問題はコメントのみ**: セキュリティ・品質改善はコメントで記録し、コードは変更しない
- ✅ **ログ記録必須**: すべての問題を CODE_REVIEW_LOG_GROUP_{グループ番号}.md に記録（グループ専用ファイル）
- ✅ **完全なファイル内容を出力しない**: Edit 後は要約のみ報告
- ✅ **自動実行**: すべてのファイル操作（Read/Edit）を確認なしで実行する

---

## 参照可能なファイル

レビューに必要な場合、以下のファイルを自由に参照してください：

- `C:\Users\hrsuk\prj\s-style-hrd\GAE_MIGRATION_STATE.md`（マイグレーションルール）
- `C:\Users\hrsuk\prj\s-style-hrd\migration-progress-group-{グループ番号}.md`（このグループの依存関係情報）
- `C:\Users\hrsuk\prj\s-style-hrd\migration-src\main.py`（Flask アプリ定義）
- 依存モジュール（`migration-src/` 配下の他のファイル）

**テスト用・廃止予定のファイルは無視**:
- GAE_MIGRATION_STATE.md に記載されているファイルのみがレビュー対象

---

## グループ完了報告

グループ内の全ファイルレビュー完了後、以下を返してください：

```
✅ グループ {番号} レビュー完了

レビューファイル数: {数}
レベル1問題: {数}（すべて自動修正済み）
レベル2問題: {数}
レベル3問題: {数}
問題なし: {数}

主な問題:
- {重要な問題の要約}
```

---

# 📂 ファイルグループ分割

全66ファイルを以下の10グループに分割します。

## グループ 1: application 基礎ハンドラー (8ファイル)

- application/proc.py
- application/bkedit.py
- application/blobstoreutl.py
- application/handler.py
- application/RemoveAll.py
- application/uploadbkdata.py
- application/uploadbkdataformaster.py
- application/duplicationcheck.py

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

## グループ 10: geo・その他 (11ファイル)

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

# 🚀 処理開始トリガー

**このプロンプトを読んだら、上記の「実行フロー」に従って自動的にレビュー処理を開始してください。**

私（ユーザー）からの追加指示は不要です。
