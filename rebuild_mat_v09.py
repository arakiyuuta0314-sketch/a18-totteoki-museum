# -*- coding: utf-8 -*-
"""A18 v09: restore formal empty picture mat on right-front exhibition wall.
Both OFF and ON include registered matte; ON additionally includes formal wood frame.
All existing 546x483 architecture and rear right pillar are preserved exactly outside matte/frame.
"""
from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,hashlib,json,shutil
R=Path(__file__).resolve().parent
PREV=R/'entrance-plain-master-v08-right-frame'
OUT=R/'entrance-plain-master-v09-right-mat'
OUT.mkdir(exist_ok=True)
LIB=Path(r'G:\マイドライブ\06.アプリ開発\03.開発・テスト\A18_パズル美術館')
D49=next(p for p in LIB.iterdir() if p.is_dir() and p.name.startswith('49_'))
size=(546,483)
def load(p):return Image.open(p).convert('RGBA')
def h(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
base=load(PREV/'entrance_OFF.png')
mat=load(D49/'right_front_content_empty.png')
wood=load(D49/'right_front_frame_wood.png')
win=np.asarray(Image.open(D49/'right_front_shared_window_mask.png').convert('L'))>0
assert base.size==mat.size==wood.size==size
mat_area=np.asarray(mat.getchannel('A'))>0
frame_area=np.asarray(wood.getchannel('A'))>0
assert np.array_equal(mat_area,win),"actual projected paper is not equal to photo window"
assert not np.any(frame_area&mat_area),"wood and matte overlap"
assert int(mat_area.sum())>6000 and int(frame_area.sum())>3000

OFF=Image.alpha_composite(base,mat)
ON=Image.alpha_composite(OFF,wood)
off_rgb=np.asarray(OFF.convert('RGB'))
on_rgb=np.asarray(ON.convert('RGB'))
old_off=np.asarray(base.convert('RGB'))
old_on=np.asarray(load(PREV/'entrance_ON.png').convert('RGB'))
paper_delta=np.any(off_rgb!=old_off,axis=2)
wood_delta=np.any(on_rgb!=off_rgb,axis=2)
oldon_to_newon=np.any(on_rgb!=old_on,axis=2)
assert not np.any(paper_delta&~mat_area),"OFF modified non-paper pixels"
assert not np.any(wood_delta&~frame_area),"ON modified non-frame pixels"
assert not np.any(oldon_to_newon&~mat_area),"v08 ON to v09 ON modified outside mat"
assert np.array_equal(on_rgb[0:157],old_on[0:157]),"ceiling or rear panels touched"
assert np.array_equal(on_rgb[370:],old_on[370:]),"floor or characters touched"
assert np.array_equal(off_rgb[:213,513:546],old_off[:213,513:546]),"right rear pillar touched"
print('ACTUAL_WINDOW_CORRECTION_PIXELS',int(np.count_nonzero(paper_delta)))
assert np.count_nonzero(paper_delta)>0
# Both ON/OFF exact pixel same except frame alpha.
assert np.all((on_rgb==off_rgb) | frame_area[...,None])
Image.fromarray(off_rgb,'RGB').save(OUT/'entrance_OFF.png',optimize=True)
Image.fromarray(on_rgb,'RGB').save(OUT/'entrance_ON.png',optimize=True)
mat.save(OUT/'right_front_content_empty_formal_v07.png',optimize=True)
wood.save(OUT/'right_front_frame_wood_formal_v07.png',optimize=True)
shutil.copy2(PREV/'entrance_ON.png',OUT/'reference_v08_ON.png')
shutil.copy2(PREV/'entrance_OFF.png',OUT/'reference_v08_OFF.png')
Image.fromarray(np.uint8(paper_delta)*255,'L').save(OUT/'QA_paper_restored_pixels.png')
Image.fromarray(np.uint8(wood_delta)*255,'L').save(OUT/'QA_frame_switch_pixels.png')
Image.fromarray(np.uint8(mat_area)*255,'L').save(OUT/'QA_photo_window_mask.png')
# Exact before/after closeups; no photomanipulation
roi=(391,149,531,383)
w=(roi[2]-roi[0])*3;hh=(roi[3]-roi[1])*3
variants=[('v08 OFF / damaged',old_off),('v08 ON / damaged',old_on),
          ('v09 OFF / paper fixed',off_rgb),('v09 ON / paper+frame',on_rgb)]
contact=Image.new('RGB',(w*4,hh+30),(21,24,23))
d=ImageDraw.Draw(contact)
for idx,(label,img) in enumerate(variants):
 x=idx*w
 contact.paste(Image.fromarray(img,'RGB').crop(roi).resize((w,hh),Image.Resampling.NEAREST),(x,30))
 d.text((x+5,6),label,fill=(239,228,199))
contact.save(OUT/'QA_four_states_detail.png',optimize=True)
for label,area in [('whole',(394,156,531,378)),('top',(418,177,501,240)),('bottom',(417,280,511,368))]:
 left,top,right,bottom=area
 width=3*(right-left);height=3*(bottom-top)
 board=Image.new('RGB',(2*width,height))
 for i,ar in enumerate((old_on,on_rgb)):
  board.paste(Image.fromarray(ar,'RGB').crop(area).resize((width,height),Image.Resampling.NEAREST),(i*width,0))
 board.save(OUT/('QA_before_after_'+label+'.png'),optimize=True)
board=Image.new('RGB',(1092,483))
board.paste(Image.fromarray(off_rgb,'RGB'),(0,0));board.paste(Image.fromarray(on_rgb,'RGB'),(546,0))
board.save(OUT/'QA_OFF_ON_full.png',optimize=True)
report={
 'version':'v09','status':'technical_pass_art_review_pending','canvas':[546,483],
 'base':'v08 OFF / v07 architecture from existing original PNG','no_image_generation':True,
 'registered_photo_mat_from':'49/right_front_content_empty.png',
 'wood_from':'49/right_front_frame_wood.png',
 'window_from':'49/right_front_shared_window_mask.png',
 'photo_mat_pixels':int(mat_area.sum()), 'frame_alpha_pixels':int(frame_area.sum()),
 'replaced_wrong_old_mat_pixels_OFF':int(paper_delta.sum()),
 'v08_ON_to_v09_ON_changes':int(oldon_to_newon.sum()),
 'changed_OUTSIDE_photo_window_from_v08':int(np.sum(oldon_to_newon&~mat_area)),
 'ON_OFF_changes':int(wood_delta.sum()),
 'ON_OFF_changes_OUTSIDE_frame':int(np.sum(wood_delta&~frame_area)),
 'frame_mat_alpha_overlap':int(np.sum(frame_area&mat_area)),
 'registered_matte_window_alpha_exact':True,
 'right_rear_column_unchanged':True,'characters_unchanged':True,'game_integrated':False,'level1_decided':False,
 'source_SHA256':{
 'v08_off':h(PREV/'entrance_OFF.png'),
 'v08_on':h(PREV/'entrance_ON.png'),
 'mat':h(D49/'right_front_content_empty.png'),
 'frame':h(D49/'right_front_frame_wood.png'),
 'window_mask':h(D49/'right_front_shared_window_mask.png')},
 'known_art_issue':'original wall and lighting overall not fully approved; this patch fixes registered paper only'}
(OUT/'QA_manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print('BUILD_V09_PAPER_FIX_PASS',json.dumps({k:report[k] for k in ('photo_mat_pixels','frame_alpha_pixels','replaced_wrong_old_mat_pixels_OFF','v08_ON_to_v09_ON_changes','changed_OUTSIDE_photo_window_from_v08','ON_OFF_changes_OUTSIDE_frame','frame_mat_alpha_overlap')}))
