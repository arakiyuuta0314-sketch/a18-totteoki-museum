from pathlib import Path
import shutil
base=Path(r'C:\Users\User\source\repos\a18-entrance-art-polish-v03-20261026')
src=base/'entrance-rebuilt-background-panel-composite-v05-candidate'
v3=base/'entrance-art-polish-v03-20261026'
shutil.copy2(src/'candidate_off.png',src/'entrance_OFF.png')
shutil.copy2(src/'candidate_on.png',src/'entrance_ON.png')
shutil.copy2(v3/'entrance_ON.png',src/'previous_v03_ON.png')
shutil.copy2(v3/'entrance_OFF.png',src/'previous_v03_OFF.png')
s=(v3/'index.html').read_text(encoding='utf8')
s=s.replace('20261026v03','20261026v05')
s=s.replace('エントランス 木製額縁 ON/OFF','背面展示壁の拡幅試作 v05｜額縁 ON/OFF')
s=s.replace('正式素材の位置を変えずに、補修跡と木枠の明暗・木目を改良した比較候補。Lv.1は未決定。','建築構成を変更した検証用の試作です。背面2面を左右端へ広げ、外側の柱を移動。美術QA未合格のため正式採用しないでください。')
s=s.replace('</div>\n<div class="compare-title">','</div>\n<p style="font-size:12px;color:#ffd7a0">※ 試作中。木材の継ぎ目・外側柱・照明除去跡に未解決の美術課題があります。</p>\n<div class="compare-title">',1)
before='''<p class="info">背景・正式キャラクター・空き台紙・建築・照明条件は共通です。照明と隠れていた壁・受付周辺には元画像から推定修復した部分があり、美術監修待ちです。</p>'''
after='''<section style="margin-top:22px"><h2 style="font-size:15px">旧v03との構図比較</h2><div class="compare-grid"><figure><img src="previous_v03_ON.png?v=20261026v05" alt="旧v03の木枠あり構図"><figcaption>旧v03｜背面が中央寄り</figcaption></figure><figure><img src="entrance_ON.png?v=20261026v05" alt="新試作の背面展示を拡幅した構図"><figcaption>新v05｜左右端の柱</figcaption></figure></div></section><p class="info">正式キャラクターPNG・手前展示面・床・中央扉は既存のままです。背面柱と額縁の位置・幅は試作上の変更で、既存の正式承認ではありません。</p>'''
assert before in s
s=s.replace(before,after)
# The zoom images from v03 cannot represent the changed architecture. Remove old zoom section
a=s.index('<details id="zoomDetails"')
b=s.index('</details>',a)+len('</details>')
s=s[:a]+s[b:]
(src/'index.html').write_text(s,encoding='utf8')
print('WEB_CANDIDATE_PREPARED',len(s))
