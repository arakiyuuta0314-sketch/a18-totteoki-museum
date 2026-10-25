# A18 背面写真展示灯 左右２灯 v01｜完成候補
**対象：台帳 E04（写真専用の展示灯）**

- entrance_picture_light_west.png / entrance_picture_light_east.png：高品質原本から抽出した透明素材。空枠用。
- entrance_picture_light_west_photo_safe.png / entrance_picture_light_east_photo_safe.png：写真登録後の表示用。写真の暗転・不自然な帯を防ぐため、写真窓に重なる画素は電球の実際の発光部分に限定。
- entrance_bg_without_picture_lights.png：照明がない状態で金色の額縁上辺が続くよう同じ原本の水平画素から復元した下地。
- build_picture_lights.py：素材生成ソース。QA_manifest.json：各画像のSHA-256・寸法・透過・テスト。
- QA_original_reassembled_two_lights.png：空き枠+２灯で、原本546×483 RGB画素完全一致。
- QA_photos_sprites_both_lights.png と QA_photos_sprites_no_lights.png：ユーザー写真と正式キャラを残した表示・非表示比較。
- QA_mobile_390x844.png：実Chromeスマホ390×844で確認した画面。両灯／左のみOFF／両方OFF／復元を検証しエラー0。

ブラウザの実表示レイヤー順序：修復済み背景→写真・額縁→写真に重なる展示灯の限定的な光→正式キャラ→UI。すべて元の光源表現を使用し、他の既採用素材やキャラは変更していません。
※ ゲーム本体へはまだ未統合。ユーザーによる美術監修待ち。
※ 背景復元（照明OFF）は原本に存在しないため、原本画素との一致を主張しません。
