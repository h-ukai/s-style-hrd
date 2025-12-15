# テンプレートマイグレーションログ

## [2025-11-23 16:24:45] 第1回処理

### ファイル名: ATENA.html

#### ルール外の改修事項
- なし

#### 懸念事項
- なし（シンプルな宛名印刷テンプレート）

#### 期待する変数データ形式
```python
{
    'memlist': [  # リスト
        {
            'zip': str,  # 郵便番号
            'address': str,  # 住所
            'name': str  # 氏名
        },
        ...
    ]
}
```

#### その他
- 絶対パス → 相対パス変換: `/css/atena.css` → `../css/atena.css`

---

### ファイル名: HAGAKI.html

#### ルール外の改修事項
- なし

#### 懸念事項
- なし（シンプルなハガキ印刷テンプレート）

#### 期待する変数データ形式
```python
{
    'memlist': [  # リスト
        {
            'zip': str,  # 郵便番号
            'address': str,  # 住所
            'name': str  # 氏名
        },
        ...
    ]
}
```

#### その他
- 絶対パス → 相対パス変換: `/css/hagaki.css` → `../css/hagaki.css`

---

### ファイル名: address2.html

#### ルール外の改修事項
- 161行目: IE専用コード `if(d.all) window.event.keyCode = 0` を削除

#### 懸念事項
- 106, 108行目: ime-mode の使用（非推奨CSS、ブラウザサポート終了済み）
  - `$(this).css("ime-mode", "active")` / `$(this).css("ime-mode", "inactive")`
  - 将来的にHTML5 inputmode属性への変更を検討すべき
- jQuery 1.6.0使用（古いバージョン）

#### 期待する変数データ形式
```python
{
    'memberID': str,
    'key': str,
    'page': str,
    'data': {
        'bbchntikbn': str,  # 売買賃貸区分
        'dtsyuri': str,  # 取扱い種類
        'bkknShbt': str,  # 物件種別
        'bkknShmk': str,  # 物件種目
        'tdufknmi': str,  # 都道府県名
        'address1': {
            'shzicmi1': str  # 所在地1
        },
        'ttmnmi': str,  # 建物名
        'ensn': {
            'ensenmei': str  # 沿線名
        },
        'thHnU': str,  # 徒歩（範囲上限）
        'thMU': str,  # 徒歩（範囲下限）
        'kutuHnU': str,  # 交通
        'tcMnsk2L': float,  # 土地面積下限
        'tcMnsk2U': float,  # 土地面積上限
        # ... その他、多数の検索条件フィールド
        'tanto': str  # 担当
    }
}
```

#### その他
- 多数の{% ifequal %}タグを{% if == %}に変換（約80箇所以上）
- 絶対パスは元々相対パスまたは外部CDN参照のため変更なし
- AJAXエンドポイント `https://s-style-hrd.appspot.com/jsonservice` は絶対パス維持（ルール通り）

---

### ファイル名: addresslist.html

#### ルール外の改修事項
- なし

#### 懸念事項
- jQuery 1.7.1使用（やや古いバージョン）
- form action属性が絶対パス `/addresslist.html`（Flask側で適切にルーティング処理が必要）

#### 期待する変数データ形式
```python
{
    'memberID': str,
    'modal': str,
    'key': str,  # リストID
    'division': str,  # 区分
    'listname': str,  # 地名一覧名
    'Message': str,  # メッセージ
    'data': {
        'tdufknmi': str,  # 都道府県名
        'address1': {
            'shzicmi1': str,  # 所在地1
            'shzicmi1id': str  # 所在地1 ID
        }
    }
}
```

#### その他
- 絶対パス → 相対パス変換:
  - `/css/baselayout.css` → `../css/baselayout.css`
  - `/css/ui-lightness/jquery-ui-1.8.16.custom.css` → `../css/ui-lightness/jquery-ui-1.8.16.custom.css`
  - `/js/jquery-1.7.1.min.js` → `../js/jquery-1.7.1.min.js`
  - `/js/jquery-ui-1.8.16.custom.min.js` → `../js/jquery-ui-1.8.16.custom.min.js`
  - `/js/jQueryMultiCheckbox.js` → `../js/jQueryMultiCheckbox.js`
  - `url('/img/ui-anim_basic_16x16.gif')` → `url('../img/ui-anim_basic_16x16.gif')`
- 多数の{% ifequal %}タグを{% if == %}に変換（都道府県選択肢、約47箇所）
- AJAXエンドポイント `https://s-style-hrd.appspot.com/jsonservice` は絶対パス維持（ルール通り）
- Google Analytics統合あり（UA-7545989-12）

---

## [2025-11-23] 第2回処理

### ファイル名: article.html

#### ルール外の改修事項
- なし

#### 懸念事項
- 136行目: Django特有の`{% regroup %}`タグを使用（Jinja2非互換）
  - サーバー側でグループ化処理が必要
- 141行目: Django特有の`{% ifchanged %}`タグを使用（Jinja2非互換）
  - サーバー側でロジック実装が必要
- Google Maps API使用時に非推奨パラメータ`sensor=false`を含む
- Galleriffic画像ギャラリープラグイン使用（jQuery 1.3.2ベース）

#### 期待する変数データ形式
```python
{
    'bkID': str,  # 物件ID
    'bkdata': {
        'ttmnmi': str,  # 建物名
        'tdufknmi': str,  # 都道府県名
        'shzicmi1': str,  # 所在地1
        'shzicmi2': str,  # 所在地2
        'kks': str,  # 価格
        'comments': str,  # コメント（複数行テキスト）
        # ... その他物件詳細フィールド
    },
    'kanren': [  # 関連物件リスト
        {
            'data_month': str,  # 月（グループ化キー）
            'bkID': str,
            'ttmnmi': str,
            'update_date': datetime
        },
        ...
    ],
    'latest_bkID': str,  # 最新の関連物件ID
    'images': [  # 画像リスト
        {
            'thumbnail': str,  # サムネイルURL
            'full': str,  # フルサイズURL
            'title': str,  # タイトル
            'description': str  # 説明
        },
        ...
    ]
}
```

#### その他
- jQuery `.live()` → `.on()`変換（136行目）
  - `$("a[rel='history']").live('click', ...)` → `$(document).on('click', "a[rel='history']", ...)`
- 絶対パスは外部CDN参照のため変更なし
- JSONP使用（クロスドメインAJAX: `https://s-style-hrd.appspot.com/jsonservice`）

---

### ファイル名: bkdchk.html

#### ルール外の改修事項
- 95, 102行目: `language="JavaScript"`属性を`type="text/javascript"`に変更

#### 懸念事項
- jQuery 1.4.2使用（古いバージョン）
- jTPS（テーブルページネーション）プラグイン使用
- form action属性が相対パス`bkdchk.html`（Flask側でルーティング設定が必要）

#### 期待する変数データ形式
```python
{
    'Message': str,  # メッセージ
    'memberID': str,  # 会員ID
    'bkdata_list': [  # 重複チェック結果リスト
        {
            'no': int,  # 番号
            'bkID': str,  # 物件ID
            'bbchntikbn': str,  # 売買賃貸区分
            'bkknShbt': str,  # 物件種別
            'bkknShmk': str,  # 物件種目
            'tdufknmi': str,  # 都道府県名
            'shzicmi1': str,  # 所在地1
            'shzicmi2': str,  # 所在地2
            'ttmnmi': str,  # 建物名
            'kks': str,  # 価格
            'tchbmnskm2': float,  # 土地面積
            'heya': str,  # 部屋番号
            'szkai': str,  # 所在階
            'senmnsk': float,  # 専有面積
            'mdri': str,  # 間取り
            'tanto': str,  # 担当
            'update_date': datetime,  # 更新日時
            'jyohogen': str,  # 情報源
            'kanri_count': int,  # 管理カウント
            'dupID': str,  # 重複ID
            'dupCount': int  # 重複数
        },
        ...
    ]
}
```

#### その他
- 絶対パス → 相対パス変換:
  - `/css/` → `../css/`
  - `/js/` → `../js/`
  - `/img/` → `../img/`
- jQuery `.live()` → `.on()`変換（95, 102行目）
- 約47個の`{% ifequal %}`タグを`{% if == %}`に変換（物件種別・種目判定）
- Google Analytics統合あり（UA-7545989-12）

---

### ファイル名: bkjoukyoulist.html

#### ルール外の改修事項
- 167, 174行目: `language="JavaScript"`属性を`type="text/javascript"`に変更

#### 懸念事項
- jQuery 1.4.2使用（古いバージョン）
- jTPS（テーブルページネーション）プラグイン使用
- form action属性が相対パス`bkjoukyoulist.html`（Flask側でルーティング設定が必要）

#### 期待する変数データ形式
```python
{
    'Message': str,  # メッセージ
    'memberID': str,  # 会員ID
    'bkdata_list': [  # 物件状況リスト
        {
            'no': int,  # 番号
            'bkID': str,  # 物件ID
            'bbchntikbn': str,  # 売買賃貸区分
            'bkknShbt': str,  # 物件種別
            'bkknShmk': str,  # 物件種目
            'tdufknmi': str,  # 都道府県名
            'shzicmi1': str,  # 所在地1
            'shzicmi2': str,  # 所在地2
            'ttmnmi': str,  # 建物名
            'kks': str,  # 価格
            'tchbmnskm2': float,  # 土地面積
            'tanto': str,  # 担当
            'bkjoukyou': str,  # 物件状況
            'update_date': datetime  # 更新日時
        },
        ...
    ]
}
```

#### その他
- 絶対パス → 相対パス変換:
  - `/css/` → `../css/`
  - `/js/` → `../js/`
  - `/img/` → `../img/`
- jQuery `.live()` → `.on()`変換（167, 174行目）
- Google Analytics統合あり（UA-7545989-12）

---

### ファイル名: bklistml.html

#### ルール外の改修事項
- 変数参照の修正（タイポ修正）:
  - `bbkdata.kdata.bsRsnmi1` → `bkdata.bkdata.bsRsnmi1`
  - `bkdat.bkdata.ekmi2` → `bkdata.bkdata.ekmi2`
  - `bkdata.bkdata.bkdata.ekmi1` → `bkdata.bkdata.ekmi1`
  - その他、不整合な変数参照を`bkdata.bkdata.*`パターンに統一

#### 懸念事項
- メール送信用テンプレート（HTMLメール）
- 外部画像URL使用（Blobstore API: `/blobimage/...`）
- Flaskでのメール送信実装が必要

