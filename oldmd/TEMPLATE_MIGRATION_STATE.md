# テンプレートマイグレーション状態

## マイグレーション済みテンプレート

### ルート（管理画面系） - 35ファイル
- ATENA.html
- HAGAKI.html
- address2.html
- addresslist.html
- article.html
- bkdchk.html
- bkedit.html ✅ 第7回処理
- bkjoukyoulist.html
- bklistml.html
- bksearch.html ✅ 第7回処理
- bksearchmain.html
- duplicationcheck.html
- blobstoreutl.html
- follow.html
- followpagebase.html
- form.html
- index.html
- info.html
- ledger.html
- login.html
- mailinglist.html
- matching.html
- memberSearchandMail.html
- memberedit.html
- proc.html
- regist.html
- resign.html
- sendmsg.html
- show1.html
- tantochange.html
- upload.html
- upload2.html
- uploadadresslist.html
- uploadbkdata.html
- userpagebase.html

### s-style/hon - 3ファイル
- bklist.html
- bklistml.html
- article.html

### s-style/hon/backoffice - 9ファイル
- article.html
- articlem.html（変換不要）
- bklist.html
- bklistm.html（変換不要）
- bksearch.html ✅ 第7回処理
- follow.html ✅ 第7回処理
- followpagebase.html ✅ 第7回処理
- sorry.html ✅ 第7回処理
- userpagebase.html ✅ 第7回処理

### s-style/hon/ww2.s-style.ne.jp - 8ファイル
- article.html ✅ 第7回処理
- articlem.html ✅ 第7回処理
- bklist.html ✅ 第7回処理
- bklistm.html ✅ 第8回処理
- index.html ✅ 第8回処理
- pict.html ✅ 第8回処理
- sorry.html ✅ 第8回処理
- userpagebase.html ✅ 第8回処理

### s-style/hon/www.chikusaku-m.com - 4ファイル
- article.html ✅ 第8回処理
- bklist.html ✅ 第8回処理
- sorry.html ✅ 第8回処理
- userpagebase.html ✅ 第8回処理

### s-style/hon/www.chikusaku-mansion.com - 18ファイル (第9回・第10回処理)
- article.html ✅ 第9回処理
- article2.html ✅ 第9回処理
- articlebkdata.html ✅ 第9回処理
- bklist.html ✅ 第9回処理
- mypagebkdata.html ✅ 第9回処理
- mypagebklist.html ✅ 第9回処理
- mypagebklistfav.html ✅ 第9回処理
- mypagefollow.html ✅ 第9回処理
- mypagemydata.html ✅ 第9回処理
- mypagenewlist.html ✅ 第9回処理
- mypageResign.html ✅ 第10回処理
- mypagesearch.html ✅ 第10回処理
- mypagesearchlist.html ✅ 第10回処理
- mypagetop.html ✅ 第10回処理
- mypagebase.html ✅ 第10回処理
- sorry.html ✅ 第10回処理
- userpagebase.html ✅ 第10回処理
- userpagebase2.html ✅ 第10回処理


### s-style/hon/www.s-style.ne.jp - 19ファイル (第11回処理)
- article-koukai-sp.html ✅ 第11回処理
- article-koukai.html ✅ 第11回処理
- article-member-login-sp.html ✅ 第11回処理
- article-member-login.html ✅ 第11回処理
- article-member-sp.html ✅ 第11回処理
- article-member.html ✅ 第11回処理
- article-soldout-sp.html ✅ 第11回処理
- article-soldout.html ✅ 第11回処理
- article-sp.html ✅ 第11回処理
- article.html ✅ 第11回処理
- articlem.html ✅ 第11回処理
- bklist-sp.html ✅ 第11回処理
- bklist.html ✅ 第11回処理
- bklistm.html ✅ 第11回処理
- index.html ✅ 第11回処理
- pict.html ✅ 第11回処理
- sorry.html ✅ 第11回処理
- userpagebase-sp.html ✅ 第11回処理
- userpagebase.html ✅ 第11回処理


