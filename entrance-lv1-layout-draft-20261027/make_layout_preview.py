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
for name,result in [('lv1_3frames_proposal_overlay.png',plan()),('lv1_3frames_passage_footprint.png',circulation())]:
    path=OUT/name; result.save(path,optimize=True)
    assert Image.open(path).size==(1322,1385)
    print('CREATED',path,path.stat().st_size)
print('APPROVED_BACKGROUND_SHA256',HASH)
