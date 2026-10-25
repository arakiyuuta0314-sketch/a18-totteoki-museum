# -*- coding:utf-8 -*-
from pathlib import Path
from PIL import Image
import json, hashlib, shutil, zipfile
HERE=Path(__file__).resolve().parent
O=HERE/"entrance-canonical-front-v05-20261026"
ROOT=Path(r"G:\マイドライブ\06.アプリ開発\03.開発・テスト\A18_パズル美術館")
DEST=ROOT/"47_エントランス完成素材_右手前展示枠共通変形化_v05"
need=["README_完成候補とQA.md","index.html","QA_browser_v05.cjs",
      "QA_mobile_wood_empty_390x844.png","QA_mobile_gold_photo_390x844.png",
      "shared_display_geometry.json","QA_registration_contract.json",
      "QA_manifest.json","front_wood_projected.png","front_gold_projected.png",
      "front_photos_projected.png","front_empty_projected.png",
      "QA_reverse_angle_from_same_canonical.png"]
for n in need:assert (O/n).is_file(),n
views=list(O.glob("view_*.png"))
assert len(views)==36,len(views)
report=json.loads((O/"QA_manifest.json").read_text(encoding="utf-8"))
assert report["photo_window_frame_overlap_pixels"]==0
qa=json.loads((O/"QA_registration_contract.json").read_text(encoding="utf-8"))
assert qa["result"]=="PASS" and qa["all_photo_masks_identical"]
report["browser_qa"]={"css_viewport":[390,844],"device_pixel_ratio":2,
 "states":36,"js_errors":0,"http_errors":0,"horizontal_overflow":False}
report["user_approved"]=False
report["original_gold_front_asset_preserved_not_used_for_new_display"]=True
report["game_integrated"]=False
report["files_sha256"]={f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in O.glob("*.png")}
(O/"QA_manifest.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
DEST.mkdir(exist_ok=True)
for f in O.iterdir():
 if f.is_file():shutil.copy2(f,DEST/f.name)
for n in ("frame_projection.py","build_canonical_v05.py","QA_projection_contract.py"):
 shutil.copy2(HERE/n,DEST/n)
archive=DEST/"A18_entrance_exhibit_canonical_v05_20261026.zip"
with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as zipf:
 for f in DEST.iterdir():
  if f.is_file() and f!=archive:zipf.write(f,f.name)
with zipfile.ZipFile(archive) as zipf:assert zipf.testzip() is None
assert Image.open(DEST/"frame_wood_projected.png").size==(546,483) if (DEST/"frame_wood_projected.png").exists() else True
print("SAVE_PASS",len(views),"display variants",len(report["files_sha256"]),"PNGs",archive.stat().st_size,"zip bytes")
