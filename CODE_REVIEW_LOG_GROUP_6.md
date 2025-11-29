# Code Review Log - Group 6

レビュー実施日: 2025-11-20
レビュー対象グループ: Group 6

---

## モジュール名: application/models/bkdata.py

### 🔴 レベル1: 重要（絶対修正が必要 - 動作に影響）

#### 問題 1
- **行番号**: 24-59
- **問題**: makedata() メソッドで Blob エンティティを検索すべきところ、BKdata を検索している
- **影響**: 旧ファイルでは `db.GqlQuery("SELECT * FROM Blob ...")` で Blob モデルをクエリしているが、新ファイルでは `BKdata.query()` となっており、間違ったモデルを検索している。これにより Blob データが取得できず、画像表示機能が動作しない。
- **修正前**:
  ```python
  query = BKdata.query(
      BKdata.nyrykkisyID == self.nyrykkisyID,
      BKdata.nyrykstnID == self.nyrykstnID,
      BKdata.bkID == self.bkID
  )
  ```
- **修正後**:
  ```python
  from application.models.blob import Blob
  query = Blob.query(
      Blob.CorpOrg_key == self.nyrykkisyID,
      Blob.Branch_Key == self.nyrykstnID,
      Blob.bkID == self.bkID,
      Blob.media == media
  )
  blobs = query.order(Blob.media, Blob.pos).fetch()
  ```
- **自動修正**: ✅ 完了

#### 問題 2
- **行番号**: 799-804
- **問題**: multiline=True 属性が必要な備考フィールドで StringProperty を使用している
- **影響**: 旧ファイルでは `db.StringProperty(multiline=True)` だったが、ndb では `multiline` オプションがなく、長いテキストには `TextProperty` を使用する必要がある。StringProperty は 1500 バイト制限があり、長い備考が保存できない。
- **修正前**:
  ```python
  bku1 = ndb.StringProperty(verbose_name=u"備考1")
  bku2 = ndb.StringProperty(verbose_name=u"備考2")
  jshKnrrn = ndb.StringProperty(verbose_name=u"自社管理欄")
  ```
- **修正後**:
  ```python
  bku1 = ndb.TextProperty(verbose_name=u"備考1")
  bku2 = ndb.TextProperty(verbose_name=u"備考2")
  jshKnrrn = ndb.TextProperty(verbose_name=u"自社管理欄")
  ```
- **自動修正**: ✅ 完了

#### 問題 3
- **行番号**: 860-863
- **問題**: multiline=True 属性が必要な備考3/4 で StringProperty を使用している
- **影響**: 同上（問題2と同様、長いテキストが保存できない）
- **修正前**:
  ```python
  bku3 = ndb.StringProperty(verbose_name=u"備考3")
  bku4 = ndb.StringProperty(verbose_name=u"備考4")
  ```
- **修正後**:
  ```python
  bku3 = ndb.TextProperty(verbose_name=u"備考3")
  bku4 = ndb.TextProperty(verbose_name=u"備考4")
  ```
- **自動修正**: ✅ 完了

#### 問題 4
- **行番号**: 971-974
- **問題**: multiline=True 属性が必要な設備/条件フィールドで StringProperty を使用している
- **影響**: 同上（問題2と同様、長いテキストが保存できない）
- **修正前**:
  ```python
  stbFrespc = ndb.StringProperty(verbose_name=u"設備")
  tkkJkuFrespc = ndb.StringProperty(verbose_name=u"条件")
  ```
- **修正後**:
  ```python
  stbFrespc = ndb.TextProperty(verbose_name=u"設備")
  tkkJkuFrespc = ndb.TextProperty(verbose_name=u"条件")
  ```
- **自動修正**: ✅ 完了

### 🟡 レベル2: 推奨（セキュリティ・品質改善）

#### 問題 1
- **行番号**: 13-15
- **問題**: GeoModel 継承 - geo/geomodel.py が db.Model ベースの可能性
- **影響**: GeoModel が依然として `db.Model` ベースの場合、BKdata クラスが正しく動作しない可能性がある。`geo/geomodel.py` が `ndb.Model` に移行済みであることを確認する必要がある。
- **推奨修正方法**: geo/geomodel.py のマイグレーション状況を確認し、未移行の場合は ndb.Model ベースに移行する
- **自動修正**: ❌ 手動対応が必要

