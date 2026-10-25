# -*- coding:utf-8 -*-
"""A18 O03: original right foreground rail from approved source;
separated from physical wall and F03 photo-frame for occlusion layering.
"""
from pathlib import Path
from PIL import Image,ImageDraw
import cv2,numpy as np,json,hashlib
R=Path(__file__).resolve().parent.parent
O=Path(__file__).resolve().parent
F=R/"entrance-right-frame-final-20261025"
G=Path(r"G:\マイドライブ\06.アプリ開発\03.開発・テスト\A18_パズル美術館")
SRC=R/"entrance-test-v3/layout-test/assets/entrance/v0.3/approved_entrance_trial.jpg"
ref=np.asarray(Image.open(SRC).convert("RGB"))
wall=np.asarray(Image.open(F/"entrance_right_wall_without_frame.png").convert("RGBA"))
frame=np.asarray(Image.open(F/"entrance_photo_frame_03.png").convert("RGBA"))
photo=np.asarray(Image.open(F/"demo_photo_03_warped.png").convert("RGBA"))
empty=np.asarray(Image.open(F/"entrance_photo_empty_03.png").convert("RGBA"))
prior=np.asarray(Image.open(G/"27_エントランス完成素材_右展示壁_v01"/"QA_complete_wall_three_photos_and_formal_sprites.png").convert("RGB"))
wall_mask=wall[:,:,3]>0
outline=[(394,146),(400,142),(406,143),(531,183),(538,189),(539,217),
         (531,210),(526,200),(401,169),(394,170)]
candidate=np.zeros((483,546),np.uint8)
cv2.fillPoly(candidate,[np.array(outline,np.int32)],255)
mask=np.uint8((candidate>0)&wall_mask)*255
# Photo aperture is never part of the handrail and must remain untouched.
ap=np.asarray(Image.open(F/"entrance_photo_window_03_mask.png"))>0
mask[ap]=0
assert np.count_nonzero(mask)>1800
# Painted backing behind removed wood: interior panel, not a second duplicate rail.
und=wall.copy()
for y in range(140,220):
 for x in range(392,543):
  if mask[y,x]==0:continue
  if y<=182:
   color=np.array([72,48,28],dtype=np.float32)
  else:
   color=np.array([22,42,29],dtype=np.float32)
  illum=1.+.07*np.cos((x-390)*.03)
  und[y,x,:3]=np.uint8(np.clip(np.rint(color*illum),0,255))
Image.fromarray(und,"RGBA").save(O/"entrance_right_wall_without_frame_and_rail.png",optimize=True)
Image.fromarray(np.dstack([ref,mask]),"RGBA").save(O/"entrance_fg_right_rail.png",optimize=True)
Image.fromarray(mask,"L").save(O/"entrance_right_rail_mask.png",optimize=True)
# baseline demo: replace right wall area only, preserve exact two photos and official actors.
base=prior.copy()
base[wall_mask]=und[:,:,:3][wall_mask]
Image.fromarray(base,"RGB").save(O/"QA_entrance_without_rail_and_right_frame.png")
def over(canvas,arr):
 canvas.alpha_composite(Image.fromarray(arr,"RGBA"))
def render(withrail=True,withphoto=True,withframe=True,scale=1.):
 c=Image.fromarray(base,"RGB").convert("RGBA")
 if withframe:
  center=(457.5,261.)
  for layer in (photo if withphoto else empty,frame):
   if scale!=1.:
    affine=cv2.getRotationMatrix2D(center,0,scale)
    layer=cv2.warpAffine(layer,affine,(546,483),flags=cv2.INTER_LINEAR,borderMode=cv2.BORDER_CONSTANT,borderValue=(0,0,0,0))
   over(c,layer)
 if withrail:over(c,np.dstack([ref,mask]))
 return c.convert("RGB")
for rail in (True,False):
 for p in (True,False):
  n=f"QA_{'rail' if rail else 'no_rail'}_{'photo' if p else 'empty'}"
  render(rail,p).save(O/(n+".png"),optimize=True)
render(True,True,True,.9).save(O/"QA_rail_frame090.png")
render(True,True,True,1.1).save(O/"QA_rail_frame110.png")
checker=Image.new("RGBA",(546,483),(202,204,202,255))
checker.alpha_composite(Image.fromarray(np.dstack([ref,mask]),"RGBA"))
checker.convert("RGB").crop((390,137,545,225)).resize((620,352),Image.Resampling.NEAREST).save(O/"QA_right_rail_isolated_checker4x.png")
cmp=Image.new("RGB",(1092,483))
cmp.paste(render(True,True),(0,0));cmp.paste(render(False,True),(546,0));cmp.save(O/"QA_right_rail_on_off.jpg",quality=95)
diff=np.abs(np.int16(render(True,True))-np.int16(prior))
assert diff.max()==0, (diff.max(),int(np.any(diff>0,axis=2).sum()))
protect=np.ones((483,546),bool);protect[141:221,393:541]=False
assert np.array_equal(np.asarray(render(False,True))[protect],prior[protect])
for name in ["curator-front-00.png","butler-front-00.png"]:
 original=G/"00_正式採用素材"/"characters"/name
 approved=G/"28_エントランス完成素材_背面展示枠左右_v01"/name
 assert original.read_bytes()==approved.read_bytes()
data={"object":"O03 right passage handrail","source_sha256":hashlib.sha256(SRC.read_bytes()).hexdigest(),
 "source_size":[546,483],"mask_outline":outline,"opaque_pixels":int(np.count_nonzero(mask)),
 "draw_order":"clean wall -> right frame/photo -> right foreground rail -> player if in front",
 "standard_full_scene_rgb_identical_to_prior":True,"display_off_region":"reconstructed dark panel/wood underlay (not a source-exact scene)",
 "reference_characters_unchanged":True,"photo_windows_unchanged":True,"game_unchanged":True,
 "user_art_approval":"pending"}
(O/"QA_manifest.json").write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding="utf-8")
print("PASS O03 physical rail",int(np.count_nonzero(mask)),"full source composite exact")
