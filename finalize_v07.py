# -*- coding: utf-8 -*-
from pathlib import Path
import json,shutil,zipfile
BASE=Path(__file__).resolve().parent
OUT=BASE/'entrance-plain-master-v07-right-column'
qa=BASE/'QA_candidate_right_column_options.png'
if qa.is_file():shutil.copy2(qa,OUT/'QA_column_width_options.png')
manifest=OUT/'QA_manifest.json'
record=json.loads(manifest.read_text(encoding='utf8'))
record['local_browser_qa']={'viewport':[390,844],'DPR':2,'result':'PASS','mode_transitions':2,'zoom_images_loaded':3,'HTTP_and_JS_errors':0}
record['final_design_approval']=False
record['game_integration']=False
manifest.write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf8')
readme="""# A18｜無装飾エントランス・右奥柱拡張 v07

2026-10-26｜無装飾基準の局所改修｜美術監修待ち

## 作業内容
- 直前の56番・v06 546x483背景画像を基準に、右奥の柱が細く端まで届かない問題を修正。
- 左奥の既存柱の実画像（x=0..32、y=0..212）を左右反転して、右側の画像端（x=513..545、y=0..212）に配置。
- PNGの原画画像からのみ素材を再利用。リサンプリングや画像生成AIによる新規図形化はしない。
- 手前右の正式展示壁と手すりを各正式素材のalphaで保護。ユーザーが指定していない扉、床、受付、キャラクター、奥の展示面は画素変更しない。
- v06とv07を切り替えるPages試作。木製額縁ONとLv1採用の判断は今回しない。

## 再構成と技術QA
- 変更：6,151画素、指定右端柱の範囲外変更0画素。
- 保護した前景素材の可視画素変更0画素。扉・床・人物・写真台紙は同一。
- Chrome 390x844 DPR2 で比較切替、拡大3箇所、JS/HTTPエラーなし。
- QA_right_corner/capital/seam_before_after.png で局所拡大検査。
- QA_column_width_options.png で複数の柱幅と旧版の見た目を比較。

## 美術上の状態
- v07で柱を左と同じ厚さにし、右端まで届く形に改善。
- y=213以降の前景・床は意図的に変更しない。外側木部の影や壁の接合など、既存背景に由来する補修問題については全館の美術承認待ち。
- 技術QA合格 != 最終美術承認。Lv.1用基準マスターに確定していない。
- 現時点で既存ゲームの正式素材もmainも変更していない。

## Git
- 既存のfeature/a18-entrance-plain-master-v06-20261026を継続（同じ無装飾背景完成の作業単位）。
- 公開用作業worktreeはfeature/a18-plain-master-v06-preview-20261026を継続。
- 正式ゲーム本体への自動統合なし。

## 公開検証
- URL: https://arakiyuuta0314-sketch.github.io/a18-art-previews/entrance-plain-master-v07-right-column/
- Pagesコミット 563b3d3 は公開完了。390x844 DPR2 Chromeで比較切替・拡大画像3点、HTTP/JSエラーなし。
- PNG5点は公開先と制作元でバイト単位一致。index.htmlは改行コード正規化後に内容一致。
"""
(OUT/'README.md').write_text(readme,encoding='utf8')
drive=Path(r'G:\マイドライブ\06.アプリ開発\03.開発・テスト\A18_パズル美術館')
assert drive.is_dir()
d=drive/'57_エントランス無装飾基準_右奥柱端まで拡張_v07_監修待ち'
d.mkdir(exist_ok=True)
for p in OUT.iterdir():
 if p.is_file():shutil.copy2(p,d/p.name)
for name in ('rebuild_right_column_v07.py','prepare_v07_page.py','finalize_v07.py','verify_public_v07.py'):
 shutil.copy2(BASE/name,d/name)
archive=d/'A18_entrance_right_column_v07_UNAPPROVED.zip'
if archive.exists():archive.unlink()
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
 for p in d.iterdir():
  if p.is_file() and p!=archive:z.write(p,p.name)
with zipfile.ZipFile(archive) as z:assert z.testzip() is None
assert (d/'entrance_OFF.png').read_bytes()==(OUT/'entrance_OFF.png').read_bytes()
assert json.loads((d/'QA_manifest.json').read_text(encoding='utf8'))['outside_declared_right_corner_change']==0
print('DRIVE_V07_ARCHIVE_VERIFIED',str(d),'FILES',len(list(d.iterdir())),'ZIP_BYTES',archive.stat().st_size)
