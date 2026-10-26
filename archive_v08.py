# -*- coding: utf-8 -*-
from pathlib import Path
import json,shutil,zipfile
ROOT=Path(__file__).resolve().parent
OUT=ROOT/'entrance-plain-master-v08-right-frame'
meta=json.loads((OUT/'QA_manifest.json').read_text(encoding='utf8'))
meta['local_browser_test']={'device':'Chrome 390x844 DPR2','default':'frame_ON','button_switches':2,'detail_zoom_images':3,'errors':0,'result':'PASS'}
(OUT/'QA_manifest.json').write_text(json.dumps(meta,indent=2,ensure_ascii=False),encoding='utf8')
(OUT/'README.md').write_text("""# A18｜右手前木製額縁の復元・比較 v08
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
""",encoding='utf8')
with (OUT/'README.md').open('a',encoding='utf8') as f:
 f.write('\n## 公開配信検証\n- GitHub Pages: https://arakiyuuta0314-sketch.github.io/a18-art-previews/entrance-plain-master-v08-right-frame/\n- 公開commit: d0d5bd5 (deploy成功)。スマホChrome 390x844 DPR2 ON/OFF切替・拡大3枚・HTTP/JSエラー0。\n- 公開PNG5点は制作元とバイト同一、HTMLは改行正規化後同一。\n')
DRIVE=Path(r'G:\マイドライブ\06.アプリ開発\03.開発・テスト\A18_パズル美術館')
assert DRIVE.is_dir()
dest=DRIVE/'58_エントランス右手前正式木製額縁復元_ONOFF比較_v08_監修待ち'
dest.mkdir(exist_ok=True)
for p in OUT.iterdir():
 if p.is_file():shutil.copy2(p,dest/p.name)
for n in ('rebuild_right_frame_v08.py','archive_v08.py','verify_public_v08.py'):
 shutil.copy2(ROOT/n,dest/n)
z=dest/'A18_front_frame_v08_review_package.zip'
if z.exists():z.unlink()
with zipfile.ZipFile(z,'w',zipfile.ZIP_DEFLATED) as f:
 for p in dest.iterdir():
  if p.is_file() and p!=z:f.write(p,p.name)
with zipfile.ZipFile(z) as f:assert f.testzip() is None
assert (dest/'entrance_OFF.png').read_bytes()==(ROOT/'entrance-plain-master-v07-right-column'/'entrance_OFF.png').read_bytes()
assert (dest/'entrance_ON.png').read_bytes()==(OUT/'entrance_ON.png').read_bytes()
print('DRIVE_V08_VERIFIED',dest,len(list(dest.iterdir())),z.stat().st_size,flush=True)
