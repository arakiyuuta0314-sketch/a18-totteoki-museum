# -*- coding: utf-8 -*-
from pathlib import Path
import shutil,json,zipfile
BASE=Path(__file__).resolve().parent
SRC=BASE/'entrance-plain-master-v09-right-mat'
manifest=SRC/'QA_manifest.json'
m=json.loads(manifest.read_text(encoding='utf8'))
m['local_browser_QA']={'Chrome':'390x844 DPR2','default':'ON','OFF_ON_switch':'PASS','compare_detail_3_images':'PASS','HTTP_JS_errors':0,'horizontal_overflow':False}
manifest.write_text(json.dumps(m,indent=2,ensure_ascii=False),encoding='utf8')
readme="""# A18｜右手前の空き台紙修復 v09／額縁ON/OFF
2026-10-26｜技術合格・美術監修待ち｜Lv1未決定

## 問題・原因
v08の木製額縁復元は枠だけのアルファ合成だった。
旧v07の無装飾背景に残った台紙上辺左の暗い三角／欠損が、
v08の木枠の内側に透けて見えていた。
この旧台紙部分は正式な右手前写真窓と完全一致していなかった。

## 修正
- 49番 right_front_content_empty.png の正式透明台紙を、v08の正規建築ベースに追加。
- OFF＝建築＋49正式台紙、ON＝OFF＋49正式木製額縁。
- 49の right_front_shared_window_mask.png と台紙alphaの対象画素が厳密一致。
- OFF・ONで額縁以外を一切変更しない。
- 右奥柱はv07の太い正式候補のまま、床・キャラクター・扉・天井など同一。
- 新しい画像生成と描き直しなし。

## QA
- 546x483。
- 49台紙：写真窓領域6595画素。前v08との差分は欠けていた157画素だけ。
- マスク外に修復差分0画素。写真窓と額縁alphaの重複0画素。
- OFF/ON差分も木製額縁alpha領域内のみ、外側0画素。
- Chromeスマホ390x844 DPR2：初期ON、OFF/ON切替、欠けの3箇所拡大、JS/HTTPエラー0。
- GitHub Pages公開後に実ブラウザで再試験。公開画像と正本の内容照合。

## 結論・留保
右手前台紙の左上欠けについて技術QA合格。
ただしエントランス背景全体の美術承認、Lv1の構成確定、ゲーム本体統合は行っていない。

作業継続ブランチ：feature/a18-entrance-plain-master-v06-20261026。
mainおよびゲーム本体は変更しない。
"""
(SRC/'README.md').write_text(readme,encoding='utf8')
root=Path(r'G:\マイドライブ\06.アプリ開発\03.開発・テスト\A18_パズル美術館')
assert root.is_dir()
dest=root/'59_エントランス右手前台紙欠損正式素材修復_v09_監修待ち'
dest.mkdir(exist_ok=True)
for p in SRC.iterdir():
 if p.is_file():shutil.copy2(p,dest/p.name)
for file in ('rebuild_mat_v09.py','build_web_v09.py','archive_v09.py'):
 shutil.copy2(BASE/file,dest/file)
z=dest/'A18_entrance_right_mat_v09_review.zip'
if z.exists():z.unlink()
with zipfile.ZipFile(z,'w',zipfile.ZIP_DEFLATED) as w:
 for p in dest.iterdir():
  if p.is_file() and p!=z:w.write(p,p.name)
with zipfile.ZipFile(z) as zf:assert zf.testzip() is None
assert (dest/'entrance_ON.png').read_bytes()==(SRC/'entrance_ON.png').read_bytes()
assert (dest/'entrance_OFF.png').read_bytes()==(SRC/'entrance_OFF.png').read_bytes()
print('ARCHIVE_V09_PASS',dest,len(list(dest.iterdir())),z.stat().st_size)