#### 期待する変数データ形式
```python
{
    'bkdata': {
        'bkdata': {  # ネストした構造
            'ttmnmi': str,  # 建物名
            'tdufknmi': str,  # 都道府県名
            'shzicmi1': str,  # 所在地1
            'shzicmi2': str,  # 所在地2
            'kks': str,  # 価格
            'tchbmnskm2': float,  # 土地面積
            'senmnsk': float,  # 専有面積
            'mdri': str,  # 間取り
            'thM21': str,  # 交通1
            'thM22': str,  # 交通2
            'thM23': str,  # 交通3
            'ekmi1': str,  # 駅名1
            'ekmi2': str,  # 駅名2
            'ekmi3': str,  # 駅名3
            'bsRsnmi1': str,  # バス路線名1
            'bsRsnmi2': str,  # バス路線名2
            'bsRsnmi3': str,  # バス路線名3
            'thHnU': str,  # 徒歩範囲上限
            'thHnL': str,  # 徒歩範囲下限
            # ... その他物件詳細フィールド
        }
    },
    'bkID': str,  # 物件ID
    'Thumbnail1': str  # サムネイル画像URL
}
```

#### その他
- 絶対パスは外部URL（Blobstore）のため変更なし
- シンプルなHTMLメールレイアウト（テーブルベース）

---

### ファイル名: bksearchmain.html

#### ルール外の改修事項
- なし

#### 懸念事項
- 静的モックアップファイル（動作しないフォーム）
- すべてのselect要素がダミーデータ（"first", "second", "third"）
- 実際の実装では動的生成が必要

#### 期待する変数データ形式
```python
# このファイルは静的モックアップのため、変数は使用されていない
# 実装時には以下のようなデータが必要になると想定:
{
    'prefectures': list,  # 都道府県リスト
    'property_types': list,  # 物件種別リスト
    'property_categories': list,  # 物件種目リスト
    'areas': list,  # エリアリスト
    'railway_lines': list,  # 沿線リスト
    'stations': list,  # 駅リスト
    # ... その他検索条件の選択肢
}
```

#### その他
- 絶対パス → 相対パス変換:
  - `css/styles.css` → `../css/styles.css`
- XHTML 1.0 Transitional使用
- 古い属性使用（leftmargin, marginheight, marginwidth, topmargin）

---

### ファイル名: duplicationcheck.html

#### ルール外の改修事項
- 9行目: 全角数字「２」を半角「2」に変更

#### 懸念事項
- METAタグによる自動リフレッシュ（10秒ごと）
- 負荷軽減のためのバッチ処理実装（サーバー側で対応が必要）

#### 期待する変数データ形式
```python
{
    'limit': int,  # 1回の処理件数
    'count': int,  # 残り処理件数
    'result': [  # 処理結果メッセージリスト
        str,
        str,
        ...
    ],
    'error_msg': str  # エラーメッセージ
}
```

#### その他
- 絶対パス → 相対パス変換:
  - `/duplicationcheck/bkdata.html` → `../duplicationcheck/bkdata.html`
- 重複チェックルール説明:
  - 物件番号が同じなら重複
  - 土地系物件: 所在地2一致 + 土地面積一致
  - マンション系物件: 所在地2一致 + (所在階+部屋番号 または 所在階+間取り+専有面積)

---

### ファイル名: blobstoreutl.html

#### ルール外の改修事項
- なし

#### 懸念事項
- GAE Blobstore API依存（`/blobimage/...`, `/multiupload`）
  - Flaskでは別のストレージ実装が必要（Cloud Storage等）
- Colorboxプラグイン使用（モーダル表示）
- jQuery 1.10.2使用

#### 期待する変数データ形式
```python
{
    'bkID': str,  # 物件ID
    'blobs': [  # メディアタイプ別グループ
        {
            'media': str,  # メディアタイプ
            'cblob': [  # 画像リスト
                {
                    'blobNo': str,  # Blob番号
                    'title': str,  # タイトル
                    'content': str,  # 説明
                    'media': str,  # メディアタイプ
                    'pos': int,  # 表示位置
                    'html': str,  # HTMLタグ（safe出力）
                    'bloburl': str,  # Blob URL
                    'thumbnailurl': str,  # サムネイルURL
                    'filename': str,  # ファイル名
                    'blobKey': str  # BlobキーGAE固有）
                },
                ...
            ]
        },
        ...
    ],
    'samples': [  # 参照画像リスト（他物件から選択）
        {
            'bkID': str,
            'ttmnmi': str,  # 建物名
            'title': str,
            'content': str,
            'media': str,
            'pos': int,
            'html': str,
            'bloburl': str,
            'thumbnailurl': str,
            'filename': str,
            'blobKey': str
        },
        ...
    ],
    'edit_url': str,  # 編集URL
    'multiupload_url': str  # 複数アップロードURL
}
```

#### その他
- 絶対パス → 相対パス変換:
  - `/css/main.css` → `../css/main.css`
  - `/img/favicon.ico` → `../img/favicon.ico`
  - `/js/` → `../js/`
  - `/bkedit.html` → `../bkedit.html`
- Colorbox設定でonClosedイベントでページリロード
- retina対応画像表示機能

---

### ファイル名: follow.html

#### ルール外の改修事項
- なし

#### 懸念事項
- `followpagebase.html`を継承（このファイルも処理が必要）
- 複雑なモーダル入力機能（顧客フォロー管理）
- jQuery 1.6.0使用（古いバージョン）
- `ime-mode` CSS使用（非推奨、ブラウザサポート終了済み）
  - 将来的にHTML5 inputmode属性への変更を検討すべき

#### 期待する変数データ形式
```python
{
    'memberID': str,  # 会員ID
    'key': str,  # キー
    'followlist': [  # フォローリスト
        {
            'followID': str,  # フォローID
            'kokyakuID': str,  # 顧客ID
            'name': str,  # 氏名
            'tel': str,  # 電話番号
            'email': str,  # メールアドレス
            'tanto': str,  # 担当
            'followbi': datetime,  # フォロー日
            'follownaiyou': str,  # フォロー内容
            'mflag0': bool,  # 方法フラグ（来店）
            'mflag1': bool,  # 方法フラグ（電話）
            'mflag2': bool,  # 方法フラグ（メール）
            'mflag3': bool,  # 方法フラグ（郵送）
            'mflag4': bool,  # 方法フラグ（FAX）
            'mflag5': bool,  # 方法フラグ（その他）
            # ... その他フィールド
        },
        ...
    ]
}
```

#### その他
- 絶対パス → 相対パス変換:
  - `/img/` → `../img/`
- jQuery `.live()`は使用されておらず、適切な`.on()`イベントデリゲーション使用
- フォロー方法フラグ（来店、電話、メール、郵送、FAX、その他）のアイコン表示機能
- モーダル内で入力検証とデータ送信を行う複雑なUI

---

## [2025-11-23] 第3回処理

### ファイル名: followpagebase.html

#### ルール外の改修事項
- 12, 17行目: `language="JavaScript"`属性を削除

#### 懸念事項
- `follow.html`によって継承される基底テンプレート
- jQuery 1.11.1使用（やや古いバージョン）
- jQuery UI 1.10.4使用
- オートコンプリート機能（顧客検索: ID、名前、電話、メール）
- JSONP使用（クロスドメインAJAX）

#### 期待する変数データ形式
```python
{
    'Domain': str,  # ドメイン名
    'memberID': str,  # 会員ID
    'userID': str,  # ユーザーID（担当者ID）
    'userkey': str,  # ユーザーキー
    'key': str,  # キー
    'page': str,  # ページ
    'CorpOrg_key_name': str,  # 法人組織キー名
    'Branch_Key_name': str,  # 支店キー名
    'name': str,  # 名前
    'sitename': str,  # サイト名
    'pagepath': str,  # ページパス
    'membername': str,  # 会員名
    'memberyomi': str,  # 会員読み仮名
    'membertel': str,  # 会員電話
    'membermail': str  # 会員メール
}
```

#### その他
- 絶対パス → 相対パス変換:
  - `/css/` → `../css/`
  - `/js/` → `../js/`
  - `/img/` → `../img/`
  - `/login.html` → `../login.html`
  - `/bkedit.html` → `../bkedit.html`
  - その他メニュー内の全パス
- オートコンプリート: 会員ID、名前、電話番号、メールアドレスで検索可能
- カレンダー機能とフォローリスト機能のためのJavaScript関数定義
- テンプレートブロック: `{% block addheder %}`, `{% block script %}`, `{% block inready %}`, `{% block function %}`, `{% block inlinecss %}`, `{% block titile %}`, `{% block titile2 %}`, `{% block maincontents %}`

---

### ファイル名: form.html

#### ルール外の改修事項
- なし

#### 懸念事項
- `applicationpagebase`テンプレートを継承（このベーステンプレートも処理が必要）
- iframeを使用したセッション管理（GAE固有の実装）

#### 期待する変数データ形式
```python
{
    'corp_name': str,  # 法人名
    'sitename': str,  # サイト名
    'branch_name': str,  # 支店名
    'togo': str,  # 遷移先
    'mail': str,  # メール
    'ref': str,  # 参照元
    'userpagebase': str,  # ユーザーページベース
    'error_msg': str,  # エラーメッセージ
    'completed_msg': str,  # 完了メッセージ
    'lastname': str,  # 姓
    'fastname': str,  # 名（typo: fastnameは本来firstnameであるべき）
    'yomi1': str,  # 読み仮名（姓）
    'yomi2': str,  # 読み仮名（名）
    'zip1': str,  # 郵便番号（前半3桁）
    'zip2': str,  # 郵便番号（後半4桁）
    'ken': str,  # 都道府県
    'address1': str,  # 市区町村
    'address2': str,  # 町字丁目
    'address3': str,  # 番地、マンション名
    'phone': str,  # 電話番号
    'reqnum': str,  # 問い合わせ物件番号
    'reqtext': str,  # 問い合わせ内容
    'sid': str,  # セッションID
    'onloadsclipt': str  # onloadスクリプト（typo: onloadscriptであるべき）
}
```

#### その他
- 47個の`{% ifequal %}`タグを`{% if == %}`に変換（都道府県選択肢）
- 絶対パスは使用されていない（外部URLのみ）
- 顧客情報入力フォーム（氏名、住所、電話番号、問い合わせ内容）

---

### ファイル名: index.html

#### ルール外の改修事項
- なし

#### 懸念事項
- フロントページ（トップページ）テンプレート
- GAE App Spotアプリケーションへの直接リンク含む
- 外部サイト（www.chikusaku-mansion.com）への画像・リンク依存
- 静的な会社情報がハードコーディング

