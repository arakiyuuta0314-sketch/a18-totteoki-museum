# -*- coding:utf-8 -*-
"""A18 B01: remove baked exhibition, doors, plants, plinths and decor into true separate layers.
Read only the source PNGs in this folder. Do not edit game, logos or character PNGs.
"""
from pathlib import Path
from PIL import Image,ImageOps
import cv2,numpy as np,json,hashlib
O=Path(__file__).resolve().parent
read=lambda p:Image.open(O/p)
src=np.asarray(read("approved_entrance_trial.jpg").convert("RGB"));H,W=src.shape[:2]
assert (W,H)==(546,483)
scene=src.copy()
changed=np.zeros((H,W),bool)
patches=[]
def im(p):return np.asarray(read(p).convert("RGBA"))
def alpha_full(p,xy=(0,0)):
 a=np.asarray(read(p).convert("RGBA").getchannel("A"))>0
 if a.shape==(H,W):assert xy==(0,0);return a
 x,y=xy;out=np.zeros((H,W),bool);out[y:y+a.shape[0],x:x+a.shape[1]]=a;return out
def rect(l,t,r,b):
 m=np.zeros((H,W),bool);m[t:b,l:r]=True;return m
def strip(tag,clean_path,mask):
 assert mask.shape==(H,W)
 clean=np.asarray(read(clean_path).convert("RGB"))
 assert clean.shape==scene.shape
 scene[mask]=clean[mask]
 changed[:]|=mask
 patches.append({"object":tag,"target_pixels":int(mask.sum())})
# Architecture background under the right exhibition partition FIRST (covers the original framed wall).
oldwall=alpha_full("rightWall/entrance_fg_right_display_wall.png")
window=alpha_full("rightWall/entrance_photo03_aperture_mask.png")
strip("O01 right wall base","rightWall/entrance_bg_without_right_display_wall.png",oldwall|window)
# Exhibition frames left/right F01,F02; wall plaster repaired behind original borders.
strip("F01 F02 background clean","rear/entrance_bg_without_rear_frames.png",rect(76,50,201,157)|rect(365,50,468,157))
# North door closed/open geometry strips out original closed wood leaves.
strip("D01 D02 north portal","door/entrance_bg_north_open_base.png",rect(243,116,322,213))
# Left foreground partition and counter lip behind actor ordering.
leftmask=alpha_full("leftWall/entrance_left_foreground_wall.png")|alpha_full("leftWall/entrance_left_foreground_rail.png")
strip("O02 left foreground underlay","leftWall/entrance_bg_without_left_foreground.png",leftmask)
countermask=alpha_full("counter/entrance_counter_fg_top_lip.png")|alpha_full("counter/entrance_counter_fg_front_face.png")
strip("O04 counter foreground underlay","counter/entrance_bg_without_counter_front.png",countermask)
# Current counter plant E03, old metal vase cannot be permanently baked.
m_flower=np.zeros((H,W),bool)
m_flower[325:391,69:118]=np.asarray(read("flower/source_tabletop_restoration_mask.png").convert("L"))>0
strip("E03 counter flowers underlay","flower/entrance_bg_without_counter_flower.png",m_flower)
# Strip front shrubs E01+E02 FIRST; after this remove wooden plinths separately.
m_flora=np.zeros((H,W),bool)
bgflora=np.asarray(read("plants/entrance_bg_without_front_plants.png").convert("RGB"))
for l,t,r,b in [(0,398,66,483),(450,398,538,483)]:
 m_flora[t:b,l:r]=np.any(bgflora[t:b,l:r]!=src[t:b,l:r],axis=2)
strip("E01 E02 front plants underlay","plants/entrance_bg_without_front_plants.png",m_flora)
m_plinth=alpha_full("plinth/entrance_plinth_left.png",(0,426))|alpha_full("plinth/entrance_plinth_right.png",(457,435))
strip("E06 wooden plinth underlay","plinth/entrance_bg_without_both_plinths.png",m_plinth)
# Remove residual green leaf pigment on the dark walnut panel after the earlier
# plant-mask extraction. This is a B01 integration correction, not a replacement
# of either approved independent transparent plant PNG.
# The earlier isolated plant alpha retains green slivers on the desk front
# (screen x=0..43, y=407..432). Rebuild only the physical walnut face from an
# adjacent *real* wooden panel at x=53..100, matched by original scanline.
walnut_base=scene.copy()
residue=np.zeros((H,W),bool)
for y in range(400,440):
 for x in range(0,51):
  if y<405:weight=(y-400)/5
  elif y>434:weight=(440-y)/6
  else:weight=1.
  if x>44:weight*=max(0,(51-x)/7)
  weight=max(0,min(1,weight))
  if weight<=0:continue
  # Use verified walnut pixels from the same approved photograph at
  # x=65..95, rather than the partially reconstructed B01 underlay.
  donor_x=65+int(x*.61)
  donor=src[y,donor_x].astype(float)
  scene[y,x]=np.uint8(np.clip(np.rint(walnut_base[y,x]*(1-weight)+donor*weight),0,255))
  residue[y,x]=True
