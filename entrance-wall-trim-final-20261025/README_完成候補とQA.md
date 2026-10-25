# A18 事後美術素材｜E05 天井・腰壁の金色飾り縁 v01
高品質承認済み approved_entrance_trial.jpg (546×483) の実画素から、固定建築の細い装飾帯を4か所、透明RGBA独立素材にした。

- entrance_wall_trim_ceiling_west.png：天井上部・左 (x=65,y=11,w=140,h=9)
- entrance_wall_trim_ceiling_east.png：天井上部・右 (x=355,y=11,w=125,h=9)
- entrance_wall_trim_wainscot_west.png：背面腰壁・左 (x=68,y=164,w=135,h=8)
- entrance_wall_trim_wainscot_east.png：背面腰壁・右 (x=358,y=164,w=42,h=8)
  ※右手前の斜め手すりに隠れる部分は分離せず、原本の前景を維持。
- entrance_bg_without_wall_trims.png：装飾を除いた木材下地の修復画像。
- entrance_wall_trim_*_mask.png：個別透過マスク。
- build_wall_trim.py：原本＋マスク制作を再生成するソース。
- QA_source_reconstruction_all_on.png：4点を戻した場合は元画像と画素単位で完全一致。
- QA_with_photos_characters_trim_on.png：既採用の写真・正式キャラクターと合成済み。
- QA_*／QA_manifest.json：変更状態、成長3状態、スマホChromeでの表示・透過・検証。
- index.html / render-wall-trims.js：スマホから個別4点ON/OFF、3パターン確認。

合成順：復元建築下地 → 各展示写真・既採用額縁・固定前景・正式キャラクター → 4点の原本金装飾 → UI。
実装時は他の独立素材の同一領域への重複描画を禁止すること。

固定建築の原本装飾であり、幅長さ変更・移動は今回の保証対象ではない。先にユーザーが確認するまでは正式採用せず完成候補。
画面上下の原本は変更していない。家具・キャラのAI描き直しなし。ゲーム本体未変更。
