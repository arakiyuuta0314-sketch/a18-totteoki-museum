# -*- coding: utf-8 -*-
"""A18: lossless source-based 3-slot frame separations; no image synthesis."""
from pathlib import Path
from PIL import Image, ImageDraw
import numpy as np, cv2, hashlib, json, shutil, math
ROOT=Path(r"G:\マイドライブ\06.アプリ開発\03.開発・テスト\A18_パズル美術館")
HERE=Path(__file__).resolve().parent
WEB=HERE/"entrance-frames-independent-20261026"
DRIVE=ROOT/"43_エントランス完成素材_3額縁本体装飾分離_v01"
D28=ROOT/"28_エントランス完成素材_背面展示枠左右_v01"
D38=ROOT/"38_エントランス完成素材_右手前可変額縁_v01"
D42=ROOT/"42_エントランス完成素材_赤絨毯本体分離_v01"
D41=ROOT/"41_エントランスA案_装飾なし比較_20261026"
CHARS=ROOT/"00_正式採用素材"/"characters"
ORIG=HERE/"entrance-test-v3/layout-test/assets/entrance/v0.3/approved_entrance_trial.jpg"
for p in [ORIG,D28/"frame_left_5x5.png",D38/"entrance_photo_frame_03.png",D42/"QA_bare_floor_without_characters.png",D41/"A18_entrance_A_plain_no_decor_preview.png"]:
    assert p.is_file(),p
WEB.mkdir(exist_ok=True)
def im(p):return Image.open(p)
def save(img,n):img.save(WEB/n,optimize=True);return img
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
raw=np.asarray(im(ORIG).convert("RGB"))
floor=np.asarray(im(D42/"QA_bare_floor_without_characters.png").convert("RGB"))
assert raw.shape==(483,546,3)==floor.shape
base=floor.copy()
rear=np.asarray(im(D28/"entrance_bg_without_rear_frames.png").convert("RGB"))
sp={"left":{"rect":(76,50,201,157),"window":(84,61,194,144),"center":(138.5,103.5)},
    "right":{"rect":(365,50,468,157),"window":(373,61,460,144),"center":(416.5,103.5)},
    "front":{"center":(457.5,261),"window":None}}
for key in ("left","right"):
    x0,y0,x1,y1=sp[key]["rect"]
    base[y0:y1,x0:x1]=rear[y0:y1,x0:x1]
wall=np.asarray(im(D38/"entrance_right_wall_without_frame.png").convert("RGBA"))
ring3=np.asarray(im(D38/"entrance_photo_frame_03.png").convert("RGBA"))[:,:,3]>0
mat3=np.asarray(im(D38/"entrance_photo_empty_03.png").convert("RGBA"))[:,:,3]>0
# Only replace the localized gilded photo assembly, NOT the whole wall:
# prior 41's repaired plant at lower-right must remain removed.
local=cv2.dilate(np.uint8(ring3|mat3)*255,np.ones((9,9),np.uint8))>0
wallalpha=wall[:,:,3]/255.*local
base=np.uint8(np.rint(base*(1-wallalpha[:,:,None])+wall[:,:,:3]*wallalpha[:,:,None]))
# Existing 38 backing exposes thin source-gold slivers outside source's hand-traced outer polygon.
# Target ONLY gold in a 6px halo around its already-removed frame, NOT wood railing or lamps.
halo=cv2.dilate(np.uint8(ring3)*255,np.ones((23,23),np.uint8))>0
hsv=cv2.cvtColor(base,cv2.COLOR_RGB2HSV)
Y,X=np.mgrid[:483,:546]
gold=(hsv[:,:,0]>5)&(hsv[:,:,0]<35)&(hsv[:,:,1]>83)&(hsv[:,:,2]>76)
fix=halo&gold&(X>=413)&(X<=504)&(Y>=185)&(Y<=341)&(wall[:,:,3]>0)
# Keep a conservative edge restoration (source-green derived from existing approved wall).
green=np.asarray(im(D38/"QA_right_green_backing.png").convert("RGB"))
# Only fix truly isolated gold remnants, not the exposed wood handrail or frame's upper lamp.
fix&=(X<501)&(Y>190)
base[fix]=green[fix]
save(Image.fromarray(base,"RGB"),"entrance_bare_three_frame_backing.png")
save(Image.fromarray(np.uint8(fix)*255,"L"),"residual_frame_gold_repair_mask.png")
# Source-derived transparent layers. Full original gold ring never painted anew.
fullframe={}
mats={}
for key in ("left","right"):
    x0,y0,x1,y1=sp[key]["rect"]
    f=im(D28/f"frame_{key}_5x5.png").convert("RGBA")
    a=np.asarray(f.getchannel("A"))
    # These alpha windows remain transparent, allowing registered photographs.
    l,t,r,b=sp[key]["window"]
    assert (a[t-y0:b-y0,l-x0:r-x0]==0).all()
    full=Image.new("RGBA",(546,483))
    full.alpha_composite(f,(x0,y0))
    fullframe[key]=full
    m=Image.new("RGBA",(546,483))
    m.alpha_composite(im(D28/f"empty_{key}.png").convert("RGBA"),(l,t))
    mats[key]=m
