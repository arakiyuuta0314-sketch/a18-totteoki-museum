# A18 受付カウンター前縁（O04） 完成候補 v01

受付カウンターの手前にある木製の上縁と前面を、元の高品質な546×483画像から分離した。

主要素材:
- entrance_counter_fg_top_lip.png：金色に照らされた右肩と前縁
- entrance_counter_fg_front_face.png：木製前面
- entrance_counter_mask_top_lip.png / entrance_counter_mask_front_face.png：遮蔽
- entrance_bg_without_counter_front.png：前景で隠れる部分の背景用下地（単体表示はしない）
- curator-front-00.png：正式採用キャラクターの原本PNG、改変なし
- build_counter_front.py：再生成可能な制作ソース
- QA_*：原本再構成・奥側／手前側のキャラ配置・390×844実Chrome画面
- QA_manifest.json：実寸・SHA等

固定カウンターの前後関係を表現するための独立レイヤーであり、家具を自由配置する用途ではない。
植物・花器・写真・扉は変更していない。元画像へ再構成すると全画素一致。
キャラクターが本当にカウンター裏へ移動可能かは、ゲーム当たり判定との統合時に検証する。
現段階で本体未統合・ユーザー美術確認待ち。