あなたは Google App Engine webapp2 から Flask へのテンプレートマイグレーションを設計するエキスパートです。

このプロジェクト専用の「テンプレートマイグレーション状態ファイル（TEMPLATE_MIGRATION_STATE.md）」を段階的に更新していきます。

## 実行環境の前提

- **プロジェクトルート**: `C:\Users\hrsuk\prj\s-style-hrd`
- **テンプレートディレクトリ**: `C:\Users\hrsuk\prj\s-style-hrd\src\templates\` 配下
- **マイグレーション状態ファイル**: `C:\Users\hrsuk\prj\s-style-hrd\TEMPLATE_MIGRATION_STATE.md`
- **マイグレーションルールファイル**: `C:\Users\hrsuk\prj\s-style-hrd\TEMPLATE_MIGRATION_RULES.md`
- **重要**: ファイルは必ず Edit ツールで直接編集し、完全なファイル内容を出力しないこと

## プロジェクト固有の要件（GAE_MIGRATION_STATE.mdより）

- webapp2 → Flask移行
- テンプレートエンジン: Jinja2
- **絶対パス → 相対パスへ全面書き換え**（しばらくテスト運用のため）
- jQuery: 可能な限り現行バージョンで動作させる
- JavaScript: ブラウザ禁止の古い記述以外は現行のまま
- 懸念のある箇所はマイグレーションログに記載して更新しない

## やってほしいこと

### 1. マイグレーション状態ファイルの確認

- `C:\Users\hrsuk\prj\s-style-hrd\TEMPLATE_MIGRATION_STATE.md` を Read ツールで読み込む
- 存在しない場合は新規作成する（以下の構造で）:

```markdown
# テンプレートマイグレーション状態

## 調査済みテンプレート
（調査が完了したテンプレートのリスト）

## 未調査テンプレート
（まだ調査していないテンプレートのリスト）

## 構造分析
（テンプレートのフォルダ構造と用途の概要）
2. テンプレートファイルの一覧作成（初回のみ）
C:\Users\hrsuk\prj\s-style-hrd\src\templates 配下の .html ファイルを全件取得
.skrold および .skrold.skrold ファイルは除外（バックアップファイル）
フォルダごとにグループ化してリスト化
「## 未調査テンプレート」セクションに記録
3. 調査対象ファイルの選定
「## 未調査テンプレート」セクションから最大10個のファイルを対象に選ぶ
以下を優先的に選定:
ルートフォルダの基本テンプレート（login.html, index.html 等）
複雑なテンプレート継承を使っているもの（{% extends %} 使用）
JavaScriptが多用されているもの
絶対パスが多用されているもの
様々なJinja2構文が使われているもの（forループ、if文、変数等）
4. テンプレートファイルの読み込みと分析
選定したファイルを Read ツールで読み込む
以下の観点で分析:
a) テンプレートエンジン構文の互換性
webapp2テンプレート構文 vs Jinja2構文の違い
{% ifequal %} → {% if == %} 等の変換が必要か
カスタムフィルターの使用状況
{% comment %} の扱い
テンプレート継承（{% extends %}, {% block %}）の使用パターン
b) パス参照パターンの抽出
絶対パス形式の抽出（例: /js/, /css/, /img/, https://s-style-hrd.appspot.com/）
相対パス変換時の基準パスの特定
外部ドメインへのリンク（変換不要）
c) JavaScript/jQueryの互換性
使用されているjQueryバージョンの推定
廃止されたAPI（.live(), .browser, $.ajax() の古い記法等）の使用状況
ブラウザ固有コード（IE専用コード等）の有無
document.all 等の古いDOM API使用状況
d) 外部ライブラリ依存
CDN/ローカルのライブラリ参照
thickbox, autocomplete, multicheckbox等のプラグイン
互換性の懸念があるライブラリ
e) Flask移行時の変更点
フォーム送信先（action 属性）
セッション変数の参照方法
CSRF対策の必要性
URL生成（url_for() の使用検討）
5. マイグレーションルールの抽出と記録
TEMPLATE_MIGRATION_RULES.md に以下の3カテゴリのみ記録:
a) 方針決定（選択肢が複数ある場合のみ）
例:
テンプレートエンジン: Jinja2使用（webapp2デフォルトテンプレートから移行）
パス変換方針: 全絶対パス→相対パス（テスト運用期間中のため）
jQuery: 現行バージョン継続使用（理由: 全面書き換え回避、段階的移行）
廃止API: .live() → .on() に統一変換
CSRF対策: Flask-WTF使用 or 独自トークン実装（選択理由を記載）
記録不要な例:
{% ifequal %} → {% if == %}（Jinja2の一般知識）
HTMLの基本構文変更
b) 大幅変更（テンプレート構造が大きく変わる箇所）
例:
webapp2 {% ifequal A B %} → Jinja2 {% if A == B %}（すべて変換必要）
絶対パス /js/xxx.js → 相対パス ../../js/xxx.js または {{ url_for('static', filename='js/xxx.js') }}
https://s-style-hrd.appspot.com/ → 環境変数ベースURL or url_for() 使用
jQuery .live() → .on() 全面書き換え
セッション参照 {{session.xxx}} → Flask {{session['xxx']}}（要確認）
c) 統一仕様（テンプレート間で認識を共有すべき仕様）
例:
相対パス変換ルール: テンプレートの階層に応じた../の数を統一
静的ファイルURL: {{ url_for('static', filename='xxx') }} 形式に統一 or 相対パス統一
JavaScript配置: {% block script %} 内に記述（ベーステンプレートで定義）
CSS配置: {% block addheder %} 内に記述
jQuery読み込み: ベーステンプレートで一元管理
文字エンコーディング: UTF-8 統一（<meta charset="UTF-8">）
CSRF トークン: すべてのフォームに {{ csrf_token() }} 追加（Flask-WTF使用時）
テンプレート継承構造: applicationpagebase.html → followpagebase.html → 各ページ
エスケープ: {{ var|escape }} vs {{ var|safe }} の使い分けルール
d) 懸念事項と保留判断（マイグレーションログに記載）
例:
thickbox.js: 古いライブラリ、代替検討が必要（保留）
.live() の大量使用: 全面書き換えが必要、段階的対応を推奨
IE専用コード document.all: 削除検討が必要だが動作確認後に判断
絶対パスの大量使用: 自動変換スクリプト作成を推奨
フォーマット:
必ず箇条書き - で記述
選択理由が必要な場合のみ併記（1行で簡潔に）
コード例は最小限（API名と変換前後のみ）
各ルールは独立して理解できるように記述
6. 処理状態の更新
今回調査したファイルを「## 未調査テンプレート」から削除
「## 調査済みテンプレート」セクションの末尾に追加
フォルダごとにグループ化して整理
7. ファイルの更新方法
必ず Edit ツールを使用して直接編集する
TEMPLATE_MIGRATION_STATE.md と TEMPLATE_MIGRATION_RULES.md の両方を更新
old_string に現在のセクション全体を指定
new_string に更新後のセクション全体を指定
完全なファイル内容を出力しない（Edit ツールで編集済みのため不要）
重要な制約
セクション構造の維持
TEMPLATE_MIGRATION_STATE.md:
「## 調査済みテンプレート」「## 未調査テンプレート」「## 構造分析」の3セクションは必須
セクション名は変更しない
TEMPLATE_MIGRATION_RULES.md:
「## 方針決定」「## 大幅変更」「## 統一仕様」「## 懸念事項」の4セクション
セクション名は変更しない
フォーマットの統一
すべての項目は Markdown の - 箇条書きで記述
選択理由や説明は同じ行に簡潔に併記
コード部分はバッククォート ` またはコードブロック ``` で囲む
パス表記の統一
TEMPLATE_MIGRATION_STATE.md 内のパスは src/templates/ からの相対パス
実際のファイル読み込み時は C:\Users\hrsuk\prj\s-style-hrd\src\templates\ を前置
例: 未調査リスト login.html → 実ファイル C:\Users\hrsuk\prj\s-style-hrd\src\templates\login.html
サブフォルダ: 未調査リスト s-style/hon/article.html → 実ファイル C:\Users\hrsuk\prj\s-style-hrd\src\templates\s-style\hon\article.html
処理量の制限
1回の実行で最大10個のテンプレートファイルまで調査
大規模ファイルは優先的に選定（情報量が多いため）
マイグレーションルールの記述例（良い例 / 悪い例）
良い例
## 方針決定
- テンプレートエンジン: Jinja2（webapp2デフォルトから移行）
- パス参照: 全絶対パス→相対パスに変換（理由: テスト運用期間中、環境切り替え容易化）
- jQuery: 現行バージョン継続（理由: 全面書き換え回避、段階的移行）
- CSRF対策: Flask-WTF使用（理由: 標準的、保守性高い）

