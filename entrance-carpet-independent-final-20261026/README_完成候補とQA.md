# A18 赤いカーペット本体の独立素材（完成候補 v01）
制作日：2026-10-26

## 構成と保存
完成候補（単体QA済み、ユーザー美術監修待ち、ゲーム未統合）
- entrance_marble_floor_without_carpet.png：カーペットが隠していた床を復元した546×483の建築下地。
- entrance_red_carpet_body.png：元絵の赤絨毯を透過PNGに分離（235×223）。
- entrance_red_carpet_plain_body.png：残留金刺繍を抑えたシンプルな赤布版（235×223）。
- entrance_red_carpet_gold_trim.png：以前採用済み31フォルダの金縁素材をバイト一致でそのまま使用。
- entrance_red_carpet_contact_shadow.png：独立した接地影（235×223、透明PNG）。
- entrance_red_carpet_body_mask.png：透過マスク、entrance_floor_repair_mask.png：床の補修範囲。
- entrance_red_carpet_gold_residue_removal_mask.png：無金縁版の補修元。
- build_carpet_independent.py：独立素材を原本から再生成するPython＋Pillow＋OpenCV＋SciPyソース。
- source_*.png/jpg：既存A案と装飾素材の原本。characters/：正式キャラ原本そのまま。
- QA_*.png/jpg、QA_manifest.json、QA_browser_mobile.cjs：品質比較とブラウザ試験。

## 描画仕様
座標系：承認済み元画像546×483。
カーペット本体は (164,226) に配置。共通アンカー (281,438) から全体の等比拡縮。
金縁は (173,235) に置き、同じアンカーと倍率に従って移動。
描画順：床下地 → 接地影 → 赤布（シンプル or 装飾対応）→ 金縁（任意）→ 正式キャラ → UI。
0%(非表示)・90%・100%・110%、横位置 -5..+5px に対応。中心は規定レベル設定ではない。

## QA
・金縁あり/なし、絨毯あり/なし、サイズ90/100/110を実画像で比較。
・原本と金縁あり100%の全体平均チャンネル絶対誤差は1未満（数値はQA_manifest）。
  完全な画素一致は主張しない。隠れていた床は完全な原本からの復元が不可能。
・正式キャラPNGは同一バイト。写真窓・建築への影響なし。
・Chrome 390×844 DPR2、表示切替とサイズ調整・位置・リセット・画像読み込み確認、
  JavaScript/HTTPエラー0。

## 採用方針
カーペット・金縁は同じオブジェクトではなく異なる成長素材。
Lv.1やLv.2の割り当ては**未決定**。絨毯なし床も比較してから決定する。
ゲーム本体の描画コード、当たり判定、保存は変更しない。
