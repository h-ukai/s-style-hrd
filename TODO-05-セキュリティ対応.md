# TODO-05: セキュリティ対応

**優先度**: 高（本番移行前に対応必須）
**作業種別**: コード修正

---

## 概要

コードレビューで発見されたセキュリティリスクへの対応。
認証情報の平文保存、XSS脆弱性、CORS設定、認証なしエンドポイントなど。

---

## 対応済み項目

### SecurePageBase.py テストモードバイパス【完了】

**ファイル**: `migration-src/application/SecurePageBase.py`
**対応日**: 2025-12-01

**問題**: `/test/` 経由のアクセスでセキュリティチェック（認証）をスキップする機能があった

**対応**: テストモードブロック全体を削除し、常に dbsession 認証を使用するよう修正

---

## 未対応項目

### 1. 認証情報の平文保存【優先度: 高】

#### SMTP 認証情報

**ファイル**: `application/messageManager.py:23-27, 45-46`
```python
# 現状: ハードコードまたは config.py から取得
SMTP_SERVER = getattr(config, 'SMTP_SERVER', 'smtp.example.com')
SMTP_PASSWORD = getattr(config, 'SMTP_PASSWORD', '')

# REVIEW-L2: SMTP接続情報が平文で設定されている
# 推奨: Cloud Secret Manager から認証情報を取得するようにセキュリティを強化
```

#### IMAP 認証情報

**ファイル**: `application/email_receiver.py:28-32, 51-52`
```python
# 現状: config.py から取得
IMAP_PASSWORD = getattr(config, 'IMAP_PASSWORD', '')

# REVIEW-L2: IMAP接続情報が平文で設定されている
# 推奨: Cloud Secret Manager から認証情報を取得するようにセキュリティを強化
```

**対応**: `TODO-01-環境変数設定.md` に詳細手順を記載

---

### 2. CORS 設定のワイルドカード使用【優先度: 中】

**ファイル**: `application/sendmsg.py:62-63`
```python
# REVIEW-L3: CORSヘッダーのワイルドカード使用
# 効果: 本番環境ではセキュリティリスク。許可するドメインを制限することを推奨
```

**対応**:
```python
# 修正前（推測）
response.headers['Access-Control-Allow-Origin'] = '*'

# 修正後
ALLOWED_ORIGINS = ['https://s-style-hrd.appspot.com']
origin = request.headers.get('Origin')
if origin in ALLOWED_ORIGINS:
    response.headers['Access-Control-Allow-Origin'] = origin
```

---

### 3. XSS 脆弱性【優先度: 中】

**ファイル**: `application/mapreducemapper.py`

```python
# Line 113: HTML生成時のエスケープ不足
# REVIEW-L2: SECURITY - XSS Risk: HTML generation without proper escaping

# Line 129: タイトルのエスケープ不足
# REVIEW-L2: Potential XSS - entity.title should be HTML-escaped

# Line 132: コンテンツのエスケープ不足
# REVIEW-L2: Potential XSS - entity.content should be HTML-escaped

# Line 141: ファイル名のエスケープ不足
# REVIEW-L2: Potential XSS - filename not escaped in HTML attribute
```

**対応**:
```python
from markupsafe import escape

# HTML 生成時にエスケープを適用
entity.html = f'<a href="{escape(blob.bloburl)}" target="_blank">'
entity.html += f'<img src="{escape(blob.thumbnailurl)}" title="{escape(blob.filename)}" /></a>'

# タイトル・コンテンツもエスケープ
escaped_title = escape(entity.title) if entity.title else ''
escaped_content = escape(entity.content) if entity.content else ''
```

---

### 4. 認証なしエンドポイント【優先度: 高】

#### CSV アップロード（認証なし）

**ファイル**: `application/uploadbkdata.py:19`
```python
# ⚠️ SECURITY WARNING: CSV upload handler without authentication
```

**ファイル**: `application/uploadbkdataformaster.py:17`
```python
# ⚠️ SECURITY WARNING: CSV upload for master data without authentication
```

**対応**:
1. これらのエンドポイントに認証チェックを追加
2. または、内部ネットワークからのみアクセス可能にする（IAP 設定）

```python
from application.SecurePageBase import SecurePageBase

def bkdata_upload_route():
    # 認証チェックを追加
    page = SecurePageBase()
    if not page.auth:
        return redirect('/login')
    # ... 既存の処理
```

#### 一括削除エンドポイント

**ファイル**: `application/RemoveAll.py:17, 88`
```python
# ⚠️ SECURITY WARNING: This endpoint performs bulk data operations
# ⚠️ SECURITY WARNING: SQL injection risk in original GQL implementation
```

**対応**:
1. 管理者権限チェックを追加
2. 本番環境では無効化を検討

---

### 5. Flask SECRET_KEY【優先度: 高】

**ファイル**: `main.py:13`
```python
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-please-change-in-production')
```

**問題**: デフォルト値が使用されるとセッションハイジャックのリスク

**対応**:
1. 強力なランダム文字列を生成
   ```bash
   python -c "import secrets; print(secrets.token_hex(32))"
   ```
2. app.yaml の env_variables に設定

---

## 作業チェックリスト

### 認証情報管理
- [ ] Cloud Secret Manager API を有効化
- [ ] `google-cloud-secret-manager` を requirements.txt に追加
- [ ] SMTP 認証情報を Secret Manager に移行
- [ ] IMAP 認証情報を Secret Manager に移行
- [ ] Flask SECRET_KEY を環境変数に設定

### CORS 設定
- [ ] sendmsg.py の CORS 設定を特定ドメインに制限

### XSS 対策
- [ ] mapreducemapper.py の HTML 生成箇所にエスケープを追加
- [ ] その他の HTML 生成箇所を確認

### 認証チェック
- [ ] uploadbkdata.py に認証チェックを追加
- [ ] uploadbkdataformaster.py に認証チェックを追加
- [ ] RemoveAll.py に管理者権限チェックを追加

---

## セキュリティチェックリスト（本番移行前）

- [ ] デフォルトの SECRET_KEY が使用されていないことを確認
- [ ] 認証情報が平文でコードに含まれていないことを確認
- [ ] 全ての管理機能に認証チェックがあることを確認
- [ ] CORS 設定が適切であることを確認
- [ ] XSS 脆弱性がないことを確認
- [ ] SQL/GQL インジェクション対策が施されていることを確認

---

## 関連ドキュメント

- [Cloud Secret Manager](https://cloud.google.com/secret-manager/docs)
- [Flask Security](https://flask.palletsprojects.com/en/2.3.x/security/)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
