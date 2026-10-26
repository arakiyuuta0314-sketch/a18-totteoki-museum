# -*- coding: utf-8 -*-
from pathlib import Path
import zipfile,shutil,json
HERE=Path(__file__).resolve().parent
SRC=HERE/"entrance-wood-onoff-v02-20261026"
ROOT=Path(r"G:\マイドライブ\06.アプリ開発\03.開発・テスト\A18_パズル美術館")
assert ROOT.is_dir()
OUT=ROOT/"53_エントランス無装飾_照明案内板痕跡修復_額縁ONOFF_v02"
OUT.mkdir(exist_ok=True)
for p in SRC.iterdir():
 if p.is_file():shutil.copy2(p,OUT/p.name)
for name in ("build_v02.py","archive_v02.py"):
 shutil.copy2(HERE/name,OUT/name)
archive=OUT/"A18_entrance_wood_ONOFF_v02_20261026.zip"
if archive.exists():archive.unlink()
with zipfile.ZipFile(archive,"w",compression=zipfile.ZIP_DEFLATED) as z:
 for p in OUT.iterdir():
  if p.is_file() and p.name!=archive.name:z.write(p,p.name)
with zipfile.ZipFile(archive) as z: assert z.testzip() is None
m=json.loads((OUT/"QA_manifest.json").read_text(encoding="utf8"))
assert m["outside_repair_mask_changed_pixels"]==m["outside_frame_alpha_changed_pixels"]==0
assert all((OUT/n).is_file() for n in ("entrance_OFF.png","entrance_ON.png","index.html","README.md"))
print("DRIVE_V02_SAVED_OK",OUT,archive.stat().st_size,len(list(OUT.iterdir())))
