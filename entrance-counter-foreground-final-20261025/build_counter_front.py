# -*- coding:utf-8 -*-
from pathlib import Path
from PIL import Image,ImageDraw
import cv2,numpy as np,json,hashlib,shutil
R=Path(r"C:\Users\User\source\repos\a18-entrance-counter-edge-20261025")
OUT=R/"entrance-counter-foreground-final-20261025"
SRC=R/"entrance-test-v3/layout-test/assets/entrance/v0.3/approved_entrance_trial.jpg"
OFF=Path(r"G:\マイドライブ\06.アプリ開発\03.開発・テスト\A18_パズル美術館\00_正式採用素材\characters")
P=R/"entrance-rear-frames-final-20261025"/"QA_photos_100pct.png"
for p in [SRC,P,OFF/"curator-front-00.png",OFF/"butler-front-00.png"]:
 assert p.exists(),p
ref=Image.open(SRC).convert("RGB");rgb=np.array(ref);H,W=rgb.shape[:2]
pieces={
 "top_lip":[(0,384),(94,384),(101,380),(105,367),(109,342),(117,324),(127,325),(119,365),(115,388),(110,395),(0,396)],
 "front_face":[(0,395),(109,395),(106,432),(101,449),(60,451),(52,421),(0,416)]
}
alpha={}
for name,poly in pieces.items():
 m=Image.new("L",(W,H),0);d=ImageDraw.Draw(m)
 d.polygon(poly,fill=255)
 if name=="front_face":
  d.polygon([(0,415),(50,415),(60,451),(0,451)],fill=0)
 m=np.asarray(m)
 alpha[name]=m
 Image.fromarray(np.dstack((rgb,m)),"RGBA").save(OUT/f"entrance_counter_fg_{name}.png",optimize=True)
 Image.fromarray(m,"L").save(OUT/f"entrance_counter_mask_{name}.png",optimize=True)
total=np.maximum.reduce(list(alpha.values()))
clean=rgb.copy()
# Hidden below counter: use surrounding original marble and wood tones, not invented scene.
donor=np.asarray(ref.crop((141,322,269,450)))
extension=cv2.resize(donor,(128,129),interpolation=cv2.INTER_CUBIC)
for y in range(322,451):
 for x in range(128):
  if total[y,x]:
   clean[y,x]=extension[y-322,x]
Image.fromarray(clean).save(OUT/"entrance_bg_without_counter_front.png",optimize=True)
top=Image.open(OUT/"entrance_counter_fg_top_lip.png").convert("RGBA")
face=Image.open(OUT/"entrance_counter_fg_front_face.png").convert("RGBA")
def compose(bk):
 can=Image.fromarray(bk).convert("RGBA")
 can.alpha_composite(top);can.alpha_composite(face)
 return can.convert("RGB")
back=compose(clean);back.save(OUT/"QA_source_exact_reassembly.png",optimize=True)
assert np.array_equal(np.asarray(back),rgb),"must match every pixel of source"
photo=np.asarray(Image.open(P).convert("RGB")).copy()
photo[total>0]=clean[total>0]
Image.fromarray(photo).save(OUT/"QA_underlay_photos.png",optimize=True)
def sprite(can,name,cx,foot,width):
 im=Image.open(OFF/name).convert("RGBA")
 h=round(im.height*width/im.width)
 im=im.resize((width,h),Image.Resampling.NEAREST)
 can.alpha_composite(im,(round(cx-width/2),foot-h))
 return hashlib.sha256((OFF/name).read_bytes()).hexdigest()
shutil.copy2(OFF/"curator-front-00.png",OUT/"curator-front-00.png")
# Behind: counter masks hide the bottom of the actor.
depth_b=Image.fromarray(photo).convert("RGBA")
sprhash=sprite(depth_b,"curator-front-00.png",65,393,35)
depth_b.alpha_composite(top);depth_b.alpha_composite(face)
depth_b.convert("RGB").save(OUT/"QA_actor_behind_counter.png")
# In front, sprite fully visible
depth_f=Image.fromarray(photo).convert("RGBA")
depth_f.alpha_composite(top);depth_f.alpha_composite(face)
sprite(depth_f,"curator-front-00.png",65,443,35)
depth_f.convert("RGB").save(OUT/"QA_actor_in_front_counter.png")
# Rest of gallery includes original photo and existing official sprite locations
gallery=Image.fromarray(photo).convert("RGBA")
gallery.alpha_composite(top);gallery.alpha_composite(face)
sprite(gallery,"butler-front-00.png",140,371,43)
sprite(gallery,"curator-front-00.png",287,366,35)
gallery.convert("RGB").save(OUT/"QA_complete_scene_formal_characters.png",optimize=True)
board=Image.new("RGB",(1092,483))
board.paste(depth_b.convert("RGB"),(0,0));board.paste(depth_f.convert("RGB"),(546,0))
board.save(OUT/"QA_counter_front_back.png")
manifest={"source_sha256":hashlib.sha256(SRC.read_bytes()).hexdigest(),"canvas":[W,H],
 "pieces":pieces,"alpha_pixels":{name:int((m>0).sum()) for name,m in alpha.items()},
 "return_to_reference_pixel_exact":True,
 "fixed_occlusion_only":True,"actor_sprite_sha256":sprhash,
 "game_implementation":False,"art_status":"completed_candidate_pending_user_review",
 "note":"countertop vase, side plants, and display photos unchanged; counter only masks actor depth"}
(OUT/"QA_manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding="utf-8")
print("PASS",len(pieces),"counter layers / source exact / pixels",manifest["alpha_pixels"])
