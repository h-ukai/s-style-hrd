# テンプレートマイグレーション作業プロンプト

## プロジェクト概要
Google App Engine Python 2.7 → Python 3.11 へのマイグレーション作業  
webapp2 + Django テンプレート → Flask + Jinja2 へのテンプレート変換

## プロジェクト構造
```
プロジェクトルート: C:\Users\hrsuk\prj\s-style-hrd

参照フォルダ: src/templates/
保存フォルダ: migration-src/templates/
```

## 作業指示

### 1. 前提条件の確認
- `TEMPLATE_MIGRATION_RULES.md` を参照し、変換ルールを理解する
- `TEMPLATE_MIGRATION_STATE.md` から未処理ファイルリストを取得
- `TEMPLATE_MIGRATION_LOG.md` が存在しない場合は新規作成

### 2. 処理対象ファイルの選定
`TEMPLATE_MIGRATION_STATE.md` の「## 未処理テンプレート」セクションから順に選択：
- **基本**: 1回につき10ファイル程度
- **コンテキスト余裕あり**: 10ファイル以上も可
- **コンテキスト不足**: 10ファイル未満でも処理進行

**処理対象**: 全96ファイル（除外ファイルは既にリストから削除済み）

### 3. 変換作業の実行

#### 3.1 ファイル読み込み
```
src/templates/[相対パス]/[ファイル名]
```

#### 3.2 ルールに従った変換
`TEMPLATE_MIGRATION_RULES.md` に記載されたルールを適用：

**主要な変換項目**:
1. **絶対パス → 相対パス**
   - `/static/` → `../static/`
   - `/css/` → `../css/`
   - `/js/` → `../js/`
   - `/images/`, `/img/` → `../images/`, `../img/`

2. **テンプレート構文**
   - `{% extends /base.html %}` → `{% extends "base.html" %}`
   - `{% extends applicationpagebase %}` → `{% extends "applicationpagebase.html" %}`
   - `{% ifequal data.name "value" %}` → `{% if data.name == "value" %}`
   - `{% comment %}...{% endcomment %}` → `{# ... #}`

3. **jQuery非推奨API**
   - `.live()` → `.on()`
   - 例: `$('#tbl tr').live('click', fn)` → `$(document).on('click', '#tbl tr', fn)`

4. **古いブラウザコード**
   - `if(d.all)` (IE検出) → 削除または標準化
   - `window.event.keyCode = 0` → 標準イベント処理

**維持する項目（変更しない）**:
- 外部CDN（jQuery、Google Maps、Analytics等）
- AJAXエンドポイント（`/jsonservice` 等）
- フォーム要素のname属性
- Django/Jinja2互換フィルタ（`|default_if_none`, `|date`, `|safe` 等）

#### 3.3 ルール外事項の対応
**ルールに記載がない項目は基本的に修正せず、ログに報告のみ**

記録が必要な項目例：
- 変数タイポ（`{{bbkdata.kdata...}}` → `{{bkdata.bkdata...}}`）
- 非標準CSS（`ime-mode`）
- 大規模リファクタリングが必要な箇所
- セキュリティ上の懸念
- 依存ライブラリの互換性問題

#### 3.4 ファイル保存
```
migration-src/templates/[相対パス]/[ファイル名]
```
※ 元のフォルダ構造を完全に維持

### 4. ログ記録（TEMPLATE_MIGRATION_LOG.md）

各ファイルごとに以下のフォーマットで記録：

```markdown
## [YYYY-MM-DD HH:MM:SS] 第N回処理

### ファイル名: [相対パス]/[ファイル名].html

#### ルール外の改修事項
- 記載なし項目で修正が必要だった箇所を列挙
- なければ「なし」

#### 懸念事項
- テンプレートに残った問題点を列挙
- 例: jQuery古いバージョン、非推奨API使用、外部依存
- 例: 変数タイポ、フィールド名不統一の報告
- なければ「なし」

#### 期待する変数データ形式
- 呼び出し側Pythonコードから渡されるべきデータ構造
- 例:
  ```python
  {
      'bkdata': {
          'bkdata': {
              'bsRsnmi1': str,
              'thM21': int,
              ...
          }
      },
      'sitename': str,
      'Domain': str
  }
  ```
- テンプレート変数が使われていない場合は「変数なし（静的テンプレート）」

#### その他
- 追加で記録すべき情報
- 次回作業への引き継ぎ事項
- なければ省略可
```

### 5. 状態管理の更新（TEMPLATE_MIGRATION_STATE.md）

処理完了したファイルを移動：
```markdown
## 未処理テンプレート
（ここから削除）

## 処理済みテンプレート
（ここに追加）
```

## コンテキスト管理

- **トークン制限**: 約19万トークン利用可能
- **処理中の判断**: コンテキストが70%超えたら10ファイル未満でも区切る
- **大規模ファイル**: 500行超のファイルは単独処理も検討

## 作業フロー（実行手順）

```
1. TEMPLATE_MIGRATION_RULES.md を読み込み
2. TEMPLATE_MIGRATION_STATE.md を読み込み
3. 未処理リストから処理対象ファイルを選定
4. 各ファイルを順次処理:
   a. src/templates/ からファイル読み込み
   b. ルールに従って変換
   c. migration-src/templates/ に保存
   d. ログに記録内容を準備
5. TEMPLATE_MIGRATION_LOG.md にログを追記（ファイルごと）
6. TEMPLATE_MIGRATION_STATE.md を更新（未処理→処理済み）
7. 処理完了報告（処理ファイル数、残りファイル数）
```

## 注意事項

1. **文字コード**: 元ファイルの文字コードを維持（shift_jis の場合も）
2. **改行コード**: 元ファイルと同じ改行コードを維持
3. **インデント**: 元ファイルのインデントスタイルを維持
4. **コメント保持**: 既存コメントは原則削除しない
5. **慎重な変換**: 不明な点はログに記録し、そのまま残す

## 完了確認

各回の処理完了時に報告：
```
✅ 第N回処理完了
- 処理ファイル数: X件
- 残り未処理: Y件
- 進捗率: XX%
```

---

## 開始コマンド例

```
TEMPLATE_MIGRATION_RULES.md と TEMPLATE_MIGRATION_STATE.md を確認し、
未処理リストの先頭から10ファイル程度を処理してください。

各ファイルごとにログを記録してください。
TEMPLATE_MIGRATION_LOG.mdは長大になりすぎたので読み込まないでください。内容を展開・解析せず、ファイル末尾にログを追記してください。
```
