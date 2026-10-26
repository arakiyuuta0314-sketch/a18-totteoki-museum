# A18 公開試遊版｜執事の足元判定（2026-10-27）

## 変更要求
執事の体全体に当たって後ろを通過できないため、足元判定へ縮小して通路を確保する。

## 正本と差分
- ソース正本: `web-tools-preview` / `feature/a18-entrance-clean-redraw-20261027` / `c9677552f17b68de45fef786c0c685ad293f82cb`。
- 配布起点: `a18-totteoki-museum` / `main` / `b83bbdb7439ffee8ff8d8d5e744405de3a8f1cf5`。
- 配布側の変更は `layout-test/layout-system.js` と `layout-test/index.html`。前者は執事の物理障害物を全身から足元（x129..149 / y361..368）へ縮小。後者は館長が執事の後ろを歩くときの描画順を修正。
- 背景・写真・他室の判定・2展示枠・2枠の調べる判定・移動禁止・キャラクター素材・ゲームデータ・保存スキーマは変更しない。
- 既存の後方通行試験：縦画面で x122→146、y329の実歩行に成功。足元x139,y360は通過不可。

## 検証
- 開発版: `entrance-collision-rebuild-regression.js`と既存の3種類の単体テストPASS、専用隔離Chrome QA PASS（JS例外・通信エラー各0）。
- 配布候補: 開発実装との2ファイル内容を一致確認、その他のランタイムと承認背景・IndexedDB保存実装を照合済み。
- 配布候補隔離Chrome: `qa-butler-foot-release.cjs` PASS（初回登録、後方移動、足元衝突、2枠操作、保存と再読込）。
- iPhone実機Safariはユーザー側の試遊確認が必要。公開URLの実HTTP照合はPush後に実施。
