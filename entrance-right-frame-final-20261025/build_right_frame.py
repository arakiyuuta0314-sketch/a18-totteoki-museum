# -*- coding:utf-8 -*-
from pathlib import Path
from PIL import Image, ImageDraw
import cv2,numpy as np,json,hashlib
R=Path(r"C:\Users\User\source\repos\a18-entrance-right-frame-final-20261025")
G=Path(r"G:\マイドライブ\06.アプリ開発\03.開発・テスト\A18_パズル美術館")
O=R/"entrance-right-frame-final-20261025"
S=R/"entrance-test-v3/layout-test/assets/entrance/v0.3/approved_entrance_trial.jpg"
D=G/"27_エントランス完成素材_右展示壁_v01"
src=np.asarray(Image.open(S).convert("RGB"))
fg=np.asarray(Image.open(D/"entrance_fg_right_display_wall.png").convert("RGBA"))
under=np.asarray(Image.open(D/"entrance_bg_without_right_display_wall.png").convert("RGBA"))
assert src.shape==(483,546,3)
# Source real gold frame outer; photo opening from 27 remains the rendering reference.
outer=np.array([[414,183],[500,212],[502,340],[413,294]],dtype=np.int32)
inner=np.array([[426,201],[489,226],[489,323],[426,276]],dtype=np.int32)
m_o=np.zeros((483,546),np.uint8);cv2.fillConvexPoly(m_o,outer,255)
m_i=np.asarray(Image.open(D/"entrance_photo03_aperture_mask.png").convert("RGBA").getchannel("A"))
ring=((m_o>0)&(m_i==0)).astype(np.uint8)*255
wall_mask=np.maximum(fg[:,:,3],m_i)
assert np.all(ring<=wall_mask), "frame extension outside approved wall"
# Green naked backing: clone actual wall color from neighboring green vertical field 
# preserving gradient of original source but removing golden frame and paper.
# Smooth column-adapted swatches from wall around x409-413 / x501-507
naked=src.copy()
for y in range(180,345):
  # Replace occluded gold and parchment with unobtrusive, dark green fabric.
  # RGB tone sampled from the real adjacent panel at x=500,y=220 / y=320;
  # do not pull golden candelabra or walnut rail into the concealed fabric.
  for x in range(411,506):
    if m_o[y,x]==0:continue
    fx=(x-411)/95
    fy=(y-180)/165
    base_green=np.array([18.5+3*fy,39.5-7*fy,27-5*fy])
    shade=.94+.07*np.sin(fx*3.14)+.012*np.sin(x*.32+y*.11)
    naked[y,x]=np.uint8(np.clip(np.rint(base_green*shade),0,255))
# Glow-neutral green/plaster base new mask preserves original architecture outside frame.
wall_layer=np.dstack([naked,wall_mask])
Image.fromarray(wall_layer,"RGBA").save(O/"entrance_right_wall_without_frame.png")
Image.fromarray(np.dstack([src,ring]),"RGBA").save(O/"entrance_photo_frame_03.png")
Image.fromarray(np.dstack([src,m_i]),"RGBA").save(O/"entrance_photo_empty_03.png")
Image.fromarray(m_i,"L").save(O/"entrance_photo_window_03_mask.png")
Image.fromarray(naked).save(O/"QA_right_green_backing.png")
# Aligned source photo sample in the exact polygon, no generated people.
photo=np.asarray(Image.open(D/"QA_photo03_in_aperture.png").convert("RGBA"))
Image.fromarray(photo,"RGBA").save(O/"demo_photo_03_warped.png")
# 100% recomposition.
def put(img,layer):
 dest=img.convert("RGBA")
 dest.alpha_composite(layer)
 return dest
canvas=Image.fromarray(under,"RGBA")
canvas=put(canvas,Image.fromarray(wall_layer,"RGBA"))
canvas=put(canvas,Image.fromarray(np.dstack([src,m_i]),"RGBA"))
canvas=put(canvas,Image.fromarray(np.dstack([src,ring]),"RGBA"))
recon=canvas.convert("RGB")
recon.save(O/"QA_exact_reassembly.png")
delta=np.abs(np.int16(recon)-np.int16(src))
print("MAX ERR",delta.max(),"PIX ERR",(delta!=0).any(axis=2).sum())
assert not delta.max()
# RGB source preserves photo if registered and no other change
canvas=Image.fromarray(under,"RGBA")
for item in [Image.fromarray(wall_layer,"RGBA"),Image.fromarray(photo,"RGBA"),Image.fromarray(np.dstack([src,ring]),"RGBA")]:canvas.alpha_composite(item)
canvas.convert("RGB").save(O/"QA_photo_registered.png")
# empty/photo pair with and without removable frame.
wallonly=Image.fromarray(under,"RGBA");wallonly.alpha_composite(Image.fromarray(wall_layer,"RGBA"))
wallonly.convert("RGB").save(O/"QA_wall_frame_hidden.png")
# frame on checker alpha
crop=(406,173,509,344)
def checker(im):
 c=Image.new("RGBA",im.size,(200,200,200,255));c.alpha_composite(im);return c.convert("RGB")
checker(Image.fromarray(np.dstack([src,ring]),"RGBA")).crop(crop).resize((412,684),Image.Resampling.NEAREST).save(O/"QA_frame_isolation_4x.png")
M={"source_sha256":hashlib.sha256(S.read_bytes()).hexdigest(),"canvas":[546,483],"outer":outer.tolist(),"inner":inner.tolist(),"reference_exact":True,"frame_ring_pixels":int((ring>0).sum()),"photo_window_pixels":int((m_i>0).sum()),"game_integrated":False}
(O/"QA_manifest.json").write_text(json.dumps(M,ensure_ascii=False,indent=2),encoding="utf-8")