#### 問題 2
- **行番号**: 136-147
- **問題**: self.corp / self.branch プロパティへのアクセス
- **影響**: BKdata モデルに `corp` と `branch` プロパティが定義されていない可能性がある。旧ファイルでは ReferenceProperty として定義されていた可能性があるが、新ファイルには存在しない。代わりに `nyrykkisyID` / `nyrykstnID` を使用すべき。
- **推奨修正方法**:
  1. corp / branch が ReferenceProperty として定義されていた場合は、KeyProperty として定義を追加
  2. または nyrykkisyID / nyrykstnID を使用するように変更（修正済み）
- **自動修正**: ✅ 完了（nyrykkisyID / nyrykstnID を使用するように変更）

### 🔵 レベル3: 提案（軽微な改善）

なし

### ✅ レビュー結果サマリー
- **レベル1問題**: 4件（すべて自動修正済み）
- **レベル2問題**: 2件（1件は自動修正済み、1件は依存関係確認が必要）
- **レベル3問題**: 0件
- **総評**:
  - 重要な問題として、makedata() メソッドでの誤ったモデルクエリを修正
  - multiline テキストフィールドの StringProperty → TextProperty 変換を完了
  - GeoModel の ndb 移行状況確認が必要
  - 全体的に基本的なマイグレーションは完了しているが、依存モジュールの確認が必要

---

## モジュール名: application/models/bklist.py

### 🔴 レベル1: 重要（絶対修正が必要 - 動作に影響）

なし

### 🟡 レベル2: 推奨（セキュリティ・品質改善）

なし

### 🔵 レベル3: 提案（軽微な改善）

#### 提案 1
- **行番号**: 1-18
- **提案**: インポート文の相対パス → 絶対パスへの変換が完璧
- **効果**: モジュール間の依存関係が明確で、Python 3 の推奨スタイルに準拠している
- **自動修正**: ❌ 手動対応が必要（修正不要、既に適切）

### ✅ レビュー結果サマリー
- **レベル1問題**: 0件
- **レベル2問題**: 0件
- **レベル3問題**: 0件
- **総評**:
  - db.ReferenceProperty → ndb.KeyProperty への変換が正しく完了
  - インポート文の絶対パス化が適切
  - マイグレーション状態は良好

---

## モジュール名: application/models/blob.py

### 🔴 レベル1: 重要（絶対修正が必要 - 動作に影響）

#### 問題 1（既に修正済み）
- **行番号**: 14-17
- **問題**: multiline content に StringProperty を使用（既にコメント付きで修正済み）
- **影響**: 長いコンテンツが保存できない可能性
- **修正前**:
  ```python
  content = ndb.StringProperty(verbose_name=u"content")
  ```
- **修正後**:
  ```python
  content = ndb.TextProperty(verbose_name=u"content")
  ```
- **自動修正**: ✅ 完了（既に修正済み）

### 🟡 レベル2: 推奨（セキュリティ・品質改善）

なし

### 🔵 レベル3: 提案（軽微な改善）

#### 提案 1
- **行番号**: 34-43
- **提案**: getNextNum() のトランザクション実装
- **効果**: @ndb.transactional デコレータを使用した正しいトランザクション処理が実装されている。原子性が保証されている。
- **自動修正**: ❌ 手動対応が必要（修正不要、既に適切）

### ✅ レビュー結果サマリー
- **レベル1問題**: 1件（すべて自動修正済み）
- **レベル2問題**: 0件
- **レベル3問題**: 0件
- **総評**:
  - multiline content の TextProperty 変換が完了
  - トランザクション処理が正しく実装されている
  - マイグレーション状態は良好

---

## モジュール名: application/bklistutl.py

### 🔴 レベル1: 重要（絶対修正が必要 - 動作に影響）

#### 問題 1
- **行番号**: 237-241
- **問題**: getreflistbyreflistkeys() で単一キー用の ndb.Key().get() を使用しているが、複数キーの場合に対応していない
- **影響**: reflist が複数のキーのリストの場合、正しく取得できない
- **修正前**:
  ```python
  return ndb.Key(BKlist, reflist).get()
  ```
- **修正後**:
  ```python
  return ndb.get_multi(reflist) if isinstance(reflist, list) else ndb.Key(BKlist, reflist).get()
  ```