fullframe["front"]=im(D38/"entrance_photo_frame_03.png").convert("RGBA")
mats["front"]=im(D38/"entrance_photo_empty_03.png").convert("RGBA")
# Make an unadorned photo-mat alternative for the foreground panel.
# The original 'empty' photo matte has glint pixels burned into its edge.
# Keep the source matte UNCHANGED for exact gold-frame reconstruction.
mats_simple=dict(mats)
frontarr=np.asarray(mats["front"].convert("RGBA"))
fa=frontarr[:,:,3]
inside=fa>0
edge=cv2.distanceTransform(np.uint8(inside),cv2.DIST_L2,3)<=3.5
repair_mat=np.uint8(edge & inside)*255
neutral=np.median(frontarr[inside][:,:3],axis=0).astype(np.uint8)
inarr=frontarr[:,:,:3].copy()
inarr[~inside]=neutral
inpainted=cv2.cvtColor(cv2.inpaint(cv2.cvtColor(inarr,cv2.COLOR_RGB2BGR),repair_mat,3,cv2.INPAINT_TELEA),cv2.COLOR_BGR2RGB)
mats_simple["front"]=save(Image.fromarray(np.dstack([inpainted,fa]),"RGBA"),"exhibition_front_plain_mat.png")
save(Image.fromarray(repair_mat,"L"),"exhibition_front_matte_edge_repair_mask.png")
# Derive a much quieter brown frame body from ORIGINAL relief and its alpha,
# retaining exact native shape/perspective rather than inventing another building.
goldbody={};decor={};woodframe={}
for key,f in fullframe.items():
    a=np.asarray(f.getchannel("A"))
    rgb=np.asarray(f.convert("RGB"),dtype=np.uint8)
    # Source wood palette + existing frame relief; opaque parts use native pixel mask.
    lum=cv2.cvtColor(rgb,cv2.COLOR_RGB2GRAY).astype(np.float32)/255
    grain=cv2.GaussianBlur(lum,(0,0),sigmaX=1.2)
    rgbwood=np.stack([56+41*grain,33+33*grain,16+20*grain],axis=-1)
    # The brown wood is a source-derived *alternative*, not a new frame geometry.
    wd=Image.fromarray(np.dstack([np.uint8(np.clip(rgbwood,0,255)),a]),"RGBA")
    save(wd,f"frame_{key}_wood_basic.png");woodframe[key]=wd
    mask=np.zeros((483,546),np.uint8)
    d=ImageDraw.Draw(Image.fromarray(mask,"L"))
    # Delicate ornaments are isolated from main gold border. Their masks follow source ring.
    if key in ("left","right"):
        x0,y0,x1,y1=sp[key]["rect"];cx=(x0+x1)//2
        for xx,yy,rx,ry in ((cx,y0+7,15,13),(cx,y1-9,14,12),
                            (x0+10,y0+13,15,20),(x1-10,y0+13,15,20),
                            (x0+8,y1-15,12,19),(x1-8,y1-15,12,19)):
            cv2.ellipse(mask,(xx,yy),(rx,ry),0,0,360,255,-1)
    else:
        for xx,yy in [(416,184),(500,211),(502,339),(413,294),(459,196),(458,317)]:
            cv2.circle(mask,(xx,yy),12,255,-1)
    mask=np.minimum(mask,a)
    # Exact reconstruction: body is original RGB with inferred replacement only at masked motifs.
    # Transparent window RGB is black in PNG; pre-fill it with warm gold before
    # inpainting or the body would acquire black holes at ornament/window edges.
    inp=rgb.copy()
    inp[a==0]=[132,94,47]
    repair=cv2.inpaint(cv2.cvtColor(inp,cv2.COLOR_RGB2BGR),mask,3,cv2.INPAINT_TELEA)
    repaired=cv2.cvtColor(repair,cv2.COLOR_BGR2RGB)
    layer=Image.fromarray(np.dstack([repaired,a]),"RGBA")
    accents=Image.fromarray(np.dstack([rgb,mask]),"RGBA")
    goldbody[key]=save(layer,f"frame_{key}_gold_body.png")
    decor[key]=save(accents,f"frame_{key}_gold_ornaments.png")
    save(Image.fromarray(mask,"L"),f"frame_{key}_ornament_mask.png")
    test=Image.alpha_composite(layer,accents)
    orig=np.asarray(f)
    tgt=np.asarray(test)
    valid=a>0
    assert np.array_equal(orig[valid],tgt[valid]),("split reconstruction",key)
    # Independent photo opening, empty mat and source photo window mask.
    save(f,f"frame_{key}_original_gold.png")
    save(mats[key],f"exhibition_{key}_empty_mat.png")
    if key in ("left","right"):
        x0,y0,x1,y1=sp[key]["window"]
        mk=Image.new("L",(546,483),0)
        ImageDraw.Draw(mk).rectangle((x0,y0,x1-1,y1-1),fill=255)
        save(mk,f"exhibition_{key}_window_mask.png")
    else:
        shutil.copy2(D38/"entrance_photo_window_03_mask.png",WEB/"exhibition_front_window_mask.png")
