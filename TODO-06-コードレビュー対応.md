# TODO-06: コードレビュー対応

**優先度**: 低〜中
**作業種別**: コード修正

---

## 概要

コードレビュー（REVIEW-L1, L2, L3）で指摘された技術的な問題への対応。
主に ndb クエリ構文、例外処理、パフォーマンスに関する指摘。

---

## REVIEW レベル説明

- **REVIEW-L1**: 必須修正（動作に影響する可能性あり）
- **REVIEW-L2**: 推奨修正（パフォーマンス・保守性向上）
- **REVIEW-L3**: 任意修正（コード品質向上）

---

## REVIEW-L1: 必須修正

### 1. ndb クエリ構文の修正

**ファイル**: `application/models/bksearchaddress.py:48, 63, 80`
```python
# REVIEW-L1: Incorrect ndb query syntax - cannot filter query object directly on ndb.Model
# REVIEW-L1: Incorrect ndb query syntax - multiple filters as positional args

# 修正例
# 誤: Query(kind=...) with bare filter
# 正: Model.query().filter(...)
```

**ファイル**: `application/models/bksearchdata.py:43, 71, 92`
```python
# REVIEW-L1: Incorrect ndb query syntax - Query(kind=...) with bare filter
# REVIEW-L1: Incorrect ndb query syntax - Query(kind=...) with bare filter/order
```

**対応**: ndb.Query() ではなく Model.query() を使用し、filter() メソッドでフィルタを適用

---

### 2. KeyProperty の kind パラメータ

**ファイル**: 複数
```python
# REVIEW-L1: ndb.KeyProperty の kind パラメータに文字列ではなくクラス名を使用している
# - application/models/bksearchaddress.py:113, 174, 194
# - application/models/bksearchdata.py:293
# - application/models/msgcombinator.py:9
```

**対応**:
```python
# 修正前
ref_member = ndb.KeyProperty(kind='member')

# 修正後（クラス参照）
from application.models.member import member
ref_member = ndb.KeyProperty(kind=member)

# または文字列のまま（これも有効）
ref_member = ndb.KeyProperty(kind='member')
```

---

### 3. ndb.Key() の使用方法

**ファイル**: `application/bklistutl.py:242`
```python
# REVIEW-L1: Incorrect usage - ndb.get_multi() for multiple keys, not ndb.Key()
```

**対応**:
```python
# 複数キーの一括取得
keys = [ndb.Key(Model, id) for id in ids]
entities = ndb.get_multi(keys)
```

---

### 4. key() vs key プロパティ

**ファイル**: `application/cron.py:58`
```python
# REVIEW-L1: meslist[i].key() → meslist[i].key (ndb では key プロパティ)
```

**ファイル**: `application/messageManager.py:218, 419`
```python
# REVIEW-L1: memdb.key() → memdb.key (ndb では key プロパティ)
# REVIEW-L1: key() → key (ndb プロパティ)
```

**対応**: `entity.key()` を `entity.key` に変更

---

### 5. Cloud Tasks タスク作成

**ファイル**: `application/matching.py:285, 297, 434`
```python
# REVIEW-L1: Cloud Tasksタスク作成コードが不完全
# REVIEW-L1: 修正: Cloud Tasks Client で task を作成
```

**対応**: Cloud Tasks クライアントを使用した正しいタスク作成実装

---

## REVIEW-L2: 推奨修正

### 1. パフォーマンス問題

**ファイル**: `application/bklistutl.py:53-59`
```python
# REVIEW-L2: Performance - 重複チェックでfetch(1000)は多い可能性
# 推奨: 必要最低限の件数に変更、またはKeys onlyクエリで高速化
mylst = cls.getlistbykey(corp,mes.key).fetch(1000)

# REVIEW-L2: N+1 query problem - refbk.get() in loop
# 推奨: ndb.get_multi() でまとめて取得
```

**対応**:
```python
# Keys-only クエリで高速化
keys = cls.getlistbykey(corp, mes.key).fetch(1000, keys_only=True)

# N+1 問題の解消
entities = ndb.get_multi(keys)
```

**ファイル**: `application/duplicationcheck.py:51`
```python
# REVIEW-L2: ndb query efficiency - avoid query.count() + fetch() pattern
```

---

### 2. 例外処理の改善

**ファイル**: `application/timemanager.py:48-49, 67-68`
```python
# REVIEW-L2: 例外処理の不足: 全例外をキャッチするのは推奨されない
# 推奨: except AttributeError as e: のように特定の例外をキャッチ
```

**ファイル**: `application/view.py:43-44`
```python
# REVIEW-L2: 例外処理の不足: match() が None を返す可能性がある
# 推奨: match の結果を確認してから group() を呼び出す
```

**対応**:
```python
# 修正例
match = re.match(pattern, text)
if match:
    result = match.group(1)
else:
    result = default_value
```

---

### 3. IndexError の可能性

**ファイル**: `application/matching.py:620-621`
```python
# REVIEW-L2: bklist[0] が空リストの場合 IndexError が発生
# 推奨: len(bklist) > 0 のチェックを追加
```

**対応**:
```python
if bklist and len(bklist) > 0:
    first_item = bklist[0]
else:
    # デフォルト処理
```

---

### 4. ndb コンテキスト

**ファイル**: `application/index.py:57`
```python
# REVIEW-L2: ndb query fetch() may need context manager (transaction/async context)
```

---

## REVIEW-L3: 任意修正

### 1. Python 3 互換性（u"" プレフィックス）

**複数ファイル**:
```python
# REVIEW-L3: u"プレフィックス"を削除（Python 3互換性）
# - application/bkdchk.py:23
# - application/json.py:73, 244
# - application/memberedit.py:21
# - application/wordstocker.py:7
```

**注意**: Python 3 では全ての文字列が Unicode なので u"" は不要だが、残しても動作する

---

### 2. 数値処理の改善

**ファイル**: `application/GqlEncoder.py:142-143`
```python
# REVIEW-L3: 提案: 数値処理の堅牢性向上
# 推奨: locale.format や格式文字列の活用で可読性向上
```

---

## 作業チェックリスト

### REVIEW-L1（必須）
- [ ] bksearchaddress.py の ndb クエリ構文を修正
- [ ] bksearchdata.py の ndb クエリ構文を修正
- [ ] KeyProperty の kind パラメータを確認・修正
- [ ] key() → key プロパティに変更
- [ ] matching.py の Cloud Tasks タスク作成を修正

### REVIEW-L2（推奨）
- [ ] bklistutl.py のパフォーマンス改善
- [ ] duplicationcheck.py のクエリ効率化
- [ ] timemanager.py の例外処理を改善
- [ ] view.py の例外処理を改善
- [ ] matching.py の IndexError 対策

### REVIEW-L3（任意）
- [ ] u"" プレフィックスの削除（必要に応じて）
- [ ] 数値処理の改善（必要に応じて）

---

## 関連ドキュメント

- [Cloud NDB ドキュメント](https://googleapis.dev/python/python-ndb/latest/)
- [Cloud Tasks](https://cloud.google.com/tasks/docs)
