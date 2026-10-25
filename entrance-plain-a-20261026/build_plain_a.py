# -*- coding:utf-8 -*-
"""A18: A案『なるべく素のエントランス』可視化。
No newly generated architecture or characters. Layer source is approved B01.
This DOES NOT assign the art to Lv.1, and does not modify the game.
"""
from pathlib import Path
from PIL import Image
import numpy as np,cv2,json,hashlib
O=Path(__file__).parent
B=O.parent/"entrance-b01-unified-20261025"
def load(path):return Image.open(B/path)
orig=load("approved_entrance_trial.jpg").convert("RGB")
background=load("B01_entrance_base_without_independent_art.png").convert("RGBA")
assert background.size==(546,483)
def layer(canvas,path,loc=(0,0)):canvas.alpha_composite(load(path).convert("RGBA"),loc)
def frame(canvas,side):
 geo={"left":(76,50,84,61),"right":(365,50,373,61)}
 x,y,xp,yp=geo[side]
 layer(canvas,f"rear/empty_{side}.png",(xp,yp))
 layer(canvas,f"rear/frame_{side}_5x5.png",(x,y))
def actor(canvas,name,cx,foot,w):
 raw=load(f"characters/{name}").convert("RGBA")
 h=round(raw.height*w/raw.width)
 canvas.alpha_composite(raw.resize((w,h),Image.Resampling.NEAREST),(round(cx-w/2),foot-h))
def compose(chars=True):
 c=background.copy()
 # Mandatory built architecture, not optional decorative objects:
 layer(c,"rail3/entrance_right_wall_without_frame_and_rail.png")
 layer(c,"door/entrance_door_north_closed.png")
 frame(c,"left");frame(c,"right")
 layer(c,"frame3/entrance_photo_empty_03.png")
 layer(c,"frame3/entrance_photo_frame_03.png")
 layer(c,"rail3/entrance_fg_right_rail.png")
 layer(c,"leftWall/entrance_left_foreground_wall.png")
 layer(c,"leftWall/entrance_left_foreground_rail.png")
 layer(c,"counter/entrance_counter_fg_top_lip.png")
 # Counter front has source E01 shrub baked into its original image. Replace
 # ONLY foliage residue pixels with the prepared B01 walnut repair, not character art.
 rawface=np.asarray(load("counter/entrance_counter_fg_front_face.png").convert("RGBA")).copy()
 br=np.asarray(background.convert("RGB"))
 for yy in range(400,440):
  for xx in range(0,51):
   if rawface[yy,xx,3]==0:continue
   old=rawface[yy,xx,:3]
   if yy<405:k=(yy-400)/5
   elif yy>434:k=(440-yy)/6
   else:k=1.
   if xx>44:k*=max(0,(51-xx)/7)
   k=max(0,min(1,k))
   rawface[yy,xx,:3]=np.uint8(np.clip(np.rint(old*(1-k)+br[yy,xx]*k),0,255))
 c.alpha_composite(Image.fromarray(rawface,"RGBA"))
 if chars:
  actor(c,"butler-front-00.png",140,371,43)
  actor(c,"curator-front-00.png",287,366,35)
 return c.convert("RGB")
plain=compose()
plain.save(O/"A18_entrance_A_plain_no_decor_preview.png",optimize=True)
compose(False).save(O/"SOURCE_pre_repair_no_characters.png",optimize=True)
# no drawn photos/flora/extra should be deliberately reinserted.
w,h=orig.size
assert (w,h)==(546,483)
manifest={
"scene":"A・なるべく素のエントランス",
"canvas":[546,483],"not_lv1_decision":True,
"removed":["3 registered photos (empty mats retained)","E01,E02 plants","E03 flower vase","E06 wooden plant plinths","E04 rear picture lights","E05 ceiling/wainscot trim","E08 carpet gold piping","left/right direction sign and wall sconces"],
"retained":["structural gallery walls","north door closed","3 empty picture frames","right passage handrail","reception counter","original formal characters"],
"source":"entrance-b01-unified-20261025 checked-in files",
"original_character_assets":"reused byte-identically; no AI redrawing",
"underlay_reconstruction":"left front walnut and planter plinth zones originally occluded, not source-exact",
"source_sha256":hashlib.sha256((B/"approved_entrance_trial.jpg").read_bytes()).hexdigest(),
"game_integrated":False,"user_art_review":"pending"}
(O/"QA_manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding="utf-8")
print("INITIAL_A",list(plain.size),"file", (O/"A18_entrance_A_plain_no_decor_preview.png").stat().st_size)