# Full-frame photo samples for all slots, unchanged user-photo handling.
samples={}
for k in ("left","right"):
    x0,y0,x1,y1=sp[k]["window"]
    pic=im(D28/f"demo_photo_{k}.jpg").convert("RGB")
    ww,hh=x1-x0,y1-y0
    factor=max(ww/pic.width,hh/pic.height)
    resized=pic.resize((math.ceil(pic.width*factor),math.ceil(pic.height*factor)),Image.Resampling.LANCZOS)
    bx=(resized.width-ww)//2;by=(resized.height-hh)//2
    sample=Image.new("RGBA",(546,483));sample.alpha_composite(resized.crop((bx,by,bx+ww,by+hh)).convert("RGBA"),(x0,y0))
    samples[k]=sample
samples["front"]=im(D38/"demo_photo_03_warped.png").convert("RGBA")
for k,v in samples.items():save(v,f"exhibition_{k}_photo_sample.png")
# For future adjustable sizes: full-canvas affine; same anchor for photo, mat and frame.
def affine(layer,key,scale):
    if scale==1:return layer
    cx,cy=sp[key]["center"]
    M=cv2.getRotationMatrix2D((cx,cy),0,scale)
    arr=cv2.warpAffine(np.asarray(layer),M,(546,483),flags=cv2.INTER_LINEAR,
                       borderMode=cv2.BORDER_CONSTANT,borderValue=(0,0,0,0))
    return Image.fromarray(arr,"RGBA")
def people(scene):
    for name,cx,foot,w in [("butler-front-00.png",140,371,43),("curator-front-00.png",287,366,35)]:
        sprite=im(CHARS/name).convert("RGBA");hh=round(sprite.height*w/sprite.width)
        scene.alpha_composite(sprite.resize((w,hh),Image.Resampling.NEAREST),(round(cx-w/2),foot-hh))
def composite(style="none",scale=1,photo=False,characters=True):
    assert style in ("none","wood","gold_basic","gold_full")
    scene=Image.fromarray(base,"RGB").convert("RGBA")
    for key in ("left","right","front"):
        mat=samples[key] if photo else (mats[key] if style in ("gold_full","gold_basic") else mats_simple[key])
        scene.alpha_composite(affine(mat,key,scale))
        if style=="wood":scene.alpha_composite(affine(woodframe[key],key,scale))
        elif style=="gold_basic":scene.alpha_composite(affine(goldbody[key],key,scale))
        elif style=="gold_full":
            scene.alpha_composite(affine(goldbody[key],key,scale))
            scene.alpha_composite(affine(decor[key],key,scale))
    if characters:people(scene)
    return scene.convert("RGB")
