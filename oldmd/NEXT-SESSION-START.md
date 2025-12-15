# 次のセッション開始手順

**作業方針: 選択肢2（作業継続）**

## 前提条件

- ✅ 処理済みファイル（15ファイル）はそのまま保持
- ✅ 作業リストから処理済みを削除して残りを処理
- ✅ 新しい手順6（呼び出し元ファイルの更新）が自動適用される

## 開始時の確認事項

### 1. migration-progress.md を確認

```
migration-progress.md を開いて、最後に処理したファイルを確認してください。
```

**最後に処理したファイル:** application/regist.py（骨格のみ）

### 2. 処理対象ファイルリスト

以下のファイルを **NEXT-SESSION-PROMPT.md** の手順に従って順次処理してください：

**優先度: 高（login.py の依存モジュール）**
```
- application/models/member.py
- application/models/CorpOrg.py
- application/models/Branch.py
- application/chkauth.py
- application/session.py
```

**優先度: 中（regist.py の依存モジュール）**
```
- application/config.py
- application/view.py
- application/bklistutl.py
- application/messageManager.py
```

**優先度: 低（その他のハンドラー）**
```
- application/proc.py
- application/bkedit.py
- application/blobstoreutl.py
- application/handler.py
- application/RemoveAll.py
- application/uploadbkdata.py
- application/uploadbkdataformaster.py
- application/duplicationcheck.py
- application/json.py
- application/memberedit.py
- application/test.py
- application/bksearch.py
- application/follow.py
- application/mypage.py
- application/bkjoukyoulist.py
- application/bkdchk.py
- application/addresslist.py
- application/show.py
- application/mailinglist.py
- application/uploadaddressset.py
- application/memberSearchandMail.py
- application/bksearchutl.py
- application/cron.py
- application/sendmsg.py
- application/email_receiver.py
- application/matching.py
- application/tantochange.py
- application/index.py
```

**その他のモジュール**
```
- application/SecurePageBase.py
- application/SecurePage.py
- application/GqlEncoder.py
- application/mapreducemapper.py
- application/timemanager.py
- application/wordstocker.py
- application/zipper.py
- application/qreki.py
- application/mailvalidation.py
- application/email_decoder.py
- application/CriticalSection.py
- application/rotor.py
- application/tantochangetasks.py
- application/bksearchensenutl.py
- application/models/bkdata.py
- application/models/bklist.py
- application/models/blob.py
- application/models/ziplist.py
- application/models/station.py
- application/models/message.py
- application/models/msgcombinator.py
- application/models/bksearchaddress.py
- application/models/bksearchdata.py
- application/models/bksearchmadori.py
- application/models/matchingparam.py
- application/models/matchingdate.py
- application/models/bksearchensen.py
- application/models/bksearcheki.py
- application/models/address.py
- dataProvider/bkdataProvider.py
- dataProvider/bkdataSearchProvider.py
- geo/geomodel.py
- geo/geocell.py
- geo/geomath.py
- geo/geotypes.py
- geo/util.py
```

## 実行指示（Claude Code への指示）

次のセッションでは、以下のように指示してください：

```
NEXT-SESSION-PROMPT.md を読み込んで、以下のファイルを順次処理してください：

優先度: 高（login.py の依存モジュール）
- application/models/member.py
- application/models/CorpOrg.py
- application/models/Branch.py
- application/chkauth.py
- application/session.py

（その後、優先度: 中 → 優先度: 低 の順に処理）

migration-progress.md に記録されているファイルはスキップしてください。
```

## 注意事項

1. **処理済みファイルの再処理は不要**
   - migration-src/ に既に存在するファイルは変更しない
   - migration-progress.md に記録済みのファイルはスキップ

2. **新しい手順6が自動適用される**
   - webapp2.RequestHandler クラスを処理したら main.py が自動更新される
   - migration-progress.md に「呼び出し元」セクションが記録される

3. **main.py ルート登録チェックリスト**
   - 各ファイル処理後に自動的に更新される
   - migration-progress.md で進捗が確認できる

4. **regist.py の完全実装**
   - 依存モジュールが揃った後に、骨格のみの regist.py を完全実装する
   - 完全実装後に main.py のルート登録を有効化する

## トラブルシューティング

### やり直しが必要になった場合

**NEXT-SESSION-PROMPT.md の「やり直しが必要な場合の手順」** を参照してください。

### 個別ファイルの修正が必要な場合

**NEXT-SESSION-PROMPT.md の「部分的なやり直し」** を参照してください。

---

**このファイルは次のセッション開始時に参照してください。**
