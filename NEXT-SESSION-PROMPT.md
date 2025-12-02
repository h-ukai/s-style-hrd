# ブラウザエラーチェック タスク

## 前提条件
- Chromeをデバッグモードで起動済み: `"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir="C:\chrome-debug-profile"`
- Chrome DevTools MCPサーバーが接続済み（`/mcp` で確認）
- 作業ディレクトリ: `C:\Users\hrsuk\prj\s-style-hrd\migration-src\`

## 注意事項
- **サブエージェント（Task tool）はMCPツールを継承できないバグがある**（GitHub Issue #7296）
- そのため、**マスターエージェントが直接MCPツールを使用**して順次チェックを行う

---

## チェック対象ルート（8件）

| # | URL | ログファイル名 |
|---|-----|---------------|
| 1 | `https://s-style-hrd.appspot.com/test/` | test-root.log |
| 2 | `https://s-style-hrd.appspot.com/test/login` | test-login.log |
| 3 | `https://s-style-hrd.appspot.com/test/addresslist` | test-addresslist.log |
| 4 | `https://s-style-hrd.appspot.com/test/mailinglist` | test-mailinglist.log |
| 5 | `https://s-style-hrd.appspot.com/test/csvupload/addressset.html` | test-csvupload.log |
| 6 | `https://s-style-hrd.appspot.com/test/follow` | test-follow.log |
| 7 | `https://s-style-hrd.appspot.com/test/bkjoukyoulist` | test-bkjoukyoulist.log |
| 8 | `https://s-style-hrd.appspot.com/test/bkdchk` | test-bkdchk.log |

---

## マスターエージェント実行手順

```
ブラウザエラーチェックを実行する。

事前確認:
1. `/mcp` でChrome DevTools MCPが接続されているか確認
2. 接続されていなければ、Chromeデバッグモードを起動してセッション再起動

実行手順（各ルートを順次処理）:
1. `mcp__chrome-devtools__navigate_page` で対象URLに移動
2. 以下をループ（最大10回）:
   a. `mcp__chrome-devtools__list_console_messages` でJSエラーを取得
   b. `mcp__chrome-devtools__list_network_requests` で4xx/5xxエラーを取得
   c. エラーがなければ次のルートへ
   d. エラーがあれば:
      - エラー内容をログファイルに記録
      - 該当ファイルを修正（作業ディレクトリ: migration-src/）
      - 修正前と修正後をログに記録
      - デプロイ: `gcloud app deploy --no-promote --quiet`
      - `mcp__chrome-devtools__navigate_page` でページをリロード
      - 再チェック
3. 10回ループしても解決しない場合:
   - ログに「10回ループで中断」と記録
   - 残っているエラーをログに記録
   - 次のルートへ進む

全ルート完了後:
- 総括レポートを作成して表示
```

---

## 使用するMCPツール

| ツール名 | 用途 |
|----------|------|
| `mcp__chrome-devtools__navigate_page` | URLに移動 |
| `mcp__chrome-devtools__list_console_messages` | コンソールログ・JSエラー取得 |
| `mcp__chrome-devtools__list_network_requests` | ネットワークリクエスト（ステータスコード）取得 |

---

## ログディレクトリ
`C:\Users\hrsuk\prj\s-style-hrd\logs\`

## ログ形式
```
=== ルート: {URL} ===
開始時刻: {timestamp}

[ループ1]
コンソールエラー: {エラー内容}
ネットワークエラー: {ステータスコード} {URL}
修正ファイル: {ファイルパス}
修正前:
{コード}
修正後:
{コード}
デプロイ: 完了

[ループ2]
...

結果: エラーなし / 未解決エラーあり / 10回ループで中断
終了時刻: {timestamp}
```

---

## 総括レポート形式

```
# 総括レポート

## 全ルート結果一覧
| # | URL | 結果 | エラー有無 |
|---|-----|------|-----------|
| 1 | /test/ | 完了 | なし |
| 2 | /test/login | 修正完了 | 404→解決 |
...

## 修正したファイル一覧
- {ファイルパス}: {修正内容の概要}
...

## 未解決のエラー
- {ルート}: {エラー内容}
...

## 10回ループで中断したルート
- なし / {ルート名}
```
