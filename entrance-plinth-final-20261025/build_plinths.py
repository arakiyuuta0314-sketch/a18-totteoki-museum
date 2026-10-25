# -*- coding: utf-8 -*-
"""A18 E06 / independent side plinths. Editable source-derived PNGs, shadows and marble repair.
No generative character redraw; all textures from approved entrance artwork.
All coordinates are 546 x 483 logical pixels. Source imagery shipped alongside this script.
"""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFilter
import cv2,numpy as np,hashlib,json,math
O=Path(__file__).resolve().parent
original=Image.open(O/"source_original_approved.jpg").convert("RGB")
woodBG=Image.open(O/"source_previous_background_without_plants.png").convert("RGB")
officialPreview=Image.open(O/"source_previous_preview_without_plants.png").convert("RGB")
for im in (original,woodBG,officialPreview):assert im.size==(546,483)
source=np.asarray(original)
wood=np.asarray(woodBG).copy()
donor=np.asarray(Image.open(O/"source_wood_panelling_donor.png").convert("RGB"))
# The left block is the near section in front of the wood desk, not the whole desk;
# the right block has its own chamfered upper lip. Both end at screen bottom.
shapes={
 "left":{"polygon":[(0,426),(52,426),(54,429),(60,431),(63,446),(60,483),(0,483)],
         "crop":[0,426,64,483],"anchor":[31,57],"repair_inside":[0,446,44,483],
         "repair_mask":[(0,446),(44,446),(44,483),(0,483)]},
 "right":{"polygon":[(458,442),(480,438),(530,437),(546,436),(546,483),(458,483),(457,467)],
         "crop":[457,435,546,483],"anchor":[45,48],"repair_inside":[476,451,536,483],
          "repair_mask":[(476,451),(536,451),(536,483),(476,483)]}
}
masks={};origmask=np.zeros((483,546),bool)
for k,g in shapes.items():
 mask=Image.new("L",(546,483),0)
 ImageDraw.Draw(mask).polygon(g["polygon"],fill=255)
 a=np.asarray(mask).copy()
 masks[k]=a
 origmask|=a>0
# Repair foliage ghosts inside only each wooden plinth; keep original outer edges.
for k,g in shapes.items():
 block=np.zeros((483,546),np.uint8)
 l,t,r,b=g["repair_inside"]
 block[t:b,l:r]=masks[k][t:b,l:r]
 inpainted=cv2.inpaint(cv2.cvtColor(wood,cv2.COLOR_RGB2BGR),block,7,cv2.INPAINT_TELEA)
 wood=cv2.cvtColor(inpainted,cv2.COLOR_BGR2RGB)
 texture=cv2.resize(donor,(r-l,b-t),interpolation=cv2.INTER_CUBIC)
 for y in range(t,b):
  for x in range(l,r):
   if block[y,x]==0:continue
   side=min(x-l+1,r-x)
   vertical=min(y-t+1,b-y)
   amount=min(1.,side/4.,vertical/4.)
   if k=="left" and x<4: amount=1.
   if k=="right" and x>532:amount=.15
   wood[y,x]=np.uint8(np.rint(wood[y,x]*(1-amount)+texture[y-t,x-l]*amount))
# Individual fully transparent PNGs with editable source mask and entire stand in the original positions.
pedestals={}
for k,g in shapes.items():
 a=masks[k]
 l,t,r,b=g["crop"]
 cropped=Image.fromarray(np.dstack((wood,a)),"RGBA").crop((l,t,r,b))
 cropped.save(O/f"entrance_plinth_{k}.png",optimize=True)
 Image.fromarray(a[t:b,l:r],"L").save(O/f"entrance_plinth_{k}_mask.png",optimize=True)
 pedestals[k]=cropped
 # Checker proof: independently visible wood panel and highlighted plinth edges
 gray=Image.new("RGBA",cropped.size,(201,203,199,255))
 gray.alpha_composite(cropped)
 gray.resize((cropped.width*6,cropped.height*6),Image.Resampling.NEAREST).convert("RGB").save(O/f"QA_plinth_{k}_isolated_6x.png")
