# -*- coding: utf-8 -*-
"""A18 E08 carpet body + gold piping split / actual source-based marble reconstruction.
All assets deterministic, photo windows and formal actor bytes untouched.
"""
from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,cv2,hashlib,json
from scipy.sparse import lil_matrix
from scipy.sparse.linalg import splu
O=Path(__file__).resolve().parent
def rd(name):return Image.open(O/name)
base=np.asarray(rd("source_A_without_characters.png").convert("RGB"))
reference=np.asarray(rd("source_A_with_formal_characters.png").convert("RGB"))
sourcegold=np.asarray(rd("source_original_red_carpet_without_gold.png").convert("RGB"))
gold=rd("entrance_red_carpet_gold_trim.png").convert("RGBA")
assert base.shape==(483,546,3)==sourcegold.shape
H,W=base.shape[:2]
# Visible source rug, with original perspective. Shape is deliberately not
# an invented rectangular rug and does not extend into the walkways.
corners=[(193,235),(367,235),(390,438),(172,438)]
rugmask=np.zeros((H,W),np.uint8)
cv2.fillConvexPoly(rugmask,np.array(corners,dtype=np.int32),255)
rugmask=cv2.GaussianBlur(rugmask,(3,3),0.5)
cropleft,croptop,cropright,cropbottom=164,226,399,449
cutalpha=rugmask[croptop:cropbottom,cropleft:cropright]
assert np.count_nonzero(cutalpha)>40000
rgba=np.dstack((sourcegold[croptop:cropbottom,cropleft:cropright],cutalpha))
body=Image.fromarray(rgba,"RGBA")
body.save(O/"entrance_red_carpet_body.png",optimize=True)
Image.fromarray(cutalpha,"L").save(O/"entrance_red_carpet_body_mask.png",optimize=True)
# Alternative matte plain red for low-decoration levels. The previously approved
# no-gold underlay still had small orange thread residues in the weave; remove
# only these locally without altering the gold version or the original source.
hsv=cv2.cvtColor(sourcegold,cv2.COLOR_RGB2HSV)
suspect=(hsv[:,:,0]>=9)&(hsv[:,:,0]<=35)&(hsv[:,:,1]>=95)&(sourcegold[:,:,0]>sourcegold[:,:,1]*1.25)&(sourcegold[:,:,1]>sourcegold[:,:,2]*1.10)
rm=np.zeros((H,W),np.uint8)
rm[croptop:cropbottom,cropleft:cropright]=cutalpha
rm=np.uint8(suspect&(rm>0))*255
rm=cv2.dilate(rm,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(3,3)))
pbg=cv2.cvtColor(cv2.inpaint(cv2.cvtColor(sourcegold,cv2.COLOR_RGB2BGR),rm,3,cv2.INPAINT_TELEA),cv2.COLOR_BGR2RGB)
plainbody=Image.fromarray(np.dstack((pbg[croptop:cropbottom,cropleft:cropright],cutalpha)),"RGBA")
plainbody.save(O/"entrance_red_carpet_plain_body.png",optimize=True)
Image.fromarray(rm[croptop:cropbottom,cropleft:cropright],"L").save(O/"entrance_red_carpet_gold_residue_removal_mask.png")
# Floor mask covers the 1-4px carpet's cast shadow as well as red pixels.
m=(rugmask>5).astype(np.uint8)*255
m=cv2.dilate(m,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(19,19)))
ys,xs=np.where(m>0)
x0,y0,x1,y1=int(xs.min()-1),int(ys.min()-1),int(xs.max()+2),int(ys.max()+2)
floor_roi=base[y0:y1,x0:x1].astype(float)
inner=m[y0:y1,x0:x1]>0
h,w=inner.shape
index=np.full((h,w),-1,dtype=np.int32)
index[inner]=np.arange(int(inner.sum()))
A=lil_matrix((int(inner.sum()),int(inner.sum())),dtype=np.float64)
rhs=np.zeros((int(inner.sum()),3),np.float64)
for yy,xx in np.argwhere(inner):
 i=index[yy,xx];A[i,i]=4
 for dy,dx in ((-1,0),(1,0),(0,-1),(0,1)):
  ny,nx=yy+dy,xx+dx
  if inner[ny,nx]:A[i,index[ny,nx]]-=1
  else:rhs[i]+=floor_roi[ny,nx]
