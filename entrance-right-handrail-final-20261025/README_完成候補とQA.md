# A18 右側手すり O03 独立素材完成候補 v01

原本 approved_entrance_trial.jpg の実木目から前景手すりを分離。
- entrance_fg_right_rail.png: 手すりの透過RGBA（546×483、局所透過）
- entrance_right_rail_mask.png: 単体マスク（546×483）
- entrance_right_wall_without_frame_and_rail.png: F03額縁もO03木の手すりも取り除いた右展示壁本体
- source_frame_03.png / source_frame_empty_03.png / source_photo_03.png: 38フォルダ採用済み素材を原本バイトで複製してQA用に使用
- build_right_rail.py: マスクと壁修復の制作ソース
- QA_rail_photo/QA_no_rail_photo / QA_right_rail_on_off.jpg: 完成例と分離確認
- QA_browser_mobile.cjs / QA_mobile_*.png / index.html: 実Chrome(390×844)操作・画像確認

合成順: 背景→額縁を外した展示壁→登録写真または空き枠→F03可変額縁→O03木製手すり→UI。
すべて表示した標準状態は、以前の27フォルダの写真・正式キャラクター入り画像と画素完全一致。
手すりを外した状態の裏面は元画像で完全に隠れていたので緑布・木材色で補修。原本完全一致ではない。
元の正式キャラ原本PNGは改変・再生成なし。
本体未統合。素材完成候補・ユーザー最終美術監修待ち。