# Base marble: extend genuine limestone from existing clear passage floor,
# not red carpet pixels, across the two masked side-furniture silhouettes.
marble=np.asarray(woodBG).copy()
for y in range(426,483):
 for x in range(546):
  if not origmask[y,x]:continue
  if x<=64: sx=min(141,64+(64-x))
  elif x>=457: sx=max(402,456-round((x-456)*.60))
  else:raise ValueError(("Unexpected pedestal mask",x,y))
  marble[y,x]=np.asarray(woodBG)[y,sx]
bg=Image.fromarray(marble,"RGB")
bg.save(O/"entrance_bg_without_both_plinths.png",optimize=True)
for k in shapes:
 a=np.asarray(woodBG).copy();test=masks[k]>0;a[test]=marble[test]
 Image.fromarray(a,"RGB").save(O/f"entrance_bg_without_{k}_plinth.png",optimize=True)
# Contact shadows in their own PNGs, not permanently burned into marble.
shadows={}
for k,g in shapes.items():
 rgba=Image.new("RGBA",(546,483),(0,0,0,0))
 # A thin shadow just outside the platform edge; no dimming of any photo window.
 m=Image.new("L",(546,483),0)
 d=ImageDraw.Draw(m)
 poly=[(x,y+2) for x,y in g["polygon"]]
 d.polygon(poly,fill=38)
 m=m.filter(ImageFilter.GaussianBlur(3))
 raw=np.asarray(m).copy()
 raw[masks[k]>0]=0
 rgba.putalpha(Image.fromarray(raw,"L"))
 l,t,r,b=g["crop"]
 canvas=rgba.crop((max(0,l-4),max(0,t-4),min(546,r+4),min(483,b+4)))
 canvas.save(O/f"entrance_plinth_shadow_{k}.png",optimize=True)
 shadows[k]=canvas
# Actual photo & character preview from the previous accepted material, not a redraw.
baseline=np.asarray(officialPreview).copy()
baseline[origmask]=marble[origmask]
previewBase=Image.fromarray(baseline,"RGB")
previewBase.save(O/"QA_no_plinths_no_plants.png",optimize=True)
plants={k:Image.open(O/f"source_original_plant_{k}.png").convert("RGBA") for k in shapes}
# Real prior sprites are unmodified; all assembled through source-over.
def assemble(enabled=("left","right"),grow=1.,move=0,show_plants=True):
 canvas=previewBase.convert("RGBA")
 for k,g in shapes.items():
  if k not in enabled:continue
  l,t,r,b=g["crop"];w=r-l;h=b-t
  ax,ay=g["anchor"]
  factor=float(grow) if not isinstance(grow,dict) else float(grow.get(k,1.))
  dx=move if k=="left" else -move
  targetx=round(l+ax+dx-ax*factor)
  targety=round(t+ay-ay*factor)
  if abs(factor-1)<1e-9 and move==0:
   box=(l,t)
  else:
   box=(targetx,targety)
  # The shadow remains behind pedestal. Render at the same anchor as its mask.
  shadow=shadows[k]
  sx=max(0,l-4);sy=max(0,t-4)
  sc=shadow.resize((round(shadow.width*factor),round(shadow.height*factor)),Image.Resampling.LANCZOS)
  canvas.alpha_composite(sc,(round(sx+ax+dx-ax*factor),round(sy+ay-ay*factor)))
  f=pedestals[k].resize((round(w*factor),round(h*factor)),Image.Resampling.LANCZOS)
  canvas.alpha_composite(f,box)
 if show_plants:
  for k,g in shapes.items():
   # Plant at its approved position on top of the plinth.
   p=plants[k]
   if k=="left": xx,yy,ax,ay=0,398,21,85
   else:xx,yy,ax,ay=450,398,51,85
   factor=float(grow) if not isinstance(grow,dict) else float(grow.get(k,1.))
   dx=move if k=="left" else -move
   rect=(round(xx+ax+dx-ax*factor),round(yy+ay-ay*factor))
   png=p.resize((round(p.width*factor),round(p.height*factor)),Image.Resampling.LANCZOS)
   canvas.alpha_composite(png,rect)
 return canvas.convert("RGB")
