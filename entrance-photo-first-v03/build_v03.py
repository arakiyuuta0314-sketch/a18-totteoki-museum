# -*- coding: utf-8 -*-
"""Non-destructive upgrade of A18 photo-first v0.2 to art material v0.3.
Only a private comparison page is changed. Artwork windows and official sprites are immutable.
Fail on missing marker or duplicate replacement.
"""
from pathlib import Path
import hashlib
p=Path(__file__).with_name("index.html")
s=p.read_text(encoding="utf-8")
def change(a,b):
 global s
 n=s.count(a)
 if n!=1: raise RuntimeError(f"Expected one marker, found {n}: {a[:95]}")
 s=s.replace(a,b)
# Theme is more intimate, avoid palace styling.
change("<title>A18｜写真が主役のエントランス構図 A案</title>",
       "<title>A18｜写真が主役のエントランス 美術質感 v0.3</title>")
change("<h1>A案を「写真が主役」に再設計</h1>","<h1>A案｜写真が主役の美術・質感試作 v0.3</h1>")
change("正式キャラクター原本を合成。Lv.1／Lv.6、写真あり／空き枠を切り替えられる構図テストです。",
       "正式キャラクター原本を合成した、質感・額装・照明の改修比較です。写真あり／空枠・Lv.1／Lv.6を切替できます。")
change("豪華な建築そのものではなく、登録した写真が3枚並ぶ喜びを優先します。中央と左右の通路は残し、額縁の表示面積と鑑賞のしやすさを先に設計しました。",
       "採用済みv0.2の額縁3か所・通路・人物位置は変更しません。壁・床・額縁の材質や、写真を柔らかく照らす光だけを改善します。写真が背景に負けないかを比較する試作です。")
