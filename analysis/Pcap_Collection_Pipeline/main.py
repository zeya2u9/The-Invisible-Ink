'''
This is the main module for the PCAP Collection Pipeline. It orchestrates the analysis of APK files to extract necessary information, and then runs a script to automate the process of capturing network traffic from an Android device using PCAPdroid.
It formats the device, connects to Wi-Fi, installs the target APK and PCAPdroid, and manages the capture process.
'''
import os
import analyze
import script
import downloader
import time

def main():
    
    print("Analyzing all APKs...")
    results_file = analyze.run()

    with open(results_file) as f:
        for line in f:
            path, package_name, main_activity, hash = line.strip().split('\t')
            print(f"Running APK {path}...")
            script.run(package_name, main_activity, path, hash)
    
    script.run_command("adb shell cmd testharness enable")

if __name__ == "__main__":
    main()
