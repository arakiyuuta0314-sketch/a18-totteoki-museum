# -*- coding:utf-8 -*-
from pathlib import Path
from PIL import Image
import json,shutil,zipfile,hashlib
R=Path(r"G:\マイドライブ\06.アプリ開発\03.開発・テスト\A18_パズル美術館")
H=Path(__file__).resolve().parent
S=H/"lighting-additional-sconces-v01"
D=R/"50_エントランス完成候補_追加壁灯4点分離_v01"
need=["index.html","README_完成候補とQA.md","QA_browser_lights.cjs","QA_manifest.json",
"QA_all_four_sconces_off.png","QA_all_four_sconces_on.png","QA_all_four_body_only.png",
"QA_mobile_all_off_390x844.png","QA_mobile_all_on_390x844.png","QA_mobile_body_only_390x844.png"]
for n in need:assert (S/n).is_file(),n
m=json.loads((S/"QA_manifest.json").read_text(encoding="utf-8"))
assert m["technical_QA"]["result"]=="PASS"
assert len(list(S.glob("fixture_*.png")))==8
m["final_art_approval"]=False
m["pending_ceiling_and_counter_lights"]=True
m["mobile_qa"]={"css_width":390,"css_height":844,"dpr":2,"states":32,"result":"PASS"}
m["materials_sha256"]={f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in S.glob("*.png")}
(S/"QA_manifest.json").write_text(json.dumps(m,ensure_ascii=False,indent=2),encoding="utf-8")
D.mkdir(exist_ok=True)
for f in S.iterdir():
 if f.is_file():shutil.copy2(f,D/f.name)
for n in ["build_missing_sconces_v01.py","QA_sconces_contract.py","inspect_unseparated_lights.py"]:
 shutil.copy2(H/n,D/n)
archive=D/"A18_missing_wall_sconces_v01_20261026.zip"
with zipfile.ZipFile(archive,"w",compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for f in D.iterdir():
  if f.is_file() and f!=archive:z.write(f,f.name)
with zipfile.ZipFile(archive) as z:assert z.testzip() is None
assert Image.open(D/"fixture_foreground_left_body.png").mode=="RGBA"
print("SAVE_QA_PASS",len(m["materials_sha256"]),"pngs",archive.stat().st_size,"zipbytes",D)
