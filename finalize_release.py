# -*- coding:utf-8 -*-
from pathlib import Path
import json,hashlib,shutil,zipfile
ROOT=Path(r"G:\マイドライブ\06.アプリ開発\03.開発・テスト\A18_パズル美術館")
HERE=Path(__file__).resolve().parent
WEB=HERE/"entrance-frames-independent-20261026"
G=ROOT/"43_エントランス完成素材_3額縁本体装飾分離_v01"
ORIG=HERE/"entrance-test-v3/layout-test/assets/entrance/v0.3/approved_entrance_trial.jpg"
for name in ("QA_mobile_no_gold_390x844.png","QA_mobile_wood_photo110_390x844.png","QA_mobile_gold_recovered_390x844.png","index.html","README_完成候補とQA.md"):
 assert (WEB/name).is_file(),name
for fn,src in [("source_approved_entrance_trial.jpg",ORIG),
 ("source_A_without_carpet_and_characters.png",ROOT/"42_エントランス完成素材_赤絨毯本体分離_v01"/"QA_bare_floor_without_characters.png")]:
 shutil.copy2(src,WEB/fn)
chars=WEB/"characters";chars.mkdir(exist_ok=True)
for fn in ("butler-front-00.png","curator-front-00.png"):
 original=ROOT/"00_正式採用素材"/"characters"/fn
 shutil.copy2(original,chars/fn)
 assert original.read_bytes()==(chars/fn).read_bytes()
data=json.loads((WEB/"QA_manifest.json").read_text(encoding="utf-8"))
assert data["full_reassembly_changed_pixels"]<=17
data["browser_qa"]={"viewport_css":[390,844],"dpr":2,"states":18,
  "styles":["none","wood","gold_full"],"photo_modes":["empty","photos"],"scales":[90,100,110],
  "http_errors":0,"javascript_errors":0,"horizontal_overflow":False,"status":"PASS"}
data["user_approval"]=False
data["game_integrated"]=False
data["lv1_6_assigned"]=False
data["approved_source_characters_recreated"]=False
data["files_after_qa"]={q.name:{"sha256":hashlib.sha256(q.read_bytes()).hexdigest(),"bytes":q.stat().st_size}
                         for q in WEB.glob("*.png")}
(WEB/"QA_manifest.json").write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding="utf-8")
G.mkdir(exist_ok=True)
for item in WEB.rglob("*"):
 if item.is_file():
  tgt=G/item.relative_to(WEB);tgt.parent.mkdir(parents=True,exist_ok=True)
  shutil.copy2(item,tgt)
shutil.copy2(HERE/"build_removable_frames.py",G/"build_removable_frames.py")
shutil.copy2(HERE/"finalize_release.py",G/"finalize_release.py")
archive=G/"A18_entrance_3_frames_independent_v01_20261026.zip"
with zipfile.ZipFile(archive,"w",zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for item in G.rglob("*"):
  if item.is_file() and item!=archive:
   z.write(item,item.relative_to(G))
with zipfile.ZipFile(archive) as z:
 assert z.testzip() is None
print('FINAL_QA_PASS',len(data["files_after_qa"]),'PNGs',archive.stat().st_size,'ZIP bytes')
print('GOOGLE_DRIVE_FOLDER',G)
