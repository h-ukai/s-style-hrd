# 本番運用時に戻すべき修正チェックリスト

このドキュメントは、テスト環境（test-service）用に行った修正のうち、本番環境へのデプロイ前に戻すか削除すべき変更を記載しています。

**作成日**: 2025-11-30
**最終更新**: 2025-12-01
**対象バージョン**: 20251130t134300 以降

---

## 修正状況サマリー

| # | 項目 | 状態 | 対応日 |
|---|------|------|--------|
| 1.1 | SecurePageBase.py テストモードバイパス | ✅ **修正済み** | 2025-12-01 |
| 2.1 | dispatch.yaml /test ルーティング | ⏸️ テスト環境用（本番デプロイ時に対応） | - |
| 2.2 | main.py Blueprint URL プレフィックス | ⏸️ テスト環境用（本番デプロイ時に対応） | - |
| 3.1 | SecurePage.py ログインリダイレクト | ⏸️ テスト環境用（本番デプロイ時に対応） | - |
| 3.2 | proc.py ログインリダイレクト | ⏸️ テスト環境用（本番デプロイ時に対応） | - |

---

## 1. セキュリティ上の最重要事項

### 1.1 SecurePageBase.py テストモードバイパス【削除必須】 ✅ 修正済み

**ファイル**: `migration-src/application/SecurePageBase.py`
**行番号**: 77-96 (旧)

**問題**: `/test/` 経由のアクセスでセキュリティチェック（認証）をスキップする機能が追加されていた。

**削除したコード**:
```python
# /test/ 経由の場合、セキュリティチェックをスキップ（開発・テスト用）
if self.is_test_mode:
    self.auth = True
    self.tmpl_val['auth'] = True
    self.userID = "test_user"
    self.userkey = "test_key"
    self.memberID = request.args.get("memberID", "")
    self.memdb = None
    self.tanto = None
    self.tmpl_val["userID"] = self.userID
    self.tmpl_val["name"] = "テストユーザー"
    self.tmpl_val["status"] = "管理者"
    self.tmpl_val["phone"] = ""
    self.tmpl_val["mobilephone"] = ""
    self.tmpl_val["usermail"] = ""
    self.tmpl_val["userkey"] = self.userkey
    self.tmpl_val["memberID"] = self.memberID
    self.tmpl_val["memdb"] = self.memdb
    self.tmpl_val["tankey"] = ""
    self.dirpath = self.pathParts[-1].split(u'?')[0] if self.pathParts else ""
```

**対応完了**: 2025-12-01 - テストモードブロック全体を削除し、常に dbsession 認証を使用するよう修正。

---

## 2. ルーティング関連（本番デプロイ時に対応）

### 2.1 dispatch.yaml の /test ルーティング【削除推奨】

**ファイル**: `dispatch.yaml`

**現在の設定**:
```yaml
dispatch:
  - url: "*/test"
    service: test-service
  - url: "*/test/*"
    service: test-service
```

**本番対応**:
- **推奨**: dispatch.yaml から /test ルールを完全に削除
- これにより外部から test-service にアクセスできなくなる
- または、IAP (Identity-Aware Proxy) で test-service へのアクセスを制限

### 2.2 main.py Blueprint URL プレフィックス【変更必要】

**ファイル**: `migration-src/main.py`
**行番号**: 17

**現在のコード**:
```python
test_bp = Blueprint('test', __name__, url_prefix='/test')
```

**本番対応**:
```python
# url_prefix を空にするか、本番用のプレフィックスに変更
main_bp = Blueprint('main', __name__, url_prefix='')
```

または、本番サービスでは Blueprint を使用せず直接 `@app.route` を使用。

---

## 3. リダイレクト先の変更（本番デプロイ時に対応）

### 3.1 SecurePage.py ログインリダイレクト

**ファイル**: `migration-src/application/SecurePage.py`
**行番号**: 21

**現在のコード**:
```python
return redirect('/test/login?' + urlstr)
```

**本番対応**:
```python
return redirect('/login?' + urlstr)
```

### 3.2 proc.py ログインリダイレクト

**ファイル**: `migration-src/application/proc.py`
**行番号**: 38

**現在のコード**:
```python
return redirect('/test/login?' + urlstr)
```

**本番対応**:
```python
return redirect('/login?' + urlstr)
```

---

## 4. 推奨される本番デプロイ手順

### オプション A: /test ルーティングを完全に削除

1. ✅ `SecurePageBase.py` のテストモードブロックを削除 **（完了）**
2. `dispatch.yaml` から /test ルールを削除
3. `main.py` の Blueprint プレフィックスを空に変更
4. `SecurePage.py`, `proc.py` のリダイレクト先を `/login` に変更
5. デプロイ

### オプション B: /test を内部アクセス専用に

1. ✅ `SecurePageBase.py` のテストモードブロックを削除 **（完了）**
2. GAE IAP を設定して test-service へのアクセスを社内IPのみに制限
3. 本番 default サービスは別途デプロイ

---

## 5. 変更履歴

| 日付 | 項目 | 変更内容 | 理由 |
|------|------|----------|------|
| 2025-11-30 | SecurePageBase.py | テストモード追加 | 開発効率化 |
| 2025-11-30 | dispatch.yaml | /test ルール追加 | test-service ルーティング |
| 2025-11-30 | SecurePage.py | リダイレクト先を /test/login に | Blueprint 対応 |
| 2025-11-30 | proc.py | リダイレクト先を /test/login に | Blueprint 対応 |
| 2025-11-30 | main.py | Blueprint /test プレフィックス追加 | dispatch.yaml 対応 |
| **2025-12-01** | **SecurePageBase.py** | **テストモードバイパス削除** | **テスト環境でも認証必須に** |

---

## 6. 確認用コマンド

テストモードが有効かどうかを確認:
```bash
grep -n "is_test_mode" migration-src/application/SecurePageBase.py
```

/test リダイレクトが残っているかを確認:
```bash
grep -rn "/test/login" migration-src/application/
```

dispatch.yaml の /test ルールを確認:
```bash
grep -n "test" dispatch.yaml
```
