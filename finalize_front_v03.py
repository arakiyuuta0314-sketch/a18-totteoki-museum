# -*- coding:utf-8 -*-
from pathlib import Path
from PIL import Image
import hashlib,json,shutil,zipfile
ROOT=Path(r"G:\マイドライブ\06.アプリ開発\03.開発・テスト\A18_パズル美術館")
HERE=Path(__file__).resolve().parent
SRC=HERE/"entrance-front-wood-aligned-v03-20261026"
DEST=ROOT/"45_エントランス完成素材_右手前木製額縁金縁位置合わせ_v03"
for n in ("index.html","README_完成候補とQA.md","QA_mobile_v03.cjs",
          "QA_mobile_front_corrected_390x844.png","QA_mobile_front_photo110_390x844.png",
          "frame_front_wood_grain_aligned_v03.png","QA_gold_with_wood_footprint_overlay.png"):
    assert (SRC/n).exists(),n
views=list(SRC.glob("view_*.png"))
assert len(views)==24,len(views)
data=json.loads((SRC/"QA_manifest.json").read_text(encoding="utf-8"))
assert data["outside_former_front_alpha_changed_pixels"]==0
data["qa_browser"]={"390x844_dpr2":"PASS","states":24,"http_error":0,"javascript_error":0,"horizontal_scroll":False}
data["user_visual_approval"]=False
data["base_version_44_untouched"]=True
data["files"]={p.name:{"sha256":hashlib.sha256(p.read_bytes()).hexdigest(),"bytes":p.stat().st_size} for p in SRC.glob("*.png")}
(SRC/"QA_manifest.json").write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding="utf-8")
DEST.mkdir(exist_ok=True)
for f in SRC.iterdir():
 if f.is_file():shutil.copy2(f,DEST/f.name)
for fn in ("front_align_v03.py","front_mask_study.py","inspect_front.py"):
 shutil.copy2(HERE/fn,DEST/fn)
if (HERE/"QA_front_geometry_study.png").exists():shutil.copy2(HERE/"QA_front_geometry_study.png",DEST/"QA_front_geometry_study.png")
archive=DEST/"A18_front_wood_frame_aligned_v03_20261026.zip"
with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for f in DEST.rglob("*"):
  if f.is_file() and f!=archive:z.write(f,f.relative_to(DEST))
with zipfile.ZipFile(archive) as z: assert z.testzip() is None
assert Image.open(DEST/"frame_front_wood_grain_aligned_v03.png").size==(546,483)
print("SAVE_QA_PASS",str(DEST),"24 views",len(data["files"]),"png",archive.stat().st_size,"zip bytes",flush=True)
