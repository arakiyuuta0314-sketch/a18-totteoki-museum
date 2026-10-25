# -*- coding: utf-8 -*-
"""A18 ceiling lights x8 + reception desk lamp.
All assets are extracted/reworked from existing artwork, no generated new art.
Only two user-switchable layers per group: body and emission.
"""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFilter
import numpy as np,cv2,json,hashlib
ROOT=Path(r"G:\マイドライブ\06.アプリ開発\03.開発・テスト\A18_パズル美術館")
SRC=ROOT/"50_エントランス完成候補_追加壁灯4点分離_v01"/"QA_all_four_sconces_on.png"
HERE=Path(__file__).resolve().parent
O=HERE/"lighting-ceiling-counter-v01"
O.mkdir(exist_ok=True)
original=np.asarray(Image.open(SRC).convert("RGB"))
H,W=original.shape[:2];assert (W,H)==(546,483)
def save(image,name):image.save(O/name,optimize=True);return image
# A: 8 ceiling luminous points, confirmed from the actual source image.
centers=[59,95,135,179,286,398,438,475]
ceiling_body=np.zeros((H,W,4),np.uint8)
ceiling_emission=np.zeros((H,W,4),np.uint8)
repair=original.copy().astype(np.float32)
ceil_rects=[]
for x in centers:
 l=max(0,x-9);r=min(W,x+10);t=0;b=15
 rgb=np.asarray(original[t:b,l:r],np.float32)
 h,w=rgb.shape[:2]
 Y,X=np.mgrid[t:b,l:r].astype(np.float32)
 # The tiny gold mounting point remains present when unlit.
 socket=((X-x)/2.3)**2+((Y-8.8)/2.7)**2
 sockalpha=np.uint8(np.clip((1.15-socket)*2,0,1)*225)
 # The source's actual illuminated pixels + halo, no inventing new fixtures.
 ell=((X-x)/6.4)**2+((Y-2.6)/5.0)**2
 warm=(np.max(rgb,axis=2)-np.min(rgb,axis=2))
 glow=np.clip(1-ell,0,1)**.65
 glowalpha=np.uint8(np.clip(glow*.90,0,1)*255)
 # For no-light underlying ceiling: copy/interpolate from adjacent ceiling strip
 # at the same y; never modify columns outside assigned 19-pixel scope.
 donor_left=np.median(original[t:b,x-16:x-11],axis=1).astype(np.float32)
 donor_right=np.median(original[t:b,x+12:x+17],axis=1).astype(np.float32)
 for j in range(w):
  f=j/max(w-1,1)
  donor=donor_left*(1-f)+donor_right*f
  # Only remove light/bloom at y=0..8; retain ornamental horizontal trim y>=10.
  radius=np.clip((1-((j+l-x)/8.0)**2),0,1)
  row_strength=np.clip((11.5-np.arange(t,b))/5,0,1)
  strength=(radius**.75)*row_strength
  repair[t:b,l+j]=rgb[:,j]*(1-strength[:,None])+donor*strength[:,None]
 # Both reusable group PNGs use the unmodified registered dimensions.
 ceiling_body[t:b,l:r,:3]=original[t:b,l:r]
 ceiling_body[t:b,l:r,3]=np.maximum(ceiling_body[t:b,l:r,3],sockalpha)
 ceiling_emission[t:b,l:r,:3]=original[t:b,l:r]
 ceiling_emission[t:b,l:r,3]=np.maximum(ceiling_emission[t:b,l:r,3],glowalpha)
 ceil_rects.append([l,t,r,b])
ceiling_off=np.uint8(np.clip(repair,0,255))
save(Image.fromarray(ceiling_body,"RGBA"),"ceiling_lamp_row_body.png")
save(Image.fromarray(ceiling_emission,"RGBA"),"ceiling_lamp_row_emission.png")
# One source lamp also provided as a reusable individual unit, plus 8 placements in manifest.
unit_idx=2;x=centers[unit_idx];xy=(x-9,0,x+10,15)
save(Image.fromarray(ceiling_body,"RGBA").crop(xy),"ceiling_lamp_unit_body.png")
save(Image.fromarray(ceiling_emission,"RGBA").crop(xy),"ceiling_lamp_unit_emission.png")
# B: one existing ornate table lamp; physically extracted body silhouette.
# Coordinates identified on the 546x483 image by source pixel grid.
lamp_poly=[
 (23,307),(32,307),(38,309),(40,315),(42,323),
 (43,330),(40,338),(36,341),(32,343),
 (33,356),(37,359),(40,364),(39,370),(34,373),
 (20,373),(16,369),(16,364),(19,360),(25,358),
 (25,344),(21,342),(16,340),(13,333),(13,326),
 (16,315),(19,310)]