# New material definitions
defs=r'''
 <linearGradient id="frameMetal" x1="0" y1="0" x2="1" y2="1">
  <stop offset="0" stop-color="#e0c69a"/><stop offset=".23" stop-color="#b79a70"/>
  <stop offset=".49" stop-color="#8d704e"/><stop offset=".66" stop-color="#c5a97d"/>
  <stop offset="1" stop-color="#6f573e"/>
 </linearGradient>
 <linearGradient id="plasterFine" x1="0" y1="0" x2="1" y2=".9">
  <stop offset="0" stop-color="#efe6d8"/><stop offset=".45" stop-color="#dfd0bd"/>
  <stop offset="1" stop-color="#c9b7a0"/>
 </linearGradient>
 <linearGradient id="plinth" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0" stop-color="#745947"/><stop offset=".18" stop-color="#594436"/>
  <stop offset=".57" stop-color="#503d30"/><stop offset="1" stop-color="#3e3028"/>
 </linearGradient>
 <linearGradient id="marbleFine" x1="0" y1="0" x2=".25" y2="1">
  <stop offset="0" stop-color="#cbbba7"/><stop offset=".55" stop-color="#eadfcf"/>
  <stop offset="1" stop-color="#bfae97"/>
 </linearGradient>
 <radialGradient id="daylight" cx=".47" cy=".39" r=".67">
  <stop offset="0" stop-color="#fffbef" stop-opacity=".13"/>
  <stop offset="1" stop-color="#86735b" stop-opacity=".09"/>
 </radialGradient>
 <radialGradient id="spotWarm" cx=".5" cy=".12" r=".73">
  <stop offset="0" stop-color="#fff9e9" stop-opacity=".27"/>
  <stop offset=".72" stop-color="#f8e6c6" stop-opacity=".09"/>
  <stop offset="1" stop-color="#fff3dc" stop-opacity="0"/>
 </radialGradient>
 <filter id="softCast" x="-25%" y="-25%" width="160%" height="160%"><feGaussianBlur stdDeviation="4"/></filter>
 <filter id="subtleNoise" x="0" y="0" width="100%" height="100%">
  <feTurbulence type="fractalNoise" baseFrequency=".22" numOctaves="3" seed="14" stitchTiles="stitch"/>
  <feColorMatrix type="saturate" values="0"/>
 </filter>
 <pattern id="wainscot" width="43" height="23" patternUnits="userSpaceOnUse">
  <rect x="4" y="4" width="35" height="15" rx="1" fill="none" stroke="#baa083" stroke-width=".65" opacity=".5"/>
  <path d="M8 7H35V16H8Z" fill="#2b211c" opacity=".10"/>
 </pattern>
 <pattern id="marblefleck" width="82" height="63" patternUnits="userSpaceOnUse">
  <path d="M7 11Q29 7 51 23T79 25M11 43Q37 58 69 41" fill="none" stroke="#97816a" stroke-width=".5" opacity=".18"/>
  <path d="M15 40l4 2M61 10l6-2M43 37l5 2M8 59l3-1" stroke="#fff9e7" stroke-width="1.2" opacity=".26"/>
 </pattern>
 <pattern id="carpetweave" width="19" height="17" patternUnits="userSpaceOnUse">
  <path d="M2 4l2 2m6 3l-2 2m4-10l2 1m-6 10l1-1" stroke="#dbbdae" stroke-width=".65" opacity=".16"/>
 </pattern>
'''
change("</defs>",defs+"\n</defs>")
# Room materials are additive, behind the architecture and pictures.
finish=r'''
<!-- v0.3 / material finish, independently removable -->
<g id="baseFinish_v03">
 <rect x="0" y="0" width="546" height="230" fill="url(#plasterFine)" opacity=".45"/>
 <rect x="0" y="0" width="546" height="231" filter="url(#subtleNoise)" opacity=".055"/>
 <rect x="0" y="259" width="546" height="224" fill="url(#marbleFine)" opacity=".32"/>
 <rect x="0" y="259" width="546" height="224" fill="url(#marblefleck)"/>
 <rect x="0" y="259" width="546" height="224" filter="url(#subtleNoise)" opacity=".045"/>
 <rect x="0" y="0" width="546" height="483" fill="url(#daylight)"/>
 <!-- subtle carved cornice above the art -->
 <path d="M0 28H546" stroke="#8d7458" stroke-width="1" opacity=".65"/>
 <path d="M0 34H546" stroke="#f6eddf" stroke-width="3" opacity=".7"/>
 <path d="M0 77H546" stroke="#aa9276" stroke-width="1" opacity=".28"/>
 <!-- the art wall is a real material with quiet recessed panels -->
 <rect x="72" y="77" width="160" height="149" rx="1" fill="#bda88d" opacity=".36"/>
 <rect x="73" y="78" width="158" height="147" rx="1" fill="none" stroke="#fdf3e5" stroke-width="2" opacity=".56"/>
 <rect x="314" y="77" width="160" height="149" rx="1" fill="#bda88d" opacity=".36"/>
 <rect x="315" y="78" width="158" height="147" rx="1" fill="none" stroke="#fdf3e5" stroke-width="2" opacity=".56"/>
 <!-- work-supporting oak wainscoting with depth, not ornamental competition -->
 <rect x="0" y="234" width="546" height="26" fill="url(#plinth)" opacity=".71"/>
 <rect x="0" y="234" width="546" height="26" fill="url(#wainscot)" opacity=".45"/>
 <path d="M0 232H546" stroke="#b49b7d" stroke-width="3" opacity=".72"/>
 <path d="M0 259H546" stroke="#30261e" stroke-width="1.5" opacity=".75"/>
</g>
'''
change("<!-- Passage openings, never occluded by art -->",finish+"\n<!-- Passage openings, never occluded by art -->")
# Hall detail in exact pass openings, before the carpet/photo
hall=r'''
<g id="passagesFinish_v03">
 <!-- retain green-tinted depth but indicate passability with perspective thresholds -->
 <path d="M12 175H64 M9 202H66 M7 229H68" fill="none" stroke="#d0c7aa" stroke-width="1" opacity=".39"/>
 <path d="M483 175H535 M479 202H538 M477 229H540" fill="none" stroke="#d0c7aa" stroke-width="1" opacity=".39"/>
 <path d="M0 270L56 259M546 270L490 259" stroke="#f3dfc6" stroke-width="3" opacity=".6"/>
 <path d="M246 125H300M246 151H300M246 177H300M246 204H300M246 231H300" stroke="#d8cead" stroke-width="1.1" opacity=".38"/>
 <!-- pilaster lights / shadows, quiet and confined to the architecture -->
 <path d="M70 55H84V257H70" fill="none" stroke="#f5e5ce" stroke-width="2" opacity=".7"/>
 <path d="M461 55H475V257H461" fill="none" stroke="#f5e5ce" stroke-width="2" opacity=".7"/>
</g>
'''
change("<!-- Narrow unobtrusive central rug -->",hall+"\n<!-- Narrow unobtrusive central rug -->")
rug=r'''
<path d="M253 269H291L353 483H193Z" fill="url(#carpetweave)" opacity=".6"/>
<path d="M256 269H288L347 483H198Z" stroke="#dec9a7" stroke-width="1" opacity=".18" fill="none"/>
'''
change("<!-- Small architectural corners -->",rug+"\n<!-- Small architectural corners -->")
# Make frame metal a little varied rather than uniform mustard blocks.
change('<rect x="78" y="83" width="148" height="137" rx="2" fill="#9e865f"/>',
       '<rect x="78" y="83" width="148" height="137" rx="2" fill="url(#frameMetal)"/>')
change('<rect x="320" y="83" width="148" height="137" rx="2" fill="#9e865f"/>',
       '<rect x="320" y="83" width="148" height="137" rx="2" fill="url(#frameMetal)"/>')
change('<path d="M405 299 L530 306 V439 L405 426Z" fill="#baa47e"/>',
       '<path d="M405 299 L530 306 V439 L405 426Z" fill="url(#frameMetal)"/>')
