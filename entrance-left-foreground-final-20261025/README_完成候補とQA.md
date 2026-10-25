# A18 エントランス 左手前壁と手すり｜完成候補 v01

## 独立素材
- entrance_left_foreground_wall.png：壁の白い前面と腰壁。背景の植物領域は除外。
- entrance_left_foreground_rail.png：壁奥へ伸びる細い木製の手すり。
- entrance_left_wall_mask.png / entrance_left_rail_mask.png：透過遮蔽マスク。
- entrance_bg_without_left_foreground.png：背面用の隠れた床・壁面下地。
- build_left_foreground.py：マスク座標・再構成元ソース。
- QA_*：原本復元、オフィシャルキャラクターの前景/奥を含めた実合成とChrome試験。

## 描画順
基本背景 → 写真・展示枠 → キャラ（背後時） → 壁・手すり → キャラ（手前時）→UI。
元絵の構図・額縁・北扉など不変。植物は将来別素材にするため、固定前景には含めない。
標準位置で再合成したRGBは原本と全画素一致。
本素材は建築の前後関係のための遮蔽専用（固定位置）であり、壁を移動させる自由配置用ではない。
下地PNG単体では部分的に合成補完した床が見えるが、完成館内では前景に完全に隠れる。
公式キャラクターは原本PNGのバイト一致を検証。ゲーム本体未統合、最終監修待ち。
