from pathlib import Path
import shutil
R=Path(__file__).resolve().parent
O=R/"entrance-wall-plane-v07-20261026"
OLD=R/"entrance-canonical-single-H-v06-20261026"
assert (O/"view_wood_empty_100.png").is_file()
shutil.copy2(OLD/"view_wood_empty_100.png",O/"QA_previous_v06_wood_empty.png")
shutil.copy2(OLD/"QA_browser_v06.cjs",O/"QA_browser_v07.cjs")
browser=(O/"QA_browser_v07.cjs").read_text(encoding="utf-8")
browser=browser.replace("A18_SINGLE_H_URL","A18_WALL_PLANE_URL")
browser=browser.replace("entrance-canonical-single-H-v06-20261026","entrance-wall-plane-v07-20261026")
browser=browser.replace("V06_BROWSER_PASS","V07_BROWSER_PASS")
(O/"QA_browser_v07.cjs").write_text(browser,encoding="utf-8")
t=(OLD/"index.html").read_text(encoding="utf-8")
t=t.replace("v06","v07").replace("v05","v06").replace("V06","V07")
t=t.replace("1つの射影変換で額縁・台紙・写真を統一","壁面を基準に額縁・台紙・写真を再投影")
t=t.replace("右手前の額縁と台紙を、同じ角度に統一しました","右手前の壁面に、額縁と台紙の角度を合わせました")
t=t.replace("正面の共通額縁を、1つの射影変換で右手前に配置しています。木製・金額縁だけでなく、台紙・写真・写真窓も同じ変換です。",
"背景画像の緑の展示壁から壁面四隅を計測して基準にしました。正面素材の木製・金縁・台紙・写真窓を、その壁面内で同じ変換により表示します。")
t=t.replace("新方式の木製額縁・台紙・写真窓が揃ったA18エントランス","壁面に揃えた木製額縁・台紙・写真窓のA18エントランス")
t=t.replace("QA_previous_v06_wood_empty.png", "QA_previous_v06_wood_empty.png")
t=t.replace("元の右手前の豪華な金額縁を画素単位で再現したものではありません。",
"壁面の四隅は原画の建築線から推定した座標であり、最終美術判断は未承認です。元の右手前の豪華な金額縁を画素単位で再現したものではありません。")
t=t.replace("今回 v07</figcaption>","壁面基準 v07</figcaption>")
t=t.replace("<p class=\"note\">",'''<h2>壁面を基準にした位置合わせ</h2>
<div class="stage"><img src="QA_wall_plane_and_derived_display_outer.png" loading="lazy" width="546" height="483" alt="元の壁面の四隅とその内部に合わせた新しい額縁の位置"></div>
<p class="note">水色は壁面の推定四隅、赤色はそこから自動計算した額縁の位置です。建築形状は修正していません。</p>
<p class="note">''')
assert "QA_previous_v06_wood_empty.png" in t
(O/"index.html").write_text(t,encoding="utf-8")
print("UI_QA_READY")