#### 期待する変数データ形式
```python
{
    'data': {
        'bkdatauri': str,  # 物件データURI（売買用）
        'bkdatauri2': str  # 物件データURI（賃貸・会員用）
    },
    'tochi': list,  # 土地物件リスト
    'shinchiku': list,  # 新築戸建リスト
    'tyuukoko': list,  # 中古戸建リスト
    'chukoman': list,  # 中古マンションリスト
    'syueki': list,  # 収益物件リスト
    'tintai': list,  # 賃貸物件リスト
    'mansion': list,  # マンション物件リスト（会員向け）
    # 各物件リストアイテムの構造:
    {
        'kakakuM': float,  # 価格（万円）
        'bkdata': {
            'bkID': str,  # 物件ID
            'ttmnmi': str,  # 建物名
            'kkkybku': list,  # 広告区分（複数選択）
            'kkkksyk': bool,  # 価格相談可
            'ensnmi1': str,  # 沿線名1
            'ekmi1': str,  # 駅名1
            'thHn11': str,  # 徒歩1（分）
            'ensnmi2': str,  # 沿線名2
            'ekmi2': str,  # 駅名2
            'thHn12': str,  # 徒歩2（分）
            'ensnmi3': str,  # 沿線名3
            'ekmi3': str,  # 駅名3
            'thHn13': str,  # 徒歩3（分）
            'snyuMnskSyuBbnMnsk2': float,  # 専有面積
            'blcnyTrsMnsk': float,  # バルコニー（テラス）面積
            'tcMcbnSumnsk': float,  # 土地共有面積
            'mdrHysu1': int,  # 間取り部屋数
            'mdrTyp1': str,  # 間取りタイプ
            'kukkTnsiKbn': str  # 広告転載区分（会員向け）
        }
    }
}
```

#### その他
- 絶対パス → 相対パス変換:
  - `css/topstyles.css` → `../css/topstyles.css`
  - `/img/` → `../img/`
- 1個の`{% ifequal %}`タグを`{% if == %}`に変換（563行目: 広告可判定）
- 物件カテゴリー別表示: 土地、新築戸建、中古戸建、中古マンション、収益物件、賃貸、マンション（会員向け）
- レスポンシブデザインなし（固定幅900px想定）

---

### ファイル名: info.html

#### ルール外の改修事項
- なし

#### 懸念事項
- GAE Blobstore API依存（file_info.blob, file_info.key.id）
- Flaskでは別のファイル管理実装が必要

#### 期待する変数データ形式
```python
{
    'file_info': {
        'blob': {
            'filename': str,  # ファイル名
            'size': int,  # サイズ（バイト）
            'content_type': str  # コンテンツタイプ
        },
        'uploaded_at': datetime,  # アップロード日時
        'uploaded_by': str,  # アップロード者
        'key': {
            'id': str  # ファイルキー（GAE固有）
        }
    }
}
```

#### その他
- 絶対パス → 相対パス変換:
  - `/file/` → `../file/`
- シンプルなファイル情報表示テンプレート
- ダウンロードリンク機能

---

### ファイル名: ledger.html

#### ルール外の改修事項
- なし

#### 懸念事項
- 静的モックアップファイル（動作しないフォーム）
- ダミーデータ（"00000000"、"aa業者"、"first/second/third"等）
- 実際の実装では動的生成が必要
- jQuery 1.6.0使用（古いバージョン）

#### 期待する変数データ形式
```python
# このファイルは静的モックアップのため、変数は最小限
# 実装時には以下のようなデータが必要になると想定:
{
    'memberID': str,  # 会員ID
    'key': str,  # キー
    'page': str,  # ページ
    # 実装時に追加される顧客台帳データ:
    'customer_data': {
        'status': str,  # 区分（顧客、業者、建築業者等）
        'tourokunengappi': date,  # 登録年月日
        'tanto': str,  # 担当
        'sitename': str,  # サイト名
        'uri': bool,  # 売
        'kai': bool,  # 買
        'kashi': bool,  # 貸
        'kari': bool,  # 借
        'baikai': str,  # 媒介種類
        'seiyaku': str,  # 成約状況
        'seiyakunengappi': date,  # 成約年月日
        'name': str,  # 氏名
        'yomi': str,  # 読み仮名
        'age': int,  # 年齢
        'zip': str,  # 郵便番号
        'address': str,  # 住所
        'phone': str,  # 電話番号
        'fax': str,  # FAX番号
        'mobilephone': str,  # 携帯番号
        'mail': str,  # メール
        'rank': str,  # ランク（A-Z）
        # ... その他多数のフィールド
    }
}
```

#### その他
- 絶対パス → 相対パス変換:
  - `css/baselayout.css` → `../css/baselayout.css`
  - `../js/` はすでに相対パスのため変更なし
- 顧客台帳入力フォームのモックアップ
- メニュー選択肢は静的（実装時に動的生成が必要）

---

## [2025-11-27] 第4回処理

### ファイル名: login.html

#### ルール外の改修事項
- なし

#### 懸念事項
- `applicationpagebase.html`を継承（このベーステンプレートも処理が必要）
- シンプルなログインフォーム

#### 期待する変数データ形式
```python
{
    'corp_name': str,  # 法人名
    'branch_name': str,  # 支店名
    'sitename': str,  # サイト名
    'togo': str,  # 遷移先
    'error_msg': str,  # エラーメッセージ
    'loginurl': str,  # ログインURL
    'return_top': str  # トップページへ戻るリンクテキスト
}
```

#### その他
- テンプレート継承: `{% extends applicationpagebase %}` → `{% extends "applicationpagebase.html" %}`
- コメント構文: `{% comment %}...{% endcomment %}` → `{# ... #}`
- シンプルなログインフォーム（ID/パスワード）

---

### ファイル名: mailinglist.html

#### ルール外の改修事項
- なし

#### 懸念事項
- jQuery 1.4.2使用（古いバージョン）
- jTPS（テーブルページネーション）プラグイン使用

#### 期待する変数データ形式
```python
{
    'Message': str,  # メッセージ
    'memberID': str,  # 会員ID
    'mailinglist': [  # メーリングリスト
        {
            'no': int,  # 番号
            'kokyakuID': str,  # 顧客ID
            'name': str,  # 氏名
            'address': str,  # 住所
            'tel': str,  # 電話番号
            'mail': str,  # メールアドレス
            'tanto': str,  # 担当
            'listID': str  # リストID
        },
        ...
    ]
}
```

#### その他
- jQuery `.live()` → `.on()`変換（3箇所）:
  - `$('#tbl tbody tr:not(.stubCell)').live('mouseover', ...)` → `$(document).on('mouseover', '#tbl tbody tr:not(.stubCell)', ...)`
  - `$('#tbl tbody tr:not(.stubCell)').live('mouseout', ...)` → `$(document).on('mouseout', '#tbl tbody tr:not(.stubCell)', ...)`
  - `$('#tbl tbody tr:not(.stubCell)').live('click', ...)` → `$(document).on('click', '#tbl tbody tr:not(.stubCell)', ...)`
- 絶対パスは外部CDN参照のため変更なし

---

### ファイル名: matching.html

#### ルール外の改修事項
- なし

#### 懸念事項
- jQuery 1.6.0使用（古いバージョン）
- 静的モックアップファイル（動作しないフォーム）
- 実際の実装では動的生成が必要

#### 期待する変数データ形式
```python
{
    'memberID': str,  # 会員ID
    'key': str,  # キー
    'page': str,  # ページ
    'param': {
        'service': str,  # サービス種別（売買/賃貸）
    }
}
```

#### その他
- 絶対パス → 相対パス変換:
  - `/css/baselayout.css` → `../css/baselayout.css`
- `{% ifequal %}` → `{% if == %}`変換（2箇所）
- マッチング検索条件入力フォームのモックアップ

---

### ファイル名: memberSearchandMail.html

#### ルール外の改修事項
- なし

#### 懸念事項
- jQuery 1.6.0使用（古いバージョン）
- `{% url %}` Djangoタグ使用（Jinja2では `url_for()` への変更が必要）
- 複雑な会員検索とメール送信機能

#### 期待する変数データ形式
```python
{
    'memberID': str,  # 会員ID
    'key': str,  # キー
    'page': str,  # ページ
    'data': {
        'tdufknmi': str,  # 都道府県名
        # ... その他検索条件
    },
    'searchresult': [  # 検索結果リスト
        {
            'kokyakuID': str,  # 顧客ID
            'name': str,  # 氏名
            'tel': str,  # 電話番号
            'mail': str,  # メールアドレス
            'address': str,  # 住所
            'tanto': str  # 担当
        },
        ...
    ]
}
```

#### その他
- 絶対パス → 相対パス変換:
  - `/css/styles.css` → `../css/styles.css`
  - `/js/` → `../js/`
- `{% ifequal %}` → `{% if == %}`変換（47箇所、都道府県選択肢）
- jQuery `.live()` → `.on()`変換
- `{% url %}` タグは今回は保留（Flask移行時に `url_for()` へ変更が必要）

---

### ファイル名: proc.html

#### ルール外の改修事項
- なし

#### 懸念事項
- `applicationpagebase.html`を継承
- GAE固有のタスクキュー処理用テンプレート

#### 期待する変数データ形式
```python
{
    'corp_name': str,  # 法人名
    'sitename': str,  # サイト名
    'branch_name': str,  # 支店名
    'togo': str,  # 遷移先
    'completed_msg': str,  # 完了メッセージ
    'return_top': str  # トップページへ戻るリンクテキスト
}
```

#### その他
- テンプレート継承: `{% extends applicationpagebase %}` → `{% extends "applicationpagebase.html" %}`
- コメント構文: `{% comment %}...{% endcomment %}` → `{# ... #}`
- シンプルな処理完了表示テンプレート

---

### ファイル名: memberedit.html

#### ルール外の改修事項
- なし

#### 懸念事項
- 非常に大きなファイル（1500行超）
- 多数の入力フォームフィールド
- jQuery 1.6.0使用（古いバージョン）
- `ime-mode` CSS使用（非推奨、ブラウザサポート終了済み）
  - 将来的にHTML5 inputmode属性への変更を検討すべき
- IE専用コード含む（`if(d.all) window.event.keyCode = 0`）

#### 期待する変数データ形式
```python
{
    'memberID': str,  # 会員ID
    'key': str,  # キー
    'page': str,  # ページ
    'data': {
        'status': str,  # 会員ステータス
        'kokyakuID': str,  # 顧客ID
        'name': str,  # 氏名
        'yomi': str,  # 読み仮名
        'zip': str,  # 郵便番号
        'tdufknmi': str,  # 都道府県名
        'address1': str,  # 市区町村
        'address2': str,  # 町字丁目
        'address3': str,  # 番地・建物名
        'tel': str,  # 電話番号
        'mail': str,  # メールアドレス
        'bbchntikbn': str,  # 売買賃貸区分
        'bkknShbt': str,  # 物件種別
        'bkknShmk': str,  # 物件種目
        # ... その他多数のフィールド（100以上）
    }
}
```

