"""Design-only overlay on actual approved A18 entrance background. Never edits source/game."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import hashlib, math
OUT=Path(__file__).resolve().parent
BASE=OUT.parent/'layout-test/assets/entrance/approved_initial_20261027/entrance_background_initial_approved.png'
FONT='C:/Windows/Fonts/meiryo.ttc'
assert BASE.is_file() and Path(FONT).is_file()
im=Image.open(BASE).convert('RGB')
assert im.size==(1322,1190)
HASH=hashlib.sha256(BASE.read_bytes()).hexdigest()
H=118  # Header above source image. Preview is not an asset replacement.
def f(n): return ImageFont.truetype(FONT,n)
def chip(d,x,y,s,size=28,color=(22,55,47,235)):
    font=f(size);r=d.textbbox((0,0),s,font=font)
    d.rounded_rectangle((x-14,y-10,x+r[2]+15,y+r[3]+19),radius=10,fill=color)
    d.text((x,y),s,font=font,fill='#fff9e9',stroke_width=0)
def dash(d,a,b,color=(61,182,139,255),width=6):
    dist=math.hypot(b[0]-a[0],b[1]-a[1])
    for t in range(0,int(dist),29):
        u=min(t+16,dist)
        start=tuple(a[j]+(b[j]-a[j])*t/dist for j in (0,1))
        end=tuple(a[j]+(b[j]-a[j])*u/dist for j in (0,1))
        d.line((*start,*end),fill=color,width=width)
def arr(d,a,b,color=(56,172,134,255)):
    d.line((*a,*b),fill=color,width=8)
    theta=math.atan2(b[1]-a[1],b[0]-a[0])
    for offset in [-0.55,0.55]:
        d.line((b[0]-22*math.cos(theta+offset),b[1]-22*math.sin(theta+offset),*b),fill=color,width=7)
def create(title):
    target=Image.new('RGBA',(1322,1385),'#f6eedf')
    target.paste(im,(0,H))
    d=ImageDraw.Draw(target)
    d.rectangle((0,0,1322,H),fill='#163830')
    d.text((38,12),title,font=f(51),fill='#fff6e7')
    d.text((41,76),'正式背景1322×1190を使用 ／ 既存背景・奥の額縁は一切変更しない',font=f(25),fill='#d6cbb4')
    d.rectangle((0,1308,1322,1385),fill='#f7f0e5')
    d.text((34,1327),'※ 色つきの面は配置検討用。壁・カウンターの完成素材ではありません。',font=f(27),fill='#503f2e')
    return target
def common(d):
    # Existing back 2 fixtures. Rectangle source: entrance-renderer.js PANELS (546x483).
    for x0,x1,s in [(104,458,'既存① 現状維持'),(906,1225,'既存② 現状維持')]:
        for x in range(x0,x1,26):
            d.line((x,159+H,min(x+14,x1),159+H),fill='#f7d48d',width=5)
            d.line((x,352+H,min(x+14,x1),352+H),fill='#f7d48d',width=5)
        for y in range(159+H,352+H,26):
            d.line((x0,y,x0,min(y+14,352+H)),fill='#f7d48d',width=5)
            d.line((x1,y,x1,min(y+14,352+H)),fill='#f7d48d',width=5)
        chip(d,x0+20,237+H,s,27,(45,41,34,224))
    # New upper side passages are requests: openings are not yet modeled.
    arr(d,(223,540+H),(0,540+H))
    arr(d,(1113,540+H),(1322,540+H))
    chip(d,21,452+H,'左上：通路予定',27,(22,87,72,235))
    chip(d,963,452+H,'右上：通路予定',27,(22,87,72,235))
def plan():
    target=create('配置イメージ｜横向きカウンター＋右展示壁・3枚')
    layer=Image.new('RGBA',target.size); d=ImageDraw.Draw(layer)
    common(d)
    S=lambda pts:[(x,y+H) for x,y in pts]
    # 90-degree turned left counter: staff faces right into central aisle.
    # Slim desk top runs back-to-front, like a horizontal reception counter
    # viewed from the side; avoid mistaking it for a standing upright column.
    d.polygon(S([(111,551),(193,525),(277,779),(186,816)]),fill=(239,197,119,231),outline=(77,49,27,255),width=8)
    d.polygon(S([(193,525),(277,779),(278,851),(193,602)]),fill=(147,91,47,203),outline=(72,42,23,255),width=8)
    d.polygon(S([(186,816),(277,779),(278,851),(186,895)]),fill=(123,75,39,226),outline=(72,42,23,255),width=8)
    d.polygon(S([(111,551),(186,816),(186,895),(111,622)]),fill=(111,74,42,211),outline=(72,42,23,255),width=7)
    # Front customer-facing vertical molding / side panel.
    d.line((209,610+H,261,788+H),fill=(222,179,95,238),width=7)
    d.ellipse((71,683+H,116,731+H),fill=(44,108,109,255),outline='white',width=5)
    chip(d,21,752+H,'爺や側',29)
    chip(d,308,704+H,'左：横向きカウンター',31,(92,60,36,239))
    chip(d,308,758+H,'受付面は右向き →',29,(92,60,36,235))
    # Right display fixture sits on measured registered photo plane frame-0-2.
    d.polygon(S([(987,451),(1218,542),(1218,845),(987,743)]),fill=(127,90,57,209),outline=(65,40,25,255),width=10)
    d.polygon(S([(1017,477),(1196,560),(1188,804),(1017,681)]),fill=(43,107,88,197),outline=(214,166,83,255),width=11)
    d.polygon(S([(1042,521),(1164,578),(1157,760),(1042,679)]),fill=(230,213,186,205),outline=(135,100,53,255),width=6)
    chip(d,817,921+H,'右：額縁③つき仕切り壁',29,(92,60,36,239))
    dash(d,(650,1185+H),(649,895+H),width=7)
    chip(d,429,1086+H,'中央歩行スペース',27,(23,85,69,238))
    return Image.alpha_composite(target,layer).convert('RGB')
def circulation():
    target=create('動線確認｜設備の占有範囲と上部左右の通路')
    layer=Image.new('RGBA',target.size);d=ImageDraw.Draw(layer)
    common(d); S=lambda pts:[(x,y+H) for x,y in pts]
    d.polygon(S([(90,536),(295,508),(310,907),(90,932)]),fill=(179,110,45,137),outline=(115,73,36,255),width=9)
    d.polygon(S([(963,444),(1237,532),(1237,853),(967,764)]),fill=(179,110,45,137),outline=(115,73,36,255),width=9)
    chip(d,111,952+H,'受付占有（仮）',32,(92,60,36,237))
    chip(d,817,890+H,'展示壁占有（仮）',30,(92,60,36,237))
    dash(d,(660,1180+H),(661,651+H),(37,166,118,255),width=9)
    arr(d,(657,681+H),(318,548+H))
    arr(d,(671,681+H),(970,546+H))
    chip(d,420,1035+H,'中央～左右へ回り込む想定',29)
    return Image.alpha_composite(target,layer).convert('RGB')
def new_counter_and_wall(angled=False,counter_vertical=False):
    """Keep source pixels exact; schematic colors only represent temporary equipment."""
    name=('C｜縦向きカウンター＋正面向き展示壁' if counter_vertical
          else 'B｜右仕切り壁を斜めにして通路を広めに' if angled
          else 'A｜真横カウンター＋正面向き展示壁')
    target=create(name)
    layer=Image.new('RGBA',target.size,(0,0,0,0))
    d=ImageDraw.Draw(layer)
    S=lambda pts:[(x,y+H) for x,y in pts]
    common(d)

    if counter_vertical:
        # The top runs straight from back to front, parallel to screen Y;
        # low legs and front panels read as a desk, not a standing divider.
        d.polygon(S([(136,568),(254,568),(265,869),(147,876)]),
                  fill=(242,196,114,230),outline=(85,55,29,255),width=8)
        d.polygon(S([(254,568),(265,869),(265,933),(254,635)]),
                  fill=(132,79,41,228),outline=(77,44,26,255),width=7)
        d.polygon(S([(147,876),(265,869),(265,933),(147,948)]),
                  fill=(112,68,38,233),outline=(77,44,26,255),width=8)
        d.polygon(S([(136,568),(147,876),(147,948),(136,642)]),
                  fill=(105,64,38,211),outline=(77,44,26,255),width=7)
        d.line((254,660+H,264,839+H),fill=(221,176,105,240),width=5)
        # Staff stands left of desk, while customers approach from right.
        d.ellipse((64,680+H,111,727+H),fill=(50,105,110,255),
                  outline=(244,241,216,255),width=5)
        chip(d,24,747+H,'爺や側（仮）',size=26,color=(30,88,88,235))
        chip(d,288,736+H,'左｜縦向きカウンター',size=30,color=(94,57,33,242))
        chip(d,288,785+H,'受付面は右側 →',size=27,color=(94,57,33,238))
    else:
        # Existing A/B: desk is parallel to the back wall; visitor stands in front.
        d.polygon(S([(95,669),(461,669),(500,713),(132,713)]),
                  fill=(241,194,109,233),outline=(84,54,30,255),width=8)
        d.polygon(S([(132,713),(500,713),(500,806),(132,806)]),
                  fill=(132,79,41,231),outline=(78,43,22,255),width=9)
        d.polygon(S([(95,669),(132,713),(132,806),(95,760)]),
                  fill=(90,57,34,228),outline=(78,43,22,255),width=8)
        for x0,x1 in [(155,281),(307,474)]:
            d.rectangle((x0,732+H,x1,786+H),outline=(228,174,98,255),width=5)
        d.ellipse((255,608+H,302,655+H),fill=(50,105,110,255),
                  outline=(244,241,216,255),width=5)
        chip(d,303,572+H,'爺や側（位置は仮）',size=25,color=(30,88,88,235))
        chip(d,49,840+H,'左｜受付カウンターを真横に配置',size=29,color=(94,57,33,242))
    # Right fixture plane: compare full front-facing and a compact angle.
    if not angled:
        d.polygon(S([(900,628),(1220,628),(1238,648),(917,648)]),
                  fill=(239,199,119,225),outline=(66,42,26,255),width=7)
        d.polygon(S([(917,648),(1238,648),(1238,910),(917,910)]),
                  fill=(125,86,53,219),outline=(70,43,25,255),width=9)
        d.polygon(S([(950,678),(1207,678),(1207,865),(950,865)]),
                  fill=(30,98,83,213),outline=(208,155,72,255),width=9)
        d.rectangle((973,701+H,1183,844+H),fill=(235,219,190,226),
                    outline=(173,123,60,255),width=7)
        chip(d,782,948+H,'右｜正面向き・幅広',size=29,color=(95,60,33,239))
    else:
        # The diagonal version uses a compact projection and keeps more of the
        # upper-right approach unobstructed. Not a measured collision clearance.
        d.polygon(S([(974,637),(1213,679),(1228,695),(990,654)]),
                  fill=(239,199,119,225),outline=(66,42,26,255),width=7)
        d.polygon(S([(990,654),(1228,695),(1220,923),(985,853)]),
                  fill=(127,86,52,215),outline=(70,43,25,255),width=9)
        d.polygon(S([(1013,684),(1205,721),(1198,883),(1008,824)]),
                  fill=(30,98,83,213),outline=(208,155,72,255),width=9)
        d.polygon(S([(1032,711),(1182,745),(1177,859),(1028,808)]),
                  fill=(235,219,190,226),outline=(173,123,60,255),width=7)
        chip(d,786,958+H,'右｜やや斜め・コンパクト',size=29,color=(95,60,33,239))
    # There is still a central corridor around both movable fixtures.
    dash(d,(681,1177+H),(681,754+H),color=(38,164,113,244),width=7)
    arr(d,(685,754+H),(736,558+H),color=(33,156,110,252))
    arr(d,(736,558+H),(1224,531+H),color=(33,156,110,252))
    arr(d,(735,558+H),(72,542+H),color=(33,156,110,252))
    chip(d,481,1045+H,'中央通路 → 奥で左右へ',size=25,
         color=(20,95,73,240))
    return Image.alpha_composite(target,layer).convert('RGB')

def side_by_side():
    from PIL import ImageOps
    left=Image.open(OUT/'lv1_horizontal_counter_front_wall.png').convert('RGB')
    right=Image.open(OUT/'lv1_horizontal_counter_angled_wall.png').convert('RGB')
    # Maintain the full backgrounds and geometry; only scale for comparison.
    w,h=735,770
    a=ImageOps.contain(left,(w,h),method=Image.Resampling.LANCZOS)
    b=ImageOps.contain(right,(w,h),method=Image.Resampling.LANCZOS)
    out=Image.new('RGB',(w*2+42,h+135),'#f3eddf')
    for n,img in enumerate([a,b]):
        x=12+n*(w+18)
        out.paste(img,(x,64))
    dr=ImageDraw.Draw(out)
    dr.rectangle((0,0,out.width,52),fill='#183a31')
    dr.text((20,8),'Lv.1｜右壁 正面 vs 斜め',font=f(29),fill='#fff8e7')
    dr.text((24,h+86),'どちらも左の受付は真横。右仕切り壁だけを比較。寸法・通路は仮。',font=f(21),fill='#574630')
    out.save(OUT/'lv1_wall_angle_comparison.jpg',quality=88,optimize=True)

def compare_counter_orientation():
    from PIL import ImageOps
    names=['lv1_horizontal_counter_front_wall.png','lv1_vertical_counter_front_wall.png']
    w,h=735,770
    imgs=[ImageOps.contain(Image.open(OUT/name).convert('RGB'),(w,h),
                           method=Image.Resampling.LANCZOS) for name in names]
    out=Image.new('RGB',(w*2+42,h+135),'#f3eddf')
    for k,img in enumerate(imgs):
        out.paste(img,(12+k*(w+18),64))
    dr=ImageDraw.Draw(out)
    dr.rectangle((0,0,out.width,52),fill='#183a31')
    dr.text((20,8),'Lv.1｜左の受付カウンター 真横 vs 縦向き',font=f(29),fill='#fff8e7')
    dr.text((24,h+86),'右の展示壁は両方とも正面向き。受付の向きだけを比較。寸法・通路は仮。',font=f(20),fill='#574630')
    out.save(OUT/'lv1_counter_orientation_comparison.jpg',quality=88,optimize=True)

for name,result in [('lv1_3frames_proposal_overlay.png',plan()),('lv1_3frames_passage_footprint.png',circulation()),
                    ('lv1_horizontal_counter_front_wall.png',new_counter_and_wall(False)),
                    ('lv1_horizontal_counter_angled_wall.png',new_counter_and_wall(True)),
                    ('lv1_vertical_counter_front_wall.png',new_counter_and_wall(counter_vertical=True))]:
    path=OUT/name; result.save(path,optimize=True)
    assert Image.open(path).size==(1322,1385)
    print('CREATED',path,path.stat().st_size)
for name in ('lv1_horizontal_counter_front_wall','lv1_horizontal_counter_angled_wall',
             'lv1_vertical_counter_front_wall'):
    src=Image.open(OUT/(name+'.png')).convert('RGB')
    src.thumbnail((1040,1110))
    jpeg=OUT/(name+'.jpg')
    src.save(jpeg,quality=84,optimize=True)
    assert jpeg.is_file() and Image.open(jpeg).size[0]<=1040
    print('PHONE_PREVIEW',jpeg,jpeg.stat().st_size)
side_by_side()
compare_counter_orientation()
assert (OUT/'lv1_wall_angle_comparison.jpg').is_file()
assert (OUT/'lv1_counter_orientation_comparison.jpg').is_file()
print('SIDE_BY_SIDE',OUT/'lv1_wall_angle_comparison.jpg')
print('COUNTER_ORIENTATION_COMPARISON',OUT/'lv1_counter_orientation_comparison.jpg')
print('APPROVED_BACKGROUND_SHA256',HASH)
