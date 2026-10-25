# A18 エントランス E03：受付の花と銀色の花器｜完成候補v01

## 美術素材
- entrance_counter_flower_vase.png：正式採用背景から実物の花4輪・葉・金属花器を抽出したRGBA（44×75）。
- entrance_counter_flower_alpha_mask.png：上記のアルファ窓。
- entrance_bg_without_counter_flower.png：花器が焼き込まれた台面を復旧した546×483の背景。
- source_flower_alpha_mask.png：後から再編集可能な抽出元のアルファマスク。
- source_tabletop_restoration_patch.png：修復したカウンター天板の切片。
- source_tabletop_restoration_mask.png：修復適用範囲の元データ。
- source_approved_preview_photos_formal_characters.png：過去の正式キャラクター・展示枠合成の検証元。
- build_counter_flower.py：素材ソース。元画像・上記マスク・復元パッチで再構成できる。
- index.html / flower-preview.js：スマホで花のオンオフ・90～110％・左右微調整を実際に検証。
- QA_* / QA_manifest.json：静止比較・サイズ比較・モバイルChrome・素材情報。

## 座標と順序
原本：approved_entrance_trial.jpg（546×483）
オブジェクト左上：（68,318）。44×75ピクセル。鉢底に近いアンカー（22,70）。
基本描画：修復済み天板背景→必要な建築/展示・正式キャラ→花器→UI。
検証済み変更：90／100／110％、標準位置から左へ5px。これ以上は周辺物との干渉を再評価すること。

## QAと美術上の注意
- 元の原画の花と花器を取り出し、キャラクターを生成・変更していない。
- 花器なしの下地は元から隠れていたため再構築したもの。原本の全画素一致は主張しない。
- 変更矩形の外側は原本と完全一致。
- 通常スケールで全画面平均RGB差 0.03924（原本との比較、情報はQA_manifest.json）。
- Chrome 390×844のモバイル表示で、表示・非表示、拡大縮小、位置・リセットを操作、JS／ネットワークエラー0。
- 前回未完成の左右観葉植物は同一フォルダに混ぜず、別途継続調整。
- ゲーム本体へは未統合。ユーザーによる美術最終採用待ち。
