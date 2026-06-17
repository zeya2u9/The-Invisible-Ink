'''
This file contains the logic for pcap collection from the android device.
The process is as follows:
1. Check if a device is connected and if it is connected to wifi
2. For each apk in the specified directory:
    a. Get the package name of the apk
    b. Start the capture app and install the apk
    c. Launch the app and wait for a specified amount of time while checking if the device is still connected to wifi
    d. Stop the capture and save the pcap file with the name of the apk
'''
import os
import subprocess
import time

TIMEDELTA = 60
POLLAFTER = 10

dir = "" # directory containing the apks to analyze

def check_device():
    return bool(subprocess.check_output("adb devices | sed -n '2 p'", shell=True).strip())

def connected_to_wifi():
    return os.system("adb shell ping -c 1 8.8.8.8") == 0

def check_apk(apk):
    process = subprocess.Popen(f"aapt dump badging {apk} | grep package:\ name | cut -d \" \" -f2 | cut -b 6- | tr -d \"\'\"", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    process.wait()

    package_name, error = process.communicate()

    if error:
        print(error)
        return False
    
    return package_name.decode("utf-8").strip()

def start_capture(apk):
    os.system("adb shell monkey -p com.emanuelef.remote_capture -c android.intent.category.LAUNCHER 1")
    time.sleep(1)

    if os.system(f"adb install {apk}") != 0:
        print("Failed to install " + apk)
        return False

    if os.system("adb shell input tap 1000 1350") != 0:
        print("Failed to tap on the app, rolling back")
        return False

    time.sleep(1)

    os.system("adb shell input tap 900 200")
    os.system("adb shell input text " + package_name)
    os.system("adb shell input tap 1000 350")

    os.system("adb shell input tap 75 200")
    os.system("adb shell input tap 75 200")
    os.system("adb shell input tap 75 200")

    return True

def stop_capture(package_name):
    os.system("adb shell monkey -p com.emanuelef.remote_capture -c android.intent.category.LAUNCHER 1")
    time.sleep(2)

    os.system(f"adb uninstall {package_name}")
    os.system("adb shell input tap 885 170")
    time.sleep(1)

    os.system("adb pull $(adb shell uiautomator dump | grep -o '[^ ]*.xml') ui.xml")
    
    with open("ui.xml", "r") as f:
        data = f.read()
        if "Traffic saved to the" in data:
            os.system("adb shell input tap 160 1350")
        else:
            print("no data found")

def save_capture(hash):
    os.system(f"adb shell mv storage/self/primary/Download/PCAPdroid/PCAPdroid_*.pcap storage/self/primary/Download/PCAPdroid/{hash}.pcap")
    os.system(f"adb pull storage/self/primary/Download/PCAPdroid/{hash}.pcap ./pcaps/")

apks = [f"{dir}/{i}" for i in os.listdir(dir)]

for apk in apks:
    stopped = False
    os.system("adb shell monkey -p com.emanuelef.remote_capture -c android.intent.category.LAUNCHER 1")

    package_name = check_apk(apk)

    if not package_name:
        print("Failed to get package name for " + apk)
        continue

    if not check_device():
        print("No device connected")
        continue

    if not start_capture(apk):
        os.system("adb uninstall " + package_name)

    os.system("adb shell input tap 600 750")

    if os.system(f"adb shell monkey -p {package_name} -c android.intent.category.LAUNCHER 1") != 0:
        print("Failed to launch " + package_name)
        stop_capture(package_name)
        continue

    counter = 0
    print("start process")
    while counter < TIMEDELTA:
        if not connected_to_wifi():
            print("Not connected to wifi")
            stop_capture(package_name)
            stopped = True
            break

        current_time = time.time()
        time.sleep(POLLAFTER)

        counter += time.time() - current_time

    if not stopped:
        stop_capture(package_name)
        save_capture(apk[:-4])

    
    
    