#### その他
- 絶対パス → 相対パス変換:
  - `/css/styles.css` → `../css/styles.css`
  - `/js/` → `../js/`
- `{% ifequal %}` → `{% if == %}`変換（大量、Pythonスクリプトで一括変換）
- 会員情報編集用の大規模フォーム
- オートコンプリート、日付ピッカー、住所検索などの機能含む

---

### ファイル名: regist.html

#### ルール外の改修事項
- なし

#### 懸念事項
- `applicationpagebase.html`を継承
- Google reCAPTCHA v3実装
- 会員登録フォーム

#### 期待する変数データ形式
```python
{
    'corp_name': str,  # 法人名
    'sitename': str,  # サイト名
    'branch_name': str,  # 支店名
    'togo': str,  # 遷移先
    'mail': str,  # メール
    'ref': str,  # 参照元
    'userpagebase': str,  # ユーザーページベース
    'error_msg': str,  # エラーメッセージ
    'completed_msg': str,  # 完了メッセージ
    'lastname': str,  # 姓
    'fastname': str,  # 名
    'yomi1': str,  # 読み仮名（姓）
    'yomi2': str,  # 読み仮名（名）
    'zip1': str,  # 郵便番号（前半）
    'zip2': str,  # 郵便番号（後半）
    'ken': str,  # 都道府県
    'address1': str,  # 市区町村
    'address2': str,  # 町字丁目
    'address3': str,  # 番地・建物名
    'phone': str,  # 電話番号
    'reqnum': str,  # 問い合わせ物件番号
    'reqtext': str,  # 問い合わせ内容
    'sid': str,  # セッションID
    'return_top': str  # トップページへ戻るリンクテキスト
}
```

#### その他
- テンプレート継承: `{% extends applicationpagebase %}` → `{% extends "applicationpagebase.html" %}`
- コメント構文: `{% comment %}...{% endcomment %}` → `{# ... #}`
- reCAPTCHA v3実装（サイトキー: 6LezIaQUAAAAAEZp9GoZ9SfYr4LuEE0V04KjAaW6）
- 会員登録フォーム（氏名、住所、電話番号、問い合わせ内容）

---

### ファイル名: resign.html

#### ルール外の改修事項
- なし

#### 懸念事項
- `applicationpagebase.html`を継承
- 会員退会フォーム

#### 期待する変数データ形式
```python
{
    'corp_name': str,  # 法人名
    'sitename': str,  # サイト名
    'branch_name': str,  # 支店名
    'togo': str,  # 遷移先
    'error_msg': str,  # エラーメッセージ
    'completed_msg': str,  # 完了メッセージ
    'mail': str,  # メール
    'reason': str,  # 退会理由
    'sid': str,  # セッションID
    'userpagebase': str,  # ユーザーページベース
    'ref': str,  # 参照元
    'return_top': str  # トップページへ戻るリンクテキスト
}
```

#### その他
- テンプレート継承: `{% extends applicationpagebase %}` → `{% extends "applicationpagebase.html" %}`
- コメント構文: `{% comment %}...{% endcomment %}` → `{# ... #}`
- 退会理由入力フォーム

---

### ファイル名: sendmsg.html

#### ルール外の改修事項
- なし

#### 懸念事項
- `applicationpagebase.html`を継承
- メッセージ送信フォーム

#### 期待する変数データ形式
```python
{
    'corp_name': str,  # 法人名
    'sitename': str,  # サイト名
    'branch_name': str,  # 支店名
    'togo': str,  # 遷移先
    'error_msg': str,  # エラーメッセージ
    'completed_msg': str,  # 完了メッセージ
    'reqnum': str,  # 問い合わせ物件番号
    'reqtext': str,  # 問い合わせ内容
    'sid': str,  # セッションID
    'userpagebase': str,  # ユーザーページベース
    'ref': str,  # 参照元
    'return_top': str  # トップページへ戻るリンクテキスト
}
```

#### その他
- テンプレート継承: `{% extends applicationpagebase %}` → `{% extends "applicationpagebase.html" %}`
- コメント構文: `{% comment %}...{% endcomment %}` → `{# ... #}`
- 問い合わせメッセージ送信フォーム

---

### ファイル名: show1.html

#### ルール外の改修事項
- なし

#### 懸念事項
- Django特有の`{% regroup %}`タグを使用（Jinja2非互換）
  - サーバー側でグループ化処理が必要
- Django特有の`{% ifchanged %}`タグを使用（Jinja2非互換）
  - サーバー側でロジック実装が必要
- Google Maps API使用
- Galleriffic画像ギャラリープラグイン使用

#### 期待する変数データ形式
```python
{
    'bkID': str,  # 物件ID
    'bkdata': {
        'ttmnmi': str,  # 建物名
        'tdufknmi': str,  # 都道府県名
        'shzicmi1': str,  # 所在地1
        'shzicmi2': str,  # 所在地2
        'kks': str,  # 価格
        'comments': str,  # コメント
        # ... その他物件詳細フィールド
    },
    'kanren': [  # 関連物件リスト（要グループ化）
        {
            'data_month': str,  # 月（グループ化キー）
            'bkID': str,
            'ttmnmi': str,
            'update_date': datetime
        },
        ...
    ],
    'latest_bkID': str,  # 最新の関連物件ID
    'images': [  # 画像リスト
        {
            'thumbnail': str,  # サムネイルURL
            'full': str,  # フルサイズURL
            'title': str,
            'description': str
        },
        ...
    ]
}
```

#### その他
- jQuery `.live()` → `.on()`変換:
  - `$("a[rel='history']").live('click', ...)` → `$(document).on('click', "a[rel='history']", ...)`
- `{% regroup %}` と `{% ifchanged %}` はJinja2非互換（サーバー側で事前処理が必要）
- JSONP使用（クロスドメインAJAX）

---

## [2025-11-27] 第5回処理

### ファイル名: tantochange.html

#### ルール外の改修事項
- なし

#### 懸念事項
- `manage/base.html`を継承（このベーステンプレートも処理が必要）
- 担当者変更機能（管理画面）

#### 期待する変数データ形式
```python
{
    'csrf_token': str,  # CSRFトークン
    'userlist': [  # ユーザーリスト
        {
            'uid': str,  # ユーザーID
            'nik': str  # ニックネーム
        },
        ...
    ],
    'result': str  # 処理結果メッセージ
}
```

#### その他
- テンプレート継承: `{% extends "manage/base.html" %}`
- CSRFトークンを条件付きで追加

---

### ファイル名: upload.html

#### ルール外の改修事項
- なし

#### 懸念事項
- CSVファイルアップロード機能
- Shift-JIS形式のファイルを前提

#### 期待する変数データ形式
```python
{
    'csrf_token': str,  # CSRFトークン
    'result': [str],  # 処理結果メッセージリスト
    'error_msg': str,  # エラーメッセージ
    'source': str  # インポート元
}
```

#### その他
- スタンドアロンテンプレート（継承なし）
- シンプルなファイルアップロードフォーム

---

### ファイル名: upload2.html

#### ルール外の改修事項
- なし

#### 懸念事項
- upload.htmlとほぼ同じ機能
- 説明文がない簡略版

#### 期待する変数データ形式
```python
{
    'csrf_token': str,  # CSRFトークン
    'result': [str],  # 処理結果メッセージリスト
    'error_msg': str,  # エラーメッセージ
    'source': str  # インポート元
}
```

#### その他
- スタンドアロンテンプレート（継承なし）

---

### ファイル名: uploadadresslist.html

#### ルール外の改修事項
- なし

#### 懸念事項
- 住所リストCSVアップロード用
- Shift-JIS形式のファイルを前提

#### 期待する変数データ形式
```python
{
    'csrf_token': str,  # CSRFトークン
    'result': [str],  # 処理結果メッセージリスト
    'error_msg': str,  # エラーメッセージ
    'source': str  # インポート元
}
```

#### その他
- スタンドアロンテンプレート（継承なし）

---

### ファイル名: uploadbkdata.html

#### ルール外の改修事項
- なし

#### 懸念事項
- 物件データCSVアップロード用
- 重複チェック機能へのリンクあり

#### 期待する変数データ形式
```python
{
    'csrf_token': str,  # CSRFトークン
    'result': [str],  # 処理結果メッセージリスト
    'error_msg': str,  # エラーメッセージ
    'source': str  # インポート元
}
```

#### その他
- スタンドアロンテンプレート（継承なし）
- 重複チェックページへのリンク: `../duplicationcheck/bkdata.html`

---

### ファイル名: userpagebase.html（ルート）

#### ルール外の改修事項
- なし

#### 懸念事項
- ユーザー向けページの基底テンプレート
- 古いHTMLスタイル（テーブルレイアウト）

#### 期待する変数データ形式
```python
# ブロック変数のみ（継承先で定義）
# {% block title %} - ページタイトル
# {% block content %} - メインコンテンツ
```

#### その他
- 基底テンプレート（継承される側）
- 静的ヘッダー・フッター
- 会社情報ハードコーディング

---

### ファイル名: s-style/hon/bklist.html

#### ルール外の改修事項
- 元ファイルの変数参照にタイポあり（修正済み）:
  - `bkdata.stHrs41` → `bkdata.bkdata.stHrs41`
  - `bkdata.thM21` → `bkdata.bkdata.thM21`
  - `bbkdata.kdata.bsRsnmi1` → `bkdata.bkdata.bsRsnmi1`
  - `bkdata.bstiMishu1` → `bkdata.bkdata.bstiMishu1`
  - `bkdata.tihM1` → `bkdata.bkdata.tihM1`
  - `bkdata.bkdat.ekmi2` → `bkdata.bkdata.ekmi2`

#### 懸念事項
- 大規模ファイル（421行）
- 物件一覧表示用
- 複雑な条件分岐（物件種別、アイコン表示）

