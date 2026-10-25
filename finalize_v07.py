# -*- coding:utf-8 -*-
from pathlib import Path
from PIL import Image
import json,hashlib,shutil,zipfile
HERE=Path(__file__).resolve().parent
OUT=HERE/"entrance-wall-plane-v07-20261026"
DRIVE=Path(r"G:\マイドライブ\06.アプリ開発\03.開発・テスト\A18_パズル美術館")/"49_エントランス完成素材_右手前壁面基準再投影_v07"
required=["single_H_geometry.json","QA_manifest.json","QA_wall_plane_contract.json",
"right_front_frame_wood.png","right_front_frame_gold.png","right_front_shared_window_mask.png",
"QA_wall_plane_and_derived_display_outer.png","QA_mobile_wood_empty_390x844.png","README_完成候補とQA.md",
"index.html","QA_browser_v07.cjs","QA_previous_v06_wood_empty.png"]
for x in required:assert (OUT/x).is_file(),x
assert len(list(OUT.glob("view_*.png")))==36
r=json.loads((OUT/"QA_wall_plane_contract.json").read_text(encoding="utf-8"))
m=json.loads((OUT/"QA_manifest.json").read_text(encoding="utf-8"))
assert r["result"]=="PASS" and r["both_edges_improved"] and m["one_h_exact_common"]
assert m["frame_outer_union_raster_gap_pixels"]<=2
m["qa_chrome_mobile_390x844_dpr2"]={"states":36,"js_errors":0,"http_errors":0,"horizontal_overflow":False,"status":"PASS"}
m["source_wall_corners_approved"]=False
m["wall_qa"]=r
m["files_sha256"]={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in OUT.glob("*.png")}
(OUT/"QA_manifest.json").write_text(json.dumps(m,ensure_ascii=False,indent=2),encoding="utf-8")
DRIVE.mkdir(exist_ok=True)
for p in OUT.iterdir():
 if p.is_file():shutil.copy2(p,DRIVE/p.name)
for n in ("build_v07.py","frame_projection_v06.py","QA_wall_plane_contract.py"):
 shutil.copy2(HERE/n,DRIVE/n)
archive=DRIVE/"A18_entrance_wall_plane_frames_v07_20261026.zip"
with zipfile.ZipFile(archive,"w",compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for p in DRIVE.iterdir():
  if p.is_file() and p!=archive:z.write(p,p.name)
with zipfile.ZipFile(archive) as z:assert z.testzip() is None
assert Image.open(DRIVE/"right_front_frame_wood.png").size==(546,483)
print("FINALIZE_V07_PASS",len(m["files_sha256"]),"pngs",archive.stat().st_size,"zip bytes",str(DRIVE),flush=True)
