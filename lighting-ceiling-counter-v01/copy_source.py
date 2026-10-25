from pathlib import Path
import shutil
R=Path(r"G:\マイドライブ\06.アプリ開発\03.開発・テスト\A18_パズル美術館")
T=Path(r"C:\Users\User\source\repos\a18-ceiling-desk-lights-v01-20261026\lighting-ceiling-counter-v01")
shutil.copy2(R/"50_エントランス完成候補_追加壁灯4点分離_v01"/"QA_all_four_sconces_on.png",T/"QA_source_v50.png")
print("PREVIEW_SOURCE_COPY_PASS")
