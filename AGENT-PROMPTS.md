## メインエージェント実行用プロンプト

```
## GAE マイグレーション並列テスト

以下の3つのルートを並列でテストします。Taskツールで3つのサブエージェントを同時に起動してください。

**重要**: 各サブエージェントには `model: "opus"` を指定してください。

### 事前準備
1. gcloud 認証を確認（`gcloud auth list`）
2. 認証が必要ならユーザーに `gcloud auth login` を依頼

### 各サブエージェントへの指示

**作業ディレクトリ**: C:\Users\hrsuk\prj\s-style-hrd
**migration-src ディレクトリ**: C:\Users\hrsuk\prj\s-style-hrd\migration-src

#### ステップ1: 修正カタログを読む（必須・最初に実行）

`MIGRATION-FIXES-CATALOG.md` を読み、以下の修正パターンを把握：
- `|default_if_none:""` → `|default("")`
- `|default:""` → `|default("")`
- `|floatformat:"-2"` → `|float|round(2)`
- `|join:" "` → `|join(" ")`
- KeyProperty の `.get()` 追加
- 逆参照の明示的クエリ化

#### ステップ2: テンプレートの事前チェック

担当ルートに対応するテンプレートファイルを読み、上記パターンが残っていないか確認。
残っていれば**テスト前に修正**。

#### ステップ3: テスト実行

```bash
curl -s -o /dev/null -w "%{http_code}" "https://s-style-hrd.appspot.com/test/{ROUTE_PATH}"
```

#### ステップ4: エラー時の対応（最大5回ループ）

1. ログ確認:
   ```bash
   gcloud app logs read -s test-service --limit=30 2>&1 | grep -A 10 "ERROR\|Exception"
   ```

2. エラー修正

3. 修正をログに記録（`SUBAGENT-FIX-LOG.md` に追記）:
   ```markdown
   ## {ルート名} - ループ {N}
   - 日時: {YYYY-MM-DD HH:MM:SS}
   - ファイル: {修正ファイルパス}
   - 修正内容: {変更の説明}
   - エラー: {元のエラーメッセージ}
   ```

4. デプロイ:
   ```bash
   cd C:/Users/hrsuk/prj/s-style-hrd/migration-src && gcloud app deploy app.yaml --project=s-style-hrd --quiet
   ```

5. 再テスト（ステップ3に戻る）

#### ステップ5: 成功時の対応

1. `SUBAGENT-FIX-LOG.md` に成功を記録
2. 新しい修正パターンがあれば `MIGRATION-FIXES-CATALOG.md` に追記
3. 本番で戻す必要がある修正があれば `PRODUCTION-REVERT-CHECKLIST.md` に追記

#### ステップ6: 5回ループ後も失敗の場合

以下を報告して終了:
- 試した修正内容
- 最終エラーメッセージ
- 推奨される次のステップ

### テスト対象ルート（3並列）

| サブエージェント | ルートパス | テンプレート | 想定修正箇所 |
|-----------------|-----------|-------------|-------------|
| 1 | /test/addresslist | addresslist.html | default_if_none 9箇所 |
| 2 | /test/mailinglist | mailinglist.html | default_if_none 1箇所 |
| 3 | /test/duplicationcheck | duplicationcheck.html | default_if_none 1箇所 |

### サブエージェント起動コマンド

3つのTaskツール呼び出しを**1つのメッセージで同時に**実行：

subagent_type: "general-purpose"
model: "opus"

各サブエージェントのプロンプトには上記の指示と担当ルート情報を含めてください。
```

---

## 個別サブエージェントプロンプト（詳細版）

### サブエージェント1: addresslist

```
あなたは GAE Python 3.11 マイグレーションのテストエージェントです。

## 担当ルート
- パス: /test/addresslist
- テンプレート: templates/addresslist.html
- 想定修正: default_if_none 9箇所

## 作業ディレクトリ
C:\Users\hrsuk\prj\s-style-hrd

## 必須: 最初に修正カタログを読む

ファイル `MIGRATION-FIXES-CATALOG.md` を読み、以下のパターンを把握してください：
- |default_if_none:"" → |default("")
- |default:"" → |default("")
- その他のDjango→Jinja2変換パターン

## テスト前チェック

templates/addresslist.html を読み、上記パターンが残っていれば修正してからテストを開始。

## テストURL
https://s-style-hrd.appspot.com/test/addresslist

## テストコマンド
curl -s -o /dev/null -w "%{http_code}" "https://s-style-hrd.appspot.com/test/addresslist"

## エラー時（最大5回ループ）

1. ログ確認: gcloud app logs read -s test-service --limit=30 2>&1 | grep -A 10 "ERROR\|Exception"
2. 修正実施
3. SUBAGENT-FIX-LOG.md に記録
4. デプロイ: cd C:/Users/hrsuk/prj/s-style-hrd/migration-src && gcloud app deploy app.yaml --project=s-style-hrd --quiet
5. 再テスト

## 成功条件
HTTP 200 が返ること

## ログ記録フォーマット
## addresslist - ループ {N}
- 日時: {timestamp}
- ファイル: {path}
- 修正内容: {description}
- エラー: {error message}

5回ループ後も失敗なら、試した内容と最終エラーを報告して終了。
```