## マイグレーション未処理テンプレート

なし - 全てのテンプレートの処理が完了しました。

---

## 構造分析

### フォルダ構造と用途

```
src/templates/
├── [ルート] (38ファイル)
│   管理画面系のテンプレート
│   - 会員管理: memberedit.html, memberSearchandMail.html, regist.html, resign.html
│   - 物件管理: bkedit.html, bkdchk.html, bkjoukyoulist.html, bksearch.html, bksearchmain.html
│   - データ管理: upload.html, upload2.html, uploadbkdata.html, uploadadresslist.html
│   - 帳票出力: ATENA.html, HAGAKI.html, ledger.html
│   - その他: login.html, index.html, follow.html, matching.html
│
├── s-style/hon/ (6ファイル)
│   共通テンプレート
│   - article.html, bklist.html
│   - 開発用: articlemlxxx.html, bklistmlxxx.html
│
├── s-style/hon/backoffice/ (10ファイル)
│   バックオフィス管理画面
│   - 記事・物件管理: article.html, articlem.html, bklist.html, bklistm.html
│   - 検索・フォロー: bksearch.html, follow.html, followpagebase.html
│
├── s-style/hon/ww2.s-style.ne.jp/ (14ファイル)
│   サブドメイン用テンプレート
│   - 記事: article.html, articlem.html
│   - 物件リスト: bklist.html, bklistm.html
│   - ページ: index.html, pict.html, sorry.html, userpagebase.html
│   ※コピーファイル多数含む
│
├── s-style/hon/www.chikusaku-m.com/ (4ファイル)
│   チクサクモバイル用
│   - 基本: article.html, bklist.html, userpagebase.html, sorry.html
│
├── s-style/hon/www.chikusaku-mansion.com/ (19ファイル)
│   チクサクマンション用
│   - 記事: article.html, article2.html, articlebkdata.html
│   - 物件リスト: bklist.html
│   - マイページ: mypagebase.html, mypagetop.html, mypagemydata.html
│   - マイページ機能: mypagebklist.html, mypagebklistfav.html, mypagefollow.html
│   - 検索: mypagesearch.html, mypagesearchlist.html
│
└── s-style/hon/www.s-style.ne.jp/ (22ファイル)
    メインサイト用
    - PC版: article.html, bklist.html, userpagebase.html
    - SP版: article-sp.html, bklist-sp.html, userpagebase-sp.html
    - 会員向け: article-member.html, article-member-sp.html, article-member-login.html
    - 公開: article-koukai.html, article-koukai-sp.html
    - 売約済み: article-soldout.html, article-soldout-sp.html
    - その他: index.html, pict.html, sorry.html
```

### サマリー
- **総ファイル数**: 112個（article-member (1).html は不在のため除外）
- **調査済み**: 112ファイル（**100%完了！**）
  - ルート: 38ファイル
  - s-style/hon: 6ファイル
  - s-style/hon/backoffice: 10ファイル
  - s-style/hon/ww2.s-style.ne.jp: 14ファイル
  - s-style/hon/www.chikusaku-m.com: 4ファイル
  - s-style/hon/www.chikusaku-mansion.com: 21ファイル
  - s-style/hon/www.s-style.ne.jp: 22ファイル（うち1ファイルは不在）
- **未調査**: 0ファイル（**全調査完了！**）
- **フォルダ数**: 7個
- **主要カテゴリ**:
  - 管理画面系（ルート）- ✅ 調査完了
  - 共通テンプレート（s-style/hon）- ✅ 調査完了
  - バックオフィス（backoffice）- ✅ 調査完了（10/10ファイル）
  - フロントエンド（ドメイン別）- ✅ 調査完了（55/55ファイル）

### 特記事項
- コピーファイル（-copy、(1) 等）が複数存在
- xxx接尾辞のファイルは開発中またはテスト用と思われる
- SP（スマートフォン）版とPC版が分離されている
- 各ドメインごとに独立したテンプレートセットを保持
