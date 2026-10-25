# A18 エントランス｜正面共通展示枠・全レイヤー同一変形 v05
制作日：2026-10-26

## 目的
木製だけ別に当てこみ、金額縁・写真窓・写真サンプルが異なる座標処理になっていた v04 の不整合を解消する。
43〜46番を上書きせず、正式キャラクター・原画・受付・床・建築を保持する。
今回の対象は右手前1か所。背面左右は既存の木製状態で固定。

## 技術的に重要な変更
- **正面共通素材**：44番の背面左木製額縁、43番の背面左金額縁・金本体・金装飾、43番の背面左写真台紙と写真サンプルを使う。
- **shared_display_geometry.json**に外周4点・写真窓4点を集約。木／金／金装飾／台紙／写真で共通。
- 外枠と内窓がサイズの違う素材を同時に一致させるため、上下左右の4辺を同じ4点組から射影変換（1枚の2D回転だけではない）。
- 写真・台紙は共通の110×83正面窓へ中心トリミング後、同一ターゲット内窓の射影変換と公式43番の写真窓アルファを使用。
- ユーザー写真対応関数は独立した **frame_projection.py** の fit_photo() と project_photo_to_window()。ただしゲーム側の登録・保存処理とは未接続。
- **逆角度**は reversed_quad() を使い共通ソースだけから技術QA画像を生成。展示室への正式設置は未実施。

## ファイル
- frame_projection.py：他エリアから読み込める副作用なしの共通処理
- build_canonical_v05.py：参照フォルダから正面元素材を読み、36シーンの再現テストと完成素材化
- canonical_wood.png / canonical_gold.png / canonical_gold_body.png / canonical_gold_ornaments.png
- canonical_empty_mat.png / canonical_photo_sample.png
- shared_display_geometry.json
- front_wood_projected.png / front_gold_projected.png / front_gold_body_projected.png / front_gold_ornaments_projected.png
- front_empty_projected.png / front_photos_projected.png：同一アルファの写真窓
- QA_canonical_4corner_registration.png、front_registration_projected.png：写真窓四隅の位置QA
- QA_reverse_angle_from_same_canonical.png と QA_reversible_common_frame.png：反対角度変形の技術例
- QA_common_geometry_4styles.png, QA_right_front_none_wood_gold_zoom3x.png, view_*.png
- QA_registration_contract.json、QA_manifest.json、QA_browser_v05.cjs、スマホスクリーンショット、index.html

## 結果
- 共通木製・金額縁のAlpha形状画素一致：PASS
- 写真あり/空き台紙/四隅QAの表示窓Alpha一致：PASS（共通5568画素）
- 木枠／金額縁による同一写真窓の侵入：0画素
- スタイル差分の額縁外への影響：0画素
- 任意の入力画像サイズ5種類（縦長、横長、正方形に近いもの等）の正面トリミング・共通窓投影：PASS
- 同一コードによる逆向きの変形：PASS（技術例）
- 390×844/DPR2 Chrome 36表示状態：PASS、エラー0／横スクロール0

## 制約（誤認防止）
- **元の右手前の華美な金額縁を画素復元したわけではない。** 同一正面素材の金額縁へ切替えたため、古い金装飾の配置は変わる。これを採用するかユーザー監修待ち。
- 外枠と写真窓は共通の幾何で一致するが、異なる美術素材の色・装飾が完全同一に見えるわけではない。
- 背景補修、カーペットなし大理石、建築照明の焼き込みは従来の43番のまま。照明の独立化は未実施。
- 新素材の画質・配色・背景との統一感もユーザー美術承認待ち。Lv1〜6割当未決定。
- 実際のゲーム写真登録、保存、UI遷移への統合試験は未実施。サンプル画像と人工の検証画像で投影を確認した段階。

## 管理
Googleドライブの47番へ保存。Gitは独立worktreeと専用ブランチ。
43〜46番、main、ゲーム本体は変更禁止。既存 Excel 台帳 v1.6 に F17 として追記。