### サブエージェント2: mailinglist

```
あなたは GAE Python 3.11 マイグレーションのテストエージェントです。

## 担当ルート
- パス: /test/mailinglist
- テンプレート: templates/mailinglist.html
- 想定修正: default_if_none 1箇所

## 作業ディレクトリ
C:\Users\hrsuk\prj\s-style-hrd

## 必須: 最初に修正カタログを読む

ファイル `MIGRATION-FIXES-CATALOG.md` を読み、Django→Jinja2変換パターンを把握してください。

## テスト前チェック

templates/mailinglist.html を読み、修正パターンが残っていれば修正してからテスト開始。

## テストURL
https://s-style-hrd.appspot.com/test/mailinglist

## テストコマンド
curl -s -o /dev/null -w "%{http_code}" "https://s-style-hrd.appspot.com/test/mailinglist"

## エラー時（最大5回ループ）
1. ログ確認 → 2. 修正 → 3. ログ記録 → 4. デプロイ(--quiet) → 5. 再テスト

## 成功条件
HTTP 200

5回ループ後も失敗なら報告して終了。
```

### サブエージェント3: duplicationcheck

```
あなたは GAE Python 3.11 マイグレーションのテストエージェントです。

## 担当ルート
- パス: /test/duplicationcheck
- テンプレート: templates/duplicationcheck.html
- 想定修正: default_if_none 1箇所

## 作業ディレクトリ
C:\Users\hrsuk\prj\s-style-hrd

## 必須: 最初に修正カタログを読む

ファイル `MIGRATION-FIXES-CATALOG.md` を読み、Django→Jinja2変換パターンを把握してください。

## テスト前チェック

templates/duplicationcheck.html を読み、修正パターンが残っていれば修正してからテスト開始。

## テストURL
https://s-style-hrd.appspot.com/test/duplicationcheck

## テストコマンド
curl -s -o /dev/null -w "%{http_code}" "https://s-style-hrd.appspot.com/test/duplicationcheck"

## エラー時（最大5回ループ）
1. ログ確認 → 2. 修正 → 3. ログ記録 → 4. デプロイ(--quiet) → 5. 再テスト

## 成功条件
HTTP 200

5回ループ後も失敗なら報告して終了。
```

---

## 関連ファイル一覧

| ファイル | 用途 |
|---------|------|
| `MIGRATION-FIXES-CATALOG.md` | 修正パターンカタログ（必読） |
| `SUBAGENT-FIX-LOG.md` | サブエージェント修正ログ（追記） |
| `PRODUCTION-REVERT-CHECKLIST.md` | 本番で戻す修正リスト |
| `migration-src/` | デプロイ対象ディレクトリ |
| `migration-src/templates/` | テンプレートファイル |

---

## 次のルート（2回目以降）

| # | パス | テンプレート | 想定修正箇所 |
|---|------|-------------|-------------|
| 4 | /test/bksearch | bksearch.html | 50箇所 |
| 5 | /test/memberedit | memberedit.html | 43箇所 |
| 6 | /test/bkdchk | bkdchk.html | 35箇所 |
| 7 | /test/mypage | 不明 | 要調査 |
| 8 | /test/bkjoukyoulist | 不明 | 要調査 |
| 9 | /test/show/s-style/hon/backoffice/show.html | show1.html | 1箇所 |

---

## トラブルシューティング

### 認証エラー
```
ERROR: (gcloud.app.deploy) You do not currently have an active account selected.
```
→ `gcloud auth login` を実行

### デプロイタイムアウト
→ `--quiet` フラグが付いているか確認

### テンプレートが見つからない
→ `templates/` ディレクトリ内のファイル名を確認（大文字小文字注意）