solver=splu(A.tocsc())
inpainted=floor_roi.copy()
for ch in range(3):inpainted[:,:,ch][inner]=solver.solve(rhs[:,ch])
floor=base.copy()
floor[y0:y1,x0:x1]=np.uint8(np.clip(np.rint(inpainted),0,255))
# Reconstruct subtle source-based marble grains and consistent ceiling reflections.
# All noncarpet exterior pixels are preserved. No generated actors or new architecture.
rng=np.random.default_rng(2026)
Y,X=np.mgrid[:H,:W]
tex=np.asarray(base[245:434,133:169],dtype=np.float32)
tex_hp=tex-cv2.GaussianBlur(tex,(0,0),sigmaX=4,sigmaY=4)
modx=(X*11+Y*3)%36
mody=(Y*7+X*2)%189
grain=cv2.GaussianBlur(tex_hp[mody,modx],(3,3),.35)
noise=rng.normal(0,1,(31,47)).astype("float32")
noise=cv2.GaussianBlur(cv2.resize(noise,(W,H),interpolation=cv2.INTER_CUBIC),(0,0),3)
f=floor.astype(float)+grain*.30+noise[:,:,None]*1.1
center=282+1.4*np.sin(Y*.013)
strength=4.5+7*np.exp(-((Y-420)/62.)**2)
flare=np.exp(-((X-center)/(4.3+.008*(Y-235)))**2)
f[:,:,0]+=flare*strength;f[:,:,1]+=flare*strength*.67;f[:,:,2]+=flare*strength*.18
for line in range(-5,6):
 pitch=39+16*np.clip((Y-235)/225,0,1)
 dist=np.abs(X-(280+line*pitch))
 f-= (4.0*np.exp(-.5*(dist/.70)**2))[:,:,None]
for yline in (294,352,407):
 f-= (2.5*np.exp(-.5*((Y-yline)/.7)**2))[:,:,None]
soft=cv2.GaussianBlur(m,(11,11),2).astype(float)/255
clean=np.uint8(np.clip(np.rint(f*soft[:,:,None]+base*(1-soft[:,:,None])),0,255))
clean[m==0]=base[m==0]
# Maintain literal original bytes where the floor-edit mask is completely zero.
assert np.array_equal(clean[m==0],base[m==0])
Image.fromarray(clean,"RGB").save(O/"entrance_marble_floor_without_carpet.png",optimize=True)
Image.fromarray(m,"L").save(O/"entrance_floor_repair_mask.png",optimize=True)
# Independent subtle contact shadow, not fused with marble and not tinted onto a user photo.
shadow=cv2.GaussianBlur((rugmask>128).astype(np.uint8)*255,(17,17),3)
ring=np.maximum(0,shadow.astype(int)-rugmask.astype(int)).astype(np.uint8)
shalpha=np.uint8(np.clip(ring.astype(float)*.24,0,255))
scrop=np.dstack((np.full((H,W),43,np.uint8),np.full((H,W),31,np.uint8),np.full((H,W),18,np.uint8),shalpha))[croptop:cropbottom,cropleft:cropright]
Image.fromarray(scrop,"RGBA").save(O/"entrance_red_carpet_contact_shadow.png",optimize=True)
# Formal character PNGs are byte-identical to officially adopted sprites.
def person(canvas,name,cx,foot,width):
 im=rd("characters/"+name).convert("RGBA");height=round(im.height*width/im.width)
 canvas.alpha_composite(im.resize((width,height),Image.Resampling.NEAREST),(round(cx-width/2),foot-height))
def render(show=True,showgold=True,scale=1.0,chars=True,shift=0):
 canvas=Image.fromarray(clean,"RGB").convert("RGBA")
 if show:
  # floor-bottom anchor (281,438): any resize keeps original truncated floor edge realistic.
  ax,ay=281,438
  sx=round(ax+shift+(cropleft-ax)*scale)
  sy=round(ay+(croptop-ay)*scale)
  bw=round((cropright-cropleft)*scale)
  bh=round((cropbottom-croptop)*scale)
  for png in [rd("entrance_red_carpet_contact_shadow.png").convert("RGBA"),(body if showgold else plainbody)]:
   canvas.alpha_composite(png.resize((bw,bh),Image.Resampling.LANCZOS),(sx,sy))
  if showgold:
   # Original already-approved piping PNG was x173,y235 220x203.
   px=round(ax+shift+(173-ax)*scale)
   py=round(ay+(235-ay)*scale)
   canvas.alpha_composite(gold.resize((round(220*scale),round(203*scale)),Image.Resampling.LANCZOS),(px,py))
 if chars:
  person(canvas,"butler-front-00.png",140,371,43)
  person(canvas,"curator-front-00.png",287,366,35)
 return canvas.convert("RGB")
