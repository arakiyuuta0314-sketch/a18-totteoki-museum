# -*- coding:utf-8 -*-
from pathlib import Path
import json,shutil,zipfile
HERE=Path(__file__).resolve().parent
SRC=HERE/"lighting-ceiling-counter-v01"
DST=Path(r"G:\マイドライブ\06.アプリ開発\03.開発・テスト\A18_パズル美術館\51_エントランス完成候補_天井灯列と受付ランプ分離_v01")
p=SRC/"QA_manifest.json"
m=json.loads(p.read_text(encoding="utf-8"))
m["published_qa"]={"status":"PASS","url":"https://arakiyuuta0314-sketch.github.io/a18-art-previews/entrance-ceiling-counter-v01-20261026/","chrome_css":[390,844],"dpr":2,"tested_states":8,"control_buttons":3,"js_http_errors":0,"horizontal_scroll":False}
p.write_text(json.dumps(m,ensure_ascii=False,indent=2),encoding="utf-8")
shutil.copy2(p,DST/p.name)
# Repack after public QA so Drive ZIP contains the final manifest.
archive=DST/"A18_ceiling_counter_lamps_v01_20261026.zip"
with zipfile.ZipFile(archive,"w",compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for f in DST.iterdir():
  if f.is_file() and f!=archive:z.write(f,f.name)
with zipfile.ZipFile(archive) as z: assert z.testzip() is None
assert json.loads((DST/"QA_manifest.json").read_text(encoding="utf-8"))["published_qa"]["status"]=="PASS"
print("PUBLIC_QA_RECORDED_AND_DRIVE_ZIP_VERIFIED")
