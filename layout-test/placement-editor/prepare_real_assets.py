"""Build editor-only, transparent previews from the two user-selected original image assets.
Originals on Google Drive are read-only. Do not treat derived images as final game assets.
"""
from PIL import Image
from pathlib import Path
import hashlib, random
SRC=Path(r"G:\マイドライブ\06.アプリ開発\03.開発・テスト\A18_パズル美術館\65_配置エディター実素材_20261027")
DEST=Path(__file__).resolve().parent
for name in ("counter_original.png","wall_original.png"):
    src=SRC/name
    assert src.is_file(), src
    im=Image.open(src).convert("RGBA")
    print("INPUT",name,im.size,src.stat().st_size,hashlib.sha256(src.read_bytes()).hexdigest())
    assert im.size==(1086,1448)
    alpha=im.getchannel("A")
    alpha=alpha.point(lambda v:0 if v<30 else v)
    im.putalpha(alpha)
    if name=="counter_original.png":
        cropped=im.crop((0,0,1050,1434))
        # Reduce outer transparent margin without altering architecture geometry.
        box=cropped.getchannel("A").getbbox()
        cropped=cropped.crop(box)
        target=cropped.copy()
        target.thumbnail((490,690),Image.Resampling.LANCZOS)
        out=DEST/"counter-real.webp"
        target.save(out,format="WEBP",quality=90,method=3)
    else:
        # The user asked for a frame/mat-FREE right wall. Keep columns/woodwork
        # from actual generated original, replace ONLY center artwork area with
        # color interpolated from the original green panels at same height.
        # Original remains untouched on Drive, and is retained as source for QA.
        px=im.load()
        rng=random.Random(20261027)
        for y in range(323,904):
            l=im.getpixel((278,y))
            rr=im.getpixel((815,y))
            # Horizontal wall tint and micro-texture (does not invent columns).
            for x in range(345,742):
                t=(x-345)/(742-345)
                nr=[]
                for c in range(3):
                    v=int(l[c]*(1-t)+rr[c]*t +rng.randint(-2,2))
                    nr.append(max(0,min(255,v)))
                # Feather to unedited side/top/bottom of the original material.
                edge=min(x-345,741-x,y-323,903-y)
                feather=max(0,min(1,edge/14))
                if feather<1:
                    old=px[x,y]
                    nr=[int(old[c]*(1-feather)+nr[c]*feather) for c in range(3)]
                px[x,y]=(*nr,255)
        box=im.getchannel("A").getbbox()
        cropped=im.crop(box)
        target=cropped.copy()
        target.thumbnail((560,720),Image.Resampling.LANCZOS)
        out=DEST/"wall-real-noframe.webp"
        target.save(out,format="WEBP",quality=89,method=3)
    test=Image.open(out)
    assert test.size[0]>=300 and test.mode in ("RGBA","RGB")
    assert out.stat().st_size>20000
    print("OUTPUT",out.name,test.size,out.stat().st_size,Image.open(out).getchannel('A').getbbox() if 'A' in test.getbands() else 'NA')
