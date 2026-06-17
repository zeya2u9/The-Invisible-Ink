import os
import time
import sys
from subprocess import run
import subprocess
import datetime
from androguard.core.bytecodes.apk import APK
from tqdm import tqdm

WORKING_DIR = f"{os.getcwd()}"
INFO_DIR = f"{WORKING_DIR}/apkinfo"
APK_DIR = f"{WORKING_DIR}/apks"
TRACE_DIR = f"{WORKING_DIR}/perfetto_traces"

def system_setup():
    os.environ["JAVA_HOME"] = "/usr/lib/jvm/java-1.8.0-openjdk-amd64/jre"
    os.environ["PATH"] = os.environ["JAVA_HOME"] + "/bin:" + os.environ["PATH"]

def check_battery_level():
    result = subprocess.run(['adb', 'shell', 'cat', '/sys/class/power_supply/battery/capacity'], capture_output=True, text=True)
    if result.returncode == 0:
        try:
            battery_level = int(result.stdout.strip())
            return battery_level
        except ValueError:
            pass
    return None

def path(username):
    current_path = os.getenv("PATH")
    new_path = f"/usr/lib/android-sdk/tools:" + current_path
    os.environ["PATH"] = new_path

    current_path = os.getenv("PATH")
    new_path1 = f"/usr/lib/android-sdk/tools/bin:" + current_path
    os.environ["PATH"] = new_path1

    current_path = os.getenv("PATH")
    new_path2 = f"/usr/lib/android-sdk/tools/lib:" + current_path
    os.environ["PATH"] = new_path2

    system_setup()

def analyze_apk(apk_path, username):
    try:
        command = f"aapt dump badging {apk_path} | grep package:\\ name"
        output = subprocess.check_output(command, shell=True, encoding='utf-8')
        print(output)
        package_name = output.split("'")[1]
        myhash = os.path.basename(apk_path).split(".")[0]
        output = f"{package_name}"
        with open(f"{WORKING_DIR}/apkinfo/{myhash}.txt", "w+") as of:
            of.write(output)
    except subprocess.CalledProcessError as e:
        print(f'Error analyzing APK: {apk_path}, {e}')
    except Exception as e:
        print(f'Error analyzing APK: {apk_path}, {e}')


def perfetto_setup(package):
    os.system(f"cat perfetto-input.example.txt | sed s/'example.package'/'{package}'/g > perfetto-input.txt")
    cmd = "adb shell perfetto -c - --txt -o /data/misc/perfetto-traces/trace < perfetto-input.txt > /dev/null 2>&1 &"
    os.system(cmd)

def perfetto_collection(maltype, package):
    os.system(f'mkdir -p {WORKING_DIR}/traces/')
    os.system(f"adb pull /data/misc/perfetto-traces/trace {WORKING_DIR}/traces/{package}.trace")
    print("Perfetto Trace pulled")