styles={"none":"QA_01_no_ornate_frames.png","wood":"QA_02_simple_wood_frames.png",
        "gold_basic":"QA_03_gold_body_only.png","gold_full":"QA_04_gold_full_restored.png"}
for style,name in styles.items():save(composite(style),name)
save(composite("none",characters=False),"QA_background_only_no_frames_no_characters.png")
for st in ("none","wood","gold_full"):
    for size in (90,100,110):
        for photographic in (False,True):
            state="photos" if photographic else "empty"
            save(composite(st,size/100,photo=photographic),
                 f"view_{st}_{state}_{size}.png")
for pct in (90,100,110):
    for style in ("wood","gold_full"):
        save(composite(style,pct/100,photo=True),f"QA_{style}_photos_{pct}pct.png")
for style in ("none","wood","gold_full"):
    save(composite(style,photo=True),f"QA_{style}_photos_100pct.png")
board=Image.new("RGB",(546*4,483))
for i,n in enumerate(styles.values()):board.paste(im(WEB/n),(i*546,0))
save(board,"QA_comparison_all_four_states.png")
# Character source binary integrity and unchanged architectural background outside controlled regions.
for n in ("butler-front-00.png","curator-front-00.png"):
    assert (CHARS/n).is_file()
charhash={n:sha(CHARS/n) for n in ("butler-front-00.png","curator-front-00.png")}
original=im(D42/"QA_marble_floor_without_carpet.png").convert("RGB")
restored=composite("gold_full",characters=True)
delta=np.abs(np.asarray(restored,dtype=np.int16)-np.asarray(original,dtype=np.int16))
change=np.zeros((483,546),bool)
for key in ("left","right"):
    x0,y0,x1,y1=sp[key]["rect"];change[y0:y1,x0:x1]=True
change|=wall[:,:,3]>0
# Check restoration does not affect left reception or central structure.
assert (delta[~change]==0).all(),("unsafe architectural changes outside frames",int(np.max(delta[~change])))
# Gold trim splits reproduce source gold exactly at all visible ring pixels.
for key in ("left","right","front"):
    a=np.asarray(fullframe[key].getchannel("A"))>0
    result=np.asarray(Image.alpha_composite(goldbody[key],decor[key]))
    src=np.asarray(fullframe[key])
    assert np.array_equal(result[a],src[a])
# Canvas snapshots and source hashes for strictly inspectable QA.
report={"status":"art_candidate_pending_visual_approval","source_canvas":[546,483],
        "reference_sha256":sha(ORIG),"bare_carpetless_source_sha256":sha(D42/"QA_bare_floor_without_characters.png"),
        "prior_rear_source_sha256":sha(D28/"frame_left_5x5.png"),
        "prior_front_source_sha256":sha(D38/"entrance_photo_frame_03.png"),
        "actual_official_character_sha256":charhash,
        "frame_slots":sp,"states":list(styles.keys()),
        "verified_scale":[0.90,1.00,1.10],
        "ornament_split_source_exact_on_ring_pixels":True,
        "outside_managed_frame_and_display_wall_pixels_changed":int((delta[~change]!=0).any(axis=1).sum()),
        "full_reassembly_vs_previous_carpetless_A_rgb_mae":float(delta.mean()),
        "full_reassembly_changed_pixels":int((delta>0).any(axis=2).sum()),
        "front_residual_gold_pixels_repaired":int(fix.sum()),
        "new_inferred_materials":["unseen green panel pixels beneath old gold frame","simple wood alternative derived from source contrast","small ornament-hidden gold base"],
        "lighting_still_baked_in":True,"carpet_removed":True,"build_revision":"v01","game_integrated":False,"lv1_fixed":False}
(WEB/"QA_manifest.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
# All staged artifacts copied to existing Drive archive, not splintered workbooks.
DRIVE.mkdir(exist_ok=True)
for f in WEB.iterdir():
    if f.is_file():shutil.copy2(f,DRIVE/f.name)
shutil.copy2(HERE/"build_removable_frames.py",DRIVE/"build_removable_frames.py")
print("BUILD_PASS",json.dumps({k:report[k] for k in ["full_reassembly_vs_previous_carpetless_A_rgb_mae","full_reassembly_changed_pixels","front_residual_gold_pixels_repaired"]},ensure_ascii=False))
print("OUTPUT",WEB,"DRIVE",DRIVE)
