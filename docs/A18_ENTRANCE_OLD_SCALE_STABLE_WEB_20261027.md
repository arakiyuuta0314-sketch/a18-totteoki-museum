# A18 Web試遊：拡大前の画角復帰と静止ちらつき対策（2026-10-27）

## 指示
iPhone Safari実機スクショで以前より拡大された表示・画質劣化・ちらつき継続を確認。ユーザーは前回拡大以前の表示倍率への復帰を希望。

## 修正対象
正本：`web-tools-preview` / `feature/a18-entrance-clean-redraw-20261027` / `ad49bb2835e968a52c80270ade85993d934658ed`

公開用差分：`layout-test/index.html` **1ファイルのみ**。承認済み1322×1190建築背景、保存データ、写真・キャラ・当たり判定、左右2つの額縁位置などは変更なし。

1. 拡大原因の縦画面`logicalW≈299.475`を撤回、前回スケール`logicalW=445`へ戻す。ゲーム描画領域390×629で`logicalH≈717.705`に復帰。
2. 30fps上限制限を撤回し、元の`requestAnimationFrame`へ戻す。
3. 再描画が不要なエントランス静止時には`canvas.clearRect`と背景再レンダリングをスキップ。カメラ1物理ピクセル以上・館長移動・作品読み込み・保存変更・canvas寸法変更時は再描画。
4. 同寸法canvasリサイズで既存ビットマップを消さない前回対策は維持。

## 公開前確認
`node a18/qa-clean-redraw-20261027/qa-entrance-display-v3.cjs` PASS、DPR3 / 390×844・横844×390、描画テスト、歩行、執事足元、2額縁、保存再読込、通信失敗0・JS例外0。
静止12測定で描画回数増加0、同一画面リサイズ6回でピクセル不変。
公開候補の独立Chromeでも同等試験PASS。iPhone Safari実機のちらつき解消はユーザーによる再試遊で判断。画質の素材由来の限界は変えていない。

## 公開管理
公開元`a18-totteoki-museum-pages/main`と作業ブランチ`feature/a18-entrance-collision-release-20261027`、現在HEADを照合し、fast-forwardのみ許可。GitHub Pagesへの反映をHTTPと実URL Chromeで検証する。
