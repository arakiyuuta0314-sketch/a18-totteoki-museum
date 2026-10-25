# A18 エントランス｜背面左右写真展示灯 完成候補v01
原本546×483の左右の写真額縁上部にある金色の専用照明をそれぞれ独立させた。
- entrance_picture_light_west.png / east.png：RGBA原本復元用
- entrance_picture_light_west_photo_safe.png / east_photo_safe.png：写真窓に光や影が不自然にかからない実装用
- entrance_bg_without_picture_lights.png：原本から展示灯を修復除去した共通下地
- 各種QA_*：左右個別・両表示・両非表示・正式キャラと登録画像・スマホ実画面
- build_picture_lights.py：制作元ソース、QA_manifest.json：座標・ハッシュ等
## QA
- 両展示灯復元では元画像RGB完全一致（平均誤差0.0）。
- 写真本体の y>=69 ピクセルは不変。写真光演出は写真との干渉を回避。
- Chromeモバイル幅390（DPR2）で左右切替・復元と読込エラー0を検証。
- ゲーム本体へは未統合。正式キャラクターの再生成なし。
- 灯りのない場合の金枠は修復された元絵の金具・壁面を使用。美術監修待ち。
