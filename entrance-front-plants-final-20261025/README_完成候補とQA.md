# A18｜エントランス左右手前観葉植物 E01・E02 完成候補 v01

## 今回の独立素材（2点とも実在、1点のみの完了ではない）
- entrance_plant_left.png … 左手前の植物・銀系鉢の透過PNG（66×85）。
- entrance_plant_right.png … 右手前の植物・銀系鉢の透過PNG（88×85）。
- entrance_plant_left_mask.png / entrance_plant_right_mask.png … 表示マスク。
- entrance_bg_without_front_plants.png … 2点を外した床・木製台座の背景（546×483）。
- entrance_bg_without_left_plant.png / entrance_bg_without_right_plant.png … 左右独立の背景修復。
- source_left_foliage_and_vase_mask.png / source_right_foliage_and_vase_mask.png … マスク編集用ソース。
- source_left_restoration_patch.png / source_right_restoration_patch.png … 背景修復素材の原本切片。
- source_left_restoration_change_mask.png / source_right_restoration_change_mask.png … 修復適用先の編集可能マスク。
- build_front_plants.py … 上記ソースから正式候補とQA画像を再生成するPython。
- QA_* … 左・右それぞれON、OFF、サイズ90/100/110、位置変更、実ブラウザスクリーンショット。
- index.html / front-plants-preview.js … 390pxスマホでサイズと表示状態を独立変更できる検証ページ。

## 確定した動作・座標
元絵 approved_entrance_trial.jpg 546×483から実在の葉と鉢を抽出。
- 左：ソース外接矩形 x=0..65, y=398..482／アンカー(21,85)、画面下端基準。
- 右：ソース外接矩形 x=450..537, y=398..482／アンカー(51,85)、画面下端基準。
- 表示は左右個別。サイズ90〜110%、左右内側へ最大5pxを比較検証。
- 元絵では鉢の下が画面境界で切れているため、上下移動・大幅拡大・回転は未保証。
- 合成順序：原本背景を左右部分的に修復 → 写真・額縁/建築 → 正式キャラクター → E01/E02透過植物 → UI。

## 品質と制限
- 元画像の葉と鉢色を使用し、AI再描画なし。正式採用キャラクターの原本のSHAと一致。背景・写真の別構図への変更なし。
- 植物を外す前には見えなかった木製台座の内部と床を原本の既存材質から復元。
- 背景修復範囲外のRGBは原本と完全一致。
- 二つとも戻した原本と比較した画像の全画面平均チャンネル絶対誤差は0.1180、修復範囲内の完全一致は保証しません。
- 非表示状態の木製台座は写真修復であり、無傷の原画ではありません。完成候補としてユーザーの美術監修を要します。
- Chromeモバイル 390×844 DPR2で実際に4状態とリセット、画像読込、ネットワーク／JSエラー0を検証。
- ゲーム本体へ未統合。旧低画質素材の正式再利用なし。
