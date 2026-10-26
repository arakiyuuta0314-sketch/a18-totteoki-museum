# -*- coding:utf-8 -*-
from pathlib import Path
import shutil,zipfile,json
BASE=Path(__file__).resolve().parent
SOURCE=BASE/'entrance-plain-master-v06-study'
DRIVE=Path(r'G:\マイドライブ\06.アプリ開発\03.開発・テスト\A18_パズル美術館')
assert DRIVE.is_dir()
OUT=DRIVE/'56_エントランス無装飾基準_背面天井再構築_v06_未承認'
OUT.mkdir(exist_ok=True)
for file in SOURCE.iterdir():
 if file.is_file():shutil.copy2(file,OUT/file.name)
for name in ('rebuild_plain_v06.py','finalize_v06.py','archive_v06.py'):
 shutil.copy2(BASE/name,OUT/name)
zpath=OUT/'A18_entrance_plain_v06_comparison_UNAPPROVED.zip'
if zpath.exists():zpath.unlink()
with zipfile.ZipFile(zpath,'w',zipfile.ZIP_DEFLATED) as z:
 for f in OUT.iterdir():
  if f.is_file() and f != zpath:z.write(f,f.name)
with zipfile.ZipFile(zpath) as z: assert z.testzip() is None
assert (OUT/'entrance_OFF.png').read_bytes()==(SOURCE/'entrance_OFF.png').read_bytes()
assert json.loads((OUT/'QA_manifest.json').read_text(encoding='utf8'))['local_browser_QA']['Chrome_result']=='PASS'
print('DRIVE_V06_VERIFIED',OUT,zpath.stat().st_size,len(list(OUT.iterdir())),flush=True)