mat=Image.new("L",(W,H));ImageDraw.Draw(mat).polygon(lamp_poly,fill=255)
# Antialias little edge; preserve same silhouette for darker body and illuminated body.
mask=np.asarray(mat.filter(ImageFilter.GaussianBlur(.55)),np.float32)/255.
roi=(8,302,48,379)
# Mask should not reach the displayed standing placard x>=47.
assert np.max(mask[:,47:])==0
# Repaint missing wall + table surface; we ONLY alter lamp and direct light reflection.
# Off illumination reflected below table lamp at (28,380) also replaced as part of clean underlay.
R=repair.copy()
for y in range(304,399):
 if y<347:
  ll=(2,10);rr=(48,64)
 elif y<355:
  ll=(3,11);rr=(73,82)
 elif y<383:
  ll=(3,12);rr=(73,82)
 else:
  ll=(3,12);rr=(79,91)
 left=np.median(original[y,ll[0]:ll[1]],axis=0).astype(np.float32)
 right=np.median(original[y,rr[0]:rr[1]],axis=0).astype(np.float32)
 # Horizontally interpolate in-plane unoccluded pixels of exactly the same row.
 for x in range(10,47):
  f=np.clip((x-10)/(46-10),0,1)
  donor=left*(1-f)+right*f
  R[y,x]=donor
# Do not touch source outside reconstructed missing-lamp region.
lamp_floor_mask=np.asarray(mat.filter(ImageFilter.GaussianBlur(.8)),np.float32)/255.
# Add small glow/reflection on countertop/brass which disappears with the fixture
reflection=np.zeros((H,W),np.float32)
Y,X=np.mgrid[:H,:W]
reflection=np.exp(-(((X-28)/5)**2+((Y-386)/13)**2)*1.4)*.86
# At the bottom lamp base x20-39 y358-374 keep fully out; reflective light lower x20..39 374..396.
# The lamp casts dark silhouette/shadows beyond the tight body. Reconstruct the
# full local blank rectangle, feathering against untouched original furniture.
# This removes the entire lamp silhouette and countertop hotspot, not just its center.
margin_x=np.minimum((X-8)/4.0,(47-X)/4.0)
margin_y=np.minimum((Y-303)/4.0,(398-Y)/4.0)
rect_repair=np.clip(np.minimum(margin_x,margin_y),0,1)
removal=np.maximum(lamp_floor_mask,rect_repair)
removal[:303]=0;removal[398:]=0;removal[:,47:]=0;removal[:,:8]=0
# Conservative: only local background area x8..46 y303..397.
clean=ceiling_off.astype(np.float32)
clean=clean*(1-removal[:,:,None])+R*removal[:,:,None]
clean=np.uint8(np.clip(np.round(clean),0,255))
# Lamp body retains original gold metal / fabric, but the head becomes subdued when emission OFF.
lamp_body=np.zeros((H,W,4),np.uint8)
body_rgb=original.copy().astype(np.float32)
# Fabric shade y314..340, darker material when switched off.
shade=((X-28)/16)**2+((Y-328)/19)**2
dim=(np.clip(1-shade,0,1)**.48)*.70
body_rgb=body_rgb*(1-dim[:,:,None])+np.array([100,69,39],np.float32)*dim[:,:,None]
lamp_body[:,:,:3]=np.uint8(np.clip(body_rgb,0,255))
lamp_body[:,:,3]=np.uint8(np.clip(mask,0,1)*255)
save(Image.fromarray(lamp_body,"RGBA"),"counter_lamp_body.png")
# Emission adds original luminous color back onto shade; reflection can be split here if
# needed for effect, but reflection strength is conservative and restricted.
emission=np.zeros((H,W,4),np.uint8)
emission[:,:,:3]=original
shade_intensity=np.clip((1-shade)*1.20,0,1)*mask
halo_intensity=np.exp(-(((X-28)/16)**2+((Y-328)/15)**2))*0.20
emalpha=np.clip(shade_intensity*.85+halo_intensity*.38*mask,0,1)
emission[:,:,3]=np.uint8(emalpha*255)
save(Image.fromarray(emission,"RGBA"),"counter_lamp_emission.png")
save(Image.fromarray(clean,"RGB"),"QA_ceiling_and_counter_removed_background.png")
# Build images from corrected background with group switches.
layers={
 "ceiling_body":Image.fromarray(ceiling_body,"RGBA"),
 "ceiling_emission":Image.fromarray(ceiling_emission,"RGBA"),
 "desk_body":Image.fromarray(lamp_body,"RGBA"),
 "desk_emission":Image.fromarray(emission,"RGBA")}