#### 期待する変数データ形式
```python
{
    'data': {
        'listKey': str,  # リストキー（カテゴリ名）
        'offsetpre': str,  # 前のページURL
        'offsetnext': str,  # 次のページURL
        'bkdataurl': str,  # 物件詳細ベースURL
        'bkdatalist': [  # 物件リスト
            {
                'kakakuM': float,  # 価格（万円）
                'bkdata': {
                    'bkID': str,  # 物件ID
                    'ttmnmi': str,  # 建物名
                    'tdufknmi': str,  # 都道府県名
                    'shzicmi1': str,  # 所在地1
                    'shzicmi2': str,  # 所在地2
                    'ekmi1': str,  # 駅名1
                    'ekmi2': str,  # 駅名2
                    'ekmi3': str,  # 駅名3
                    'mdrHysu1': float,  # 間取り部屋数
                    'mdrTyp1': str,  # 間取りタイプ
                    'bbchntikbn': str,  # 売買賃貸区分
                    'dtsyuri': str,  # 取扱種類
                    'bkknShmk': str,  # 物件種目
                    'icons': [str],  # アイコンリスト
                    # ... その他多数
                },
                'picdata': [  # 画像リスト
                    {'bloburl': str}
                ]
            },
            ...
        ]
    }
}
```

#### その他
- `{% ifequal %}` → `{% if == %}` 変換（全て）
- `floatformat` → `float` フィルター変換
- 配列アクセス: `bkdata.picdata.0.bloburl` → `bkdata.picdata[0].bloburl`
- Google Analytics統合あり

---

### ファイル名: s-style/hon/bklistml.html

#### ルール外の改修事項
- 元ファイルの変数参照にタイポあり（修正済み）:
  - `bbkdata.kdata.bsRsnmi1` → `bkdata.bkdata.bsRsnmi1`
  - `bkdata.bkdat.bkdata.ekmi2` → `bkdata.bkdata.ekmi2`
  - `bkdata.bkvdata.ekmi2` → `bkdata.bkdata.ekmi2`
  - その他ネスト構造の不整合を修正

#### 懸念事項
- HTMLメールテンプレート
- Flaskでのメール送信実装が必要

#### 期待する変数データ形式
```python
{
    'subject': str,  # メール件名
    'body': str,  # メール本文（HTML safe）
    'data': {
        'bkdatalist': [  # 物件リスト
            {
                'kakakuM': float,  # 価格（万円）
                'bkdata': {
                    'bkID': str,  # 物件ID
                    'ttmnmi': str,  # 建物名
                    'tdufknmi': str,  # 都道府県名
                    'shzicmi1': str,  # 所在地1
                    'shzicmi2': str,  # 所在地2
                    'kkkksyk': bool,  # 価格応談フラグ
                    # ... その他
                },
                'picdata': [  # 画像リスト
                    {'bloburl': str}
                ]
            },
            ...
        ],
        'bkdataurl': str  # 物件詳細ベースURL
    }
}
```

#### その他
- `linebreaks` フィルターは削除（Jinja2では `safe` のみ使用）
- HTMLメール用テーブルレイアウト

---

## [2025-11-27] 第6回処理

### ファイル名: s-style/hon/article.html

#### ルール外の改修事項
- なし

#### 懸念事項
- Django特有の`{% regroup %}`タグを使用（Jinja2非互換）
- Django特有の`{% ifchanged %}`タグを使用（Jinja2非互換）
- Google Maps API使用
- Galleriffic画像ギャラリープラグイン使用

#### 期待する変数データ形式
```python
{
    'data': {
        'bkdata': {
            'bkID': str,  # 物件ID
            'ttmnmi': str,  # 建物名
            'tdufknmi': str,  # 都道府県名
            'shzicmi1': str,  # 所在地1
            'shzicmi2': str,  # 所在地2
            'sduFtnUm': str,  # 私道負担有無（"有"/"無"）
            # ... その他多数
        },
        'listKey': str,  # リストキー
        'kakakuM': float,  # 価格（万円）
        'picdata': list,  # 画像リスト
        'heimenzu': dict,  # 平面図データ
    }
}
```

#### その他
- 1箇所の`{% ifequal %}` → `{% if == %}` 変換（601行目: 私道負担有無判定）
  - `{% ifequal data.bkdata.sduFtnUm "有" %}` → `{% if data.bkdata.sduFtnUm == "有" %}`

---

### ファイル名: s-style/hon/backoffice/article.html

#### ルール外の改修事項
- なし

#### 懸念事項
- Django特有の`{% regroup %}`タグを使用（Jinja2非互換）
- Django特有の`{% ifchanged %}`タグを使用（Jinja2非互換）
- Google Maps API使用
- Galleriffic画像ギャラリープラグイン使用

#### 期待する変数データ形式
```python
{
    'data': {
        'bkdata': {
            'bkID': str,  # 物件ID
            'ttmnmi': str,  # 建物名
            'tdufknmi': str,  # 都道府県名
            'shzicmi1': str,  # 所在地1
            'shzicmi2': str,  # 所在地2
            'sduFtnUm': str,  # 私道負担有無（"有"/"無"）
            # ... その他多数
        },
        'listKey': str,  # リストキー
        'kakakuM': float,  # 価格（万円）
        'picdata': list,  # 画像リスト
        'heimenzu': dict,  # 平面図データ
    }
}
```

#### その他
- 1箇所の`{% ifequal %}` → `{% if == %}` 変換（600行目: 私道負担有無判定）
  - `{% ifequal data.bkdata.sduFtnUm "有" %}` → `{% if data.bkdata.sduFtnUm == "有" %}`

---

### ファイル名: s-style/hon/backoffice/articlem.html

#### ルール外の改修事項
- なし

#### 懸念事項
- モバイル版の物件詳細ページ
- シンプルな構造

#### 期待する変数データ形式
```python
{
    'data': {
        'bkdata': {
            'ttmnmi': str,  # 建物名
            'tdufknmi': str,  # 都道府県名
            'shzicmi1': str,  # 所在地1
            'shzicmi2': str,  # 所在地2
            # ... その他多数
        },
        'kakakuM': float,  # 価格（万円）
        'picdata': list,  # 画像リスト
        'heimenzu': dict,  # 平面図データ
    }
}
```

#### その他
- `{% ifequal %}` タグなし、変換不要

---

### ファイル名: s-style/hon/backoffice/bklist.html

#### ルール外の改修事項
- なし

#### 懸念事項
- 物件一覧表示用テンプレート
- 複雑なアイコン表示ロジック

#### 期待する変数データ形式
```python
{
    'data': {
        'listKey': str,  # リストキー（カテゴリ名）
        'offsetpre': str,  # 前のページURL
        'offsetnext': str,  # 次のページURL
        'bkdataurl': str,  # 物件詳細ベースURL
        'bkdatalist': [  # 物件リスト
            {
                'kakakuM': float,  # 価格（万円）
                'bkdata': {
                    'bkID': str,  # 物件ID
                    'ttmnmi': str,  # 建物名
                    'bbchntikbn': str,  # 売買賃貸区分
                    'dtsyuri': str,  # 取扱種類
                    'bkknShmk': str,  # 物件種目
                    'icons': [str],  # アイコンリスト
                    # ... その他
                },
                'picdata': [{'bloburl': str}]  # 画像リスト
            },
            ...
        ]
    }
}
```

#### その他
- 10箇所の`{% ifequal %}` → `{% if == %}` 変換:
  - `{% ifequal bkdata.bkdata.bbchntikbn "賃貸" %}` → `{% if bkdata.bkdata.bbchntikbn == "賃貸" %}`
  - `{% ifequal bkdata.bkdata.dtsyuri "事例" %}` → `{% if bkdata.bkdata.dtsyuri == "事例" %}`
  - `{% ifequal bkdata.bkdata.bkknShmk "中古戸建" %}` → `{% if bkdata.bkdata.bkknShmk == "中古戸建" %}`
  - `{% ifequal bkdata.bkdata.bkknShmk "新築戸建" %}` → `{% if bkdata.bkdata.bkknShmk == "新築戸建" %}`
  - `{% ifequal bkdata.bkdata.bkknShmk "売地" %}` → `{% if bkdata.bkdata.bkknShmk == "売地" %}`
  - `{% ifequal bkdata.bkdata.bkknShmk "中古マンション" %}` → `{% if bkdata.bkdata.bkknShmk == "中古マンション" %}`
  - `{% ifequal bkdata.bkdata.bbchntikbn "売買" %}{% ifequal bkdata.bkdata.bkknShmk "事務所" %}` → ネストされた if 文に変換
  - `{% ifequal icon "リフォーム" %}` → `{% if icon == "リフォーム" %}`
  - `{% ifequal icon "収益" %}` → `{% if icon == "収益" %}`
  - `{% ifequal icon "テナント" %}` → `{% if icon == "テナント" %}`

---

### ファイル名: s-style/hon/backoffice/bklistm.html

#### ルール外の改修事項
- なし

#### 懸念事項
- モバイル版物件一覧
- シンプルな構造

#### 期待する変数データ形式
```python
{
    'data': {
        'listKey': str,  # リストキー（カテゴリ名）
        'offsetpre': str,  # 前のページURL
        'offsetnext': str,  # 次のページURL
        'bkdataurl': str,  # 物件詳細ベースURL
        'bkdatalist': [  # 物件リスト
            {
                'bkdata': {
                    'bkID': str,  # 物件ID
                    'ttmnmi': str,  # 建物名
                    'tdufknmi': str,  # 都道府県名
                    'shzicmi1': str,  # 所在地1
                    'shzicmi2': str,  # 所在地2
                },
                'picdata': [{'bloburl': str}]  # 画像リスト
            },
            ...
        ]
    }
}
```

#### その他
- `{% ifequal %}` タグなし、変換不要

---

---

## [2025-11-27] 第7回処理

### ファイル名: bkedit.html

#### ルール外の改修事項
- 676行目: IE専用コード `if(d.all) window.event.keyCode = 0` を削除

#### 懸念事項
- 非常に大規模なファイル（265KB超、511箇所のifequal変換）
- jQuery 1.10.2使用
- Google Maps API使用
- ime-mode CSS使用（非推奨、ブラウザサポート終了済み）
- 多数のオートコンプリート機能（住所、沿線、駅検索）
- JSONP使用（クロスドメインAJAX: `https://s-style-hrd.appspot.com/jsonservice`）

#### 期待する変数データ形式
```python
{
    'bkdb': {
        'bkID': str,  # 物件ID
        'bbchntikbn': str,  # 売買賃貸区分
        'dtsyuri': str,  # 取扱い種類
        'bkknShbt': str,  # 物件種別
        'bkknShmk': str,  # 物件種目
        'tdufknmi': str,  # 都道府県名
        'shzicmi1': str,  # 所在地名1
        'shzicmi2': str,  # 所在地名2
        'shzicmi3': str,  # 所在地名3
        'ttmnmi': str,  # 建物名
        'kkkuCnryu': float,  # 価格
        'tcMnsk2': float,  # 土地面積
        'snyuMnskSyuBbnMnsk2': float,  # 専有面積
        'chzsntidkd': {'lat': float, 'lon': float},  # センター座標
        'idkd': {'lat': float, 'lon': float},  # マーカー座標
        'chzrnj': int,  # ズームレベル
        # ... その他多数の物件フィールド
    },
    'blobs': [  # 画像リスト
        {'bloburl': str}
    ]
}
```

