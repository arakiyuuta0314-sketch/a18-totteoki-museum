# A18｜エントランス E06 左右木製台座・完成候補 v01

## 原本・品質
元の承認画 approved_entrance_trial.jpg (546×483)、以前完成した E01/E02 観葉植物と背景修復から制作。
左右木製台座の見えていた外枠・木目・金色のハイライトを維持し、植物の陰に隠れていた前面に
原本の腰壁の木目 source_wood_panelling_donor.png を用いた。AIキャラ・新しい絵への置換なし。

## 正式候補
- entrance_plinth_left.png（RGBA、64×57）と entrance_plinth_right.png（RGBA、89×48）
- entrance_plinth_left_mask.png / right_mask.png：独立したアルファマスク
- entrance_plinth_shadow_left.png / right.png：独立した接地影
- entrance_bg_without_both_plinths.png：両台座を外して本来見えなかった石床を原本の大理石から補完
- entrance_bg_without_left_plinth.png / right_plinth.png：片側別下地
- source_original_approved.jpg：原本参照（変更不可）
- source_previous_background_without_plants.png：E01/E02既存の背景
- source_previous_preview_without_plants.png：E01/E02既存の正式キャラ＋写真合成
- source_original_plant_left.png / right.png：既存正式候補の植物（バイト一致）
- source_wood_panelling_donor.png：同じ館の木製腰壁由来の補修元画像
- build_plinths.py：寸法、分離マスク、影、石床修復、QA画像の再生成ソース
- QA_*.png/jpg、QA_browser_mobile.cjs、QA_manifest.json：静的比較・390×844ブラウザQA
- index.html / render-plinths.js：スマホで個別表示・90/100/110%・内側5px・植物の載せ替えを検証可能

## 描画・制約
順序：補完された石床背景 → 左右台座の接地影 → 台座前景 → E01/E02植物原本 → UI。
通常素材の元画像外接矩形は左(0,426)-(64,483)、右(457,435)-(546,483)。
各台座も鉢も元画像で下端が切れているため、画面下端固定で90〜110%と内側5pxのみ検証。
上下移動や回転・大幅拡大、ゲームの当たり判定は未検証。
原本との全画素一致は主張しない（木目と床の一部を補修）。
写真・正式キャラクターの領域は未変更。遊べるゲーム本体へは未統合。
ステータス：素材・美術QA完成候補。ユーザーの最終美術採用判断待ち。
