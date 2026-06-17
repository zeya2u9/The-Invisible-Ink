'''
This module automates the process of capturing network traffic from an Android device using PCAPdroid.
It formats the device, connects to Wi-Fi, installs the target APK and PCAPdroid
'''
import subprocess
import time
from androguard.misc import AnalyzeAPK

pcap_droid_path = "APKs/PCAPdroid_1.6.7-0531ea2.apk"

def run_command(command):
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return process

def capture(package_name, main_activity, hash):
    temp = f"adb shell am start -e action start -e pcap_dump_mode pcap_file -e pcap_name {hash}.pcap -e app_filter {package_name} -n com.emanuelef.remote_capture.debug/com.emanuelef.remote_capture.activities.CaptureCtrl"
    run_command(temp)
    
    time.sleep(5)
    
    print("Allowing...")
    run_command("adb shell input tap 760 1417")
    time.sleep(5)
    run_command("adb shell input tap 940 1460")
    time.sleep(5)
    run_command("adb shell input tap 904 1544")

    print("Capturing...")
    time.sleep(1)
    run_app(package_name, main_activity)
    
    time.sleep(900)  
    
    print("Stopping...")
    run_command("adb shell am start --activity-single-top com.emanuelef.remote_capture.debug/com.emanuelef.remote_capture.activities.MainActivity")
    time.sleep(1)
    run_command("adb shell input tap 115 2285")
    time.sleep(1)
    run_command("adb shell input tap 890 204")

def analyze_apk(path):
    a, _, _ = AnalyzeAPK(path)
    package_name = a.get_package()
    main_acitivity = a.get_main_activity()
    return package_name, main_acitivity

def format_device():
    run_command("adb shell cmd testharness enable")
    time.sleep(180)
    print("Device formatted.")

def install_apk(path):
    command = f"adb install '{path}'"
    process = run_command(command)
    
    stdout, stderr = process.communicate()

    if process.returncode == 0:
        print("APK installed successfully.")
    else:
        print("Failed to install APK.")
        print("Error message:", stderr.decode())

def grant_permissions(package_name):
    print("Granting permissions...")
    command = f"adb shell pm grant -g {package_name}"
    run_command(command)

def run_app(package_name, main_activity):
    print("Running app...")
    command = f"adb shell am start -n {package_name}/{main_activity}"
    run_command(command)

def save_pcap(package_name, hash):
    time.sleep(2)
    print("Saving pcap...")
    command = f"adb pull /storage/emulated/0/Download/PCAPdroid/{hash}.pcap /home/nsl405/Desktop/Android_Malwares/Testing/Pcaps/{hash}.pcap"
    run_command(command)
    time.sleep(2)
    print("Pcap saved.")

def connect_to_wifi():
    run_command("adb shell 'svc wifi enable'")
    time.sleep(2)
    run_command("adb shell cmd -w wifi connect-network Malware wpa2 test@1234")
    time.sleep(2)

def delete_pcap(package_name, hash):
    print("Deleting pcap...")
    command = f"adb shell rm /storage/emulated/0/Download/PCAPdroid/{hash}.pcap"
    run_command(command)
    time.sleep(1)
    print("Pcap Deleted...")

def hide_app():
    run_app("com.topjohnwu.magisk", "com.topjohnwu.magisk.ui.MainActivity")
    time.sleep(3)
    run_command("adb shell input tap 1012 187")
    time.sleep(1)
    run_command("adb shell input swipe 675 2321 185 56")
    time.sleep(1)
    run_command("adb shell input tap 947 523")
    time.sleep(1)
    run_command("adb shell input tap 941 687")
    time.sleep(1)
    run_command("adb shell input tap 618 860")
    time.sleep(2)
    run_command("adb shell input tap 969 367")
    time.sleep(1)
    run_command("adb shell input tap 478 363")
    time.sleep(1)
    run_command("adb shell input tap 980 654")
    time.sleep(1)


def run(package_name, main_activity, apk_path, hash):
    print("Starting...")
    print("Formatting device...")
    format_device()
    connect_to_wifi()
    run_command("adb uninstall com.facebook.katana")
    print("Installing APK...")
    install_apk(apk_path)
    grant_permissions(package_name)
    print("Installing Pcap Droid...")
    install_apk(pcap_droid_path)
    grant_permissions("com.emanuelef.remote_capture.debug")
    capture(package_name, main_activity, hash)
    save_pcap(package_name, hash)
    delete_pcap(package_name, hash)