# Visible full candidates, both stages and 3 scales / reposition.
cases=[
 ("QA_plinths_and_plants_100pct.png",("left","right"),1.,0,True),
 ("QA_plinths_only.png",("left","right"),1.,0,False),
 ("QA_no_plinths_with_plants.png",(),1.,0,True),
 ("QA_left_plinth_only.png",("left",),1.,0,False),
 ("QA_right_plinth_only.png",("right",),1.,0,False),
 ("QA_plinths_and_plants_090pct.png",("left","right"),.9,0,True),
 ("QA_plinths_and_plants_110pct.png",("left","right"),1.1,0,True),
 ("QA_plinths_and_plants_shift_inwards_5px.png",("left","right"),1.,5,True)
]
for name,on,scale,dx,plants_on in cases:
 assemble(on,scale,dx,plants_on).save(O/name,optimize=True)
comparison=Image.new("RGB",(546*2,483))
comparison.paste(assemble(),(0,0));comparison.paste(assemble((),1,0,False),(546,0))
comparison.save(O/"QA_full_vs_empty_background.jpg",quality=95)
sizeboard=Image.new("RGB",(546*3,483))
for i,s in enumerate((.9,1.,1.1)):sizeboard.paste(assemble(grow=s),(546*i,0))
sizeboard.save(O/"QA_three_sizes.jpg",quality=95)
# Independent source, mask, fill, and normal display validations.
ref=np.asarray(officialPreview)
final=np.asarray(assemble())
outside=np.ones((483,546),bool)
outside[398:483,0:70]=False
outside[398:483,450:546]=False
assert np.array_equal(final[outside],ref[outside]),"Photo or original characters changed"
assert np.array_equal(np.asarray(previewBase)[~origmask],ref[~origmask])
assert all(img.mode=="RGBA" for img in pedestals.values())
assert all(np.asarray(Image.open(O/f"entrance_plinth_{k}_mask.png")).max()==255 for k in shapes)
mae=float(np.abs(np.int16(final)-np.int16(ref)).mean())
manifest={
 "title":"A18 E06 left/right independent walnut plinths under front plants",
 "source_original_sha256":hashlib.sha256((O/"source_original_approved.jpg").read_bytes()).hexdigest(),
 "source_approved_plant_art_sha256":{k:hashlib.sha256((O/f"source_original_plant_{k}.png").read_bytes()).hexdigest() for k in shapes},
 "canvas":[546,483],"objects":shapes,
 "layers":["marble_without_both_plinths","plinth_contact_shadow_left/right","plinth_left/right","existing_plant_left/right","official_character_layer/UI"],
 "coordinate_system":"source 546x483, fixed floor-bottom anchor",
 "verified_sizes":[.9,1.0,1.1],"verified_inward_shift_pixels":5,
 "photo_and_character_pixels_unchanged_outside_bottom_regions":True,
 "reference_reassembled_pixel_identical":False,
 "reference_reassembled_rgb_mae":round(mae,5),
 "notes":"Both plinths extend past bottom screen edge in the original. Back-side wood hidden by plants is reconstructed with the real original wood panel texture; ground underneath was never visible and is inferred from adjacent original marble.",
 "integrated_into_game":False,"user_art_review":"pending"}
(O/"QA_manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding="utf-8")
print("PLINTHS",len(shapes),"REF_RGB_MAE",mae,"FILES",len(list(O.iterdir())))
