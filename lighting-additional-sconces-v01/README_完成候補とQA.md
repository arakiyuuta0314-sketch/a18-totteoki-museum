# A18 エントランス｜未分離の壁灯4点・独立素材 v01
2026-10-26｜美術採用候補・ユーザー監修待ち（ゲーム本体未統合）

## 元データ
- 43番 entrance_bare_three_frame_backing.png（原画由来・未分離照明を含む）
- 49番 view_wood_empty_100.png（最新の右手前額縁・正式キャラ・カーペットなしエントランス）
- 29番 左右案内板・中央扉まわり壁灯：制作済み、今回は上書きしない
- 30番 背面展示灯2点：制作済み、今回は上書きしない

## 今回分離した4灯
各灯の本体・発光は **2レイヤーのみ**。透明RGBA。制御は任意の組み合わせで可能。
- fixture_outer_left_body.png + fixture_outer_left_emission.png  左外側柱
- fixture_outer_right_body.png + fixture_outer_right_emission.png  右外側柱
- fixture_foreground_left_body.png + fixture_foreground_left_emission.png  右手前展示壁の左側
- fixture_foreground_right_body.png + fixture_foreground_right_emission.png  右手前展示壁の右側

本体は原画の器具と炎に見える部分を抽出、発光は原画の光成分を参照して分離候補にした。器具のスタイルはAI再生成していない。
発光PNGには周辺の柔らかいにじみを含むが、壁反射を独立した3番目の素材として量産していない。
ゲーム内で配置する際は、各名前の基準座標（QA_manifest.json 内の矩形左上）に重ねること。

## 修復下地
QA_all_four_sconces_off.png は49番を基準に、4灯があった局所だけを修復した画像。
柱の隠れていた画素は、元画像の同じ柱の上端・下端から補間した**推定修復**。原画と画素一致するものではない。
明暗の継ぎ目が一部に残る可能性があるため、美術監修で確認する。
QA_all_four_sconces_on.png / QA_all_four_body_only.png は戻した比較。
全灯ONは原画に可能な限り近づけた合成候補であり、原画RGB完全一致の主張はしない。
個別壁灯の拡大 QA_..._3x.png も保存。

## 保護・技術QA
- 546×483、4つの対象範囲外で49番からの変更画素は0。
- 49番と43番の差分（新しい右手前額縁・壁面等）は対象矩形内でも優先して維持。破壊・隠蔽画素0。
- 各灯の「器具本体」「発光」のPNGはすべて透明領域あり、独立表示できる。
- 実Chrome 390x844 CSS / DPR2で4灯の全組合せ16×発光ON/OFF2=32状態を検証、JS/HTTPエラー0、ページ横はみ出し0。
- 29番・30番と既存43〜49番、Git main、ゲーム本体、公式キャラ48枚は変更していない。

## あえて今回やっていないこと
- 天井の小型照明列の分離
- 受付の卓上ランプの分離
- 壁や床の広範囲の反射光の独立レイヤー化（必要になったときに扱う）
- 既存29番・30番の器具と発光の再分離（既存PNGを再利用）
- v07最新シーンへのゲーム側のレイヤー実装・Lv1〜6割り当て
- 美術としての承認
- 背景の修復痕まで含めた完全な最小構成エントランスの最終QA

## データ
build_missing_sconces_v01.py：元原画から再制作できるソース
QA_sconces_contract.py：最新49番保護・RGBA独立性・4灯範囲の数値QA
index.html / QA_browser_lights.cjs：スマホ表示・切替検証
QA_manifest.json：表示座標、SHA256、QA結果、完了していない作業を区別

本フォルダは**最終採用済みという意味ではない**。
