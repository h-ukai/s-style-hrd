# TODO-03: メール機能移行

**優先度**: 高
**作業種別**: コード実装・設定

---

## 概要

GAE Python 2.7 の Mail API（`/_ah/mail/*`）は Python 3.11 で廃止。
IMAP ポーリング + SMTP 送信方式への移行が必要。

---

## 現状の構成

### メール受信（IMAP ポーリング）
- **対象ファイル**: `application/email_receiver.py`
- **Cron ジョブ**: `cron.yaml` で 10分間隔で実行
- **エンドポイント**: `/tasks/check-incoming-mail`

### メール送信（SMTP）
- **対象ファイル**:
  - `application/messageManager.py`
  - `application/sendmsg.py`
- **使用ライブラリ**: Python 標準の `smtplib`

---

## ソースコード内のTODOコメント

### email_receiver.py

```python
# Line 28-32: IMAP設定がハードコード
# IMAP server configuration (should be in Cloud Secret Manager)
IMAP_SERVER = getattr(config, 'IMAP_SERVER', 'imap.example.com')
IMAP_PORT = getattr(config, 'IMAP_PORT', 993)
IMAP_USER = getattr(config, 'IMAP_USER', 'mailbox@example.com')
IMAP_PASSWORD = getattr(config, 'IMAP_PASSWORD', '')

# Line 51-52: セキュリティ警告
# REVIEW-L2: IMAP接続情報が平文で設定されている
# 推奨: Cloud Secret Manager から認証情報を取得するようにセキュリティを強化

# Line 90-93: 既読フラグの扱い
# REVIEW-L3: \Seen フラグを立てているが、マイグレーション仕様では「既読フラグ付与せず」
# 提案: GAE_MIGRATION_STATE.md の仕様(Line 190)と一致させるため、このフラグ付与を削除するか確認
imap.store(msg_id, '+FLAGS', '\\Seen')

# Line 155-161: Noneチェック追加済み
# REVIEW-L1: tanto の None チェックを追加（修正済み）
```

### messageManager.py

```python
# Line 23-27: SMTP設定がハードコード
# SMTP Configuration (should be in Cloud Secret Manager)
SMTP_SERVER = getattr(config, 'SMTP_SERVER', 'smtp.example.com')
SMTP_PORT = getattr(config, 'SMTP_PORT', 587)
SMTP_USER = getattr(config, 'SMTP_USER', '')
SMTP_PASSWORD = getattr(config, 'SMTP_PASSWORD', '')

# Line 45-46: セキュリティ警告
# REVIEW-L2: SMTP接続情報が平文で設定されている
# 推奨: Cloud Secret Manager から認証情報を取得するようにセキュリティを強化
```

### sendmsg.py

```python
# Line 153-158: SMTP認証がコメントアウト
# REVIEW-L2: SMTP認証がコメントアウトされている
# 推奨: Cloud Secret Manager から認証情報を取得し、server.login() を有効化
# Note: SMTP credentials should be stored in Cloud Secret Manager
```

### cron.yaml

```python
# Line 7-13: IMAP Cronジョブ
# IMAP メール受信ジョブ（/_ah/mail/* の代替）
- description: check incoming mail via IMAP
  url: /tasks/check-incoming-mail
  schedule: every 10 minutes
  timezone: Asia/Tokyo
  # 既存の email_receiver.py の処理ロジックを IMAP 版に変更する必要があります
```

### main.py

```python
# Line 64: memberSearchandMail 未移行
# from application.memberSearchandMail import memberSearchandMail, memberSearchandMailback, mailsendback  # TODO: Flask migration incomplete

# Line 68: mail_handler_route コメントアウト
# from application.email_receiver import mail_handler_route  # /_ah/mail/* は廃止、IMAP ポーリング方式に移行

# Line 123-140: memberSearchandMail ルートがコメントアウト
# TODO: memberSearchandMail Flask migration incomplete
```

---

## 必要な設定

### 1. IMAP 設定（メール受信用）

使用するメールサービス:
- **プロバイダ**: Nifty (`s-style.s8@nifty.com` の場合)
- **IMAPサーバー**: `imap.nifty.com`
- **IMAPポート**: 993 (SSL)

```python
# config.py に追加（または Secret Manager で管理）
IMAP_SERVER = 'imap.nifty.com'
IMAP_PORT = 993
IMAP_USER = 's-style.s8@nifty.com'
IMAP_PASSWORD = '****'  # Secret Manager から取得
```

### 2. SMTP 設定（メール送信用）

**オプションA: SendGrid（推奨）**
```python
SMTP_SERVER = 'smtp.sendgrid.net'
SMTP_PORT = 587
SMTP_USER = 'apikey'
SMTP_PASSWORD = os.environ.get('SENDGRID_API_KEY')
```

