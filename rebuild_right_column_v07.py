# -*- coding: utf-8 -*-
"""A18 entrance architecture v07: continuous full-width right corner column.

Authoritative base is v06 undecorated image. Copy actual existing left corner
column, mirror into image x=513..545; no generative art or new geometry.
Preserve real right-foreground exhibition-wall/rail alpha exactly.
"""
from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib,cv2
BASE=Path(__file__).resolve().parent
PREV=BASE/'entrance-plain-master-v06-study'
OUT=BASE/'entrance-plain-master-v07-right-column'
OUT.mkdir(exist_ok=True)
orig=np.asarray(Image.open(PREV/'entrance_OFF.png').convert('RGB'))
assert orig.shape==(483,546,3)
root=Path(r'G:\マイドライブ\06.アプリ開発\03.開発・テスト\A18_パズル美術館')
occlusion=np.zeros(orig.shape[:2],np.uint8)
files={}
for foldernum,name in [(27,'entrance_fg_right_display_wall.png'),(39,'entrance_fg_right_rail.png')]:
 d=next(p for p in root.iterdir() if p.is_dir() and p.name.startswith(str(foldernum)+'_'))
 path=d/name
 overlay=Image.open(path).convert('RGBA')
 assert overlay.size==(546,483)
 a=np.asarray(overlay.getchannel('A'))
 occlusion=np.maximum(occlusion,a)
 files[name]=hashlib.sha256(path.read_bytes()).hexdigest()
# Match leftmost column's EXACT original 33-pixel silhouette, not stretched.
# Source x=0..32, flipped so its inner edge is at x=513, exterior at x=545.
new=orig.copy()
mirror=orig[:213,:33,:][:,::-1,:]
orig_roi=orig[:213,513:546,:]
vis=occlusion[:213,513:546] > 4
target=orig_roi.copy()
target[~vis]=mirror[~vis]
new[:213,513:546]=target
# QA: intersection with actual foreground cannot change.
assert np.array_equal(new[:213,513:546][vis],orig_roi[vis])
assert np.array_equal(new[:213,:513],orig[:213,:513])
assert np.array_equal(new[213:],orig[213:])
assert np.array_equal(new[42:213,236:333],orig[42:213,236:333])
change=np.any(new!=orig,axis=2)
allowed=np.zeros((483,546),bool);allowed[:213,513:546]=True
assert not np.any(change&~allowed)
assert int(change.sum())>1000
# Source consistency: no resampling or synthetic texture.
assert np.array_equal(new[:213,513:546][~vis],mirror[~vis])
Image.fromarray(new,'RGB').save(OUT/'entrance_OFF.png',optimize=True)
Image.fromarray(orig,'RGB').save(OUT/'reference_v06_OFF.png',optimize=True)
Image.fromarray(change.astype(np.uint8)*255,'L').save(OUT/'QA_modified_pixel_mask.png')
Image.fromarray(occlusion,'L').save(OUT/'QA_foreground_occlusion_alpha.png')
dual=Image.new('RGB',(1092,483))
dual.paste(Image.fromarray(orig,'RGB'),(0,0))
dual.paste(Image.fromarray(new,'RGB'),(546,0))
dual.save(OUT/'QA_v06_vs_v07_full.png',optimize=True)
for name,area in {'right_corner':(375,0,546,218),'right_capital':(475,0,546,115),'left_reference':(0,0,74,215),'right_seam':(483,119,546,214)}.items():
 l,t,r,b=area
 size=((r-l)*3,(b-t)*3)
 trip=Image.new('RGB',(size[0]*2,size[1]))
 for i,src in enumerate((orig,new)):
  patch=Image.fromarray(src,'RGB').crop(area).resize(size,Image.Resampling.NEAREST)
  trip.paste(patch,(i*size[0],0))
 trip.save(OUT/('QA_'+name+'_before_after.png'))
report={
 'version':'v07','status':'art_review_pending',
 'source':'v06 undecorated base commit 4f80b69','canvas':[546,483],
 'authoritative_OFF_v06_sha256':hashlib.sha256((PREV/'entrance_OFF.png').read_bytes()).hexdigest(),
 'right_column_position':[513,0,546,213],'left_existing_column_source':[0,0,33,213],
 'method':'exact horizontal mirror without interpolation; official right foreground alpha occlusion protected',
 'foreground_mask_source_hashes':files,'changed_pixels':int(change.sum()),
 'outside_declared_right_corner_change':int((change&~allowed).sum()),
 'foreground_occlusion_change_count':int(np.any((new[:213,513:546]!=orig_roi)[vis],axis=1).sum()),
 'door_floor_characters_and_front_walls_unchanged':True,
 'picture_mats_unchanged':True,'new_image_generation':False,'level1_approved':False,
 'notes':'This fixes only the far right architectural corner pillar. Broader backdrop lighting/wood seams remain v06 and require art review.'
}
(OUT/'QA_manifest.json').write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf8')
print('V07_RIGHT_COLUMN_BUILD_PASS',json.dumps({x:report[x] for x in ('changed_pixels','outside_declared_right_corner_change','foreground_occlusion_change_count')},ensure_ascii=False))
