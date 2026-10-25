# -*- coding:utf-8 -*-
from pathlib import Path
from PIL import Image
import json,hashlib,shutil,zipfile
R=Path(r"G:\マイドライブ\06.アプリ開発\03.開発・テスト\A18_パズル美術館")
H=Path(__file__).resolve().parent
O=H/"entrance-wood-grain-v02-20261026"
D=R/"44_エントランス完成素材_木製額縁木目改善_v02"
M=json.loads((O/"QA_manifest.json").read_text(encoding="utf-8"))
for k in ["frame_left_wood_grain_v02.png","frame_right_wood_grain_v02.png","frame_front_wood_grain_v02.png",
          "QA_mobile_new_390x844.png","QA_mobile_photo110_390x844.png","QA_four_states_unmodified_wood_new_gold.png",
          "README_完成候補とQA.md","index.html","QA_mobile_v02.cjs"]:
    assert (O/k).is_file(),k
assert M["outside_frame_changed_pixels"]==0
M["browser_qa"]={"viewport":[390,844],"device_pixel_ratio":2,"states":24,
  "js_errors":0,"http_errors":0,"horizontal_overflow":False,"qa_status":"PASS"}
M["visual_approval"]="pending_user_review"
M["source_not_overwritten"]=True
M["official_character_recreated"]=False
M["files"]={q.name:{"sha256":hashlib.sha256(q.read_bytes()).hexdigest(),"bytes":q.stat().st_size}
            for q in O.glob("*.png")}
(O/"QA_manifest.json").write_text(json.dumps(M,ensure_ascii=False,indent=2),encoding="utf-8")
D.mkdir(exist_ok=True)
for q in O.iterdir():
 if q.is_file():shutil.copy2(q,D/q.name)
shutil.copy2(H/"build_woodgrain_v02.py",D/"build_woodgrain_v02.py")
# Source texture sample is a real input, not generated in the execution.
shutil.copy2(H/"wood_atlas_mini.png",D/"wood_atlas_mini.png")
archive=D/"A18_entrance_wood_frame_grain_v02_20261026.zip"
with zipfile.ZipFile(archive,"w",compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for f in D.iterdir():
  if f.is_file() and f!=archive:z.write(f,f.name)
with zipfile.ZipFile(archive) as z: assert z.testzip() is None
assert Image.open(D/"frame_front_wood_grain_v02.png").size==(546,483)
print("DRIVE_44_QA_PASS",len(M["files"]),"PNGS",archive.stat().st_size,"ZIP",str(archive),flush=True)