**オプションB: Nifty SMTP**
```python
SMTP_SERVER = 'smtp.nifty.com'
SMTP_PORT = 587
SMTP_USER = 's-style.s8@nifty.com'
SMTP_PASSWORD = '****'  # Secret Manager から取得
```

---

## 実装手順

### ステップ1: Secret Manager への移行

1. **シークレット作成**
   ```bash
   # IMAP
   echo -n "imap.nifty.com" | gcloud secrets create imap-server --data-file=-
   echo -n "s-style.s8@nifty.com" | gcloud secrets create imap-user --data-file=-
   echo -n "YOUR_PASSWORD" | gcloud secrets create imap-password --data-file=-

   # SMTP
   echo -n "smtp.sendgrid.net" | gcloud secrets create smtp-server --data-file=-
   echo -n "apikey" | gcloud secrets create smtp-user --data-file=-
   # SMTP_PASSWORD は SendGrid API Key を使用（既に app.yaml に設定済み）
   ```

2. **コード修正（email_receiver.py）**
   ```python
   from google.cloud import secretmanager

   def get_secret(secret_id):
       client = secretmanager.SecretManagerServiceClient()
       name = f"projects/s-style-hrd/secrets/{secret_id}/versions/latest"
       response = client.access_secret_version(request={"name": name})
       return response.payload.data.decode("UTF-8")

   IMAP_SERVER = get_secret('imap-server')
   IMAP_PORT = 993
   IMAP_USER = get_secret('imap-user')
   IMAP_PASSWORD = get_secret('imap-password')
   ```

3. **コード修正（messageManager.py）**
   ```python
   import os

   # SendGrid を使用する場合
   SMTP_SERVER = 'smtp.sendgrid.net'
   SMTP_PORT = 587
   SMTP_USER = 'apikey'
   SMTP_PASSWORD = os.environ.get('SENDGRID_API_KEY')
   ```

### ステップ2: main.py へのルート登録

```python
# email_receiver のインポートを有効化
from application.email_receiver import mail_handler_route

# Cron ジョブ用ルート
@test_bp.route('/tasks/check-incoming-mail', methods=['GET', 'POST'])
def check_incoming_mail():
    """IMAP mail polling handler (called by Cron)"""
    return mail_handler_route()
```

### ステップ3: memberSearchandMail の Flask 移行

**対象ファイル**: `application/memberSearchandMail.py`

現状の問題点:
- webapp2 クラスベースハンドラーのまま
- Flask の request/response 形式に未対応

対応方針:
1. クラスを関数ベースに変換
2. `self.request.get()` → `request.form.get()` / `request.args.get()`
3. `self.response.out.write()` → `return render_template()`

---

## 作業チェックリスト

### IMAP（メール受信）
- [ ] IMAP サーバー情報を確認（プロバイダのドキュメント参照）
- [ ] Secret Manager に IMAP 認証情報を登録
- [ ] email_receiver.py を修正して Secret Manager から認証情報を取得
- [ ] main.py に `/tasks/check-incoming-mail` ルートを登録
- [ ] cron.yaml の設定を確認
- [ ] 既読フラグの扱いを決定（\Seen を付けるかどうか）
- [ ] テスト環境でメール受信テスト

### SMTP（メール送信）
- [ ] SendGrid または SMTP プロバイダを決定
- [ ] Secret Manager に SMTP 認証情報を登録
- [ ] messageManager.py を修正して Secret Manager / 環境変数から認証情報を取得
- [ ] sendmsg.py の SMTP 認証コードを有効化
- [ ] テスト環境でメール送信テスト

### memberSearchandMail 移行
- [ ] memberSearchandMail.py を Flask 関数ベースに変換
- [ ] memberSearchandMailback.py を Flask 関数ベースに変換
- [ ] mailsendback を Flask 関数ベースに変換
- [ ] main.py にルートを登録
- [ ] テスト環境で動作確認

---

## テスト方法

### メール受信テスト
```bash
# Cron ジョブを手動実行
curl -X POST https://s-style-hrd.appspot.com/test/tasks/check-incoming-mail \
  -H "X-Appengine-Cron: true"
```

### メール送信テスト
アプリケーションからメッセージを投稿し、メール送信が行われることを確認

---

## 関連ドキュメント

- [SendGrid SMTP](https://docs.sendgrid.com/for-developers/sending-email/integrating-with-the-smtp-api)
- [Cloud Secret Manager](https://cloud.google.com/secret-manager/docs)
- [Nifty IMAP設定](https://support.nifty.com/support/manual/mail/imap.htm)