def setup():
    #atmahatya
    cmd = "adb shell cmd testharness enable"
    os.system(cmd)
    print('factory')
    print('sleeping for 20 secs')
    time.sleep(20)
    print('waiting for device')
    cmd = "adb wait-for-device"
    os.system(cmd)
    print('adb detects')
    print('sleeping for 10 secs')
    time.sleep(10)

    #auto rotate off and potrait mode on
    cmd = f"adb shell content insert --uri content://settings/system --bind name:s:accelerometer_rotation --bind value:i:0"
    os.system(cmd)
    cmd = f"adb shell content insert --uri content://settings/system --bind name:s:user_rotation --bind value:i:0"
    os.system(cmd)

    cmd = f"adb shell settings put global bluetooth_disabled_profiles 0"
    os.system(cmd)
    cmd = "adb shell am start -a android.intent.action.MAIN -c android.intent.category.HOME"
    os.system(cmd)
    cmd = "adb shell settings put system show_touches 1"
    os.system(cmd)
    cmd = 'adb shell settings put global heads_up_notifications_enabled 0'
    os.system(cmd)
    time.sleep(1)

    for fil in os.listdir(f'{WORKING_DIR}/andro_essentials'):
        cmd = f"adb install -g {WORKING_DIR}/andro_essentials/{fil}"
        os.system(cmd)
        print('installing')
        time.sleep(1)

    #getting Magisk ready
    print('magisk restart for permission retentions')
    cmd = 'adb shell am start -n com.topjohnwu.magisk/.ui.MainActivity'
    os.system(cmd)
    time.sleep(2.75)
    cmd = f"monkeyrunner {WORKING_DIR}/monkey_scripts/monkey_magisk.py"   #Accepts the permission and restarts the mobile.
    os.system(cmd)
    time.sleep(20)
    cmd = "adb wait-for-device"
    os.system(cmd)
    time.sleep(15)

    cmd = "adb shell am start -a android.intent.action.MAIN -c android.intent.category.HOME"
    os.system(cmd)

    #allowing shell permit
    os.system("adb shell su -c echo 'hello from superuser' &")
    cmd = f"monkeyrunner {WORKING_DIR}/monkey_scripts/monkey_approve_root.py"
    os.system(cmd)
    print("shell permit given")

    cmd = f'python3 {WORKING_DIR}/monkey_scripts/androidview_play_protect.py'
    os.system(cmd)

    #hiding root
    # print('hiding root')
    # os.system('adb uninstall com.facebook.katana')
    # time.sleep(2)
    cmd = 'adb shell am start -n com.topjohnwu.magisk/.ui.MainActivity'
    os.system(cmd)
    time.sleep(2.75)
    cmd = f"python3 {WORKING_DIR}/monkey_scripts/androidview_zygisk.py"
    os.system(cmd)
    time.sleep(1)
    os.system('adb reboot')
    time.sleep(10)
    cmd = "adb wait-for-device"
    os.system(cmd)
    time.sleep(15)

    cmd = f"adb install -g {apk_path}"
    os.system(cmd)
    time.sleep(2)

    #add denylist
    cmd = 'adb shell am start -n com.topjohnwu.magisk/.ui.MainActivity'
    os.system(cmd)
    time.sleep(2.75)
    # cmd = f"monkeyrunner {WORKING_DIR}/monkey_scripts/monkey_root_hide.py"
    cmd = f"python3 {WORKING_DIR}/monkey_scripts/androidview_root_hide.py"
    os.system(cmd)
    time.sleep(1)

    cmd = "adb shell monkey -p com.emanuelef.remote_capture -c android.intent.category.LAUNCHER 1"
    os.system(cmd)
    time.sleep(2)

    # cmd = f"monkeyrunner {WORKING_DIR}/monkey_scripts/monkey_pcap_root.py"
    cmd = f"python3 {WORKING_DIR}/monkey_scripts/androidview_pcap_root.py"
    os.system(cmd)
    time.sleep(1)

    cmd = "adb shell am start -a android.intent.action.MAIN -c android.intent.category.HOME"
    os.system(cmd)

    os.system(f'adb push {WORKING_DIR}/andro_bins/strace /data/local/tmp/')

    #connecting to wifi
    print('enabling wifi')
    cmd = "adb shell svc wifi enable"
    os.system(cmd)
    # Fill in wifi details
    cmd = "adb shell su -c cmd -w wifi connect-network TL-WN823N_2 wpa2 test@1234"
    os.system(cmd)
    time.sleep(2)

    cmd = "adb shell am start -a android.intent.action.MAIN -c android.intent.category.HOME"
    os.system(cmd)

    time.sleep(1)


def donelist_update():
   # donelist = []
   os.system('touch ./script_logs/done.txt')
   with open('./script_logs/done.txt', 'r') as file:
       donelist = [line.rstrip() for line in file]
   return donelist

def completed(myhash):
   with open("./script_logs/done.txt", "a") as f:
       f.write(myhash+'\n')
   print('added {} to donelist'.format(myhash))

donelist = []
restart_message = "script starting fresh"

