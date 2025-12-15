# テンプレートマイグレーションルール

## 基本方針

### 1. 絶対パス → 相対パスへの変換
- すべての絶対パス参照を相対パスに変更
- テスト運用のため、完全な相対パス化を実施

### 2. Jinja2テンプレートエンジン
- webapp2からFlaskへの移行
- Jinja2構文は基本的に互換性あり
- 変数展開、フィルタ、制御構文はそのまま利用可能

### 3. JavaScript/jQuery
- 可能な限り現行バージョンで動作させる
- ブラウザ禁止の古い記述のみ修正
- jQuery依存コードは原則維持

## パス変換ルール

### 静的リソースパス
```
変更前: /static/css/style.css
変更後: ../static/css/style.css
```

### テンプレート継承・インクルード
```
変更前: {% extends "/base.html" %}
変更後: {% extends "base.html" %}
```

### 画像・メディアファイル
```
変更前: /images/logo.png
変更後: ../images/logo.png
```

## 保留事項・確認が必要な項目
- [ ] CDN参照はそのまま維持するか確認
- [ ] 動的URL生成（url_for等）の移行方針
- [ ] フォーム送信先URLの書き換え方針

## 移行対象外
- .skrold ファイル（バックアップファイル）
- desktop.ini
- .txt ファイル

---

# 調査結果（第1回: ルート管理画面系 10ファイル）

## 大幅変更

### webapp2テンプレート構文の変換
- `{% ifequal data.name "value" %}` → `{% if data.name == "value" %}`
- 調査対象では複数のファイルで多用されている (address2.html, addresslist.html, article.html, bkdchk.html, bksearch.html)
- 変換対象: select要素のoption selected属性、条件分岐全般

### jQuery廃止API の置き換え
- `.live()` → `.on()` に変換必要 (addresslist.html, article.html, bkjoukyoulist.html, bksearch.html)
- 例: `$('#tbl tbody tr').live('mouseover', fn)` → `$(document).on('mouseover', '#tbl tbody tr', fn)`

### 絶対パス → 相対パスへの変換
- ローカル静的ファイル: `/css/`, `/js/`, `/img/` → `../css/`, `../js/`, `../img/`
- テンプレート継承: `{% extends "/base.html" %}` → `{% extends "base.html" %}`
- フォーム action属性の変換必要

### 古いブラウザ固有コードの削除
- `if(d.all)` (IE検出) → モダンな方法に変更または削除 (address2.html, bksearch.html)
- `window.event.keyCode = 0` → 標準的なイベント処理に変更

## 統一仕様

### 外部CDN・APIの参照
- jQueryとjQuery UI: CDN参照を維持（絶対パス）
- Google Maps API: 絶対パス維持
- Google Analytics: 絶対パス維持
- 外部ドメイン画像・リソース（https://www.chikusaku-mansion.com/など）: 絶対パス維持

### AJAXエンドポイント
- `/jsonservice` → `/jsonservice` (絶対パス維持、Flask側で対応)
- `https://s-style-hrd.appspot.com/jsonservice` → 絶対パス維持

### DjangoテンプレートフィルタとJinja2の互換性
- `|default_if_none:""` → Jinja2でそのまま使用可能
- `|floatformat:"-2"` → そのまま使用可能
- `|date:"Y/m/d H:i:s"` → そのまま使用可能
- `|safe`, `|linebreaks`, `|join` → そのまま使用可能
- `{% regroup %}` → Jinja2に移行（構文確認必要）

### フォーム要素のname属性
- name属性はサーバー側処理と連携しているため、変更不可
- Flask側でリクエスト処理時に同じname属性を使用

## 懸念事項

### jQueryバージョンの不統一
- jQuery 1.6.0 (address2.html, bkdchk.html, ledger.html)
- jQuery 1.7.1 (addresslist.html, bkjoukyoulist.html)
- jQuery 1.10.2 (bkedit.html, blobstoreutl.html)
- jQuery 1.6.1 (article.html)
- jQuery 1.11.1 (followpagebase.html)
- → 統一バージョンへの移行検討が必要だが、互換性テスト必須

### 古いjQueryプラグインの依存
- galleriffic (画像ギャラリー) - article.html
- jTPS (テーブルページネーション) - bkdchk.html, bkjoukyoulist.html, jTPS.html
- multicheckbox (カスタムチェックボックス) - followpagebase.html, ledger.html, 他複数
- thickbox (モーダル) - bksearch.html
- colorbox (画像ライトボックス) - blobstoreutl.html
- autocomletecustom (カスタムオートコンプリート) - followpagebase.html
- → これらのプラグインがjQuery最新版で動作するか要確認

### DOCTYPE宣言の不統一
- XHTML 1.0 Transitional (多数: bksearchmain.html, followpagebase.html, ledger.html, index.html)
- HTML 4.01 Transitional (bkedit.html)
- XHTML 1.0 Strict (blobstoreutl.html, jTPS.html)
- DOCTYPE なし (info.html, duplicationcheck.html)
- → HTML5への統一を検討するか、現状維持か

