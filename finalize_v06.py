# -*- coding:utf-8 -*-
from pathlib import Path
from PIL import Image
import json,hashlib,shutil,zipfile
HERE=Path(__file__).resolve().parent
OUT=HERE/"entrance-canonical-single-H-v06-20261026"
ROOT=Path(r"G:\マイドライブ\06.アプリ開発\03.開発・テスト\A18_パズル美術館")
DEST=ROOT/"48_エントランス完成素材_右手前共通単一射影変換_v06"
required=["README_完成候補とQA.md","index.html","QA_browser_v06.cjs",
"QA_mobile_wood_empty_390x844.png","QA_mobile_gold_photos_390x844.png",
"QA_mobile_registration_390x844.png","single_H_geometry.json",
"right_front_frame_wood.png","right_front_frame_gold.png",
"right_front_content_empty.png","right_front_content_photos.png",
"right_front_shared_window_mask.png","QA_previous_v05_wood_empty.png",
"QA_opposite_angle_same_source.png","QA_manifest.json"]
for f in required: assert (OUT/f).is_file(),f
assert len(list(OUT.glob("view_*.png")))==36
m=json.loads((OUT/"QA_manifest.json").read_text(encoding="utf-8"))
assert m["one_h_exact_common"] and m["photo_window_overlap"]==0
assert m["frame_outer_union_raster_gap_pixels"]==0
m["chrome_qa"]={"resolution_css":[390,844],"device_pixel_ratio":2,
 "tested_states":36,"http_errors":0,"js_errors":0,"overflow":False,"result":"PASS"}
m["user_approved"]=False
m["parent_43_to_47_unchanged"]=True
m["file_hashes"]={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in OUT.glob("*.png")}
(OUT/"QA_manifest.json").write_text(json.dumps(m,ensure_ascii=False,indent=2),encoding="utf-8")
DEST.mkdir(exist_ok=True)
for f in OUT.iterdir():
 if f.is_file():shutil.copy2(f,DEST/f.name)
for name in ["build_v06.py","frame_projection_v06.py","finalize_v06.py"]:
 shutil.copy2(HERE/name,DEST/name)
z=DEST/"A18_entrance_canonical_single_H_v06_20261026.zip"
with zipfile.ZipFile(z,"w",compression=zipfile.ZIP_DEFLATED,compresslevel=6) as a:
 for f in DEST.iterdir():
  if f.is_file() and f!=z:a.write(f,f.name)
with zipfile.ZipFile(z) as a:assert a.testzip() is None
assert Image.open(DEST/"right_front_frame_wood.png").size==(546,483)
print("DRIVE48_SAVE_PASS",len(m["file_hashes"]),"PNGs",z.stat().st_size,"ZIP_BYTES")