changed[:]|=residue
patches.append({"object":"B01 dark walnut residual leaf repair","target_pixels":int(np.count_nonzero(residue))})
# Transparent gold carpet edge E08
strip("E08 carpet gold piping","carpet/entrance_bg_carpet_without_gold_trim.png",alpha_full("carpet/entrance_carpet_gold_trim.png",(173,235)))
# Plaster wall sconces, signs, and picture-mounted lamps from original architecture.
m_fixed=np.zeros((H,W),bool)
fixture_coords={"west_sign":(4,61),"east_sign":(503,61),"west_sconce":(214,83),"east_sconce":(334,83)}
for name,xy in fixture_coords.items():m_fixed |=alpha_full(f"fixtures/entrance_{name}.png",xy)
strip("fixtures left/right signs and sconces","fixtures/entrance_bg_without_signs_sconces.png",m_fixed)
m_lights=rect(116,30,161,69)|rect(391,30,438,69)
strip("E04 rear picture lights","lights/entrance_bg_without_picture_lights.png",m_lights)
m_trim=np.zeros((H,W),bool)
trim_loc={"ceiling_west":(65,11),"ceiling_east":(355,11),"wainscot_west":(68,164),"wainscot_east":(358,164)}
for n,xy in trim_loc.items():m_trim|=alpha_full(f"trim/entrance_wall_trim_{n}.png",xy)
strip("E05 ceiling and wainscot ornament","trim/entrance_bg_without_wall_trims.png",m_trim)
Image.fromarray(scene).save(O/"B01_entrance_base_without_independent_art.png",optimize=True)
Image.fromarray(np.uint8(changed)*255).save(O/"B01_removed_baked_objects_mask.png")
# Rebuild actual visual layers in a clearly defined draw order.
def draw(b,source,xy=(0,0)):
 b.alpha_composite(read(source).convert("RGBA"),xy)
def frame(canvas,name,mode):
 geo={"left":(76,50,125,107,84,61,110,83),"right":(365,50,103,107,373,61,87,83)}
 x,y,w,h,wx,wy,ww,wh=geo[name]
 if mode=="photo":
  photo=ImageOps.fit(read(f"rear/demo_photo_{name}.jpg").convert("RGB"),(ww,wh),method=Image.Resampling.LANCZOS)
  canvas.alpha_composite(photo.convert("RGBA"),(wx,wy))
 else:draw(canvas,f"rear/empty_{name}.png",(wx,wy))
 draw(canvas,f"rear/frame_{name}_5x5.png",(x,y))
def person(canvas,name,cx,foot,width):
 image=read(f"characters/{name}").convert("RGBA")
 h=round(image.height*width/image.width)
 canvas.alpha_composite(image.resize((width,h),Image.Resampling.NEAREST),(round(cx-width/2),foot-h))
