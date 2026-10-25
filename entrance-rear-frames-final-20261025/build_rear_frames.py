# -*- coding: utf-8 -*-
"""A18 back-wall frame set: photographed-source 5x5 preserved decoration and clean underlay."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter
import cv2, numpy as np, json, hashlib, shutil, zipfile, math
ROOT=Path(r"G:\マイドライブ\06.アプリ開発\03.開発・テスト\A18_パズル美術館")
REF=Path(r"C:\Users\User\source\repos\a18-totteoki-museum-pages\entrance-test-v3\layout-test\assets\entrance\v0.3\approved_entrance_trial.jpg")
GT=Path(r"C:\Users\User\source\repos\a18-rear-frames-final-20261025")
WEB=GT/"entrance-rear-frames-final-20261025"
DRIVE=ROOT/"28_エントランス完成素材_背面展示枠左右_v01"
SPRITES=ROOT/"00_正式採用素材"/"characters"
SAMPLE=ROOT/"24_エントランス再設計_品質基準"
for p in [REF,SPRITES/"butler-front-00.png",SPRITES/"curator-front-00.png",SAMPLE/"memory_dog_demo.jpg",SAMPLE/"memory_holiday_demo.jpg"]:
    assert p.is_file(),p
assert not DRIVE.exists() or not any(DRIVE.iterdir()),"Existing output must be empty to prevent accidental overwrite"
WEB.mkdir(parents=True,exist_ok=True);DRIVE.mkdir(parents=True,exist_ok=True)
src=Image.open(REF).convert("RGB")
assert src.size==(546,483)
specs={
 "left":{"outer":[76,50,201,157],"inner":[84,61,194,144],"col":[0,20,48,77,105,125],"row":[0,25,47,71,87,107],"center":[138.5,103.5]},
 "right":{"outer":[365,50,468,157],"inner":[373,61,460,144],"col":[0,17,40,65,86,103],"row":[0,25,47,71,87,107],"center":[416.5,103.5]}
}
# Authenticated, unchanged original sprites (never synthesize the characters).
original_sprite_hashes={n:hashlib.sha256((SPRITES/n).read_bytes()).hexdigest() for n in ["butler-front-00.png","curator-front-00.png"]}
def hashfile(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rgba_from_rgb(rgb,alpha):
    return Image.fromarray(np.dstack([np.array(rgb),alpha]),"RGBA")
basearr=np.asarray(src).copy()
for key,sp in specs.items():
    l,t,r,b=sp["outer"]; il,it,ir,ib=sp["inner"]
    # The original frame with a completely transparent image opening.
    crop=src.crop((l,t,r,b))
    a=np.full((b-t,r-l),255,dtype=np.uint8)
    a[it-t:ib-t,il-l:ir-l]=0
    frame=rgba_from_rgb(crop,a)
    frame.save(WEB/f"frame_{key}_5x5.png",optimize=True)
    # Perfectly separate blank artwork from gold; no photo darkening/matting.
    blank=src.crop((il,it,ir,ib)).convert("RGBA")
    blank.save(WEB/f"empty_{key}.png",optimize=True)
    Image.fromarray(np.full((ib-it,ir-il),255,dtype=np.uint8)).save(WEB/f"window_{key}_mask.png")
    # Remove baked-in frame AND artwork, reconstruct underlying green inset from
    # SAME original left and right exposed wall texture (no new composition).
    yy=np.arange(t,b); donor_l=np.asarray(src.crop((l-6,t,l-1,b)),dtype=np.float32)
    donor_r=np.asarray(src.crop((r+1,t,r+6,b)),dtype=np.float32)
    # robust median per row; cut image background only in these precise areas.
    lc=np.median(donor_l,axis=1);rc=np.median(donor_r,axis=1)
    # Smooth sparse donor scanlines vertically before 2D interpolation;
    # avoids diagonal row-stepping artifacts on temporarily exposed green plaster.
    lc=cv2.GaussianBlur(lc.astype(np.float32),(1,29),sigmaX=0,sigmaY=7)
    rc=cv2.GaussianBlur(rc.astype(np.float32),(1,29),sigmaX=0,sigmaY=7)
    for j in range(b-t):
        for i in range(r-l):
            f=i/max(1,(r-l-1))
            # gentle central vignette, preserves existing teal wall family.
            val=lc[j]*(1-f)+rc[j]*f
            grain=((i*37+j*17)%19-9)*0.15
            basearr[t+j,l+i]=np.uint8(np.clip(val+grain,0,255))
# Overlay preserves original JPEG pixels outside the two frame rectangles exactly.
under=Image.fromarray(basearr,"RGB")
under.save(WEB/"entrance_bg_without_rear_frames.png",optimize=True)
shutil.copy2(REF,WEB/"approved_reference.jpg")
# Cover-fit demo artwork, only inside window.
photos={"left":Image.open(SAMPLE/"memory_dog_demo.jpg").convert("RGB"),
        "right":Image.open(SAMPLE/"memory_holiday_demo.jpg").convert("RGB")}
for key,im in photos.items():
    im.save(WEB/f"demo_photo_{key}.jpg",quality=90,optimize=True)

def segments(edges,target):
    orig=edges[-1]; delta=target-orig
    original=[edges[i+1]-edges[i] for i in range(5)]
    # keep the 4 corners AND central motifs at their unchanged size.
    sizes=[original[0],original[1]+delta//2,original[2],original[3]+delta-delta//2,original[4]]
    assert min(sizes)>0,(orig,target,sizes)
    return sizes
def resize_ornate(key,w,h):
    sp=specs[key];l,t,r,b=sp["outer"]
    ox,oy=sp["col"],sp["row"]; sw,sh=r-l,b-t
    dw,dh=segments(ox,w),segments(oy,h)
    dst=Image.new("RGBA",(w,h),(0,0,0,0))
    srcframe=Image.open(WEB/f"frame_{key}_5x5.png").convert("RGBA")
    dy=0
    for j in range(5):
        dx=0
        for i in range(5):
            chunk=srcframe.crop((ox[i],oy[j],ox[i+1],oy[j+1]))
            destw,desth=dw[i],dh[j]
            if chunk.size!=(destw,desth):
                chunk=chunk.resize((destw,desth),Image.Resampling.BICUBIC)
            dst.alpha_composite(chunk,(dx,dy));dx+=destw
        dy+=dh[j]
    return dst
def cover(im,size):
    w,h=size
    scale=max(w/im.width,h/im.height)
    dw,dh=math.ceil(im.width*scale),math.ceil(im.height*scale)
    return im.resize((dw,dh),Image.Resampling.LANCZOS).crop(((dw-w)//2,(dh-h)//2,(dw-w)//2+w,(dh-h)//2+h))
def sprite(onto,name,cx,foot,width):
    sp=Image.open(SPRITES/name).convert("RGBA")
    hh=round(sp.height*width/sp.width)
    sp=sp.resize((width,hh),Image.Resampling.NEAREST)
    onto.alpha_composite(sp,(round(cx-width/2),foot-hh))
def scene(scale,photos_enabled,character=True):
    layer=under.convert("RGBA")
    for key,sp in specs.items():
        l,t,r,b=sp["outer"];il,it,ir,ib=sp["inner"]
        sw,sh=r-l,b-t
        w,h=round(sw*scale),round(sh*scale)
        # fixed centre: no change in building layout or room paths
        x=l+(sw-w)//2;y=t+(sh-h)//2
        padl,padt,padr,padb=il-l,it-t,r-ir,b-ib
        inner=(w-padl-padr,h-padt-padb)
        assert min(inner)>0
        pic=(cover(photos[key],inner) if photos_enabled else Image.open(WEB/f"empty_{key}.png").resize(inner,Image.Resampling.BICUBIC))
        layer.alpha_composite(pic.convert("RGBA"),(x+padl,y+padt))
        layer.alpha_composite(resize_ornate(key,w,h),(x,y))
    # Actual user approved sprites, from original 48 unaltered files.
    if character:
        sprite(layer,"butler-front-00.png",140,371,43)
        sprite(layer,"curator-front-00.png",287,366,35)
    return layer.convert("RGB")
# baseline rebuild: the source should be reconstructed pixel-for-pixel except sprites.
base_rebuild=scene(1,False,False)
diff=np.abs(np.asarray(base_rebuild).astype("int16")-np.asarray(src).astype("int16"))
assert np.count_nonzero(diff)==0,(np.count_nonzero(diff),diff.max())
base_rebuild.save(WEB/"QA_exact_reconstruction_empty.png")
# Source wall texture remains unchanged outside the precise two restoration rectangles.
mask=np.zeros((483,546),np.uint8)
for x in specs.values():
    l,t,r,b=x["outer"];mask[t:b,l:r]=1
assert np.array_equal(np.asarray(under)[mask==0],np.asarray(src)[mask==0])
# test readable three scales (left and right independently scaled, 0.90/1/1.08).
scales=[.90,1.,1.08]
board=Image.new("RGB",(546*3,483*2),"white")
for j,hasphoto in enumerate([False,True]):
    for i,scale in enumerate(scales):
        im=scene(scale,hasphoto)
        im.save(WEB/f"QA_{'photos' if hasphoto else 'empty'}_{int(scale*100):03d}pct.png",optimize=True)
        board.paste(im,(i*546,j*483))
board.save(WEB/"QA_comparison_empty_and_photos_three_sizes.jpg",quality=93)
# individual cutouts of the repaired wall for visible independent resizing proof
under.crop((65,38,480,169)).resize((1245,393),Image.Resampling.NEAREST).save(WEB/"QA_clean_backwall_3x.png")
# alpha correctness, center ornament preservation, no accidental image darkening
tests={}
for key,sp in specs.items():
    f=Image.open(WEB/f"frame_{key}_5x5.png")
    l,t,r,b=sp["outer"];il,it,ir,ib=sp["inner"]
    alpha=np.array(f.getchannel("A"))
    assert np.all(alpha[it-t:ib-t,il-l:ir-l]==0)
    assert np.all(alpha[0,:]==255)
    for scale in scales:
        w,h=round((r-l)*scale),round((b-t)*scale)
        img=resize_ornate(key,w,h)
        pa=np.array(img.getchannel("A"))
        padl,padt,padr,padb=il-l,it-t,r-ir,b-ib
        assert np.all(pa[padt:h-padb,padl:w-padr]==0),(key,scale)
        tests[f"{key}_{scale}"]={"outer":[w,h],"window":[w-padl-padr,h-padt-padb],"alpha_window_zero":True}
        if scale==1:
            aa,bb=np.asarray(img),np.asarray(f)
            assert np.array_equal(aa[:,:,3],bb[:,:,3]) and np.array_equal(aa[bb[:,:,3]>0,:3],bb[bb[:,:,3]>0,:3])
manifest={
 "title":"A18 entrance back-wall exhibition frames left/right v01",
 "source":str(REF),"source_sha256":hashfile(REF),
 "canvas":[546,483],
 "source_sprite_sha256":original_sprite_hashes,
 "frame_units":"logical 546x483 pixels; 5x5 mapping of one RGBA source to target outer rectangle",
 "specs":specs,"scale_verified":[.90,1.0,1.08],
 "minimum_recommended_scale":.90,"maximum_recommended_scale":1.08,
 "pixel_exact_standard_empty":True,"source_unchanged_outside_rectangles":True,
 "photo_unshaded":True,"browser_qa_required":True,
 "game_integration":False, "tests":tests,"files":{}
}
for p in WEB.iterdir():
    if p.is_file() and p.suffix.lower() in [".png",".jpg",".jpeg"]:
        im=Image.open(p);manifest["files"][p.name]={"px":list(im.size),"mode":im.mode,"sha256":hashfile(p)}
(WEB/"QA_manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding="utf-8")
print("ART GENERATED",len(manifest["files"]),"FRAME CANDIDATES 2","PIXEL EXACT",np.count_nonzero(diff)==0,"SCALES",scales)