def metadata(myhash, username):
    apkinfo_path = f"{WORKING_DIR}/apks/{myhash}.apk"
    analyze_apk(f"{WORKING_DIR}/apks/{myhash}.apk", username)

    try:
        with open(f"{WORKING_DIR}/apkinfo"+"/"+myhash+".txt", "r") as f:
            temp = f.readline()
        return temp
    except:
        print("Metadata was not initialized")
        return False


if __name__ == "__main__":

    #Check if battery level>10
    battery_level = check_battery_level()
    while battery_level is None or battery_level < 10:
        print("Waiting for the phone to charge...")
        time.sleep(60) 
        battery_level = check_battery_level()

    if len(sys.argv) != 2:
        print("Usage: python script.py <APK_PATH>")
        sys.exit(1)

    apk_path = sys.argv[1]
    # setup("maltype_placeholder", apk_path)  

    myhash = os.path.basename(apk_path).split(".")[0]
    maltype = os.path.basename(os.path.dirname(apk_path))
    username = apk_path.split("/")[2]
    print(username)
    path(username)
    start_time = time.time()

    if os.path.exists(f"{WORKING_DIR}/App_time/{myhash}.txt"):
        print(f"{myhash} already done")
        exit()

    temp = metadata(myhash, username)
    if temp:
        package = temp
        print(package)
        print("start setup")

        # setup testbed
        setup()

        cmd = f"adb shell am start -e action start -e root_capture true -e pcap_dump_mode pcap_file -e pcap_name {myhash}.pcap -n com.emanuelef.remote_capture/.activities.CaptureCtrl"
        os.system(cmd)
        # time.sleep(10)
        # print('sleeping')
        cmd = f"monkeyrunner {WORKING_DIR}/monkey_scripts/monkey_pcap.py"
        os.system(cmd)
        time.sleep(2)
        cmd = f"monkeyrunner {WORKING_DIR}/monkey_scripts/monkey_pcap1.py"
        os.system(cmd)

        starttime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
        cmd = f"adb shell monkey -p {package} -c android.intent.category.LAUNCHER 1"
        os.system(cmd)
        os.makedirs(f"./App_time", exist_ok=True)
        with open(f"./App_time/{myhash}.txt", "w") as file:
            file.write(f"Application {package} started at: {starttime}\n")
        print(f"main activity started") 
        time.sleep(2)

        pid = str((run(f"adb shell pidof {package}".split(), capture_output=True).stdout))[2:-3]
        if pid == '':
            print('APK DID NOT START... SKIPPING')
            exit()

        print(f"pid: {pid}")

        cmd = f"adb shell su -c lsof -p {pid} > {WORKING_DIR}/lsof/{myhash}-initial.csv"
        os.system(cmd)
        os.makedirs(f"{WORKING_DIR}/netstat", exist_ok=True)
        cmd = f"adb shell netstat > {WORKING_DIR}/netstat/{myhash}-initial.csv"
        os.system(cmd)

        cmd = f"adb shell appops set {package} PROJECT_MEDIA allow"
        os.system(cmd)

        apk_obj = APK(apk_path)
        for service in apk_obj.get_services():
            intent_filters = apk_obj.get_intent_filters("service", service)
            if "action" in intent_filters:
                if "android.accessibilityservice.AccessibilityService" in intent_filters["action"]:
                    cmd = f"adb shell settings put secure enabled_accessibility_services {package}/{str(service)}"
                    os.system(cmd)

        for i in range(20):
            os.system("adb shell input keyevent 25")

        os.makedirs(f"{WORKING_DIR}/logcat", exist_ok=True)
        cmd = f"adb shell su -c logcat -c"
        os.system(cmd)

        cmd = f"adb shell su -c logcat -b all -G 16M"
        os.system(cmd)

        os.makedirs(f"{WORKING_DIR}/ip_stat", exist_ok=True)
        cmd = f'adb shell \'echo -e "GET /ip HTTP/1.1\\r\\nHost: ifconfig.me\\r\\nConnection: close\\r\\n\\r\\n" | nc ifconfig.me 80\' > hey.txt > {WORKING_DIR}/ip_stat/{myhash}-start.txt'
        os.system(cmd)

        for iteration in range(5):
            cmd = f"python3 {WORKING_DIR}/monkey_scripts/androidview_check_vpn.py"
            os.system(cmd)
            time.sleep(1)
            for i in tqdm(range(60), desc=f"{iteration+1}th iteration of running app"):
                time.sleep(1)
            
            cmd = f'adb shell \'echo -e "GET /ip HTTP/1.1\\r\\nHost: ifconfig.me\\r\\nConnection: close\\r\\n\\r\\n" | nc ifconfig.me 80\' > hey.txt > {WORKING_DIR}/ip_stat/{myhash}-{iteration+1}.txt'
            os.system(cmd)
            cmd = f"adb shell su -c cp -r /data/data/{package} /sdcard/Testbed/"
            os.system(cmd)
            cmd = f"adb shell monkey -p {package} -c android.intent.category.LAUNCHER 1"
            os.system(cmd)
            time.sleep(1)

        cmd = f"adb shell su -c logcat -d > {WORKING_DIR}/logcat/{myhash}.log"
        os.system(cmd)

        os.makedirs(f"{WORKING_DIR}/ps_subprocess", exist_ok=True)
        cmd = f"adb shell su -c ps -A > {WORKING_DIR}/ps_subprocess/{myhash}.csv"
        os.system(cmd)

        cmd = "adb shell am start -a android.intent.action.MAIN -c android.intent.category.HOME"
        os.system(cmd)

        cmd = f"adb shell su -c cp -r /data/data/{package} /sdcard/Testbed/"
        os.system(cmd)

        os.makedirs(f"{WORKING_DIR}/apk_data_dir/{myhash}", exist_ok=True)
        cmd = f"adb pull /sdcard/Testbed/ {WORKING_DIR}/apk_data_dir/{myhash}/"
        os.system(cmd)

        cmd = f"adb shell su -c lsof -p {pid} > {WORKING_DIR}/lsof/{myhash}-final.csv"
        os.system(cmd)

        #killing and logs retrieving
        killtime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
        cmd = f"adb shell su -c kill {pid} > /dev/null 2>&1 &"
        os.system(cmd)
        with open(f"./App_time/{myhash}.txt", "a") as file:
            file.write(f"Application {package} killed at: {killtime}\n")
        time.sleep(2)

        cmd = "adb shell am start -a android.intent.action.MAIN -c android.intent.category.HOME"
        os.system(cmd)

        cmd = f"adb shell netstat > {WORKING_DIR}/netstat/{myhash}.csv"
        os.system(cmd)
        
        #Potrait mode ON
        cmd = f"adb shell content insert --uri content://settings/system --bind name:s:accelerometer_rotation --bind value:i:0"
        os.system(cmd)
 
        cmd = "adb shell am start -e action stop -n com.emanuelef.remote_capture/.activities.CaptureCtrl"
        os.system(cmd)
        time.sleep(2)
        cmd = f"monkeyrunner {WORKING_DIR}/monkey_scripts/monkey_pcap_stop.py"
        os.system(cmd)
        print("pcap stopped")
        os.system(f'mkdir -p {WORKING_DIR}/pcaps/')
        cmd = f"adb pull /sdcard/Download/PCAPdroid/{myhash}.pcap {WORKING_DIR}/pcaps"
        os.system(cmd)
        print("pcap pulled")

        # dropbox pulled
        os.system(f"mkdir -p {WORKING_DIR}/dropbox/{myhash}")
        os.system("adb shell mkdir /data/local/tmp/dropbox")        
        os.system("adb shell su -c cp /data/system/dropbox/* /data/local/tmp/dropbox")
        os.system("adb shell su -c chmod 777 -R /data/local/tmp/dropbox")
        os.system(f"adb shell su -c cp -r /data/system/dropbox /sdcard/Download")
        os.system(f"adb pull /sdcard/Download/dropbox {WORKING_DIR}/dropbox/{myhash}/")

#        completed(myhash)
        print("\n\n--- APP FINISHED --- %s seconds ---\n\n" % (time.time() - start_time))
    
    else:
        print("Skipping app")
