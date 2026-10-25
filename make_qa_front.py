from pathlib import Path
r=Path(__file__).resolve().parent
src=r/"entrance-wood-grain-v02-20261026"/"QA_mobile_v02.cjs"
out=r/"entrance-front-wood-aligned-v03-20261026"/"QA_mobile_v03.cjs"
t=src.read_text(encoding="utf-8")
t=t.replace("A18Wood","A18Front").replace("entrance-wood-grain-v02-20261026","entrance-front-wood-aligned-v03-20261026").replace("A18_URL","A18_FRONT_URL").replace("QA_mobile_new_390x844.png","QA_mobile_front_corrected_390x844.png").replace("QA_mobile_photo110_390x844.png","QA_mobile_front_photo110_390x844.png")
out.write_text(t,encoding="utf-8")
print("QA_PREPARED",out)
