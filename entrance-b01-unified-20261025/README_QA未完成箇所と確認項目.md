# A18 エントランス B01 全体合成QA v01

これは完成版ではありません。高品質な正式背景と個別素材を分離し直して、
各PNGを合成する統合テスト資料です。ゲーム本体と正式キャラ48枚は変更していません。

- B01_entrance_base_without_independent_art.png: 原本の焼き込み素材を除いた描画下地
- build_b01_scene.py: 55画像の原本を組み立てるPythonソース
- 14カテゴリのサブフォルダ: 背面額縁・北扉・左右建築・装飾・植物・台座などの実素材
- QA_B01_complete_pictures_and_characters.png: 写真入り・正式キャラ入りの標準合成
- QA_B01_all_empty_photos.png: 3か所空き枠
- QA_B01_north_open.png: 北扉を開いた状態
- QA_B01_no_gold_ornaments.png: 一部装飾なし
- QA_B01_no_plants_no_plinths.png: 植物と台座なし（未合格、修復継ぎ目あり）

Chrome 390x844 DPR2で表示状態5点切替、画像読込、JavaScript/HTTPエラー0。
未解決: 左カウンター木製腰壁の植物なし状態に補修継ぎ目あり。
B01の裸の下地画像は、それ単独で公開できる空の部屋を表すものではありません。
右展示壁・北扉・額縁等の建築を必ず上乗せする前提の下地です。
今後必要: 修復完成、Lv2-6増分、ゲーム描画統合、移動/扉/当たり判定回帰、実機QA。
