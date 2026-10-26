# -*- coding: utf-8 -*-
from pathlib import Path
from shutil import copy2
BASE=Path(__file__).resolve().parent
OLD=BASE/'entrance-plain-master-v06-study'
NEW=BASE/'entrance-plain-master-v07-right-column'
source=(OLD/'index.html').read_text(encoding='utf8')
rep={
 "A18 無装飾エントランス背景 v06｜再構築試作":"A18 無装飾エントランス背景 v07｜右端の柱修正",
 "エントランス背景の再構築 v06":"エントランス背景・右奥の柱 v07",
 "旧v05の拡幅構図をもとに、天井材と左右の緑壁面を再構築した試作です。木製額縁・植物・壁灯・カーペットは追加しません。美術承認前です。":"無装飾のv06背景はそのままに、右奥の細い柱を左奥と同じ幅の柱に改め、右端へ配置しました。木製額縁などの装飾は追加していません。",
 "新・無装飾 v06":"修正後 v07","旧・拡幅 v05":"修正前 v06",
 "reference_v05_OFF.png":"reference_v06_OFF.png",
 "20261026v06":"20261026v07",
 "旧 v05（修正前）":"旧 v06（修正前）",
 "新 v06（無装飾基準の試作）":"新 v07（右端の柱を修正）",
 "天井・背面左右を拡大して確認":"右端の柱を拡大して確認",
 "天井｜左：旧、右：新":"右端全体｜左：旧、右：新",
 "背面左｜左：旧、右：新":"柱頭｜左：旧、右：新",
 "背面右｜左：旧、右：新":"柱と手前の展示壁｜左：旧、右：新",
 "QA_ceiling_before_after.png":"QA_right_corner_before_after.png",
 "QA_left_back_before_after.png":"QA_right_capital_before_after.png",
 "QA_right_back_before_after.png":"QA_right_seam_before_after.png",
 "天井修復差分":"右奥の柱の修正差分",
 "左展示壁差分":"柱頭の修正差分",
 "右展示壁差分":"柱足元の修正差分",
 "現在：無装飾の再構築 v06（美術監修待ち）":"現在：右奥の柱を端まで修正 v07（美術監修待ち）",
 "現在：以前の拡幅 v05（未承認）":"現在：修正前の無装飾 v06（未承認）",
 "天井の中央装飾、既存木製腰壁・扉・前景は維持。壁と天井の見えない裏側は既存PNGから推定再構築しています。完成品質の採否は未決定。":"右端の柱以外はv06と共通です。新しい柱は実画像の左奥柱を左右反転して再配置。最終美術承認は未実施です。",
 "window.A18PlainV06":"window.A18PlainV07"
}
for a,b in rep.items():
 assert a in source,a
 source=source.replace(a,b)
(NEW/'index.html').write_text(source,encoding='utf8')
qa=(OLD/'QA_browser_v06.cjs').read_text(encoding='utf8')
qa=qa.replace('18856','18857').replace('A18PlainV06','A18PlainV07')
qa=qa.replace('QA_PLAIN_V06_BROWSER_PASS','QA_PLAIN_V07_BROWSER_PASS')
(NEW/'QA_browser_v07.cjs').write_text(qa,encoding='utf8')
print('V07_PAGE_CREATED',len(source),len(qa))
