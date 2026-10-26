from pathlib import Path
root=Path(r"C:\Users\User\source\repos\a18-entrance-art-polish-v03-20261026")
src=root/"entrance-wood-onoff-v02-20261026"/"index.html"
out=root/"entrance-art-polish-v03-20261026"/"index.html"
s=src.read_text(encoding="utf8").replace("20261026v02","20261026v03")
s=s.replace("既存の正式PNGから合成した2状態。どちらもLv.1未確定。","正式素材の位置を変えずに、補修跡と木枠の明暗・木目を改良した比較候補。Lv.1は未決定。")
s=s.replace(".info{margin-top:", """.zoom-details{margin-top:18px;border:1px solid var(--border);border-radius:12px;background:#202623;padding:12px}
.zoom-details summary{cursor:pointer;font-weight:700;color:#e9cfaa;list-style-position:inside}
.zoom-details .hint{font-size:12px;color:#bdc7bf;margin:5px 0 12px}
.zoom-details figure{margin:0 0 16px}
.zoom-details figcaption{text-align:left;margin-bottom:5px}
.zoom-details img{display:block;width:100%;height:auto;border-radius:8px;border:1px solid var(--border)}
.zoom-details a{display:block;color:inherit}
.info{margin-top:""")
part='''</section>
<details id="zoomDetails" class="zoom-details">
<summary>木製フレームの差を拡大（3か所）</summary>
<p class="hint">左がOFF・右がON。画像を押すとさらに大きく表示できます。</p>
<figure><figcaption>背面左｜最も見比べたい展示壁</figcaption><a href="QA_zoom_rear_left.png?v=20261026v03" target="_blank" rel="noopener"><img src="QA_zoom_rear_left.png?v=20261026v03" alt="背面左木製フレーム OFFとONの拡大比較" loading="lazy"></a></figure>
<figure><figcaption>背面右</figcaption><a href="QA_zoom_rear_right.png?v=20261026v03" target="_blank" rel="noopener"><img src="QA_zoom_rear_right.png?v=20261026v03" alt="背面右木製フレーム OFFとONの拡大比較" loading="lazy"></a></figure>
<figure><figcaption>右手前｜壁面基準のv07</figcaption><a href="QA_zoom_right_front.png?v=20261026v03" target="_blank" rel="noopener"><img src="QA_zoom_right_front.png?v=20261026v03" alt="右手前木製フレーム OFFとONの拡大比較" loading="lazy"></a></figure>
</details>
'''
assert s.count("</section>")==1
s=s.replace("</section>",part)
out.write_text(s,encoding="utf8")
print("WEB_GENERATED",out,out.stat().st_size)
