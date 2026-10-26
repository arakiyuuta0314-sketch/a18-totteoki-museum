# A18 「とっておき美術館」初期背景・Web試遊更新（2026-10-27）

## 依頼と正本
- ユーザーから承認済みのエントランス初期建築背景を**既存のWeb試遊版**に公開し、iPhoneで確認可能にする。
- ゲーム実装済み正本：`web-tools-preview` / `feature/a18-entrance-clean-redraw-20261027` / `14644ccfb62c75bc23610d4c905a0515105a9614`。
- 背景PNG：`layout-test/assets/entrance/approved_initial_20261027/entrance_background_initial_approved.png` 1322×1190、SHA-256 `cc4bca9821242facbee3984d1df7034514845195205c2b30cc94ef4628a469cf`。
- 公開サイト：`https://arakiyuuta0314-sketch.github.io/a18-totteoki-museum/layout-test/`。

## 変更を限定
公開側の既存`main`（基準 `2165a879cb9c8ca05b688670a18771acadcad1e8`）を起点に、別worktree `feature/a18-approved-initial-background-release-20261027` にて以下の**3ファイルのみ**取り込んだ。

- `layout-test/index.html`（JS読み込みキャッシュキーと説明コメントのみ）
- `layout-test/entrance-renderer.js`（承認済み背景読み込み、縦横比を維持した中央クロップ、写真の下地参照更新）
- `layout-test/assets/entrance/approved_initial_20261027/entrance_background_initial_approved.png`（ユーザー承認画像をバイト単位で同一コピー）

描画に使うその他の既存ランタイムファイルは開発正本とハッシュ比較して不一致0。既存のIndexedDB `a18-totteoki-museum-v3`、ストレージ、イベント、キャラPNG、他室、総合ポータルは変更なし。前景カウンター／左右中間仕切り壁はまだ未追加で、旧当たり判定の調整が残る。

## 公開前QA
- 現行公開URLの更新前HTTP 200と旧`10-hq-20261026`マーカーを確認。
- 取り込み差分3ファイル限定、他ランタイムSHA一致、PNG SHA一致。
- 独立Chromeの127.0.0.1配布候補テスト：画像ロード・Canvas描画・JS例外0・通信失敗0（PASS）。
- 独立Chromeのゲームプレイ：初回登録、性別設定、初回ストーリー、D-padでの移動、保存、再読み込み、縦390×844／横844×390の画面キャプチャ（PASS）。
- 開発側で全28展示枠・館レベル閾値・フレーム復元等の単体回帰 PASS。
- 旧総合ブラウザスモークは初回保存待機のテスト側不備がありFAILのまま。全館QA、iPhone Safari実機の確認は未完了。

## 公開判定
これは**開発中のWeb試遊版**の更新。完成版またはiPhone実機動作保証ではない。古い素材・既存ゲームセーブを破壊する変更は含めない。ユーザーのiPhone試遊を次の視覚監修とする。
