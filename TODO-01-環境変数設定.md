# TODO-01: 環境変数・シークレット設定

**優先度**: 最高（本番移行前に必須）
**作業種別**: 設定作業

---

## 概要

アプリケーション動作に必要な環境変数とシークレットの設定。
現在、多くの設定値がハードコードまたはプレースホルダーになっている。

---

## 必要な環境変数一覧

### 1. Flask アプリケーション設定

| 変数名 | 用途 | 現状 | 設定箇所 |
|--------|------|------|----------|
| `SECRET_KEY` | Flaskセッション暗号化キー | デフォルト値使用 | app.yaml |

**対象ファイル**: `main.py:13`
```python
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-please-change-in-production')
```

**対応**:
1. 強力なランダム文字列を生成: `python -c "import secrets; print(secrets.token_hex(32))"`
2. Cloud Secret Manager に保存
3. app.yaml の env_variables に追加

---

### 2. reCAPTCHA 設定

| 変数名 | 用途 | 現状 | 設定箇所 |
|--------|------|------|----------|
| `RECAPTCHA_SITE_KEY` | reCAPTCHA サイトキー | テスト環境に設定済み | app.yaml |
| `RECAPTCHA_SECRET_KEY` | reCAPTCHA シークレットキー | テスト環境に設定済み | app.yaml |

**対象ファイル**: `app.yaml:95-96`（現在設定済み）

**本番対応**:
- 本番用の reCAPTCHA キーペアを Google reCAPTCHA Console で取得
- app.yaml.template のプレースホルダーを本番値に置換

---

### 3. SMTP 設定（Cloud Secret Manager 推奨）

**使用するSMTPサーバー**: Xserver

| 変数名 | 用途 | 設定値 | 設定箇所 |
|--------|------|--------|----------|
| `SMTP_SERVER` | SMTPサーバーホスト | `sv1231.xserver.jp` | Secret Manager |
| `SMTP_PORT` | SMTPポート | `465`（SSL/TLS推奨）または `587`（STARTTLS） | Secret Manager |
| `SMTP_USER` | SMTP認証ユーザー | `info@s-style.ne.jp` | Secret Manager |
| `SMTP_PASSWORD` | SMTP認証パスワード | （Secret Managerに保存） | Secret Manager |

**対象ファイル**:
- `application/messageManager.py:23-27`
- `application/sendmsg.py:153-158`

**対応手順**:
1. Cloud Secret Manager でシークレットを作成
   ```bash
   echo -n "sv1231.xserver.jp" | gcloud secrets create smtp-server --data-file=-
   echo -n "465" | gcloud secrets create smtp-port --data-file=-
   echo -n "info@s-style.ne.jp" | gcloud secrets create smtp-user --data-file=-
   echo -n "YOUR_PASSWORD" | gcloud secrets create smtp-password --data-file=-
   ```
2. コードを修正して Secret Manager から取得
```python
from google.cloud import secretmanager

def get_secret(secret_id):
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/s-style-hrd/secrets/{secret_id}/versions/latest"
    response = client.access_secret_version(request={"name": name})
    return response.payload.data.decode("UTF-8")

SMTP_SERVER = get_secret('smtp-server')
SMTP_PORT = int(get_secret('smtp-port'))
SMTP_USER = get_secret('smtp-user')
SMTP_PASSWORD = get_secret('smtp-password')
```

**SSL/TLS接続の場合（ポート465）**:
```python
import smtplib
import ssl

context = ssl.create_default_context()
with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, context=context) as server:
    server.login(SMTP_USER, SMTP_PASSWORD)
    server.send_message(message)
```

---

### 4. IMAP 設定（Cloud Secret Manager 推奨）

**使用するIMAPサーバー**: Xserver

| 変数名 | 用途 | 設定値 | 設定箇所 |
|--------|------|--------|----------|
| `IMAP_SERVER` | IMAPサーバーホスト | `sv1231.xserver.jp` | Secret Manager |
| `IMAP_PORT` | IMAPポート | `993`（SSL） | Secret Manager |
| `IMAP_USER` | IMAP認証ユーザー | `info@s-style.ne.jp` | Secret Manager |
| `IMAP_PASSWORD` | IMAP認証パスワード | （SMTPと同じ） | Secret Manager |

