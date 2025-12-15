# TODO-04: 本番移行対応

**優先度**: 中（テスト完了後に実施）
**作業種別**: 設定変更・コード修正
**参照**: `PRODUCTION-REVERT-CHECKLIST.md`

---

## 概要

テスト環境（`/test/*`）から本番環境への移行時に必要な変更。
Blueprint の URL プレフィックス、リダイレクト先、静的ファイルパスの変更が必要。

---

## 変更一覧

### 1. Blueprint URL プレフィックス変更

**ファイル**: `migration-src/main.py:17`

```python
# 現在（テスト環境）
test_bp = Blueprint('test', __name__, url_prefix='/test')

# 本番移行後
main_bp = Blueprint('main', __name__, url_prefix='')
```

**影響範囲**:
- 全ての `@test_bp.route()` を `@main_bp.route()` に変更
- または Blueprint 名を `test_bp` のまま URL プレフィックスのみ変更

---

### 2. dispatch.yaml の /test ルール削除

**ファイル**: `dispatch.yaml`

```yaml
# 現在（テスト環境）
dispatch:
  - url: "*/test"
    service: test-service
  - url: "*/test/*"
    service: test-service

# 本番移行後：上記ルールを削除
dispatch:
  # /test ルールは削除
```

**注意**: dispatch.yaml の変更後は `gcloud app deploy dispatch.yaml` でデプロイ

---

### 3. ログインリダイレクト先変更

**ファイル**: `migration-src/application/SecurePage.py:21`

```python
# 現在（テスト環境）
return redirect('/test/login?' + urlstr)

# 本番移行後
return redirect('/login?' + urlstr)
```

**ファイル**: `migration-src/application/proc.py:38`

```python
# 現在（テスト環境）
return redirect('/test/login?' + urlstr)

# 本番移行後
return redirect('/login?' + urlstr)
```

---

### 4. app.yaml の service 行削除

**ファイル**: `migration-src/app.yaml:3`

```yaml
# 現在（テスト環境）
service: test-service

# 本番移行後：この行を削除（default サービスになる）
# service: test-service  # 削除
```

---

### 5. 静的ファイルハンドラーの変更

**ファイル**: `migration-src/app.yaml`

```yaml
# 現在（テスト環境）
handlers:
- url: /test/js
  static_dir: static_dir/js
- url: /test/css
  static_dir: static_dir/css
- url: /test/img
  static_dir: static_dir/img

# 本番移行後：/test プレフィックスを削除
handlers:
- url: /js
  static_dir: static_dir/js
- url: /css
  static_dir: static_dir/css
- url: /img
  static_dir: static_dir/img
```

---

### 6. テンプレート内の静的ファイルパス

テンプレート内で `/test/css/`, `/test/js/` などを使用している場合は変更が必要。

**確認コマンド**:
```bash
grep -rn "/test/" migration-src/templates/
```

**変更例**:
```html
<!-- 現在（テスト環境） -->
<link rel="stylesheet" href="/test/css/baselayout.css">

<!-- 本番移行後 -->
<link rel="stylesheet" href="/css/baselayout.css">
```

---

## 本番デプロイ手順

### オプション A: /test ルーティングを完全に削除（推奨）

1. **main.py の Blueprint プレフィックス変更**
   ```python
   # test_bp → main_bp に名前変更（または url_prefix を空に）
   main_bp = Blueprint('main', __name__, url_prefix='')
   ```

2. **app.yaml の修正**
   - `service: test-service` 行を削除
   - 静的ファイルハンドラーから `/test` プレフィックスを削除

3. **リダイレクト先の修正**
   - `SecurePage.py` の `/test/login` → `/login`
   - `proc.py` の `/test/login` → `/login`

4. **dispatch.yaml の /test ルール削除**

5. **デプロイ**
   ```bash
   cd migration-src
   gcloud app deploy app.yaml --project=s-style-hrd
   gcloud app deploy dispatch.yaml --project=s-style-hrd
   ```

### オプション B: /test を内部アクセス専用に

1. **GAE IAP を設定**して test-service へのアクセスを社内IPのみに制限
2. 本番 default サービスは別途デプロイ

---

## 移行スクリプト例

```bash
#!/bin/bash
# production-migrate.sh

# 1. バックアップ
cp migration-src/main.py migration-src/main.py.test-backup
cp migration-src/app.yaml migration-src/app.yaml.test-backup
cp migration-src/application/SecurePage.py migration-src/application/SecurePage.py.test-backup
cp migration-src/application/proc.py migration-src/application/proc.py.test-backup

# 2. main.py: Blueprint プレフィックス変更
sed -i "s/url_prefix='\/test'/url_prefix=''/g" migration-src/main.py
sed -i "s/test_bp/main_bp/g" migration-src/main.py

# 3. app.yaml: service 行削除、静的ファイルパス変更
sed -i '/^service: test-service/d' migration-src/app.yaml
sed -i 's/url: \/test\//url: \//g' migration-src/app.yaml

# 4. リダイレクト先変更
sed -i "s/\/test\/login/\/login/g" migration-src/application/SecurePage.py
sed -i "s/\/test\/login/\/login/g" migration-src/application/proc.py

# 5. dispatch.yaml から /test ルール削除（手動確認推奨）
echo "dispatch.yaml の /test ルールを手動で削除してください"

echo "本番移行準備完了。デプロイ前に変更内容を確認してください。"
```

---

## 作業チェックリスト

- [ ] main.py の Blueprint URL プレフィックスを空に変更
- [ ] app.yaml の `service: test-service` を削除
- [ ] app.yaml の静的ファイルハンドラーから `/test` を削除
- [ ] SecurePage.py のリダイレクト先を `/login` に変更
- [ ] proc.py のリダイレクト先を `/login` に変更
- [ ] dispatch.yaml から `/test` ルールを削除
- [ ] テンプレート内の `/test/` パスを確認・修正
- [ ] ローカルで動作確認
- [ ] 本番デプロイ
- [ ] 全ルートの動作確認

---

## ロールバック手順

本番移行後に問題が発生した場合:

```bash
# 1. テスト環境のバックアップからリストア
cp migration-src/main.py.test-backup migration-src/main.py
cp migration-src/app.yaml.test-backup migration-src/app.yaml
cp migration-src/application/SecurePage.py.test-backup migration-src/application/SecurePage.py
cp migration-src/application/proc.py.test-backup migration-src/application/proc.py

# 2. test-service として再デプロイ
gcloud app deploy migration-src/app.yaml --project=s-style-hrd
```

---

## 関連ドキュメント

- **PRODUCTION-REVERT-CHECKLIST.md** - 詳細なチェックリスト
