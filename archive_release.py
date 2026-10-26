# -*- coding: utf-8 -*-
from pathlib import Path
import shutil,zipfile,json,hashlib
repo=Path(r"C:\Users\User\source\repos\a18-entrance-wood-onoff-v01-20261026")
src=repo/"entrance-wood-onoff-v01-20261026"
parent=Path(r"G:\マイドライブ\06.アプリ開発\03.開発・テスト\A18_パズル美術館")
assert parent.is_dir()
dest=parent/"52_エントランス完成候補_無装飾木額縁ONOFF比較_v01"
dest.mkdir(exist_ok=True)
assert (src/"entrance_ON.png").is_file()
for p in src.iterdir():
 if p.is_file():shutil.copy2(p,dest/p.name)
for name in ("build_wood_onoff.py","archive_release.py"):
 shutil.copy2(repo/name,dest/name)
zip_path=dest/"A18_entrance_wood_ONOFF_v01_20261026.zip"
with zipfile.ZipFile(zip_path,"w",compression=zipfile.ZIP_DEFLATED) as z:
 for p in src.iterdir():
  if p.is_file():z.write(p,p.name)
 for name in ("build_wood_onoff.py","archive_release.py"):z.write(repo/name,name)
manifest=json.loads((dest/"QA_manifest.json").read_text(encoding="utf8"))
assert manifest["non_wood_changed_pixels"]==0
assert zipfile.is_zipfile(zip_path)
print("DRIVE_RELEASE_VERIFIED",dest,zip_path.stat().st_size,len(list(dest.iterdir())))