### 外部ドメイン依存
- article.html が https://www.chikusaku-mansion.com/ に強く依存
- iframeでhead.html, sidemenu.html, footer.htmlを読み込み
- index.html が外部画像を参照 (https://www.chikusaku-mansion.com/article/cmn_img/b-kuwashiku.jpg)
- → 外部サイトが利用不可になった場合のフォールバック検討

### Google Maps API キー
- API キーが複数のテンプレートにハードコード
- → 環境変数化やテンプレート変数への移行検討

### 大規模ファイル
- bkedit.html (265KB超) - 物件編集画面
- followpagebase.html - 大規模JavaScript (360行以上)、複雑なモーダル処理
- → ファイル分割や部品化の検討余地あり

### Google App Engine Blobstore API 依存
- blobstoreutl.html が Blobstore API に強く依存
- Flask移行時にストレージAPI全体の設計変更が必要

---

# 調査結果（第2回: ルート管理画面系 10ファイル）

## 大幅変更

### メタリフレッシュの削除または変更
- duplicationcheck.html: `<META HTTP-EQUIV="REFRESH" CONTENT="10;URL=/duplicationcheck/bkdata.html">`
- 10秒ごとに自動リロードする仕様
- Flask移行時はJavaScript setTimeoutまたはAJAXポーリングへの変更を検討

### テンプレート継承構文の修正
- `{% extends applicationpagebase %}` (form.html) - 引数が引用符なし
- Jinja2では `{% extends "applicationpagebase.html" %}` 形式に変更必要
- follow.html の `{% extends "followpagebase.html" %}` は正常

### Blobstore URL構造の変更
- blobstoreutl.html: `action="{{ edit_url }}/{{blob.blobNo}}"`
- Google App Engine固有のBlobstore APIからFlaskストレージへの移行必要

## 統一仕様

### iframe によるセッション管理
- form.html (144行): `<iframe src="https://{{sitename}}/auth/setsid?sid={{sid}}" width="0" height="0">`
- セッションIDを別ドメインに送信する仕組み
- Flask移行時はCookie/セッション管理の見直しが必要

### 複雑なモーダル実装パターン
- follow.html, followpagebase.html で共通のモーダル表示ロジック
- グレーレイヤー + オーバーレイ + タイムアウト処理
- 実装パターンは統一されており、共通化可能

### AJAXエンドポイントのドメイン変数化
- followpagebase.html: `ajaxURL = "https://{{Domain|default_if_none:""}}/jsonservice"`
- テンプレート変数でドメインを管理
- Flask移行時も継続可能だが、url_for()の利用を検討

### jTPSプラグインの設定保存
- jTPS.html でクッキーにページネーション状態を保存
- ユーザー体験を維持するため、この機能は継続すべき

## 懸念事項

### 相対パスと絶対パスの混在
- bksearchmain.html: 相対パス (css/styles.css)
- ledger.html: 相対パス (css/baselayout.css)
- 他多数: 絶対パス (/css/, /js/, /img/)
- → パス解決ルールの統一が必要

### 空のaction属性
- form.html: `<form ... action="">`
- 現在のページに送信する仕様だが、Flask移行時は明示的なURLが望ましい

### 大規模なインラインJavaScript
- followpagebase.html: 360行以上のJavaScript
- 保守性のため外部ファイル化を検討すべき

### テストファイルの扱い
- jTPS.html: プラグインのデモ/テストファイル
- 本番環境では不要の可能性あり、移行対象から除外を検討

### DOMセレクタの複雑さ
- follow.html, followpagebase.html で複雑なDOM操作
- jQuery依存度が高く、バージョンアップ時の動作確認が必須

---

# 調査結果（第3回: ルート管理画面系 10ファイル）

## 大幅変更

### reCAPTCHA v3 の実装
- regist.html: `grecaptcha.execute()` でトークン取得後に動的input要素を生成してフォーム送信
- Flask移行時も同様の実装を継続可能
- サイトキーをテンプレート変数で渡す実装は維持

### 非標準CSS ime-mode の削除または代替
- memberedit.html: `$(this).css("ime-mode", "active")` で日本語入力モード制御
- ime-modeは非標準でブラウザサポート終了済み
- Flask移行時は削除するか、HTML5 inputmode属性への変更を検討

### キーボードナビゲーション実装の移行
- memberedit.html: Enter/Tab キーでフォーカス移動する独自実装（200行以上）
- `if(d.all) window.event.keyCode = 0` (IE専用) の削除必要
- モダンブラウザ向けにイベント処理を書き直し

### Google Maps API v3 の実装維持
- show1.html: マーカー表示、初期化処理
- APIキーがハードコード: `AIzaSyB3Pj9gP_x_Gjdgg2GqXaGHQnB5hNaw3no`
- Flask移行時は環境変数化を検討

### jquery.history プラグインの動作確認
- show1.html: Galleriffic との連携で使用
- 古いプラグインのため、モダンブラウザでの動作確認必須

## 統一仕様

### JSONP 通信パターン
- mailinglist.html, memberSearchandMail.html: `dataType: "jsonp"` でクロスドメイン通信
- AJAXエンドポイント `/jsonservice` でJSONP応答を返す実装
- Flask移行時もJSONP対応が必要（または CORS 設定に変更）

### フォーム action 属性の空文字列パターン
- login.html: `action=""`
- sendmsg.html: `action="./"`
- mailinglist.html: `action="./mailinglist.html"`
- → Flask移行時は url_for() で明示的にエンドポイント指定を検討

### テンプレート継承の引用符なしパターン
- login.html, regist.html, resign.html: `{% extends applicationpagebase %}`
- Jinja2では `{% extends "applicationpagebase.html" %}` に変更必須

### 完全HTMLドキュメント（継承なし）の扱い
- mailinglist.html, matching.html, memberSearchandMail.html, show1.html
- 独立した完全なHTMLドキュメントとして実装
- Flask移行時は基底テンプレート化を検討するか、現状維持するか判断必要

## 懸念事項

### Galleriffic プラグインの依存
- show1.html: 画像ギャラリー表示に使用
- jquery.history と連携した複雑な実装
- モダンなギャラリーライブラリへの移行を検討するか、動作確認必須

### ハードコードされた外部ドメイン
- login.html, regist.html: `https://{{sitename}}/auth/setsid?sid={{sid}}`
- show1.html: Google Maps リンク、iframe参照
- → 外部ドメインが変更された場合の影響範囲を確認

### jQuery バージョンの不統一（追加）
- jQuery 1.3.2 (mailinglist.html) - 最古バージョン
- jQuery 1.6.0, 1.6.1 (memberSearchandMail.html, show1.html)
- → 既存の懸念事項に追加

### 大規模なインラインJavaScript（追加）
- memberedit.html: 320行のキーナビゲーション実装
- show1.html: 150行以上の Google Maps + Galleriffic 実装
- → 既存の懸念事項に追加、外部ファイル化を検討

### テストファイルの可能性
- proc.html: シンプルな認証成功画面、言語切り替えのみ
- → 本番環境で使用されているか確認必要

---

# 調査結果（第4回: ルート管理画面系 8ファイル + s-style/hon 2ファイル）

## 大幅変更

### Djangoテンプレートタグの変換（追加発見）
- `{% regroup data.picdata by title as title_list %}` → Jinja2でカスタムフィルタまたはループロジックで再実装必要
- `{% ifchanged %}` → Jinja2では非サポート、ループ内でprevループ変数を使った条件分岐に変更
- s-style/hon/article.html (327, 330行), s-style/hon/articlemlxxx.html (594, 596行) で使用
- 画像ギャラリーのグルーピング表示に使用されており、重要な機能

### Plupload（ファイルアップロードライブラリ）の移行
- upload.html, upload2.html で使用
- Flash/Silverlight依存（古い技術、現代ブラウザで非サポート）
- `runtimes: 'html5,flash,silverlight,html4'` 指定あり
- Flask移行時はHTML5のみのファイルアップロードに変更推奨

### GAE Blobstore API 呼び出しの変更
- upload.html (61-71行), upload2.html (22-30行): `/FileUploadFormHandler/generate_upload_url` エンドポイント
- アップロード前にAJAXでBlobstore URLを取得する実装
- Flask移行時はストレージAPI全体の再設計が必要

### HTMLコメント構文エラーの修正
- test2.html (107行): `<--!` → `<!--` に修正必要
- HTMLパーサーエラーの原因となる可能性

### 廃止されたJavaScript属性の削除
- `language="JavaScript"` (uploadadresslist.html:5, uploadbkdata.html:5) → `type="text/javascript"` に変更
- またはHTML5では script タグの type 属性自体を省略可能

## 統一仕様

### URLパラメータ取得の共通パターン
- upload.html (78-88行), upload2.html (32-42行) で同一の `getUrlVars()` 関数
- クエリ文字列を解析して連想配列で返す実装
- Flask移行後も同様の処理が必要な場合、共通JSライブラリ化を検討

### CSVアップロードフォームの統一パターン
- uploadadresslist.html, uploadbkdata.html でほぼ同一構造
- 結果表示: `{% for info in result %} <li>{{info|default_if_none:""}}`
- エラー表示: `{{error_msg}}`
- 共通コンポーネント化の可能性あり

### テンプレート基底ファイルパターン
- userpagebase.html: `{% block title %}`, `{% block content %}` による継承
- tableレイアウト、絶対パス（/css/, /js/, /img/）使用
- 既存パターンと一貫性あり

### iframe による外部HTMLの埋め込み（追加発見）
- s-style/hon/articlemlxxx.html (168, 215行): head.html, sidemenu.html, footer.html を読み込み
- 高さ・幅を固定値で指定（scrolling="no"）
- レスポンシブ対応時に課題となる可能性

### 画像プリロード実装
- s-style/hon/articlemlxxx.html (165行): onload属性で `preloadImages()` 関数呼び出し
- ロールオーバー画像（menu01o.jpg, menu02o.jpg等）のプリロード
- 古い手法だが、機能的には問題なし

## 懸念事項

### jQuery .live() メソッドの追加使用箇所
- s-style/hon/article.html (167行), s-style/hon/articlemlxxx.html (136行)
- `$("a[rel='history']").live('click', function)`
- jQuery 1.7以降は非推奨、.on() への変更必須
- 既存の懸念事項に追加箇所を記録

### テストファイルの扱い（追加）
- test.html: 極めてシンプル、`{{res|linebreaksbr}}` のみ表示
- test2.html: jQuery autocompleteのテスト、appspot.comへのハードコードリンク複数
- 本番環境では不要の可能性、移行対象から除外を検討

### 外部API依存（追加）
- test2.html: JSONP通信で ws.geonames.org の外部APIを使用
- ネットワーク接続が必要、外部サービス停止時の影響

### アップロードファイルの重複実装
- upload.html (新しいバージョン: plupload.full.min.js, jQuery 1.10.2)
- upload2.html (古いバージョン: plupload.full.js, jQuery 1.7.1)
- 機能がほぼ同一、統合を検討すべき

### 相対パスの混在（追加発見）
- uploadbkdata.html (26行): `../duplicationcheck/bkdata.html` で相対パス使用
- 他のファイルは絶対パス（/css/）が多数
- パス解決ルールの統一が引き続き必要

---

# 調査結果（第5回: s-style/hon 4ファイル + backoffice 5ファイル）

## 大幅変更

### メールテンプレート専用の構造
- bklistml.html, bklistmlxxx.html: メール送信用の特殊なテーブルレイアウト
- `{{subject}}`, `{{body|safe|linebreaks}}` でメール本文を挿入
- インラインスタイルを多用（メールクライアント対応）
- 既存のbklist.htmlとは大きく異なる構造

### モバイル専用テンプレートのインラインスタイル
- articlem.html, bklistm.html: モバイル専用のレイアウト
- `style="text-align:center; background-color:#c8911c; font-size:xx-small;"` 等を多用
- 外部CSSではなくインラインスタイルで完結

### 巨大な検索フォームの実装
- bksearch.html (2342行): 極めて大規模な物件検索画面
- 457行のインラインJavaScript
- jQueryプラグイン（autocomplete, multicheckbox）の複雑な実装
- 動的フォーム追加/削除の仕組み

## 統一仕様

### 物件リスト表示の共通パターン
- bklist.html (s-style/hon), bklist.html (backoffice), bklistm.html で同様の構造
- `{% for bkdata in data.bkdatalist %}` → 物件情報の繰り返し表示
- 間取り表示のネスト条件分岐（stTyp11, stTyp21...stTyp71まで7段階）
- アイコン表示の統一パターン（{% ifequal %}による条件分岐）

### Google Analytics の実装
- bklist.html (s-style/hon, backoffice): `_gaq.push(['_setAccount', 'UA-7545989-4'])`
- articlem.html, bklistm.html: 古い形式の Google Analytics
- Flask移行時は最新版への更新を検討

### ページネーション実装
- bklist.html, bklistm.html: `{{data.offsetpre}}`, `{{data.offsetnext}}` でページング
- モバイル版も同様の仕組み
- Flask移行後も同じ変数名を使用可能

### メールテンプレート用の条件付き表示
- bklistml.html (22-28行): `{% if data.bkdatalist %}` で物件情報の有無を判定
- 特選情報セクションの表示/非表示を制御
- メール送信時の柔軟性を確保

### jQueryプラグインの複雑な実装パターン
- bksearch.html: autocomplete, multicheckbox, thickbox の組み合わせ
- 動的要素の追加時に `tb_init()` で再初期化
- プラグイン間の連携処理

## 懸念事項

### テンプレート変数のタイポ（広範囲）
- bklist.html (236, 235行): `{{bbkdata.kdata.bsRsnmi1}}` → `bkdata` が `bbkdata.kdata` になっている
- bklistml.html (130行), bklistmlxxx.html (135行), bklist (backoffice) (235行), bklistm (backoffice) でも同様
- 元から動いていなかった可能性あり、修正の影響範囲を確認必要

### 変数参照の不整合
- bklist.html (251行): `bkdat.ekmi2` → `bkdata.ekmi2` (typo)
- bklistml.html (145行): `bkdat.bkdata.ekmi2` → `bkdata.ekmi2` (重複)
- 複数のファイルで同様のパターン、一括修正が必要

### 極めて大規模なファイル
- bksearch.html: 2342行（超巨大、保守困難）
- article.html (backoffice): 929行
- 機能分割やコンポーネント化の検討が必要

### 巨大なインラインJavaScript
- bksearch.html (15-457行): 457行のJavaScript
- article.html, articlem.html: 150-190行程度のJavaScript
- 外部ファイル化を検討すべき、保守性とキャッシュ効率の改善

### コピーファイルの日本語ファイル名
- "bklistml - コピー.html": ファイル名に日本語、読み込みエラー
- 移行時にファイル名の正規化が必要

### jQuery .live() の使用（追加箇所）
- bksearch.html (39行): `$(".mdrHysu,.mdrTyp").live("keyup mouseup", function())`
- bksearch.html (175行): `$("a[rel='history']").live('click', function(e))`
- article.html (167行), articlem.html (175行): 同様
- 全ファイルで .on() への変換が必要

### IE専用コードの削除必要
- bksearch.html (319行): `if(d.all) window.event.keyCode = 0`
- IE検出と非標準イベント処理、モダンブラウザ向けに書き直し必要

### ime-mode の非標準CSS
- bksearch.html (263-267行): `$(this).css("ime-mode", "active")`
- ブラウザサポート終了済み、削除またはHTML5 inputmode属性への変更検討

### DOCTYPE の不統一（追加）
- bklist.html (s-style/hon): DOCTYPE なし
- bklistml.html: HTML 4.01 Frameset
- bklistmlxxx.html: HTML 4.01 Frameset
- TEST.html: DOCTYPE なし
- article.html (backoffice): HTML 4.01 Strict
- articlem.html: HTML 4.01 Transitional
- bklist (backoffice): DOCTYPE なし
- bklistm.html: HTML 4.01 Transitional
- bksearch.html: XHTML 1.0 Transitional
- HTML5への統一を検討するか判断必要

### onMouseOver/onClick の大文字小文字混在
- bklist.html: `onMouseOver`, `onMouseOut`, `onClick` (大文字O/C)
- HTML標準では小文字が推奨、統一を検討

### JSONP 通信の大規模使用
- bksearch.html (113, 154, 208行): クロスドメイン通信に使用
- Flask移行時はCORS設定への変更を検討
- または引き続きJSONP対応が必要か判断

### モバイル版テンプレートの古いHTML属性
- articlem.html, bklistm.html: `<hr style="..." size="1">` など非推奨属性使用
- `<font size="-2">` タグの使用（HTML5で廃止）
- CSSへの移行が必要

---

# 調査結果（第6回: backoffice 4ファイル + ww2.s-style.ne.jp 6ファイル）

## 大幅変更

### Thickbox ライブラリの置き換え
- article-copy.html, article.html (ww2.s-style.ne.jp): `class="thickbox"` で画像ライトボックス表示
- 開発終了済みのライブラリ、モダンな代替ライブラリへの移行検討
- または Galleriffic に統合可能か確認

### floatformat:"-2" の使用パターン
- article.html (587-623, 700-751行): 土地面積・建物面積・接道状況の幅員/間口で使用
- 小数点以下2桁までの表示制御
- Jinja2でそのまま使用可能

### 変数タイポの広範囲な分布
- article-copy.html (764-767行): `hushjyuZih`, `hushjyuGtgk`
- article.html (762-767行): `chushjyuZih`, `chushjyuGtgk`
- 駐車場情報のフィールド名が不統一、どちらが正しいか要確認

## 統一仕様

### 物件詳細ページの共通構造
- article*.html: Galleriffic + Google Maps + 物件情報テーブルの組み合わせ
- 画像ギャラリー: `{% regroup data.picdata by title as title_list %}` でグループ化
- 地図表示: `initialize()`, `createMarker()` による初期化
- テーブルレイアウト: 2カラム（左右で物件概要を分割）

### floatformat フィルタのパラメータパターン
- 引数なし: `{{data.bkdata.knpirt|floatformat}}` - デフォルト表示
- `-2`: `{{data.bkdata.tcMnsk2|floatformat:"-2"}}` - 小数点以下2桁まで（不要な0は非表示）
- 土地・建物面積など精度が重要な箇所で使用

### 周辺環境情報の表示パターン
- article.html (780-844行): shuhnKnkyu1Fre～shuhnKnkyu5Fre の条件分岐
- 各施設までの距離（kyr1～kyr5）と所要時間（jkn1～jkn5）を表示
- shuhnAccs1～shuhnAccs5でアクセス手段（徒歩/車）を表示
- 5件まで表示可能な拡張性のある実装

### モバイル版のインラインスタイル
- articlem*.html: `<div style="text-align:center; background-color:#c8911c; font-size:xx-small;">`
- すべてのスタイルをインライン記述
- メール用テンプレートと同様の手法、外部CSS非依存

### PC版とモバイル版の分離
- article.html (857行) vs articlem.html (531行): 別構造
- モバイル版は簡略化、Galleriffic非使用、単一画像のみ表示
- Google Maps はモバイル版で非表示、リンクのみ提供

### sorry.html のシンプルなエラーページ
- {% extends "userpagebase.html" %} で基底テンプレート継承
- `{{error_msg}}`, `{{completed_msg}}` の表示
- hiddenフィールドで corp_name, sitename, branch_name, togo を保持
- 軽量で汎用性の高い実装

### テンプレート基底ファイル userpagebase.html
- tableレイアウトによるヘッダー/コンテンツ/フッター構造
- ログインボタン、会員登録ボタンの配置
- smooth.pack.js（スムーズスクロール）の使用
- 絶対パス（/css/, /js/, /img/）使用

## 懸念事項

### jQuery .live() の使用（追加箇所）
- article.html (165行), article-copy.html (167行): `$("a[rel='history']").live('click', function(e))`
- articlem.html (175行), articlem-copy.html (175行): 同様
- 全ファイルで .on() への変換必須

### 変数タイポの広範囲な分布（追加）
- article-copy.html: `hushjyuZih` ↔ article.html: `chushjyuZih`
- 駐車場有無のフィールド名が不統一
- articlem.html (463-467行): `hushjyuZih` と `hushjyuGtgk` を使用
- どちらが正しいか確認必要、全ファイルで統一が必要

### 設備フィールドのタイポ
- article-copy.html (773行): `tbFrespc`
- article.html (771行): `stbFrespc`
- 設備（Free Spec?）のフィールド名が不統一、要確認

### コピーファイルの乱立
- article-copy.html, articlem-copy.html, bklist-copy (1).html, bklist-copy.html
- コピーファイルが多数存在、本番で使用されているか確認必要
- 不要なファイルは移行対象から除外を検討

### Google Analytics の実装不統一（追加）
- article.html (911-925行): モダンな `_gaq.push` 形式
- articlem.html (522-527行): 古い `var gaJsHost = ...` 形式
- bklist*.html: モダンな形式
- モバイル版のみ古い実装、統一を検討

### DOCTYPE の不統一（追加箇所）
- sorry.html: XHTML 1.0 Transitional
- userpagebase.html: HTML 4.01 Frameset
- article-copy.html, article.html: HTML 4.01 Strict
- articlem-copy.html, articlem.html: HTML 4.01 Transitional
- bklist-copy.html, bklist-copy (1).html: DOCTYPE なし
- HTML5への統一を引き続き検討

### テーブルレイアウトの大規模使用
- article*.html, bklist*.html, userpagebase.html で `<table>` レイアウト多用
- モダンなCSS Grid/Flexboxへの移行は大規模作業となる
- 現状維持か、段階的移行か判断必要

### インラインイベントハンドラの大量使用
- article*.html: `onMouseOver`, `onMouseOut`, `onClick` を多用
- 画像ロールオーバー: `document.images['menu01'].src='...'`
- モダンなイベントリスナー（addEventListener）への移行を検討

### Galleriffic の複雑な実装
- article*.html (107-183行): 900ms遷移、自動再生、履歴管理
- jquery.history.js との連携
- モダンブラウザでの動作確認必須、代替ライブラリへの移行も検討

### Google Maps API のセンサーパラメータ
- article*.html (8行), articlem*.html (16行): `sensor=false`
- このパラメータは非推奨、削除または最新APIバージョンへの移行検討

### API キーのハードコード（再確認）
- article*.html, articlem*.html: `AIzaSyB3Pj9gP_x_Gjdgg2GqXaGHQnB5hNaw3no`
- 環境変数化またはテンプレート変数化を引き続き検討

### モバイル版の古いHTML属性（追加箇所）
- articlem*.html (201, 485行): `<hr style="..." size="1">`
- articlem*.html (495行): `<font size="-2">`, `<font size="-3">`, `<font size="-4">`
- CSSへの移行が必要

---

# 調査結果（第7回: ww2.s-style.ne.jp 8ファイル + www.chikusaku-m.com 2ファイル）

## 大幅変更

### 文字エンコーディングの変更
- index.html, pict.html (ww2.s-style.ne.jp): `<meta charset="shift_jis">`
- UTF-8への変更必須、Flask移行時のエンコーディング統一
- テンプレート変数の文字化け防止

### ローンシミュレーター実装の保守
- article.html (www.chikusaku-m.com, 59-96行): 複雑なローン計算ロジック
- CalcRepaymentMoney(), gocal() 関数による月次返済額計算
- jQuery.cookie でシミュレーション設定を保存
- Flask移行後も機能維持が必要

### 大量コメントアウトコードの削除
- article.html (www.chikusaku-m.com, 191-342行): 152行のコメントアウトされたローン計算関数
- calc(), ClearIP(), Acheck() 等の未使用関数
- 削除してコードサイズを削減すべき

## 統一仕様

### モバイル版テンプレートの軽量実装
- bklistm.html, bklistm-copy.html: 全スタイルをインライン記述
- 外部CSS非依存、メール配信と同様の手法
- `<a href="tel:0527515900">` によるタップ発信対応

### 静的モックアップページの扱い
- index.html (ww2.s-style.ne.jp): テンプレート変数なし、完全静的HTML
- 相対パス（../js/, ../css/, ../cmn_img/）を使用
- 開発時のデザイン確認用、本番環境では不要の可能性

### 画像表示専用テンプレート
- pict.html: JavaScript:window.close() でウィンドウを閉じる
- 単一画像の拡大表示用、シンプルな実装

### エラーページの共通構造
- sorry.html (ww2.s-style.ne.jp): {% extends "userpagebase.html" %}
- `{{error_msg}}`, `{{completed_msg}}` の条件付き表示
- フォームhiddenフィールドで状態保持（corp_name, sitename等）

### 基底テンプレートの構造
- userpagebase.html, userpagebase (1).html: tableレイアウトによるヘッダー/フッター
- Google Analytics の統一実装（_gaq.push形式）
- smooth.pack.js（スムーススクロール）の共通使用

### iframe による外部コンテンツ読み込み
- article.html (www.chikusaku-m.com, 427行): `<iframe src="https://www.chikusaku-m.com/head.html">`
- ヘッダー、サイドメニュー、フッターを独立したHTMLとして管理
- 各iframe の高さ・幅を固定値で指定（scrolling="no"）

## 懸念事項

### 変数タイポの継続発見
- bklist.html (ww2.s-style.ne.jp, 188行): `{{bkdata.stHrs41}}` → `{{data.bkdata.stHrs41}}` に修正必要
- bklist.html (193行): 同様のタイポ
- bklist.html (236行): `{{bbkdata.kdata.bsRsnmi1}}` → `{{bkdata.bkdata.bsRsnmi1}}`
- bklist.html (251, 258行): `bkdat.ekmi2` → `bkdata.ekmi2`
- bklist.html (www.chikusaku-m.com, 193, 243, 258行): 同様のタイポ
- 複数ファイルで同一パターンのタイポ、一括置換が必要

### コピーファイルの重複
- bklistm-copy.html: bklistm.html と完全同一内容
- userpagebase (1).html: userpagebase.html と完全同一内容
- 本番環境で使用されているか確認、不要なら移行対象から除外

### 文字エンコーディング shift_jis の使用
- index.html (ww2.s-style.ne.jp, 5行): `<meta charset="shift_jis">`
- pict.html (3行): 同様
- Flask移行時のUTF-8統一で文字化けリスク、変換テスト必須

### 巨大ファイルの継続発見
- article.html (www.chikusaku-m.com, 1044行): 極めて大規模
- Galleriffic + Google Maps + ローンシミュレーター + iframe の複合実装
- コンポーネント分割の検討が必要

### 大量のインラインJavaScript
- article.html (www.chikusaku-m.com, 20-189行): 170行のJavaScript
- Google Maps初期化、Galleriffic設定、ローンシミュレーター
- 外部ファイル化でキャッシュ効率とメンテナンス性を改善

### jQuery .live() の使用（追加箇所）
- article.html (www.chikusaku-m.com, 171行): `$("a[rel='history']").live('click', function(e))`
- jQuery 1.7以降は非推奨、.on() への変更必須

### jQuery バージョンの不統一（追加）
- article.html (www.chikusaku-m.com): jQuery 1.7.1
- 既存の懸念事項に追加、統一バージョンへの移行検討

### iframe の多用
- article.html (www.chikusaku-m.com, 427行): head.html 読み込み
- 固定高さ指定（height="100"）、レスポンシブ対応時に課題
- 外部サイト依存、アクセス不可時の影響

### Google Maps API の古いパラメータ
- article.html (www.chikusaku-m.com, 10行): `sensor=false` パラメータ
- 非推奨パラメータ、最新APIバージョンへの移行検討

### コメントアウトコードの大量残存
- article.html (www.chikusaku-m.com, 191-411行): 221行のコメントアウトコード
- calc(), Acheck(), Bcheck() 等の未使用関数、削除を推奨

### preloadImages の古い実装
- article.html (www.chikusaku-m.com, 424行): `onload="preloadImages(...)"`
- 7個の画像をプリロード、モダンなリソースヒントへの移行検討

### Google Analytics の実装不統一（追加）
- index.html (ww2.s-style.ne.jp, 238-248行): 古い形式 `var gaJsHost = ...`
- userpagebase.html: モダンな `_gaq.push` 形式
- article.html (www.chikusaku-m.com): モダンな形式
- index.htmlのみ古い実装、統一を検討

### DOCTYPE の不統一（追加箇所）
- bklist.html (ww2.s-style.ne.jp): DOCTYPE なし
- bklistm.html, bklistm-copy.html: HTML 4.01 Transitional
- index.html: HTML 4.01 Transitional
- pict.html: XHTML 1.0
- sorry.html: HTML 4.01 Frameset
- userpagebase.html, userpagebase (1).html: HTML 4.01 Frameset
- article.html (www.chikusaku-m.com): HTML 4.01 Transitional
- bklist.html (www.chikusaku-m.com): HTML 4.01 Frameset
- HTML5への統一を引き続き検討

---

# 調査結果（第9回: www.chikusaku-mansion.com 10ファイル）

## 懸念事項

### 静的モックアップファイルの混在
- mypagefollow.html, mypagenewlist.html, mypagesearchlist.html: テンプレート変数が一切なし、完全静的HTML
- ハードコードされたサンプルデータ（日付、物件情報等）のみ表示
- 本番環境では不要の可能性が高い、デザイン確認用と思われる
- 移行対象から除外を検討

### 変数タイポの新パターン（追加）
- mypagebklist.html (102行), mypagebklistfav.html (102行): `{% if bkdata.bkdata.bkdata.ekmi1 %}` - 三重ネスト誤り
- mypagebklist.html (130行), mypagebklistfav.html (130行): `{% if bkdata.bkdat.bkdata.ekmi2 %}` - `bkdat` タイポ
- mypagebklist.html (132行), mypagebklistfav.html (132行): `{{bkdata.bkvdata.ekmi2}}` - `bkvdata` タイポ
- 複数ファイルで同一パターンの誤り、一括修正が必要

### フォーム name 属性の重複
- mypagemydata.html (60, 66行): 会社連絡先セクションで `name="phone"`, `name="fax"` が重複
- 個人情報セクション（51-53行）と会社情報セクション（60-78行）で同一name属性
- 本来は `CorpOrg_phone`, `CorpOrg_fax` であるべき、サーバー側処理に影響

### 絶対パスの混在（追加箇所）
- mypagetop.html (6行): `/img/t-maypage.jpg` - ルート絶対パス使用
- mypagesearch.html (8-10行): `/js/`, `/css/` - ルート絶対パス使用
- 他のマイページ系ファイルは相対パス（`img/`）を使用、不統一

### jQuery .live() の使用（追加箇所）
- mypagesearch.html (29行): `$(".mdrHysu,.mdrTyp").live("keyup mouseup", function())`
- jQuery 1.7以降は非推奨、.on() への変更必須

### IE専用コードの削除必要（追加箇所）
- mypagesearch.html (310行): `if(d.all) window.event.keyCode = 0`
- userpagebase.html (40行): `javascript:window.external.addFavorite(...)`
- IE専用機能、モダンブラウザで非サポート

### ime-mode の非標準CSS（追加箇所）
- mypagesearch.html (255行): `$(this).css("ime-mode", "active")`
- ブラウザサポート終了済み、削除またはHTML5 inputmode属性への変更検討

### Thickbox の使用（追加箇所）
- mypagesearch.html (9-10行): thickbox.css, thickbox.js の読み込み
- 開発終了済みライブラリ、モダンな代替への移行検討

### インラインイベントハンドラの大量使用（追加箇所）
- userpagebase.html (20行): onload属性でpreloadImages()実行
- userpagebase.html (73-90行): onmouseover, onmouseout, onclick を多用
- モダンなイベントリスナー（addEventListener）への移行を検討

### iframe の使用（追加箇所）
- userpagebase.html (122行): sidemenu.html を iframe で読み込み
- userpagebase.html (149行): footer.html を iframe で読み込み
- 高さ・幅を固定値で指定、レスポンシブ対応時に課題

### 外部ドメインへの強い依存（追加箇所）
- userpagebase.html: https://www.chikusaku-mansion.com/ に全面依存
- CSS, JS, 画像リソース、iframe コンテンツをすべて外部ドメインから読み込み
- 外部サイトが利用不可になった場合の影響大

### ページネーション実装の共通パターン（確認）
- mypagebklist.html, mypagebklistfav.html: `{{data.offsetpre}}`, `{{data.offsetnext}}` 使用
- 既存パターンと一貫性あり、Flask移行後も継続可能

---

# 調査結果（第10回: www.chikusaku-mansion.com 1ファイル + www.s-style.ne.jp 9ファイル）

## 大幅変更

### スライダーライブラリの統一または廃止
- flickslide (article-koukai-sp.html, article-member-login-sp.html) - jQuery 1.5.2
- swipeshow (article-koukai-spxxx.html, article-member-login-spxxx.html) - jQuery 1.9.0
- flipsnap (article-member-sp.html) - 相対パス参照 `js/flipsnap.js`
- xxx接尾辞のファイルはテスト版、本番環境では不要の可能性
- Flask移行時にスライダーライブラリの統一を検討

### 変数タイポの新パターン
- article-member-login-sp.html (60-72行): `bkdata.bkdata.*` という二重参照
- 正しくは `data.bkdata.*` であるべき
- 元から動いていなかった可能性あり、修正の影響範囲を確認必要

### 会員登録フォームの実装パターン
- article-member.html (PC版): formタグで `onSubmit="javascript:_gaq.push(['_linkByPost',this])"`
- article-member-sp.html (SP版): formなし、JavaScriptで動的フォーム生成の可能性
- 2つの実装パターンが混在、Flask移行時に統一を検討

## 統一仕様

### xxx接尾辞ファイルの扱い
- article-koukai-spxxx.html: swipeshow スライダーのテスト版
- article-member-login-spxxx.html: 同様にテスト版
- 本番環境では不要の可能性、移行対象から除外を検討

### 会員限定物件表示の分岐パターン
- article-koukai*.html: 「只今好評発売中」メッセージ
- article-member-login*.html: 「この物件は会員様にだけ限定で」メッセージ
- article-member*.html: ログイン/会員登録フォームのみ表示
- 3段階の表示切り替えパターン、Flask側でルーティング設計が必要

### PC版とSP版のテンプレート分離
- article-koukai.html (PC版, 943行) vs article-koukai-sp.html (SP版, 517行)
- PC版: Galleriffic + jQuery.live() + tableレイアウト
- SP版: flickslide/swipeshow + 軽量実装 + viewportメタタグ
- Flask移行時は両方の実装を維持

### 基底テンプレート userpagebase2.html
- userpagebase.html (www.chikusaku-mansion.com) とほぼ同一構造
- 違い: {% block loginurl %} ブロックの有無
- 複数の基底テンプレートが存在、統合を検討すべきか

## 懸念事項

### 相対パスと絶対パスの混在（追加箇所）
- article-member-sp.html (10行): `js/flipsnap.js` - 相対パス使用
- 他のSP版テンプレート: 絶対パス（https://www.s-style.ne.jp/js/）使用
- パス解決ルールの統一が引き続き必要

### ファイル不在
- article-member (1).html: ファイルが存在しない
- 状態ファイルに記載されているが実際には存在せず
- 移行対象から除外、状態ファイルの記録を更新

### 重複したhiddenフィールド
- article-member.html (328, 329行): `id="sid"` が2回定義
- HTML仕様違反、1つは削除が必要
- サーバー側でどちらが使用されているか確認

### jQuery .live() の使用（追加箇所）
- article-koukai.html (166行): `$("a[rel='history']").live('click', function(e))`
- article-member-login.html (166行): 同様
- 全ファイルで .on() への変換必須

### Google Maps API の非推奨パラメータ（追加箇所）
- article-koukai.html (9行): `sensor=false`
- article-member-login.html (9行): 同様
- sensor パラメータは非推奨、削除または最新APIバージョンへの移行検討

### jQuery バージョンの不統一（追加）
- article-koukai-sp.html: jQuery 1.5.2 - 極めて古い
- article-koukai-spxxx.html: jQuery 1.9.0
- article-koukai.html: jQuery 1.7.1
- 統一バージョンへの移行検討が必要

### reCAPTCHA v3 の実装（確認）
- 今回調査したファイルでは未使用
- 既存調査（regist.html, article.html (www.chikusaku-mansion.com)）で確認済み

### Galleriffic プラグインの使用（継続）
- article-koukai.html, article-member-login.html で使用
- jquery.history.js との連携
- モダンブラウザでの動作確認必須

---

# 調査結果（第11回: www.s-style.ne.jp 10ファイル）

## 大幅変更

### ルーティングテンプレートの実装パターン
- article.html, article-sp.html: 極めてシンプル（13行）、{% include %} による分岐専用
- 物件状態（dtsyuri）と公開状態（webkkkk, auth）によって4種類のテンプレートを切り替え
- 売約済み: article-soldout.html / article-soldout-sp.html
- 公開中: article-koukai.html / article-koukai-sp.html
- 会員限定（ログイン済み）: article-member-login.html / article-member-login-sp.html
- 会員限定（未ログイン）: article-member.html / article-member-sp.html
- Flask移行時はルーティング層での制御も検討可能

### shift_jis エンコーディングの変更必須
- index.html (ww2.s-style.ne.jp, 5行), pict.html (3行): `<meta charset="shift_jis">`
- UTF-8への変更必須、Flask移行時のエンコーディング統一
- ファイル保存形式の変換と文字化けテストが必要

### JavaScript void演算子の古い記法
- article-soldout-sp.html (28行): `javascript:void BookMark();`
- モダンな記法: `javascript:void(0)` または `#` 推奨
- onClick イベントハンドラでの使用を検討

## 統一仕様

### 売約済みページの実装パターン
- article-soldout.html (PC版, 380行): フル機能の物件詳細レイアウト維持、中央に売約済みメッセージ表示
- article-soldout-sp.html (SP版, 100行): 簡素なレイアウト、「この物件は販売終了致しました」メッセージのみ
- PC版: Galleriffic + Google Maps実装を残したまま、コンテンツ部分のみ差し替え
- SP版: 軽量実装、スライダーライブラリ（flipsnap.js）使用
- 両方ともお問い合わせフォームへのリンクを提供

### 静的モックアップファイルの扱い
- bklistm.html (96行): テンプレート変数なし、完全静的HTML、サンプル物件データのみ
- index.html (ww2.s-style.ne.jp, 250行): 完全静的、相対パス使用、shift_jis
- pict.html (33行): シンプルな画像表示用、JavaScript:window.close() 使用
- デザイン確認用、本番環境では不要の可能性が高い
- 移行対象から除外を検討

### ルーティング専用テンプレートの実装
- article.html, article-sp.html: 13行のみ、ロジックのみ記述
- {% ifequal %} と {% if %} の組み合わせで4段階の条件分岐
- 実装の集約化により保守性向上
- Flask移行時は同様の構造を維持可能

### 物件リスト表示の共通パターン（確認）
- bklist.html, bklist-sp.html: 同様の構造（間取り表示の7段階ネスト、アイコン表示）
- ページネーション: `{{data.offsetpre}}`, `{{data.offsetnext}}`
- 変数タイポも同様のパターン（既存ルールで記録済み）

## 懸念事項

### shift_jis エンコーディングの変換リスク
- index.html, pict.html で使用
- UTF-8変換時の文字化けリスク（特にタイトル、メッセージなど）
- ファイル内容の保存形式変換が必要
- テスト環境での動作確認必須

### 静的モックアップファイルの本番環境での必要性
- bklistm.html: 完全静的、テンプレート変数なし
- index.html (ww2.s-style.ne.jp): 相対パス使用、shift_jis
- pict.html: 画像表示専用、シンプル
- 本番環境で使用されているか確認必要
- 使用されていない場合は移行対象から除外

### 変数タイポの追加箇所
- bklist-sp.html (138, 141行): `{{bbkdata.kdata.bsRsnmi1}}` → `{{bkdata.bkdata.bsRsnmi1}}`
- bklist-sp.html (141行): `{{bkdata.bstiMishu1}}` → `{{bkdata.bkdata.bstiMishu1}}`
- bklist-sp.html (132, 147行): `{{bkdata.thM21}}` → `{{bkdata.bkdata.thM21}}`
- bklist.html (ww2.s-style.ne.jp, 243, 258行): `{{bkdata.thM21}}` → `{{bkdata.bkdata.thM21}}`
- bklist.html (249, 264行): `{{bbkdata.kdata.bsRsnmi1}}` → `{{bkdata.bkdata.bsRsnmi1}}`
- bklist.html (252, 258行): `{{bkdata.bstiMishu1}}` → `{{bkdata.bkdata.bstiMishu1}}`
- bklist.html (258, 264行): `{{bkdata.tihM1}}` → `{{bkdata.bkdata.tihM1}}`
- 複数ファイルで同一パターン、一括修正が必要

### jQuery .live() の使用（追加箇所）
- article-soldout.html (166行): `$("a[rel='history']").live('click', function(e))`
- articlem.html (175行): 同様
- 全ファイルで .on() への変換必須

### Google Maps API の非推奨パラメータ（追加箇所）
- article-soldout.html (9行): `sensor=false`
- articlem.html (16行): 同様
- sensor パラメータは非推奨、最新APIバージョンへの移行検討

### jQuery バージョンの不統一（追加）
- article-soldout.html: jQuery 1.7.1
- articlem.html: jQuery 1.7.1
- bklist-sp.html: jQuery 1.9.1 (Google CDN)
- 統一バージョンへの移行検討が必要

### Google Analytics の実装不統一（追加）
- article-soldout.html: モダンな `_gaq.push` 形式
- article-soldout-sp.html: モダンな `_gaq.push` 形式
- articlem.html: 古い `var gaJsHost = ...` 形式
- index.html (ww2.s-style.ne.jp): 古い形式
- モバイル版と静的ファイルのみ古い実装、統一を検討

### DOCTYPE の不統一（追加箇所）
- article-soldout-sp.html: XHTML 1.0 Transitional
- article-soldout.html: HTML 4.01 Strict
- article-sp.html: DOCTYPE なし（ルーティング専用、継承元に依存しない）
- article.html: DOCTYPE なし（ルーティング専用、継承元に依存しない）
- articlem.html: HTML 4.01 Transitional
- bklist-sp.html: XHTML 1.0 Transitional
- bklist.html (ww2.s-style.ne.jp): DOCTYPE なし
- bklistm.html: HTML 4.01 Transitional
- index.html (ww2.s-style.ne.jp): HTML 4.01 Transitional
- pict.html: XHTML 1.0
- HTML5への統一を引き続き検討

### Galleriffic プラグインの使用（継続）
- article-soldout.html: 使用（売約済みだが実装は維持）
- articlem.html: 使用
- モダンブラウザでの動作確認必須

### Thickbox の使用（追加箇所）
- articlem.html (21-23行): thickbox.js, thickbox.css の読み込み
- 開発終了済みライブラリ、モダンな代替への移行検討

### インラインイベントハンドラの大量使用（追加箇所）
- article-soldout.html (203-240行): onMouseOver, onMouseOut, onClick を多用
- モダンなイベントリスナー（addEventListener）への移行を検討

### モバイル版の古いHTML属性（追加箇所）
- articlem.html (201行): `<hr style="..." size="1">`
- articlem.html (503-548行): `<font size="-2">`, `<font size="-3">`, `<font size="-4">`
- CSSへの移行が必要

---

# 調査結果（第12回・最終: www.s-style.ne.jp 3ファイル）

## 大幅変更

### {% comment %} タグの変換
- sorry.html (3-10行): Django/webapp2 の {% comment %} タグ使用
- 著作権情報、バージョン情報をコメント内に記載
- Jinja2では `{# ... #}` 形式に変更必要

## 統一仕様

### エラーページの実装パターン
- sorry.html: {% extends "userpagebase.html" %} で基底テンプレート継承
- {% block title %}, {% block content %} でコンテンツ差し替え
- error_msg, completed_msg の条件付き表示
- hiddenフィールドで状態保持（corp_name, sitename, branch_name, togo）
- シンプルで汎用性の高い実装

### 基底テンプレートの構造（SP版）
- userpagebase-sp.html: XHTML 1.0 Transitional
- {% block content %} でコンテンツブロック定義
- flipsnap.js スライダーライブラリ使用
- Google Analytics統合（モダン_gaq.push形式）
- シンプルなヘッダー・フッター構造

### 基底テンプレートの構造（PC版）
- userpagebase.html: DOCTYPE なし
- {% block title %}, {% block content %} でコンテンツブロック定義
- tableレイアウトによる2カラム構造
- サイドバー: バナー・リンク集・ブログリンク・QRコード
- Google Analytics統合（モダン_gaq.push形式）
- smooth.pack.js（スムーススクロール）使用

### バージョン管理ブロックの実装
- sorry.html (12-13行): {% block revision %}, {% block date %} でバージョン管理
- CVSのバージョン情報を埋め込む仕組み
- Flask移行時は削除または別の方法で管理を検討

## 懸念事項

### 相対パスと絶対パスの混在（追加箇所）
- userpagebase-sp.html (10行): `js/flipsnap.js` - 相対パス使用
- 他のリソース: 絶対パス（https://www.s-style.ne.jp/）使用
- パス解決ルールの統一が引き続き必要

### JavaScript void演算子の古い記法（追加箇所）
- userpagebase-sp.html (28行): `javascript:void BookMark();`
- article-soldout-sp.html と同様の古い記法
- モダンな記法への変更を検討

### DOCTYPE の不統一（最終確認）
- sorry.html: DOCTYPE なし（userpagebase.html に依存）
- userpagebase-sp.html: XHTML 1.0 Transitional
- userpagebase.html: DOCTYPE なし
- HTML5への統一を引き続き検討

### インラインスタイルの使用
- userpagebase.html (8-13行): `<style>` タグで色指定
- `p {color: red}`, `h2 {color: blue; font-size: 120%}` をインライン定義
- 外部CSSファイルへの移行を検討

### インラインイベントハンドラの大量使用（追加箇所）
- userpagebase.html (41-82行): onMouseOver, onMouseOut, onClick を多用
- 画像ロールオーバー: `document.images['menu01'].src='...'`
- モダンなイベントリスナー（addEventListener）への移行を検討

### テンプレート変数の埋め込み位置
- userpagebase.html (34行): `{{data.value1}}{{data.value2}}|` をh1タグ内に直接埋め込み
- 通常のテンプレート変数と異なる使用方法、用途確認が必要

### 外部広告スクリプトの使用
- userpagebase.html (18-23行): `https://j1.ax.xrea.com/l.j?id=100716419`
- 外部広告サービスへの依存
- Flask移行時の動作確認が必要

---

# 調査結果（第8回: www.chikusaku-m.com 2ファイル + www.chikusaku-mansion.com 8ファイル）

## 大幅変更

### テンプレート継承の引用符なし構文（追加箇所）
- article.html (www.chikusaku-mansion.com, 1行): `{% extends applicationpagebase %}`
- article2.html (www.chikusaku-mansion.com, 1行): 同様
- Jinja2では `{% extends "applicationpagebase.html" %}` に変更必須
- 既存の懸念事項に追加、全ファイルで統一対応が必要

### IE専用API window.external.addFavorite の削除
- article2.html (228行): `javascript:window.external.addFavorite(...)`
- IE専用機能、モダンブラウザで非サポート
- 代替方法: ブックマーク追加のUIを表示するか、機能削除を検討

### コンポーネントインクルードの実装
- article.html (331, 357, 369行): `{% include "articlebkdata.html" %}`
- articlebkdata.html は物件詳細表示の共通コンポーネント
- テンプレートの部品化が既に実装されている良い例

## 統一仕様

### マイページ系テンプレートの共通構造
- mypageResign.html, mypagebkdata.html: `{% extends "mypagebase.html" %}`
- mypagebase.html: ヘッダー・メニュー・フッターの統一レイアウト
- container ブロックでコンテンツを差し替える実装
- Google Analytics 統合（UA-7545989-12）

### マイページ基底テンプレートのCSS参照
- mypagebase.html (9行): `/css/s-style/hon/www.chikusaku-mansion.com/mypage.css`
- サイト固有のCSSパスを絶対パスで参照
- Flask移行時は相対パスへの変更を検討

### 絶対パスと相対パスの混在（追加発見）
- bklist.html (www.chikusaku-mansion.com, 228-230行): `/article/img-waku/01.jpg` 等
- 同じファイル内で相対パス（83行: `cmn_img/t01.jpg`）と混在
- パス解決ルールの統一が引き続き必要

### iframe による外部HTML読み込み（継続パターン）
- userpagebase.html (www.chikusaku-m.com, 25行): head.html 読み込み
- bklist.html (www.chikusaku-mansion.com, 18, 80, 332行): head.html, sidemenu.html, footer.html 読み込み
- 高さ・幅を固定値で指定（scrolling="no"）
- 複数サイトで共通の実装パターン

### 物件詳細表示の共通構造パターン
- article.html, article2.html, mypagebkdata.html で同様の構造
- Galleriffic + Google Maps + 物件情報テーブル
- `{% regroup data.picdata by title as title_list %}` でグループ化
- 間取り表示のネスト条件分岐（stTyp11～stTyp71）

### reCAPTCHA v3 の実装パターン
- article.html (514-545行): grecaptcha.execute() でトークン取得
- 動的に hidden input 要素を生成してフォーム送信
- サイトキーをテンプレート変数で渡す実装
- Flask移行後も同様の実装を継続可能

### 静的モックアップファイルの扱い
- TEST.html (www.chikusaku-mansion.com): 極めてシンプル、相対パス使用
- デザイン確認用、本番環境では不要の可能性

## 懸念事項

### jQuery .live() の使用（追加箇所）
- article.html (www.chikusaku-mansion.com, 225行): `$("a[rel='history']").live('click', function(e))`
- article2.html (190行): 同様
- mypagebkdata.html (132行): 同様
- 全ファイルで .on() への変換必須

### 駐車場フィールド名の不統一（追加発見）
- article.html (www.chikusaku-mansion.com, 788-793行): `hushjyuZih`, `hushjyuGtgk`
- article2.html (788-793行): 同様に `hushjyuZih`
- articlebkdata.html (416-421行): `chushjyuZih`, `chushjyuGtgk`
- mypagebkdata.html (496-501行): `hushjyuZih`, `hushjyuGtgk`
- フィールド名が不統一（`hushjyuZih` vs `chushjyuZih`）、どちらが正しいか要確認

### 変数タイポの継続発見（追加）
- bklist.html (www.chikusaku-mansion.com, 172行): `{{bkdata.stHrs41}}` → `{{bkdata.bkdata.stHrs41}}` に修正必要
- 他の箇所では `bkdata.bkdata.stHrs41` を使用しているため、不整合

### ime-mode の非標準CSS（追加箇所）
- articlebkdata.html (43行): `style="ime-mode: disabled;"`
- ブラウザサポート終了済み、削除またはHTML5 inputmode属性への変更検討
- 既存の懸念事項に追加箇所を記録

### Google Maps API の非推奨パラメータ（追加箇所）
- article.html (www.chikusaku-mansion.com, 9行): `sensor=false`
- article2.html (9行): 同様
- mypagebkdata.html (7行): 同様
- sensor パラメータは非推奨、最新APIバージョンへの移行検討

### 絶対パスの混在（追加詳細）
- bklist.html (www.chikusaku-mansion.com): `/article/img-waku/` で画像枠を参照
- 同ファイル内で `cmn_img/t01.jpg` のような相対パスも使用
- パス解決の不統一、相対パスへの統一変換が必要

### userpagebase.html の大規模メニュー実装
- userpagebase.html (www.chikusaku-m.com, 250行): 複雑なドロップダウンメニュー
- 外部ドメイン（https://www.chikusaku-m.com）への強い依存
- インラインイベントハンドラ（onmouseover, onmouseout）の多用
- 画像ロールオーバー処理: `document.images['menu01'].src='...'`

### article.html のマルチモード実装
- article.html (www.chikusaku-mansion.com, 567行): 3つの条件分岐でコンテンツ切り替え
- サンプル表示（270-331行）、公開表示（349-357行）、会員向け表示（361-369行）、ログイン画面（373-423行）
- 複雑な分岐構造、保守性の観点から分割を検討すべき

### jQuery バージョンの不統一（追加）
- mypagebkdata.html (9行): jQuery 1.6.1
- 既存の懸念事項に追加、統一バージョンへの移行検討

### onload属性によるプリロード実装
- userpagebase.html (www.chikusaku-m.com, 16行): `onload="preloadImages(...)"`
- bklist.html (www.chikusaku-mansion.com, 15行): 同様
- 古い手法だが、機能的には問題なし

### DOCTYPE の不統一（追加箇所）
- TEST.html (www.chikusaku-mansion.com): XHTML 1.0 Transitional
- article.html (www.chikusaku-mansion.com): DOCTYPE なし（継承元に依存）
- article2.html: DOCTYPE なし（継承元に依存）
- articlebkdata.html: HTML 4.01 Frameset（インクルードされるコンポーネント）
- bklist.html (www.chikusaku-mansion.com): HTML 4.01 Frameset
- mypageResign.html: DOCTYPE なし（継承元に依存）
- mypagebase.html: HTML 4.01 Frameset
- mypagebkdata.html: DOCTYPE なし（継承元に依存）
- userpagebase.html (www.chikusaku-m.com): HTML 4.01 Frameset
- sorry.html (www.chikusaku-m.com): DOCTYPE なし（継承元に依存）
- HTML5への統一を引き続き検討