#### その他
- 511箇所の`{% ifequal %}` → `{% if == %}` 変換
- 5箇所の絶対パス → 相対パス変換
- IE専用コード削除
- 物件登録用の大規模フォーム

---

### ファイル名: bksearch.html

#### ルール外の改修事項
- 335行目: IE専用コード `if(d.all) window.event.keyCode = 0` を削除

#### 懸念事項
- 大規模なファイル（2000行超、166箇所のifequal変換）
- jQuery 1.10.2使用
- ime-mode CSS使用（非推奨）
- 複雑な検索フォーム

#### 期待する変数データ形式
```python
{
    'memberID': str,  # 会員ID
    'key': str,  # キー
    'page': str,  # ページ
    'data': {
        'bbchntikbn': str,  # 売買賃貸区分
        'tdufknmi': str,  # 都道府県名
        # ... その他多数の検索条件フィールド
    }
}
```

#### その他
- 166箇所の`{% ifequal %}` → `{% if == %}` 変換
- 3箇所の絶対パス → 相対パス変換
- IE専用コード削除
- 物件検索用の大規模フォーム

---

### ファイル名: s-style/hon/backoffice/bksearch.html

#### ルール外の改修事項
- 319行目: IE専用コード `if(d.all) window.event.keyCode = 0` を削除

#### 懸念事項
- 大規模なファイル（2342行、138箇所のifequal変換）
- jQuery 1.10.2使用
- ime-mode CSS使用（264行目）
- 物件検索フォーム

#### 期待する変数データ形式
```python
{
    'memberID': str,  # 会員ID
    'key': str,  # キー
    'page': str,  # ページ
    'data': {
        'bbchntikbn': str,  # 売買賃貸区分
        'tdufknmi': str,  # 都道府県名
        # ... その他多数の検索条件フィールド
    }
}
```

#### その他
- 138箇所の`{% ifequal %}` → `{% if == %}` 変換
- IE専用コード削除

---

### ファイル名: s-style/hon/backoffice/follow.html

#### ルール外の改修事項
- なし

#### 懸念事項
- `followpagebase.html`を継承
- フォロー管理画面

#### 期待する変数データ形式
```python
{
    'memberID': str,  # 会員ID
    'key': str,  # キー
    'followlist': [  # フォローリスト
        {
            'followID': str,
            'name': str,
            'tel': str,
            'email': str,
            # ... その他フォロー情報
        }
    ]
}
```

#### その他
- 11箇所の絶対パス → 相対パス変換

---

### ファイル名: s-style/hon/backoffice/followpagebase.html

#### ルール外の改修事項
- なし

#### 懸念事項
- 基底テンプレート
- jQuery 1.11.1使用
- オートコンプリート機能

#### 期待する変数データ形式
```python
{
    'Domain': str,  # ドメイン名
    'memberID': str,  # 会員ID
    'userID': str,  # ユーザーID
    # ... その他セッション情報
}
```

#### その他
- 11箇所の絶対パス → 相対パス変換

---

### ファイル名: s-style/hon/backoffice/sorry.html

#### ルール外の改修事項
- なし

#### 懸念事項
- エラーページ
- シンプルな構造

#### 期待する変数データ形式
```python
{
    'error_msg': str,  # エラーメッセージ
    'completed_msg': str  # 完了メッセージ
}
```

#### その他
- 変換不要（ifequal、絶対パスなし）

---

### ファイル名: s-style/hon/backoffice/userpagebase.html

#### ルール外の改修事項
- なし

#### 懸念事項
- ユーザーページ基底テンプレート
- テーブルレイアウト使用

#### 期待する変数データ形式
```python
# ブロック変数のみ（継承先で定義）
# {% block title %} - ページタイトル
# {% block content %} - メインコンテンツ
```

#### その他
- 9箇所の絶対パス → 相対パス変換

---

### ファイル名: s-style/hon/ww2.s-style.ne.jp/article.html

#### ルール外の改修事項
- なし

#### 懸念事項
- Django特有の`{% regroup %}`タグを使用（Jinja2非互換）
- Django特有の`{% ifchanged %}`タグを使用（Jinja2非互換）
- Google Maps API使用
- Galleriffic画像ギャラリープラグイン使用

#### 期待する変数データ形式
```python
{
    'data': {
        'bkdata': {
            'bkID': str,  # 物件ID
            'ttmnmi': str,  # 建物名
            # ... その他物件詳細フィールド
        },
        'picdata': list,  # 画像リスト
    }
}
```

#### その他
- 1箇所の`{% ifequal %}` → `{% if == %}` 変換
- 1箇所の絶対パス → 相対パス変換

---

### ファイル名: s-style/hon/ww2.s-style.ne.jp/articlem.html

#### ルール外の改修事項
- なし

#### 懸念事項
- モバイル版物件詳細ページ
- シンプルな構造

#### 期待する変数データ形式
```python
{
    'data': {
        'bkdata': {
            'ttmnmi': str,  # 建物名
            # ... その他物件詳細フィールド
        },
        'picdata': list,  # 画像リスト
    }
}
```

#### その他
- 変換不要（ifequal、絶対パスなし）

---

### ファイル名: s-style/hon/ww2.s-style.ne.jp/bklist.html

#### ルール外の改修事項
- 変数タイポ修正:
  - `{{bkdata.stHrs41}}` → `{{bkdata.bkdata.stHrs41}}`
  - `{{bkdata.thM21}}` → `{{bkdata.bkdata.thM21}}`
  - `{{bbkdata.kdata.bsRsnmi1}}` → `{{bkdata.bkdata.bsRsnmi1}}`
  - `{{bkdata.bstiMishu1}}` → `{{bkdata.bkdata.bstiMishu1}}`
  - `{{bkdata.tihM1}}` → `{{bkdata.bkdata.tihM1}}`
  - `{% if bkdata.bkdat.ekmi2 %}` → `{% if bkdata.bkdata.ekmi2 %}`

#### 懸念事項
- 物件一覧表示用テンプレート
- 複雑な条件分岐（物件種別、アイコン表示）

#### 期待する変数データ形式
```python
{
    'data': {
        'listKey': str,  # リストキー
        'offsetpre': str,  # 前のページURL
        'offsetnext': str,  # 次のページURL
        'bkdataurl': str,  # 物件詳細ベースURL
        'bkdatalist': [  # 物件リスト
            {
                'kakakuM': float,  # 価格（万円）
                'bkdata': {
                    'bkID': str,
                    'ttmnmi': str,
                    # ... その他
                },
                'picdata': [{'bloburl': str}]
            }
        ]
    }
}
```

#### その他
- 11箇所の`{% ifequal %}` → `{% if == %}` 変換
- 6箇所の変数タイポ修正

---

## [2025-11-27] 第8回処理

### ファイル名: ww2.s-style.ne.jp/bklistm.html

#### ルール外の改修事項
- 配列アクセス構文変換: `{{bkdata.picdata.0.bloburl}}` → `{{bkdata.picdata[0].bloburl}}`

#### 懸念事項
- モバイル版物件一覧ページ
- シンプルな構造

#### 期待する変数データ形式
```python
{
    'data': {
        'listKey': str,  # リストキー
        'offsetpre': str,  # 前のページURL
        'offsetnext': str,  # 次のページURL
        'bkdataurl': str,  # 物件詳細ベースURL
        'bkdatalist': [  # 物件リスト
            {
                'bkdata': {
                    'bkID': str,
                    'ttmnmi': str,
                    'tdufknmi': str,
                    'shzicmi1': str,
                    'shzicmi2': str,
                },
                'picdata': [{'bloburl': str}]
            }
        ]
    }
}
```

#### その他
- charset=utf-8 のまま維持
- 絶対URLは外部参照のため変更なし

---

### ファイル名: ww2.s-style.ne.jp/index.html

#### ルール外の改修事項
- なし

#### 懸念事項
- 静的モックアップファイル（テンプレート変数なし）
- 古いHTMLスタイル（テーブルレイアウト）
- アクセスカウンター使用（j1.ax.xrea.com）

#### 期待する変数データ形式
```python
# 静的モックアップのため変数なし
```

#### その他
- charset: shift_jis → utf-8 に変換
- 相対パスはそのまま維持（../css/, ../js/, ../cmn_img/ 等）

---

### ファイル名: ww2.s-style.ne.jp/pict.html

#### ルール外の改修事項
- なし

#### 懸念事項
- 画像ポップアップ用テンプレート
- シンプルな構造

#### 期待する変数データ形式
```python
# 静的モックアップのため変数なし
```

#### その他
- charset: shift_jis → utf-8 に変換
- 相対パスはそのまま維持

---

### ファイル名: ww2.s-style.ne.jp/sorry.html

#### ルール外の改修事項
- コメント構文変換: `{% comment %}...{% endcomment %}` → `{# ... #}`

#### 懸念事項
- `userpagebase.html`を継承
- エラーページ

#### 期待する変数データ形式
```python
{
    'error_msg': str,  # エラーメッセージ
    'completed_msg': str,  # 完了メッセージ
    'corp_name': str,  # 法人名
    'sitename': str,  # サイト名
    'branch_name': str,  # 支店名
    'togo': str  # 遷移先
}
```

#### その他
- 変換不要（ifequal、絶対パスなし）

---

### ファイル名: ww2.s-style.ne.jp/userpagebase.html

#### ルール外の改修事項
- 絶対パス → 相対パス変換:
  - `/css/styles.css` → `../css/styles.css`
  - `/favicon.ico` → `../favicon.ico`
  - `/js/smooth.pack.js` → `../js/smooth.pack.js`
  - `/img/back01.jpg` → `../img/back01.jpg`
  - `/img/back-head.jpg` → `../img/back-head.jpg`
  - `/img/yajirushi01.gif` → `../img/yajirushi01.gif`
  - `/img/login-side01.jpg` → `../img/login-side01.jpg`
  - `/img/login-back.jpg` → `../img/login-back.jpg`
  - `/img/b-login.jpg` → `../img/b-login.jpg`
  - `/img/b-touroku.jpg` → `../img/b-touroku.jpg`
  - `/img/login-side02.jpg` → `../img/login-side02.jpg`
  - `/img/yajirushi02.gif` → `../img/yajirushi02.gif`

