# -*- coding: utf-8 -*-
"""Final A naked-entrance material QA.
Runs the deterministic existing-alpha renderer then removes two plants that remained baked
in the source gallery image. Structural pixels elsewhere are not painted or regenerated.
A must not be equated to Lv1 without user design approval.
"""
from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,cv2,json,hashlib,runpy,shutil
O=Path(__file__).resolve().parent
B=O.parent/"entrance-b01-unified-20261025"
runpy.run_path(str(O/"build_plain_a.py"),run_name="__main__")
base=np.asarray(Image.open(O/"A18_entrance_A_plain_no_decor_preview.png").convert("RGB"))
empty_people=np.asarray(Image.open(O/"SOURCE_pre_repair_no_characters.png").convert("RGB"))
H,W=base.shape[:2]
def mask_create():
 m=Image.new("L",(W,H),0);d=ImageDraw.Draw(m)
 # Left embedded planter foliage, excluding the golden desk fixture:
 d.polygon([(0,264),(13,263),(24,267),(36,276),(41,292),(37,310),(44,321),(38,341),(0,341)],fill=255)
 d.polygon([(15,309),(34,306),(41,321),(37,348),(12,348),(12,324)],fill=0)
 # Right embedded plant and metal vase in front of the freestanding wall:
 d.polygon([(540,311),(545,317),(545,407),(517,407),(514,394),(507,378),(500,373),(497,367),(505,357),(503,348),(507,340),(508,323),(517,320)],fill=255)
 a=np.asarray(m).copy()
 a=cv2.dilate(a,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(3,3)))
 return a
raw_mask=mask_create()
mask=(raw_mask>0)
def repair(I):
 hsv=cv2.cvtColor(I,cv2.COLOR_RGB2HSV)
 # green slips remaining behind the desk lamp are treated as part of foliage
 green=((hsv[:,:,0]>=28)&(hsv[:,:,0]<=95)&(hsv[:,:,1]>=34)&(hsv[:,:,2]>23))
 fix=(green & (np.indices(mask.shape)[1]<43) & (np.indices(mask.shape)[0]>=300) & (np.indices(mask.shape)[0]<=341))
 mm=mask|fix
 final=I.astype(float).copy()
 top=np.array([np.median(I[299:313,max(0,x-1):min(546,x+2)],axis=(0,1)) for x in range(W)],np.float32)
 bottom=np.array([np.median(I[412:430,max(0,x-1):min(546,x+2)],axis=(0,1)) for x in range(W)],np.float32)
 top=cv2.GaussianBlur(top.reshape(1,W,3),(9,1),1.3)[0]
 bottom=cv2.GaussianBlur(bottom.reshape(1,W,3),(9,1),1.3)[0]
 for yy in range(252,440):
  for xx in range(W):
   if not mm[yy,xx]:continue
   if xx<80:
    if yy<304:color=np.median(I[yy,47:60],axis=0).astype(float)*(.985+.015*np.cos(.07*xx))
    elif yy<320:color=np.median(I[yy,45:54],axis=0).astype(float)
    else:color=np.median(I[min(yy,343),44:58],axis=0).astype(float)
   elif xx>480:
    f=np.clip((yy-340)/77,0,1)
    f=f*f*(3-2*f)
    color=top[xx]*(1-f)+bottom[xx]*f
    color+=.45*(I[305+int(6*np.sin(.025*yy)),xx].astype(float)-top[xx])
   else:continue
   final[yy,xx]=color
 # Seam softening. This tiny line is not a claim that unseen plaster is authentic.
 a=cv2.GaussianBlur(np.uint8(mm)*255,(5,5),1.0).astype(float)/255
 return np.uint8(np.clip(np.rint(final*a[:,:,None]+I*(1-a[:,:,None])),0,255)),mm
full,repair_mask=repair(base)
empty,repair_mask2=repair(empty_people)
assert np.array_equal(repair_mask,repair_mask2)
assert full.shape==(483,546,3)
outside=~cv2.dilate(np.uint8(repair_mask)*255,np.ones((7,7),np.uint8)).astype(bool)
assert np.array_equal(full[outside],base[outside])
assert np.array_equal(empty[outside],empty_people[outside])
# Registered-photograph windows remain the B01 empty-paper images.
ref=np.asarray(Image.open(B/"QA_B01_all_empty_photos.png").convert("RGB"))
for rect in [(91,82,180,134),(389,82,451,134),(434,230,482,293)]:
 x0,y0,x1,y1=rect
 assert np.array_equal(full[y0:y1,x0:x1],ref[y0:y1,x0:x1]),("photo not empty",rect)
# Official curator and butler pixels are outside these repairs; original PNG files intact.
G=Path(r"G:\マイドライブ\06.アプリ開発\03.開発・テスト\A18_パズル美術館\00_正式採用素材\characters")
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for actor in ["butler-front-00.png","curator-front-00.png"]:
 assert sha(B/"characters"/actor)==sha(G/actor)
# Output is not an AI-painted replacement room, but source re-composited plus localized background restoration.
Image.fromarray(full).save(O/"A18_entrance_A_plain_no_decor_preview.png",optimize=True)
Image.fromarray(empty).save(O/"QA_plain_without_characters.png",optimize=True)
Image.fromarray(np.uint8(repair_mask)*255,"L").save(O/"QA_embedded_plant_restoration_mask.png",optimize=True)
shutil.copy2(B/"QA_B01_complete_pictures_and_characters.png",O/"QA_prior_decorated_reference.png")
comparison=Image.new("RGB",(1092,483))
comparison.paste(Image.fromarray(full),(0,0))
comparison.paste(Image.open(O/"QA_prior_decorated_reference.png").convert("RGB"),(546,0))
comparison.save(O/"QA_A_vs_decorated_original.jpg",quality=94)
M={
 "scenario":"A – nearly undecorated entrance",
 "not_approved_for_Lv1":True,"canvas":[546,483],
 "primary_image":"A18_entrance_A_plain_no_decor_preview.png",
 "source_project":"entrance-b01-unified-20261025",
 "removed":["Three registered sample photos; retain blank display mats","E01/E02 front planters","E03 countertop flower vase","E06 wooden plinths","E04 rear picture lamps","E05 ceiling and wainscot additional trim","E08 red-carpet gold trim","two directional signs and two wall sconces","two original baked-in ornamental plants, local material restoration"],
 "retained":["Existing door (closed)","Three functional picture frames and blank mats","Architectural walls, rails and reception desk","Original red carpet","Reception desk lantern and nameplate (baked-in permanent fixtures)","Real original official character sprites (butler and curator)","Architectural gold/lighting that is part of original background"],
 "source_pixel_preservation_outside_repair":True,
 "local_restoration_mask_count":int(repair_mask.sum()),
 "repaired_areas":["left wall shrub behind desk lamp","right freestanding display-wall shrub/pot"],
 "uncertainty":"Unseen wall/cabinet pixels cannot be verified source-exact; repaired from adjacent original material. This is a design comparison, not an adopted Lv1 design.",
 "game_integrated":False,
 "official_character_hashes":{a:sha(B/"characters"/a) for a in ["butler-front-00.png","curator-front-00.png"]},
 "restoration_qa":"outside repair mask unchanged; empty frame center windows verified; actor PNG hashes match originals"
}
(O/"QA_manifest.json").write_text(json.dumps(M,ensure_ascii=False,indent=2),encoding="utf-8")
print("PASS_FINAL_A",int(repair_mask.sum()),"repaired plant pixels",len(list(O.glob("*.png"))),"png files")