- **自動修正**: ✅ 完了

### 🟡 レベル2: 推奨（セキュリティ・品質改善）

#### 問題 1
- **行番号**: 46-52
- **問題**: refmem が None の場合のエラーハンドリング不足
- **影響**: messageManager.getrefmembykey() が空リストまたは None を返す場合、IndexError が発生する可能性
- **推奨修正方法**:
  ```python
  if not refmem:
      refmemlist = messageManager.getrefmembykey(corp, mes.key)
      if refmemlist:
          refmem = refmemlist[0].refmem
      else:
          raise bklistutlError("refmem not found for message: " + refmesID)
  ```
- **自動修正**: ❌ 手動対応が必要

#### 問題 2
- **行番号**: 53-61
- **問題**: 重複チェックで fetch(1000) とループ内 get() による N+1 クエリ問題
- **影響**: パフォーマンス低下。特にリストが大きい場合、1000回のデータベースアクセスが発生する可能性
- **推奨修正方法**:
  1. fetch(1000) → fetch(100) など必要最低限に変更
  2. keys_only=True でキーのみ取得し、必要な場合のみ ndb.get_multi() でまとめて取得
  3. または BKlist.query(BKlist.refmes == mes.key, BKlist.refbk.bkID == refbk.bkID) で直接クエリ
- **自動修正**: ❌ 手動対応が必要（コメント追記済み）

### 🔵 レベル3: 提案（軽微な改善）

#### 提案 1
- **行番号**: 20-21
- **提案**: isinstance チェックによる型安全性の向上
- **効果**: refbk が BKdata エンティティかキーかを判定し、適切に処理している。エラーを未然に防ぐ良い実装。
- **自動修正**: ❌ 手動対応が必要（修正不要、既に適切）

#### 提案 2
- **行番号**: 180-183, 194-197
- **提案**: fetch(999999) のハードコーディング
- **効果**: 999999 という大きな数値をハードコーディングしているが、定数として定義すべき（例: MAX_FETCH_SIZE = 999999）。可読性とメンテナンス性が向上する。
- **自動修正**: ❌ 手動対応が必要

### ✅ レビュー結果サマリー
- **レベル1問題**: 1件（すべて自動修正済み）
- **レベル2問題**: 2件（1件はコメント追記済み）
- **レベル3問題**: 2件
- **総評**:
  - db → ndb の基本変換は完了しているが、パフォーマンス最適化が必要
  - エラーハンドリングの強化が推奨される
  - N+1 クエリ問題の解決が望ましい
  - 全体的にマイグレーションは適切だが、品質向上の余地あり

---

## グループ 6 全体サマリー

### ファイル別問題数

| ファイル | レベル1 | レベル2 | レベル3 | 合計 |
|---------|---------|---------|---------|------|
| application/models/bkdata.py | 4 | 2 | 0 | 6 |
| application/models/bklist.py | 0 | 0 | 0 | 0 |
| application/models/blob.py | 1 | 0 | 0 | 1 |
| application/bklistutl.py | 1 | 2 | 2 | 5 |
| **合計** | **6** | **4** | **2** | **12** |

### 自動修正状況

- **レベル1問題**: 6件中 6件 自動修正完了 ✅
- **レベル2問題**: 4件中 1件 自動修正完了、3件 手動対応が必要
- **レベル3問題**: 2件（すべて手動対応が必要、または修正不要）

### 主要な発見事項

1. **makedata() メソッドの誤ったクエリ**（bkdata.py）
   - Blob モデルを検索すべきところ、BKdata を検索していた重大なバグを修正

2. **multiline テキストフィールドの移行**
   - db.StringProperty(multiline=True) → ndb.TextProperty への変換漏れを複数箇所で修正

3. **パフォーマンス問題**（bklistutl.py）
   - N+1 クエリ問題が残存しており、今後の最適化が必要

4. **依存関係の課題**
   - geo/geomodel.py の ndb 移行状況確認が必要
   - messageManager.getrefmembykey() のエラーハンドリング強化が推奨

### 推奨事項

1. geo/geomodel.py の ndb.Model 移行を確認・完了させる
2. messageManager モジュールのマイグレーション状況を確認
3. パフォーマンス最適化（N+1 クエリ問題の解決）を実施
4. エラーハンドリングの強化（特に refmem 取得処理）