#### 懸念事項
- ユーザーページ基底テンプレート
- テーブルレイアウト使用

#### 期待する変数データ形式
```python
# ブロック変数のみ（継承先で定義）
# {% block title %} - ページタイトル
# {% block content %} - メインコンテンツ
```

#### その他
- charset=utf-8 のまま維持
- 12箇所の絶対パス → 相対パス変換

---

### ファイル名: www.chikusaku-m.com/article.html

#### ルール外の改修事項
- フィルター構文変換:
  - `|default:""` → `|default("")`
  - `|join:"<br />"` → `|join("<br />")`
  - `|date:"n"` → `|date("n")`
  - `|floatformat:"-2"` → `|floatformat("-2")`
  - `|default_if_none:""` → `|default("")`
- 配列アクセス構文変換: `.0.` → `[0].`

#### 懸念事項
- Django特有の`{% regroup %}`タグを使用（Jinja2非互換）
- Django特有の`{% ifchanged %}`タグを使用（Jinja2非互換）
- Google Maps API使用
- Galleriffic画像ギャラリープラグイン使用
- jQuery 1.7.1使用

#### 期待する変数データ形式
```python
{
    'data': {
        'bkdata': {
            'bkID': str,  # 物件ID
            'ttmnmi': str,  # 建物名
            'tdufknmi': str,  # 都道府県名
            'shzicmi1': str,  # 所在地1
            'shzicmi2': str,  # 所在地2
            'shzicmi3': str,  # 所在地3
            'idkd': str,  # 座標（緯度,経度）
            'kkkuCnryu': str,  # 価格
            'kkkybku': list,  # 広告区分（複数）
            'bku3': str,  # 備考3
            'bku4': str,  # 備考4
            # ... その他多数の物件フィールド
        },
        'kakakuM': float,  # 価格（万円）
        'picdata': list,  # 画像リスト
        'heimenzu': dict,  # 平面図データ
        'tknngtG': str,  # 築年月（和暦）
    },
    'gakkuS': str,  # 学区（小学校）
    'gakkuC': str,  # 学区（中学校）
}
```

#### その他
- 全URL絶対パス維持（https://www.chikusaku-m.com/）
- jQuery `.live()` → 将来的に `.on()` への変更検討
- regroupタグ、ifchangedタグはサーバー側でのグループ化処理が必要

---

### ファイル名: www.chikusaku-m.com/bklist.html

#### ルール外の改修事項
- フィルター構文変換:
  - `|default:""` → `|default("")`
  - `|floatformat:"-2"` → `|floatformat("-2")`
  - `|default_if_none:""` → `|default("")`
- 配列アクセス構文変換: `.0.` → `[0].`

#### 懸念事項
- 物件一覧表示用テンプレート
- jQuery使用

#### 期待する変数データ形式
```python
{
    'data': {
        'listKey': str,  # リストキー
        'offsetpre': str,  # 前のページURL
        'offsetnext': str,  # 次のページURL
        'bkdataurl': str,  # 物件詳細ベースURL
        'bkdatalist': [  # 物件リスト
            {
                'kakakuM': float,  # 価格（万円）
                'bkdata': {
                    'bkID': str,
                    'ttmnmi': str,
                    'tdufknmi': str,
                    'shzicmi1': str,
                    'shzicmi2': str,
                    'shzicmi3': str,
                    'ekmi1': str,  # 駅名1
                    'ekmi2': str,  # 駅名2
                    'ekmi3': str,  # 駅名3
                    'mdrHysu1': float,  # 間取り部屋数
                    'mdrTyp1': str,  # 間取りタイプ
                    # ... その他
                },
                'picdata': [{'bloburl': str}]
            }
        ]
    }
}
```

#### その他
- 全URL絶対パス維持（https://www.chikusaku-m.com/）
- Google Analytics統合あり（UA-7545989-12）

---

### ファイル名: www.chikusaku-m.com/sorry.html

#### ルール外の改修事項
- コメント構文変換: `{% comment %}...{% endcomment %}` → `{# ... #}`

#### 懸念事項
- `userpagebase.html`を継承
- エラーページ

#### 期待する変数データ形式
```python
{
    'error_msg': str,  # エラーメッセージ
    'completed_msg': str,  # 完了メッセージ
    'corp_name': str,  # 法人名
    'sitename': str,  # サイト名
    'branch_name': str,  # 支店名
    'togo': str  # 遷移先
}
```

#### その他
- 変換不要（ifequal、絶対パスなし）

---

### ファイル名: www.chikusaku-m.com/userpagebase.html

#### ルール外の改修事項
- フィルター構文変換:
  - `|default:""` → `|default("")`

#### 懸念事項
- ユーザーページ基底テンプレート
- テーブルレイアウト使用

#### 期待する変数データ形式
```python
{
    'data': {
        'listKey': str,  # リストキー
    }
    # ブロック変数（継承先で定義）
    # {% block head %}
    # {% block contents_header %}
    # {% block content %}
    # {% block contents_footer %}
}
```

#### その他
- 全URL絶対パス維持（https://www.chikusaku-m.com/）
- Google Analytics統合あり（UA-7545989-12）

---

## [2025-11-28] 第9回処理

### ファイル名: s-style/hon/www.chikusaku-mansion.com/article.html

#### ルール外の改修事項
- なし

#### 懸念事項
- Django特有の`{% regroup %}`タグを使用（Jinja2非互換）
- Django特有の`{% ifchanged %}`タグを使用（Jinja2非互換）
- Google Maps API使用
- Galleriffic画像ギャラリープラグイン使用
- Google reCAPTCHA v3実装

#### 期待する変数データ形式
```python
{
    'data': {
        'bkdata': {
            'bkID': str,  # 物件ID
            'ttmnmi': str,  # 建物名
            'tdufknmi': str,  # 都道府県名
            'shzicmi1': str,  # 所在地1
            'shzicmi2': str,  # 所在地2
            'shzicmi3': str,  # 所在地3
            'dtsyuri': str,  # 取扱種類（"サンプル"/"事例"/etc）
            'idkd': str,  # 緯度経度
            'kkkuCnryu': str,  # 価格（通貨）
            'knrh': str,  # 管理費
            'shznTmttkn': str,  # 修繕積立金
            # ... その他多数
        },
        'kakakuM': float,  # 価格（万円）
        'picdata': list,  # 画像リスト
        'heimenzu': dict,  # 平面図データ
        'mailmsg': str,  # メールメッセージ
        'mailmsgCP932': str,  # メールメッセージ（CP932）
        'webkkkk': bool,  # Web公開フラグ
    },
    'auth': bool,  # 認証フラグ
    'sitekey': str,  # reCAPTCHAサイトキー
}
```

#### その他
- jQuery `.live()` → `.on()`変換
- `applicationpagebase.html`を継承
- 条件分岐で複数表示パターンあり（サンプル/事例/公開/会員限定/未ログイン）

---

### ファイル名: s-style/hon/www.chikusaku-mansion.com/article2.html

#### ルール外の改修事項
- なし

#### 懸念事項
- article.htmlの簡略版（認証判定が少ない）

#### 期待する変数データ形式
- article.htmlと同様

#### その他
- jQuery `.live()` → `.on()`変換
- `applicationpagebase.html`を継承

---

### ファイル名: s-style/hon/www.chikusaku-mansion.com/articlebkdata.html

#### ルール外の改修事項
- なし

#### 懸念事項
- インクルード用テンプレート（article.htmlから呼び出し）
- ローンシミュレーション機能
- Django特有の`{% regroup %}`タグを使用

#### 期待する変数データ形式
```python
{
    'data': {
        'bkdata': {
            # 物件詳細フィールド（多数）
        },
        'kakakuM': float,  # 価格（万円）
        'picdata': list,  # 画像リスト
        'heimenzu': dict,  # 平面図データ
        'gakkuS': list,  # 学区（小学校）
        'gakkuC': list,  # 学区（中学校）
    }
}
```

#### その他
- スタンドアロンではなく、article.htmlからincludeされる

---

### ファイル名: s-style/hon/www.chikusaku-mansion.com/bklist.html

#### ルール外の改修事項
- なし

#### 懸念事項
- 物件一覧表示用
- 複雑な条件分岐

#### 期待する変数データ形式
```python
{
    'data': {
        'listKey': str,  # リストキー
        'offsetpre': str,  # 前のページURL
        'offsetnext': str,  # 次のページURL
        'bkdataurl': str,  # 物件詳細ベースURL
        'bkdatalist': [  # 物件リスト
            {
                'kakakuM': float,  # 価格（万円）
                'bkdata': {
                    'bkID': str,  # 物件ID
                    'ttmnmi': str,  # 建物名
                    # ... その他
                },
                'picdata': [{'bloburl': str}]
            }
        ]
    }
}
```

#### その他
- `applicationpagebase.html`を継承
- Google Analytics統合あり

---

### ファイル名: s-style/hon/www.chikusaku-mansion.com/mypagebkdata.html

#### ルール外の改修事項
- なし

#### 懸念事項
- マイページ物件詳細
- Django特有の`{% regroup %}`タグを使用

#### 期待する変数データ形式
- article.htmlと類似

#### その他
- jQuery `.live()` → `.on()`変換
- `mypagebase.html`を継承

---

### ファイル名: s-style/hon/www.chikusaku-mansion.com/mypagebklist.html

#### ルール外の改修事項
- なし

#### 懸念事項
- マイページ物件一覧

#### 期待する変数データ形式
- bklist.htmlと類似

#### その他
- `mypagebase.html`を継承

---

### ファイル名: s-style/hon/www.chikusaku-mansion.com/mypagebklistfav.html

#### ルール外の改修事項
- なし

#### 懸念事項
- お気に入り物件一覧

#### 期待する変数データ形式
- bklist.htmlと類似

#### その他
- `mypagebase.html`を継承

---

### ファイル名: s-style/hon/www.chikusaku-mansion.com/mypagefollow.html

#### ルール外の改修事項
- なし

#### 懸念事項
- 検索条件フォロー機能

#### 期待する変数データ形式
- 静的コンテンツ（サンプルデータ）

#### その他
- `mypagebase.html`を継承

---

### ファイル名: s-style/hon/www.chikusaku-mansion.com/mypagemydata.html

#### ルール外の改修事項
- `{% ifequal %}` → `{% if == %}` 変換（5箇所）

#### 懸念事項
- 会員情報編集フォーム

