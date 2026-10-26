from pathlib import Path
R=Path(r'C:\Users\User\source\repos\a18-entrance-plain-master-v06-20261026')
old=R/'entrance-plain-master-v08-right-frame'
d=R/'entrance-plain-master-v09-right-mat'
html=(old/'index.html').read_text(encoding='utf8')
changes={
 'v08':'v09',
 '20261026v08':'20261026v09',
 '右手前の木製額縁を復元':'右手前の欠けた台紙を修復',
 '修正後は49番の正式な木製額縁を四辺とも表示。右奥の柱を端まで伸ばしたv07建築はそのまま維持しています。':'右手前の台紙を49番の正式PNGで復元しました。OFF・ONのどちらも台紙が揃い、ONでは正式な木製額縁を追加します。右奥の柱はそのままです。',
 '額縁あり（修正後）':'台紙修復＋木枠 ON',
 '無装飾（OFF）':'台紙修復・木枠 OFF',
 '額縁なし｜無装飾の下地':'台紙あり｜木枠 OFF',
 '額縁あり｜修正後v09':'台紙と木枠｜ON',
 '右手前の額縁を拡大して確認':'台紙の欠けを修正前／後で拡大比較',
 '左がOFF、右がONです。画像をタップすると拡大できます。':'左が修正前v08、右が台紙修復後v09です。どちらも木製額縁ありで比較しています。',
 '右手前の額縁全体':'右手前の台紙全体',
 '上側・角の接合':'欠けていた台紙の左上',
 '下側の縁':'台紙の下側',
 'QA_right_front_comparison.png':'QA_before_after_whole.png',
 'QA_top_corner_comparison.png':'QA_before_after_top.png',
 'QA_lower_edge_comparison.png':'QA_before_after_bottom.png',
 '額縁以外はON/OFFで同一。無装飾版は消さずに維持しています。Lv.1デザイン・最終美術採用は未決定です。':'正式台紙はON/OFFで共通。木枠の有無のみが切替対象です。Lv.1デザイン・最終美術採用は未決定です。',
 '額縁あり｜修正後v08':'台紙修復＋額縁 ON',
 '右手前の額縁あり':'右手前の台紙修復と木枠あり',
 '表示中：右手前の木製額縁あり':'表示中：台紙修復済み＋木枠あり',
 '表示中：無装飾・木製額縁なし':'表示中：台紙修復済み・木枠なし',
 '右手前の額縁ありなし比較':'右手前の台紙修正前後比較',
 '額縁上部の接合比較':'欠けていた台紙上端の修復比較',
 '額縁下部の接合比較':'台紙下端の修復比較',
 'A18RightFrameV08':'A18RightMatV09'
}
for a,b in changes.items():
 if a in html:
  html=html.replace(a,b)
html=html.replace('<h2>左右に並べて比較</h2>','<h2>同じ背景で木製額縁だけ切替</h2>')
html=html.replace('<details id="zoom">','<details id="zoom" open>')
(d/'index.html').write_text(html,encoding='utf8')
qa=(old/'QA_browser_v08.cjs').read_text(encoding='utf8')
for a,b in [('18858','18859'),('A18RightFrameV08','A18RightMatV09'),('QA_A18_RIGHT_FRAME_V08_PASS','QA_A18_RIGHT_MAT_V09_PASS')]:
 qa=qa.replace(a,b)
(d/'QA_browser_v09.cjs').write_text(qa,encoding='utf8')
print('PAGE_AND_QA_V09_PREPARED',len(html),len(qa))