# Add highlights that DO NOT overlap the actual artwork apertures.
bevel=r'''
<!-- Mouldings and picture-glass speculars, foreground separated from photo windows -->
<g id="frameDetails_v03" fill="none">
 <rect x="79.5" y="84.5" width="145" height="134" stroke="#eedcbd" stroke-width="1.5" opacity=".7"/>
 <rect x="85.5" y="90" width="135" height="125" stroke="#322822" stroke-width="1" opacity=".6"/>
 <path d="M79 84H225M79 84V219" stroke="#f3dfbb" stroke-width="1.5" opacity=".65"/>
 <path d="M225 84V218H80" stroke="#473725" stroke-width="1.5" opacity=".6"/>
 <rect x="321.5" y="84.5" width="145" height="134" stroke="#eedcbd" stroke-width="1.5" opacity=".7"/>
 <rect x="327.5" y="90" width="135" height="125" stroke="#322822" stroke-width="1" opacity=".6"/>
 <path d="M321 84H467M321 84V219" stroke="#f3dfbb" stroke-width="1.5" opacity=".65"/>
 <path d="M467 84V218H321" stroke="#473725" stroke-width="1.5" opacity=".6"/>
 <path d="M399 291L537 301M399 291V433" stroke="#ecd1a7" stroke-width="2" opacity=".6"/>
 <path d="M536 302V447L400 433" stroke="#37261c" stroke-width="1.5" opacity=".72"/>
 <path d="M407 301L529 308" stroke="#f1ddbb" stroke-width="1.3" opacity=".6"/>
</g>
<!-- Lamps illuminate the photograph, not the room's decorations -->
<g id="photoSpotlight_v03">
 <ellipse cx="152" cy="142" rx="90" ry="92" fill="url(#spotWarm)" opacity=".45" pointer-events="none"/>
 <ellipse cx="394" cy="142" rx="90" ry="92" fill="url(#spotWarm)" opacity=".45" pointer-events="none"/>
</g>
'''
change("<!-- Empty-wall framing markers -->",bevel+"\n<!-- Empty-wall framing markers -->")
# Quiet furniture details, add on top of furniture before detachable ornaments
counter=r'''
<!-- Subtle wood counter grain and protective glass; supports the butler -->
<g id="counterDetail_v03">
 <path d="M24 345L101 345M24 349L107 349" stroke="#b29677" stroke-width="1.1" opacity=".8"/>
 <path d="M32 356V392M100 356V392" stroke="#ae886a" stroke-width="1.2" opacity=".65"/>
 <rect x="47" y="367" width="27" height="13" rx="1" stroke="#b59571" stroke-width="1" fill="none" opacity=".64"/>
 <path d="M63 368V380" stroke="#9c7c5e" stroke-width=".9"/>
</g>
'''
change("<!-- Lv.6 add-ons: detachable independent layer and no overlap with display windows -->",
       counter+"\n<!-- Lv.6 add-ons: detachable independent layer and no overlap with display windows -->")
# Decorative items are detachable (the only color enrichment for Lv6); replacing original crude circles within same group.
change('<g fill="#59705b"><ellipse cx="35" cy="323" rx="22" ry="14"/><ellipse cx="30" cy="309" rx="18" ry="18"/><ellipse cx="355" cy="287" rx="17" ry="12"/><ellipse cx="364" cy="278" rx="13" ry="13"/></g>',
r'''<g stroke="#456451" stroke-width="1.1" fill="none">
  <path d="M32 336L29 308M31 336L18 319M30 331L46 313M358 298L355 276M355 297L370 283"/>
 </g>
 <g fill="#587866">
  <ellipse cx="27" cy="306" rx="10" ry="17" transform="rotate(-22 27 306)"/>
  <ellipse cx="19" cy="316" rx="12" ry="7" transform="rotate(21 19 316)"/>
  <ellipse cx="43" cy="315" rx="13" ry="8" transform="rotate(-25 43 315)"/>
  <ellipse cx="360" cy="274" rx="9" ry="15" transform="rotate(18 360 274)"/>
  <ellipse cx="368" cy="285" rx="11" ry="7" transform="rotate(-18 368 285)"/>
 </g>
 <g fill="#8fa382" opacity=".62"><ellipse cx="28" cy="300" rx="3" ry="10" transform="rotate(-22 28 300)"/><ellipse cx="359" cy="270" rx="3" ry="9"/></g>''')
# Frame metal glints slightly brighter on Lv6, removable independent group.
change('<path d="M0 273H546" stroke="#c7ad84" stroke-opacity=".34" stroke-width="1"/>',
       '<path d="M0 273H546" stroke="#c7ad84" stroke-opacity=".34" stroke-width="1"/>\n <path d="M83 86H219M325 86H461" stroke="#f5dfb7" stroke-opacity=".6" stroke-width="1.4"/>\n <path d="M418 304L524 310" stroke="#f5dfb7" stroke-opacity=".43" stroke-width="1.4"/>')
# Annotate correct art area and stage separation.
change("現在の3展示窓は試案として約", "3枠の表示位置・寸法を維持したまま質感を変えています。現在の3展示窓は試案として約")
change("Lv.1／Lv.6の切替は美術の構成比較であり", "Lv.1／Lv.6の切替は仮装飾の分離試験であり")
p.write_text(s,encoding="utf-8",newline="\n")
print("EDITED",p,"bytes",p.stat().st_size,"SHA256",hashlib.sha256(p.read_bytes()).hexdigest())