#### 期待する変数データ形式
```python
{
    'corp': str,  # 法人名
    'branch': str,  # 支店名
    'data': {
        'name': str,  # 氏名
        'yomi': str,  # 読み仮名
        'age': int,  # 年齢
        'kinzoku': int,  # 勤続年数
        'otona': int,  # 入居大人数
        'kodomo': int,  # 入居子供数
        'tutomesaki': str,  # 勤め先
        'zip': str,  # 郵便番号
        'address': str,  # 住所
        'address1': str,  # 所在地1
        'address2': str,  # 所在地2
        'phone': str,  # 電話番号
        'fax': str,  # FAX番号
        'mobilephone': str,  # 携帯番号
        'access': str,  # 送信方法
        'mail': str,  # メール
        'netID': str,  # ネットID
        'netPass': str,  # パスワード
        'zikoshikin': float,  # 自己資金
        'heisaituki': float,  # 返済予定額月々
        'heisaibonasu': float,  # 返済予定額ボーナス
        'kounyuziki': str,  # 購入時期
    }
}
```

#### その他
- `mypagebase.html`を継承

---

### ファイル名: s-style/hon/www.chikusaku-mansion.com/mypagenewlist.html

#### ルール外の改修事項
- なし

#### 懸念事項
- 新着物件通知設定

#### 期待する変数データ形式
- 静的コンテンツ（サンプルデータ）

#### その他
- `mypagebase.html`を継承

---

## [2025-11-28] 第10回処理

### ファイル名: s-style/hon/www.chikusaku-mansion.com/mypageResign.html

#### ルール外の改修事項
- なし

#### 懸念事項
- なし（シンプルな退会確認テンプレート）

#### 期待する変数データ形式
- 静的コンテンツ（確認メッセージのみ）

#### その他
- `mypagebase.html`を継承
- 変換不要（テンプレート変数のみ）

---

### ファイル名: s-style/hon/www.chikusaku-mansion.com/mypagesearch.html

#### ルール外の改修事項
- 絶対パス → 相対パス変換多数
- `.live('click')` → `$(document).on('click', selector, fn)` 変換（jQuery modernization）
- `{% ifequal %}` → `{% if == %}` 変換
- IE専用 `ime-mode` CSSコード削除

#### 懸念事項
- jQuery autocomplete使用（`AC_options`設定）
- jQuery UI依存
- Googleマップ API使用

#### 期待する変数データ形式
```python
{
    'data': {
        'bkknShbt': str,  # 物件種別
        'bkknShmk': str,  # 物件種目
        'tdufknmi': str,  # 都道府県名
        'shzicmi1': str,  # 所在地1
        'ensenmei': str,  # 沿線名
        # 検索条件フィールド多数
    }
}
```

#### その他
- `mypagebase.html`を継承
- 複雑な検索フォーム

---

### ファイル名: s-style/hon/www.chikusaku-mansion.com/mypagesearchlist.html

#### ルール外の改修事項
- なし

#### 懸念事項
- なし（静的モックアップ）

#### 期待する変数データ形式
- 静的コンテンツ（サンプルデータ）

#### その他
- `mypagebase.html`を継承
- 変換不要（静的HTML）

---

### ファイル名: s-style/hon/www.chikusaku-mansion.com/mypagetop.html

#### ルール外の改修事項
- `/img/` → `../img/` 変換

#### 懸念事項
- なし

#### 期待する変数データ形式
- 静的コンテンツ（トピックスサンプルデータ）

#### その他
- `mypagebase.html`を継承

---

### ファイル名: s-style/hon/www.chikusaku-mansion.com/mypagebase.html

#### ルール外の改修事項
- `/js/` → `../js/` 変換
- `/css/` → `../css/` 変換

#### 懸念事項
- なし

#### 期待する変数データ形式
- ベーステンプレート（変数なし）

#### その他
- マイページ系のベーステンプレート
- Google Analytics（UA-7545989-12）

---

### ファイル名: s-style/hon/www.chikusaku-mansion.com/sorry.html

#### ルール外の改修事項
- `{% comment %}...{% endcomment %}` → `{# ... #}` 変換

#### 懸念事項
- なし

#### 期待する変数データ形式
```python
{
    'error_msg': str,  # エラーメッセージ（オプション）
    'completed_msg': str,  # 完了メッセージ（オプション）
    'corp_name': str,  # 法人名
    'sitename': str,  # サイト名
    'branch_name': str,  # 支店名
    'togo': str  # 遷移先URL
}
```

#### その他
- `userpagebase.html`を継承

---

### ファイル名: s-style/hon/www.chikusaku-mansion.com/userpagebase.html

#### ルール外の改修事項
- `/js/` → `../js/` 変換

#### 懸念事項
- なし

#### 期待する変数データ形式
```python
{
    'data': {
        'bkdata': {
            'ttmnmi': str,  # 建物名
            'tdufknmi': str,  # 都道府県名
            'shzicmi1': str,  # 所在地1
            'shzicmi2': str  # 所在地2
        }
    }
}
```

#### その他
- メインサイト用ベーステンプレート
- サイドメニュー iframe使用
- フッター iframe使用
- Google Analytics（UA-7545989-12）

---

### ファイル名: s-style/hon/www.chikusaku-mansion.com/userpagebase2.html

#### ルール外の改修事項
- `/css/` → `../css/` 変換
- `/js/` → `../js/` 変換
- `/img/` → `../img/` 変換

#### 懸念事項
- なし

#### 期待する変数データ形式
- ベーステンプレート（変数なし）

#### その他
- シンプルなベーステンプレート（サイドメニューなし）
- Google Analytics（UA-7545989-12）

---

## [2025-11-28] 第11回処理 (www.s-style.ne.jp - 19ファイル)

### ファイル名: s-style/hon/www.s-style.ne.jp/article-koukai-sp.html

#### ルール外の改修事項
- `{% ifequal %}` → `{% if == %}` 変換（約13箇所）

#### 懸念事項
- スマートフォン用テンプレート
- FlickSlide jQuery プラグイン使用

#### その他
- 物件詳細表示用SP版テンプレート

---

### ファイル名: s-style/hon/www.s-style.ne.jp/article-koukai.html

#### ルール外の改修事項
- `/js/` → `../js/` 変換
- `.live('click')` → `$(document).on('click')` 変換
- `{% ifequal %}` → `{% if == %}` 変換

#### 懸念事項
- Galleriffic jQuery ギャラリープラグイン使用
- Google Maps API使用
- jQuery History プラグイン使用

#### その他
- 物件詳細表示用PC版テンプレート

---

### ファイル名: s-style/hon/www.s-style.ne.jp/article-member-login-sp.html

#### ルール外の改修事項
- `{% ifequal %}` → `{% if == %}` 変換

#### 懸念事項
- 会員ログイン後の物件詳細SP版

#### その他
- `{% ifequal %}` パターンを `{% if == %}` に変換

---

### ファイル名: s-style/hon/www.s-style.ne.jp/article-member-login.html

#### ルール外の改修事項
- `/js/` → `../js/` 変換
- `.live('click')` → `$(document).on('click')` 変換
- `{% ifequal %}` → `{% if == %}` 変換

#### 懸念事項
- 会員ログイン後の物件詳細PC版

#### その他
- Galleriffic ギャラリー使用

---

### ファイル名: s-style/hon/www.s-style.ne.jp/article-member-sp.html

#### ルール外の改修事項
- `{% ifequal %}` → `{% if == %}` 変換

#### 懸念事項
- 会員専用物件詳細SP版

---

### ファイル名: s-style/hon/www.s-style.ne.jp/article-member.html

#### ルール外の改修事項
- `/js/` → `../js/` 変換
- `.live('click')` → `$(document).on('click')` 変換
- `{% ifequal %}` → `{% if == %}` 変換

#### 懸念事項
- 会員専用物件詳細PC版

---

### ファイル名: s-style/hon/www.s-style.ne.jp/article-soldout-sp.html

#### ルール外の改修事項
- `{% ifequal %}` → `{% if == %}` 変換

#### 懸念事項
- 成約済み物件詳細SP版

---

### ファイル名: s-style/hon/www.s-style.ne.jp/article-soldout.html

#### ルール外の改修事項
- `/js/` → `../js/` 変換
- `.live('click')` → `$(document).on('click')` 変換
- `{% ifequal %}` → `{% if == %}` 変換

#### 懸念事項
- 成約済み物件詳細PC版

---

### ファイル名: s-style/hon/www.s-style.ne.jp/article-sp.html

#### ルール外の改修事項
- `{% ifequal %}` → `{% if == %}` 変換（シングルクォート対応）

#### 懸念事項
- 物件詳細SP版ベーステンプレート

---

### ファイル名: s-style/hon/www.s-style.ne.jp/article.html

#### ルール外の改修事項
- `{% ifequal %}` → `{% if == %}` 変換（シングルクォート対応）

#### 懸念事項
- 物件詳細PC版ベーステンプレート
- 条件分岐で他のテンプレートを include

---

### ファイル名: s-style/hon/www.s-style.ne.jp/articlem.html

#### ルール外の改修事項
- `{% ifequal %}` → `{% if == %}` 変換（シングルクォート対応）

#### 懸念事項
- モバイル版物件詳細テンプレート

---

### ファイル名: s-style/hon/www.s-style.ne.jp/bklist-sp.html

#### ルール外の改修事項
- `{% ifequal %}` → `{% if == %}` 変換

#### 懸念事項
- 物件一覧SP版

---

### ファイル名: s-style/hon/www.s-style.ne.jp/bklist.html

#### ルール外の改修事項
- `{% ifequal %}` → `{% if == %}` 変換

#### 懸念事項
- 物件一覧PC版

---

### ファイル名: s-style/hon/www.s-style.ne.jp/bklistm.html

#### ルール外の改修事項
- 変換不要

#### 懸念事項
- なし

---

### ファイル名: s-style/hon/www.s-style.ne.jp/index.html

#### ルール外の改修事項
- 変換不要

#### 懸念事項
- なし

---

### ファイル名: s-style/hon/www.s-style.ne.jp/pict.html

#### ルール外の改修事項
- 変換不要

#### 懸念事項
- なし

---

### ファイル名: s-style/hon/www.s-style.ne.jp/sorry.html

#### ルール外の改修事項
- 変換不要

#### 懸念事項
- なし

---

### ファイル名: s-style/hon/www.s-style.ne.jp/userpagebase-sp.html

#### ルール外の改修事項
- 変換不要

#### 懸念事項
- なし

---

### ファイル名: s-style/hon/www.s-style.ne.jp/userpagebase.html

#### ルール外の改修事項
- `/js/` → `../js/` 変換

#### 懸念事項
- なし

#### その他
- PC版ベーステンプレート