def scene(ceiling=True,desk=True,glow=True):
 canvas=Image.fromarray(clean,"RGB").convert("RGBA")
 if ceiling:
  canvas.alpha_composite(layers["ceiling_body"])
  if glow:canvas.alpha_composite(layers["ceiling_emission"])
 if desk:
  canvas.alpha_composite(layers["desk_body"])
  if glow:canvas.alpha_composite(layers["desk_emission"])
 return canvas.convert("RGB")
for nm,opts in [
 ("all_on",(True,True,True)),("all_off",(False,False,False)),
 ("bodies_only",(True,True,False)),("ceiling_only",(True,False,True)),
 ("desk_only",(False,True,True)),("desk_body_only",(False,True,False))]:
 save(scene(*opts),f"QA_{nm}.png")
board=Image.new("RGB",(W*4,H))
for i,nm in enumerate(("all_off","bodies_only","all_on","ceiling_only")):
 board.paste(Image.open(O/f"QA_{nm}.png"),(i*W,0))
save(board,"QA_four_state_contact_sheet.png")
# Four-up close-ups of desk/ceiling.
for nm,crop in [("desk",(0,300,92,404)),("ceiling",(0,0,546,29))]:
 w,h=crop[2]-crop[0],crop[3]-crop[1];factor=4 if nm=="desk" else 2
 out=Image.new("RGB",(w*4*factor,h*factor))
 for i,src in enumerate((Image.fromarray(original),Image.open(O/"QA_all_off.png"),
                           Image.open(O/"QA_bodies_only.png"),Image.open(O/"QA_all_on.png"))):
  res=src.crop(crop).resize((w*factor,h*factor),Image.Resampling.NEAREST)
  out.paste(res,(i*w*factor,0))
 save(out,f"QA_{nm}_original_off_body_on_zoom.png")
allowed=np.zeros((H,W),bool)
allowed[0:15]=True;allowed[304:399,10:47]=True
assert np.array_equal(clean[~allowed],original[~allowed])
m={
 "status":"technical_candidate_requires_art_review",
 "input_art":"50_エントランス完成候補_追加壁灯4点分離_v01/QA_all_four_sconces_on.png",
 "ceiling_lamps_count":8,"ceiling_centers_x":centers,
 "ceiling_body_and_emission_reusable":True,"ceiling_placement":[[x-9,0] for x in centers],
 "ceiling_unit_source_x":centers[unit_idx],"counter_lamp_polygon":lamp_poly,
 "counter_lamp_body_and_emission_independent":True,
 "outside_light_source_regions_changed_pixels":int(np.count_nonzero(np.any(clean!=original,axis=2)&(~allowed))),
 "restored_background_is_estimated":True,"input_matches_after_recombination_pixel_exact":False,
 "game_integration":False,"user_art_approval":False,
 "old_29_30_49_50_modified":False,
 "files_sha256":{f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in O.glob("*.png")}}
(O/"QA_manifest.json").write_text(json.dumps(m,ensure_ascii=False,indent=2),encoding="utf-8")
print("BUILD_DONE",O, "onscreen-difference-average",float(np.abs(np.asarray(scene(),np.float32)-original.astype(np.float32)).mean()),"group assets",4)
