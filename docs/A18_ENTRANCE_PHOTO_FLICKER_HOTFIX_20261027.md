# A18 Web公開：移動後に展示写真が消える不具合修正 (2026-10-27)

## 状況と根拠
- ユーザー実機スクリーンショット（6:08）で背景・執事・キャラは存在し、展示2/2なのに両作品の写真が消えている。
- ゲーム `applyCommitted()` が**歩行位置だけの保存**でも `P2.hydrate(save.works)` で写真Blob URLを再作成し、旧URLをrevokeしていた。再読み込みと描画省略による写真消失・ちらつきに直結。
- 開発正本：`web-tools-preview` / `feature/a18-entrance-clean-redraw-20261027` / `288700e2b3c66bc24df3bb8f0c776ea730bd3231`。

## 修正差分（index.htmlのみ）
- 位置保存に限り `preservePhotoURLs:true` を渡し、Blob URLとデコードした画像を再利用。
- 位置以外の通常更新は従来の保存・画像再読込を維持し、古い画像キャッシュだけクリア。
- 保存整合性ガード（作品ID、配置、タイトル、Blobサイズ、MIME）が不一致ならfail-fast。
- 正式採用背景PNG、写真Blob、ユーザーのセーブ、キャラクター、当たり判定、縦画面の`logicalW=445`は一切変更しない。

## 隔離Chrome実ブラウザQA
- マゼンタ/緑の2枚の写真Blobをテスト用IndexedDBに登録・展示。
- 色ピクセルを検出し、3回歩いて450ms位置保存を各回実行。
- 歩行中の`URL.createObjectURL`、`URL.revokeObjectURL`とも0回。画像表示が消えず、revision4→7へ保存された。
- ブラウザ再読み込み後、2枚とも色ピクセルを再確認。iPhone DPR3相当・縦/横画面、壁、額縁、執事、保存再読込のQA成功。JS/通信例外0。
- iPhone Safari実機の再現解消はユーザー試遊で最終判断。サンプル画像は隔離プロファイルに限定し、ユーザーの作品は変更していない。

## 公開管理
- 公開用作業ブランチ`feature/a18-entrance-collision-release-20261027`を継続。既存`main`との差分限定して確認後、fast-forward公開。
- GitHub Pagesの実HTTP一致とブラウザQA後に完了判定。作業前からの未追跡資料は維持。
