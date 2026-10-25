# -*- coding:utf-8 -*-
from pathlib import Path
from PIL import Image
import hashlib,json,shutil,zipfile
ROOT=Path(r"G:\マイドライブ\06.アプリ開発\03.開発・テスト\A18_パズル美術館")
HERE=Path(__file__).resolve().parent
SRC=HERE/"lighting-ceiling-counter-v01"
DST=ROOT/"51_エントランス完成候補_天井灯列と受付ランプ分離_v01"
need=["index.html","README_完成候補とQA.md","QA_browser_ceiling_counter.cjs",
      "QA_mobile_all_off_390x844.png","QA_mobile_all_on_390x844.png","QA_mobile_body_only_390x844.png",
      "ceiling_lamp_row_body.png","ceiling_lamp_row_emission.png",
      "ceiling_lamp_unit_body.png","ceiling_lamp_unit_emission.png",
      "counter_lamp_body.png","counter_lamp_emission.png",
      "QA_ceiling_and_counter_removed_background.png",
      "QA_eight_reusable_identical_units_demo.png","QA_manifest.json"]
for filename in need:assert (SRC/filename).is_file(),filename
manifest=json.loads((SRC/"QA_manifest.json").read_text(encoding="utf-8"))
assert manifest["technical_qa"]["pass"] is True
assert manifest["technical_qa"]["pixels_outside_ceiling_or_counter_regions_changed"]==0
assert manifest["ceiling_lamps_count"]==8
assert len(manifest["technical_qa"]["transparent_assets"])==6
manifest["art_user_approved"]=False
manifest["published_qa"]="will_validate_after_push"
manifest["files_sha256"]={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in SRC.glob("*.png")}
(SRC/"QA_manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding="utf-8")
DST.mkdir(exist_ok=True)
for f in SRC.iterdir():
 if f.is_file():shutil.copy2(f,DST/f.name)
for name in ["build_ceiling_desk_v01.py","QA_ceiling_counter_contract.py","inspect_ceiling_counter.py"]:
 p=HERE/name
 if p.exists():shutil.copy2(p,DST/name)
zip_path=DST/"A18_ceiling_counter_lamps_v01_20261026.zip"
with zipfile.ZipFile(zip_path,"w",compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for file in DST.iterdir():
  if file.is_file() and file!=zip_path:z.write(file,file.name)
with zipfile.ZipFile(zip_path) as z:assert z.testzip() is None
assert Image.open(DST/"counter_lamp_body.png").size==(546,483)
print("DRIVE_51_ASSET_SAVE_PASS",len(manifest["files_sha256"]),"PNGs",zip_path.stat().st_size,"ZIP_BYTES")
