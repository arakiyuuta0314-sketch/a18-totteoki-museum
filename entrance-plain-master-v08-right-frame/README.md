# A18｜右手前木製額縁の復元・比較 v08
2026-10-26｜技術QA合格／美術監修待ち・Lv1未決定

## 事実確認と対応
前v07の右奥柱修正で右手前の枠が欠けたわけではなく、v07は木製額縁をOFFにした無装飾版のみだった。
写真用の台紙とごく細い縁が残るため、右手前の木枠が中途半端に見えていた。
今回、49番の正式 right_front_frame_wood.png を、既存v07 OFFの上にアルファ合成してONを復元。
OFFのファイルはv07とバイト同一。右奥柱の構図は完全に保持した。

## 技術QA
- 元キャンバス546x483。正式PNGに再投影等の再計算なし。
- ON/OFFは木枠PNGアルファの範囲だけ変更。差分は3386画素、アルファ領域外0画素。
- 正式写真窓マスクへの額縁の侵入0画素。
- 右奥の柱・床・キャラ・壁・手すり・建築は同じ。
- ローカルChrome 390x844 DPR2: ON既定表示、OFF/ON切替、3か所拡大画像、HTTP/JSエラー0。
- 公開Pagesでの同じ検査を必須とする。最終監修待ち。

## ファイル
- entrance_OFF.png：v07装飾なし建築の正本をバイト同一で保存
- entrance_ON.png：正式木製枠を載せた候補
- right_front_frame_wood_formal_v07.png：49番の正式独立素材
- QA_*comparison.png：額縁全体・上部・下部の比較
- QA_manifest.json、index.html、QA_browser_v08.cjs
- rebuild_right_frame_v08.py：再現可能な合成コード

## 今後の採用判断
木枠が四辺揃ったON案は美術比較用であり、OFF／ONをLv1に採用するかは決定していない。
既存ゲーム本体とmainは変更していない。
Gitの作業単位を継続し、feature/a18-entrance-plain-master-v06-20261026を使用する。

## 公開配信検証
- GitHub Pages: https://arakiyuuta0314-sketch.github.io/a18-art-previews/entrance-plain-master-v08-right-frame/
- 公開commit: d0d5bd5 (deploy成功)。スマホChrome 390x844 DPR2 ON/OFF切替・拡大3枚・HTTP/JSエラー0。
- 公開PNG5点は制作元とバイト同一、HTMLは改行正規化後同一。
