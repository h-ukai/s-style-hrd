# マイグレーションテストデプロイ作業プロンプト

## プロジェクト概要
現在 Google App EngineはPython 2.7のデプロイをブロックしています
そのためのPython 3.11 へのマイグレーション作業を行いました
結果はC:\Users\hrsuk\prj\s-style-hrd\migration-srcにあります
既存のサービスはC:\Users\hrsuk\prj\s-style-hrd\src\にありpy2.7で稼働しています
これを現在のコードPython 2.7を上書きせずにデプロイし/test/にルーティングする設定をしたいです
どのようにすすめますか？

## プロジェクト構造
```
プロジェクトルート: C:\Users\hrsuk\prj\s-style-hrd
デプロイ対象フォルダ: migration-src
```