## 大幅変更
- webapp2構文 → Jinja2: `{% ifequal A B %}` → `{% if A == B %}`
- 絶対パス → 相対パス: `/js/xxx.js` → `{{ url_for('static', filename='js/xxx.js') }}`
- jQuery非推奨API: `.live()` → `.on()` 全件変換
- セッション参照: webapp2 `{{session.xxx}}` → Flask `{{session['xxx']}}`

## 統一仕様
- 静的ファイル参照: `{{ url_for('static', filename='xxx') }}` 形式統一
- テンプレート継承: `applicationpagebase.html` をルートとする階層構造
- CSRF トークン: 全フォームに `<input type="hidden" name="csrf_token" value="{{ csrf_token() }}" />` 追加
- 文字コード: `<meta charset="UTF-8">` 統一
- JavaScript配置: `{% block script %}` 内に記述

## 懸念事項
- `thickbox.js`: 10年以上更新なし、lightbox2等への移行検討が必要（保留）
- `.live()` 大量使用: 100箇所以上、自動変換スクリプト作成推奨
- IE専用コード: `document.all` 使用箇所あり、削除検討（動作確認後判断）
悪い例（冗長すぎ、一般知識を記録）
- HTMLの`<head>`タグ内に`<meta charset="UTF-8">`を記述する必要があります。これはHTML5の標準的な文字エンコーディング指定方法です。
- Jinja2では`{% for item in list %}`のようにループを記述します。ループの終了は`{% endfor %}`で示します。
- 変数を出力する場合は`{{ variable }}`のように二重波括弧で囲みます。
- コメントは`{# コメント #}`の形式で記述します。
→ これらは一般知識なので記録不要
注意事項
プロジェクト構造: C:\Users\hrsuk\prj\s-style-hrd\src\templates\ フォルダ配下にテンプレートがある
重複確認: 未調査リストに追加する前に、既存の調査済み/未調査リストを確認
実用性重視: マイグレーションルールは プロジェクト固有の決定事項のみ を記録
Edit後の出力は不要: Edit ツールが自動的に変更結果を表示するため、完全なファイル内容を再出力しない
懸念事項は積極的に記録: 判断に迷う箇所は必ず「## 懸念事項」に記載
段階的移行: 一度にすべてを変更せず、テスト可能な単位でルール化
初回実行時の特別処理
初回実行時のみ以下を実施:
テンプレートファイル一覧の全件取得（.skrold除外）
TEMPLATE_MIGRATION_STATE.md の新規作成
TEMPLATE_MIGRATION_RULES.md の新規作成
フォルダ構造の分析と「## 構造分析」セクションへの記録

---