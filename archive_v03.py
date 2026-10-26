# -*- coding: utf-8 -*-
from pathlib import Path
import json,shutil,zipfile,hashlib
ROOT=Path(r'G:\マイドライブ\06.アプリ開発\03.開発・テスト\A18_パズル美術館')
BASE=Path(__file__).resolve().parent
SRC=BASE/'entrance-art-polish-v03-20261026'
assert ROOT.is_dir()
DEST=ROOT/'54_エントランス木製額縁視認性と照明跡再修復_v03'
DEST.mkdir(exist_ok=True)
for file in SRC.iterdir():
 if file.is_file():shutil.copy2(file,DEST/file.name)
for file in ['build_v03.py','build_web_v03.py','prepare_qa_v03.py','finalize_manifest_v03.py','archive_v03.py']:
 shutil.copy2(BASE/file,DEST/file)
zip_path=DEST/'A18_entrance_wood_frame_and_lighting_polish_v03_20261026.zip'
if zip_path.exists():zip_path.unlink()
with zipfile.ZipFile(zip_path,'w',zipfile.ZIP_DEFLATED) as archive:
 for p in DEST.iterdir():
  if p.is_file() and p!=zip_path:archive.write(p,arcname=p.name)
with zipfile.ZipFile(zip_path) as archive:assert archive.testzip() is None
m=json.loads((DEST/'QA_manifest.json').read_text(encoding='utf8'))
assert m['outside_managed_frame_plus_shadow_changed_pixels']==0
assert m['base_outside_repair_changed_pixels']==0
assert (DEST/'entrance_OFF.png').read_bytes()==(SRC/'entrance_OFF.png').read_bytes()
assert (DEST/'entrance_ON.png').read_bytes()==(SRC/'entrance_ON.png').read_bytes()
print('DRIVE_V03_VERIFIED',str(DEST),zip_path.stat().st_size,len(list(DEST.iterdir())),flush=True)