files={
 "QA_marble_floor_without_carpet.png":dict(show=False),
 "QA_red_carpet_without_gold.png":dict(show=True,showgold=False),
 "QA_red_carpet_with_gold.png":dict(show=True,showgold=True),
 "QA_red_carpet_090pct.png":dict(show=True,showgold=True,scale=.9),
 "QA_red_carpet_110pct.png":dict(show=True,showgold=True,scale=1.1),
 "QA_red_carpet_shift_5px.png":dict(show=True,showgold=True,shift=5),
 "QA_bare_floor_without_characters.png":dict(show=False,chars=False),
}
for name,options in files.items():render(**options).save(O/name,optimize=True)
orig_comp=np.asarray(rd("source_A_with_formal_characters.png").convert("RGB"))
comparison=np.asarray(render(True,True))
delta=np.abs(np.int16(comparison)-np.int16(orig_comp))
mae=float(delta.mean())
board=Image.new("RGB",(546*3,483))
for i,n in enumerate(["QA_marble_floor_without_carpet.png","QA_red_carpet_without_gold.png","QA_red_carpet_with_gold.png"]):
 board.paste(rd(n).convert("RGB"),(i*546,0))
board.save(O/"QA_three_carpet_states.jpg",quality=94)
sizes=Image.new("RGB",(546*3,483))
for i,n in enumerate(["QA_red_carpet_090pct.png","QA_red_carpet_with_gold.png","QA_red_carpet_110pct.png"]):
 sizes.paste(rd(n).convert("RGB"),(i*546,0))
sizes.save(O/"QA_carpet_three_sizes.jpg",quality=94)
# Global architecture/empty photo regions must be unchanged, as must the actors
area=np.zeros((H,W),bool)
area[215:452,157:404]=True
assert np.array_equal(clean[~area],base[~area]),"unexpected edits outside carpet"
for region in [(80,60,190,143),(368,60,465,143),(414,200,503,326)]:
 x0_,y0_,x1_,y1_=region
 assert np.array_equal(np.asarray(render(False))[y0_:y1_,x0_:x1_],orig_comp[y0_:y1_,x0_:x1_])
G=Path(r"G:\マイドライブ\06.アプリ開発\03.開発・テスト\A18_パズル美術館\00_正式採用素材\characters")
for n in ["butler-front-00.png","curator-front-00.png"]:
 assert (G/n).read_bytes()==(O/"characters"/n).read_bytes()
print("FINAL CARPET ART",{"mask":int((rugmask>0).sum()),"repair":int((m>0).sum()),"mae_ref":round(mae,4)},flush=True)
metadata={
 "art_id":"E08-carpet-body-split", "canvas":[W,H], "source_corners":corners,
 "body":{"file":"entrance_red_carpet_body.png","crop_xyxy":[cropleft,croptop,cropright,cropbottom]},
 "piping":{"file":"entrance_red_carpet_gold_trim.png","crop_xywh":[173,235,220,203],"preserved_prior_approved":True},
 "floor_underlay":"entrance_marble_floor_without_carpet.png",
 "contact_shadow":"entrance_red_carpet_contact_shadow.png",
 "carpet_floor_anchor_xy":[281,438],"scaling_tested":[.9,1.,1.1],
 "translation_x_tested":[0,5],
 "comparison_full_image_mae_vs_previous_A":round(mae,4),
 "floor_repair_pixels":int((m>0).sum()),
 "scene_reflectance":"marble below old rug is inferred from surrounding approved marble; not source-exact",
 "original_characters_preserved":True,
 "photo_frame_windows_preserved":True,
 "game_integrated":False,"user_approved":False,
 "lv1_or_lv2_assignment":"not assigned"
}
(O/"QA_manifest.json").write_text(json.dumps(metadata,ensure_ascii=False,indent=2),encoding="utf-8")