**対象ファイル**: `application/email_receiver.py:28-32`

**対応手順**:
```bash
echo -n "sv1231.xserver.jp" | gcloud secrets create imap-server --data-file=-
echo -n "993" | gcloud secrets create imap-port --data-file=-
echo -n "info@s-style.ne.jp" | gcloud secrets create imap-user --data-file=-
# パスワードはSMTPと同じ（smtp-passwordを共用可能）
```

**注意**: SMTP/IMAPで同じメールアカウントを使用するため、パスワードは共通

---

### 5. GCP プロジェクト設定

| 変数名 | 用途 | 現状 | 設定箇所 |
|--------|------|------|----------|
| `GCP_PROJECT` | GCPプロジェクトID | 環境変数から取得 | app.yaml |
| `BASE_URL` | アプリケーションベースURL | config.py でハードコード | app.yaml |

**対象ファイル**:
- `application/bksearchutl.py:293, 303`
- `application/tantochangetasks.py:22, 49`

**対応**:
```yaml
# app.yaml に追加
env_variables:
  GCP_PROJECT: 's-style-hrd'
  BASE_URL: 'https://s-style-hrd.appspot.com'
```

---

### 6. Redis 設定（オプション）

| 変数名 | 用途 | 現状 | 設定箇所 |
|--------|------|------|----------|
| `REDIS_HOST` | Redis ホスト | localhost | app.yaml |
| `REDIS_PORT` | Redis ポート | 6379 | app.yaml |

**対象ファイル**: `application/bksearchutl.py:31-32`

**注意**: GAE Standard では Memorystore for Redis の使用にはVPCコネクタが必要

---

### 7. GCS バケット設定

| 変数名 | 用途 | 現状 | 設定箇所 |
|--------|------|------|----------|
| `GCS_BUCKET_NAME` | GCSバケット名 | YOUR_BUCKET | app.yaml |

**対象ファイル**: `application/mapreducemapper.py:119-122`
```python
# 現状（プレースホルダー）
entity.thumbnailurl = f"https://storage.googleapis.com/YOUR_BUCKET/{entity.blobKey}"
```

**対応**:
1. GCSバケット `s-style-hrd-blobs` を作成
2. app.yaml に環境変数追加
3. コードを修正して環境変数を参照

---

## 作業チェックリスト

- [ ] Cloud Secret Manager API を有効化
- [ ] `google-cloud-secret-manager` を requirements.txt に追加
- [ ] シークレット取得ユーティリティ関数を作成
- [ ] SMTP シークレットを Secret Manager に登録
- [ ] IMAP シークレットを Secret Manager に登録
- [ ] `SECRET_KEY` を生成して app.yaml に設定
- [ ] `GCP_PROJECT` を app.yaml に設定
- [ ] `BASE_URL` を app.yaml に設定
- [ ] `GCS_BUCKET_NAME` を app.yaml に設定
- [ ] messageManager.py を修正して Secret Manager を使用
- [ ] email_receiver.py を修正して Secret Manager を使用
- [ ] sendmsg.py を修正して Secret Manager を使用

---

## app.yaml 環境変数の最終形

```yaml
env_variables:
  SECRET_KEY: 'YOUR_GENERATED_SECRET_KEY'
  RECAPTCHA_SITE_KEY: 'YOUR_RECAPTCHA_SITE_KEY'
  RECAPTCHA_SECRET_KEY: 'YOUR_RECAPTCHA_SECRET_KEY'
  GCP_PROJECT: 's-style-hrd'
  BASE_URL: 'https://s-style-hrd.appspot.com'
  GCS_BUCKET_NAME: 's-style-hrd-blobs'
  # REDIS_HOST: 'your-redis-host'  # Memorystore使用時のみ
  # REDIS_PORT: '6379'
```

**注意**: SMTP認証情報はCloud Secret Managerで管理（app.yamlには含めない）

---

## 関連ドキュメント

- [Cloud Secret Manager](https://cloud.google.com/secret-manager/docs)
- [GAE 環境変数](https://cloud.google.com/appengine/docs/standard/python3/config/appref#environment_variables)
