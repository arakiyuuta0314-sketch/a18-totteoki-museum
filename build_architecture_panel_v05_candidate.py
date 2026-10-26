# -*- coding:utf-8 -*-
from pathlib import Path
import numpy as np,cv2,json,hashlib
from PIL import Image
root=Path(r'C:\Users\User\source\repos\a18-entrance-art-polish-v03-20261026')
old=root/'entrance-art-polish-v03-20261026'
out=root/'entrance-rebuilt-background-panel-composite-v05-candidate'
out.mkdir(exist_ok=True)
H,W=483,546
off=np.asarray(Image.open(old/'entrance_OFF.png').convert('RGB'))
on=np.asarray(Image.open(old/'entrance_ON.png').convert('RGB'))
drive=Path(r'G:\マイドライブ\06.アプリ開発\03.開発・テスト\A18_パズル美術館')
mask=np.zeros((H,W),np.uint8)
for num,names in [(27,['entrance_fg_right_display_wall.png']),
                  (32,['entrance_left_foreground_wall.png','entrance_left_foreground_rail.png']),
                  (39,['entrance_fg_right_rail.png'])]:
 folder=next(d for d in drive.iterdir() if d.name.startswith(f'{num}_'))
 for name in names:
  a=np.asarray(Image.open(folder/name).convert('RGBA').getchannel('A'))
  mask=cv2.max(mask,a)
def stretch(piece,width):
 h=piece.shape[0]
 return cv2.resize(piece,(width,h),interpolation=cv2.INTER_CUBIC)
def design(src):
 p=src.copy()
 # Background upper beams below ceiling, replace abandoned outer capitals in
 # their original positions using intact neighboring header trim texture.
 for l,r,dl,dr in ((34,69,83,117),(481,521,435,474)):
  p[:35,l:r]=stretch(src[:35,dl:dr],r-l)
 # Larger exhibition field and frames use ORIGINAL photographic green/white
 # source samples from the uncovered rear-left wall, across both wings.
 upper=src[35:166,75:207].copy()
 p[35:166,28:211]=stretch(upper,183)
 p[35:166,354:519]=np.flip(stretch(upper,165),axis=1)
 # Architectural wooden wainscot behind expanded exhibitions, sampled from
 # original unobstructed x116..207 and mirrored symmetrically.
 wood_lower=src[166:212,117:208].copy()
 p[166:212,28:211]=stretch(wood_lower,183)
 p[166:212,354:519]=np.flip(stretch(wood_lower,165),axis=1)
 # Place existing formal architectural columns at both EXTREME edges.
 p[:212,0:30]=stretch(src[:212,36:65],30)
 p[:212,516:546]=stretch(src[:212,489:518],30)
 # Keep already-separated foreground EXACT: no stretched extra rail / wall.
 q=mask>6
 p[q]=src[q]
 return p
new0=design(off);new1=design(on)
for nm,ar in [('candidate_off.png',new0),('candidate_on.png',new1),('QA_old_vs_new.png',np.concatenate([on,new0,new1],axis=1))]:
 Image.fromarray(ar).save(out/nm,optimize=True)
for region,box in {'floor':(115,243,391,483),'characters':(100,315,318,373),'door':(236,42,333,211),'counter':(0,322,111,445),'right_foreground':(394,221,546,424)}.items():
 l,t,r,b=box
 assert np.array_equal(new0[t:b,l:r],off[t:b,l:r]),region
manifest={
 'status':'candidate_technical_only_visual_review_required',
 'source':'v03 (26b2466)', 'image_generation':False,
 'canvas':[W,H],
 'backwall_left':[28,211],'backwall_right':[354,519],
 'column_extremes':[[0,30],[516,546]],
 'independently_recropped_underlying_panels':True,
 'foreground_preserved_pixels':int((mask>6).sum()),
 'floor_door_reception_people_preserved':True,
 'ON_diff_pixels':int(np.any(new0!=new1,axis=2).sum()),
 'unresolved':'Photographic texture stretch, lighting bakes and lower wood-panel seams require user design acceptance',
 'source_sha256':{n:hashlib.sha256((old/n).read_bytes()).hexdigest() for n in ('entrance_OFF.png','entrance_ON.png')}
}
(out/'QA_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf8')
print('V05_CANDIDATE_RENDERED',json.dumps(manifest,ensure_ascii=True)[:650])
