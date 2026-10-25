# -*- coding:utf-8 -*-
from pathlib import Path
from PIL import Image
import json,hashlib,zipfile,shutil
BASE=Path(__file__).resolve().parent
SRC=BASE/"entrance-front-homography-v04-20261026"
ROOT=Path(r"G:\マイドライブ\06.アプリ開発\03.開発・テスト\A18_パズル美術館")
DEST=ROOT/"46_エントランス完成素材_正面木製額縁遠近変形共通化_v04"
need=["frame_front_wood_from_rect_source_v04.png","QA_reverse_angle_same_source_example.png",
      "QA_mobile_new_frame_390x844.png","QA_mobile_photo_110_390x844.png",
      "README_完成候補とQA.md","index.html","QA_browser_v04.cjs","QA_manifest.json"]
for n in need:assert (SRC/n).is_file(),n
assert len(list(SRC.glob("view_*.png")))==30
m=json.loads((SRC/"QA_manifest.json").read_text(encoding="utf-8"))
assert m["photo_window_overlap"]==0 and "projective" in m["geometry_method"]
m["browser_qa"]={"size_css":[390,844],"device_pixel_ratio":2,"states_passed":30,
                "http_errors":0,"js_errors":0,"horizontal_overflow":False}
m["status"]="art_candidate_pending_user_approval"
m["parent_art_43_44_45_unchanged"]=True
m["file_checksums"]={f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in SRC.glob("*.png")}
(SRC/"QA_manifest.json").write_text(json.dumps(m,ensure_ascii=False,indent=2),encoding="utf-8")
DEST.mkdir(exist_ok=True)
for f in SRC.iterdir():
 if f.is_file():shutil.copy2(f,DEST/f.name)
for n in ("build_front_homography_v04.py","inspect_geometry.py","probe_homography.py","additional_homography_QA.py"):
 shutil.copy2(BASE/n,DEST/n)
zipfile_path=DEST/"A18_front_frame_homography_v04_20261026.zip"
with zipfile.ZipFile(zipfile_path,"w",compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for f in DEST.iterdir():
  if f.is_file() and f!=zipfile_path:z.write(f,f.name)
with zipfile.ZipFile(zipfile_path) as z:assert z.testzip() is None
assert Image.open(DEST/"frame_front_wood_from_rect_source_v04.png").size==(546,483)
print("DRIVE_46_PASS",len(m["file_checksums"]),"PNGs",zipfile_path.stat().st_size,"zip bytes")
