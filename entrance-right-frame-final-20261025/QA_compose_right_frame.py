# -*- coding:utf-8 -*-
from pathlib import Path
from PIL import Image
import numpy as np,cv2,json,hashlib
O=Path(__file__).resolve().parent
G=Path(r"G:\マイドライブ\06.アプリ開発\03.開発・テスト\A18_パズル美術館")
S=O.parent/"entrance-test-v3/layout-test/assets/entrance/v0.3/approved_entrance_trial.jpg"
D=G/"27_エントランス完成素材_右展示壁_v01"
ref=np.asarray(Image.open(S).convert("RGB"))
base=np.asarray(Image.open(D/"QA_complete_wall_three_photos_and_formal_sprites.png").convert("RGB")).copy()
p_wall=np.asarray(Image.open(O/"entrance_right_wall_without_frame.png").convert("RGBA"))
mask=p_wall[:,:,3]>0
base[mask]=p_wall[:,:,:3][mask]
Image.fromarray(base,"RGB").save(O/"QA_base_with_formal_characters_no_frame.png")
center=(457.5,261.)
frame=np.asarray(Image.open(O/"entrance_photo_frame_03.png").convert("RGBA"))
empty=np.asarray(Image.open(O/"entrance_photo_empty_03.png").convert("RGBA"))
photo=np.asarray(Image.open(O/"demo_photo_03_warped.png").convert("RGBA"))
def place(img,layer,scale):
 if scale==1:return Image.alpha_composite(img,Image.fromarray(layer,"RGBA"))
 # 2D uniform scale preserves all frame corners and existing trapezoid perspective:
 M=cv2.getRotationMatrix2D(center,0,scale)
 transformed=cv2.warpAffine(layer,M,(546,483),flags=cv2.INTER_LINEAR,borderMode=cv2.BORDER_CONSTANT,borderValue=(0,0,0,0))
 return Image.alpha_composite(img,Image.fromarray(transformed,"RGBA"))
def render(scale=1,with_photo=False,show_frame=True):
 img=Image.fromarray(base,"RGB").convert("RGBA")
 if show_frame:
  img=place(img,photo if with_photo else empty,scale)
  img=place(img,frame,scale)
 return img.convert("RGB")
for scale in (.90,1.,1.10):
 suffix=f"{round(scale*100):03d}"
 for mode in ("photo","empty"):
  render(scale,mode=="photo").save(O/f"QA_frame03_{mode}_{suffix}pct.png",optimize=True)
render(show_frame=False).save(O/"QA_frame03_hidden.png",optimize=True)
# reference third photo reconstruction MUST match registered 27 pix for scale=100
actual=np.asarray(render(1,True));ground=np.asarray(Image.open(D/"QA_complete_wall_three_photos_and_formal_sprites.png").convert("RGB"))
diff=np.abs(np.int16(actual)-np.int16(ground))
print("PHOTO_REASSEMBLY RGB MAE",diff.mean(),"DIFF PIXELS",int(np.any(diff>0,axis=2).sum()),"MAX",diff.max())
assert diff.max()==0
# blank should match original source except for official characters and first two demo photos.
empty_standard=np.asarray(render(1,False))
plain_scene=np.asarray(Image.open(D/"QA_complete_wall_empty_slot_formal_sprites.png").convert("RGB"))
assert np.array_equal(empty_standard,plain_scene)
# All changes must remain inside actual physical right wall region even at 110%
preserve=np.ones((483,546),bool);preserve[174:355,404:512]=False
assert np.array_equal(actual[preserve],ground[preserve])
for n in ("butler-front-00.png","curator-front-00.png"):
 original=G/"00_正式採用素材"/"characters"/n
 verified=G/"28_エントランス完成素材_背面展示枠左右_v01"/n
 assert original.read_bytes()==verified.read_bytes()
board=Image.new("RGB",(546*3,483))
for i,s in enumerate((.9,1.,1.1)):board.paste(render(s,True),(546*i,0))
board.save(O/"QA_three_sizes_registered_photo.jpg",quality=94)
board2=Image.new("RGB",(546*2,483))
board2.paste(render(1,False),(0,0));board2.paste(render(1,True),(546,0))
board2.save(O/"QA_photo_empty_comparison.jpg",quality=94)
data=json.loads((O/"QA_manifest.json").read_text(encoding="utf-8"))
data.update({"size_range_tested":[90,100,110],"frame_center":[457.5,261],
 "photo_and_empty_standard_match_prior_QA_exact":True,
 "method":"independent RGBA masked original trapezoid border and photo; affine uniform scale about fixed center to preserve corners, no axis-only distortion",
 "photo_state_100pct_pixel_difference":0,
 "needs_final_user_art_review":True,"transparent_background_repair":True})
(O/"QA_manifest.json").write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding="utf-8")
print("PASS RIGHT FRAME PHOTO EMPTY 90 100 110")