def render(photos=True,door_open=False,plants=True,plinths=True,extra=True,chars=True,frame3=True):
 c=Image.fromarray(scene).convert("RGBA")
 # Front wall: wall body independent of rail and photo.
 draw(c,"rail3/entrance_right_wall_without_frame_and_rail.png")
 # North wood leaves, old exact closed source or previously accepted open state.
 draw(c,f"door/entrance_door_north_{'open' if door_open else 'closed'}.png")
 for side in ("left","right"):frame(c,side,"photo" if photos else "empty")
 # Perspective picture attached to right-hand freestanding display wall
 if frame3:
  draw(c,f"frame3/{'demo_photo_03_warped' if photos else 'entrance_photo_empty_03'}.png")
  draw(c,"frame3/entrance_photo_frame_03.png")
 draw(c,"rail3/entrance_fg_right_rail.png")
 # Fixed architecture blockers (always present) in front of invisible rear objects
 draw(c,"leftWall/entrance_left_foreground_wall.png")
 draw(c,"leftWall/entrance_left_foreground_rail.png")
 draw(c,"counter/entrance_counter_fg_top_lip.png")
 # O04's original front-face crop includes foliage from E01 in its left edge.
 # Replace only that overlap by the B01 repaired walnut, preserving the official
 # O04 source bytes on disk. E01 is composited independently later.
 if plants:
  draw(c,"counter/entrance_counter_fg_front_face.png")
 else:
  rawface=np.asarray(read("counter/entrance_counter_fg_front_face.png").convert("RGBA")).copy()
  should_fix=residue & (rawface[:,:,3]>0)
  rawface[should_fix,:3]=scene[should_fix]
  c.alpha_composite(Image.fromarray(rawface,"RGBA"))
 if extra:
  draw(c,"carpet/entrance_carpet_gold_trim.png",(173,235))
  for side in ("west","east"):
   draw(c,f"fixtures/entrance_{side}_sign.png",fixture_coords[f"{side}_sign"])
   draw(c,f"fixtures/entrance_{side}_sconce.png",fixture_coords[f"{side}_sconce"])
  for side in ("west","east"):
   source=f"lights/entrance_picture_light_{side}{'_photo_safe' if photos else ''}.png"
   draw(c,source,(116,30) if side=="west" else (391,30))
  for name,xy in trim_loc.items():draw(c,f"trim/entrance_wall_trim_{name}.png",xy)
 if plinths:
  draw(c,"plinth/entrance_plinth_shadow_left.png",(0,422))
  draw(c,"plinth/entrance_plinth_shadow_right.png",(453,431))
  draw(c,"plinth/entrance_plinth_left.png",(0,426))
  draw(c,"plinth/entrance_plinth_right.png",(457,435))
 if plants:
  draw(c,"plants/entrance_plant_left.png",(0,398))
  draw(c,"plants/entrance_plant_right.png",(450,398))
  draw(c,"flower/entrance_counter_flower_vase.png",(68,318))
 if chars:
  person(c,"butler-front-00.png",140,371,43)
  person(c,"curator-front-00.png",287,366,35)
 return c.convert("RGB")
cases={
 "QA_B01_complete_pictures_and_characters.png":dict(),
 "QA_B01_all_empty_photos.png":dict(photos=False),
 "QA_B01_north_open.png":dict(door_open=True),
 "QA_B01_no_plants_no_plinths.png":dict(plants=False,plinths=False),
 "QA_B01_no_gold_ornaments.png":dict(extra=False),
 "QA_B01_clean_base_only.png":None
}
for n,k in cases.items():
 (render(**k) if k is not None else Image.fromarray(scene)).save(O/n,optimize=True)
board=Image.new("RGB",(1092,483));board.paste(render(),(0,0));board.paste(Image.fromarray(scene),(546,0));board.save(O/"QA_B01_composed_vs_clean_base.jpg",quality=95)
# The new original-derived base must no longer contain baked-in objects where removed.
assert changed.sum()>35000
# Assembled aesthetic comparison, registration and official sprites are only difference.
original=src
complete=np.asarray(render(False,False,True,True,True,False,True))
rgb_delta=np.abs(np.int16(complete)-np.int16(original))
mae=float(rgb_delta.mean())
# Count drift outside original physically dynamic zones: should remain small.
assert np.array_equal(src[223,270],complete[223,270]) # central floor
assert np.array_equal(src[300,280],complete[300,280]) # carpet center
assert np.array_equal(src[20,280],complete[20,280]) # lintel
manifest={"source":"approved_entrance_trial.jpg","source_canvas":[546,483],
 "base":"B01_entrance_base_without_independent_art.png","component_count":len(patches),
 "components":patches,"separated_pixels":int(changed.sum()),
 "empty_original_rgb_mae":round(mae,4),
 "qa_images":list(cases),
 "formal_characters":"Original bytes, no redraw",
 "game_integration":False,"release_candidate":False,
 "status":"B01 art composite candidate, requires cross-layer visual review and browser QA"}
(O/"QA_manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding="utf-8")
print("B01_BUILT",len(patches),"independent repairs;","covered",int(changed.sum()),"pixels; MAE original empty",round(mae,3))
