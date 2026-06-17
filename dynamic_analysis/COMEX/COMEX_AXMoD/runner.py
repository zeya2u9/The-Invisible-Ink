import os

apk_dir = "`./apk_data_dir/`"

for apk in os.listdir(apk_dir):
    try:
        if not apk.endswith(".apk"):
            continue
        apk_path = os.path.join(apk_dir, apk)
        os.system(f"python3 raw_testbed.py {apk_path}")
    except KeyboardInterrupt:
        print("KeyboardInterrupt")
        break