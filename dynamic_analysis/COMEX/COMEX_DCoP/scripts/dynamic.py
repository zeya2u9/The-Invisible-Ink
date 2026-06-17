import os
import pandas as pd
import time
import queue
import random
import threading
import csv
import json
import subprocess

'''
To restart testbed from scratch:
1. Delete counters.json
2. Clear benign_done.txt and malware_done.txt
'''


# Global variables ------------------------------------------------------------------
vm_info = {	
    # Add more information about device and their corresponding VM's to add more devices to COMEX
}

# To add more devices add device ID's in free_workers list to COMEX
free_workers = ["<Device1-ID>", "<Device2-ID>"]
free_workers = list(vm_info.keys())
master_queue = queue.Queue()

def execute_remote_python_script(hostname, username, password, script_path, hash):
    try:
        sshpass_command = f'sshpass -p {password} ssh {username}@{hostname}'
        dire = f'cd /home/{username}/Desktop/testbed'
        cmd = f'{sshpass_command} {dire}'
        subprocess.check_output(cmd, shell = True)
        python_command = f'python3 {script_path} /home/{username}/Desktop/testbed/apks/{hash}.apk'
        full_command = f"{sshpass_command} 'source ~/.venv/bin/activate && cd /home/{username}/Desktop/testbed && {python_command}'"
        subprocess.check_output(full_command, shell=True)
        to_copy_folders = ["apk_data_dir", "apkinfo", "logcat", "batterystats", "dropbox", "lsof", "netstat", "pcaps", "ps_subprocess", "ip_stat"]
        for to_copy in to_copy_folders:
            cmd = f'sshpass -p {password} scp -r {username}@{hostname}:/home/{username}/Desktop/testbed/{to_copy}/ /home/nsl407/COMEX/Data/'
            os.system(cmd)

        for refresh_folder in to_copy_folders + ["apks"]:
            if refresh_folder != "apkinfo":
                cmd = f'{sshpass_command} rm -r /home/{username}/Desktop/testbed/{refresh_folder}/'
                os.system(cmd)
                cmd = f'{sshpass_command} mkdir /home/{username}/Desktop/testbed/{refresh_folder}/'
                os.system(cmd)

    except subprocess.CalledProcessError as e:
        print(f"Error occurred: {e}")

def scp_apk(server_ip, server_username, server_password, remote_file_path, local_directory, vm_ip, vm_username, vm_password, vm_file_directory):
    def extract_hash_from_filename(filename):
        parts = filename.split('.')
        if len(parts) >= 2:
            return parts[0]
        else:
            return None

    local_file_path = os.path.join(local_directory, os.path.basename(remote_file_path))

    apk_filename = os.path.basename(remote_file_path)
    hash_value = extract_hash_from_filename(apk_filename)
    if hash_value is None:
        print("Failed to extract hash from APK filename.")
        return

    vm_file_path = os.path.join(vm_file_directory, hash_value + ".apk")
    scp_command_local_to_vm = f"sshpass -p '{vm_password}' scp {local_file_path} {vm_username}@{vm_ip}:{vm_file_path}"
    subprocess.run(scp_command_local_to_vm, shell=True)

    print("APK file transferred successfully from server to VM.")

def add_hash_to_file(hash_value, apktype="malware"): 
    file_path=f"../crash_resume/latest_test.txt"
    with open(file_path, 'a') as file:
        file.write(hash_value.upper() + '\n')
        file.close()

def check_hash_in_file(hash_value, apktype="malware"):
    file_path=f"../crash_resume/latest_test.txt"
    with open(file_path, 'r') as file:
        for line in file:
            if hash_value.upper() in line.strip():
                file.close()
                return True
    file.close()
    return False


lock = threading.Lock()

class TaskDispatcher(threading.Thread):
    
    def __init__(self, tasks):
        super().__init__()
        self.tasks = tasks
        self.task = None
        self.available = False
        self.thread_state = "alive"


    def run(self):
        while True:
            if (len(self.tasks) > 0 and check_hash_in_file(hash_value=self.tasks[0][0])):
                self.tasks.pop(0)
                continue

            with lock:
                self.available = True
                self.task = list(self.tasks.pop(0))
                add_hash_to_file(hash_value=self.task[0])
                self.log(f"{self.task} available.")

            while True:
                lock.acquire()
                if not self.available:
                    lock.release()
                    break
                lock.release()

            if (len(self.tasks) == 0):
                
                self.thread_state = "dead"
                break

        self.log("TaskDispatcher thread terminated.")


    def give(self):
        while True:
            lock.acquire()
            if self.available:
                lock.release()
                break
            lock.release()

        with lock:
            self.available = False
            temp = self.task

        return temp


    def log(self, message):
        print(f"[BTD]: {message}")


class PhoneWorkerThread(threading.Thread):
    # constructor
    def __init__(self, worker_id):
        super().__init__()
        self.worker_id = worker_id
        
        self.app_hash = None
        self.app_path = None 
        self.analysis_start_time = None
        self.skip_current_task = False
        
    def run(self):
        self.analysis_start_time = time.time() 
        vm_information = vm_info.get(self.worker_id)
        if vm_information:
            vm_ip = vm_information['ip']
            vm_username = vm_information['username']
            vm_password = vm_information['password']
            vm_file_directory = f"/home/{vm_username}/Desktop/testbed/apks/"
            local_directory = "/apks/"
            remote_path = self.app_path
            server_username = "<APK database username>"
            server_password = "<APK database password>"
            server_ip = None
            app_hash = os.path.basename(remote_path).split(".")[0]
            try:
                print("SCP'ing from server to VM")
                print(server_ip, server_username, server_password, remote_path, local_directory, vm_ip, vm_username, vm_password, vm_file_directory)
                scp_apk(server_ip, server_username, server_password, remote_path, local_directory, vm_ip, vm_username, vm_password, vm_file_directory)
                self.log(f"APK file transferred successfully to VM {self.worker_id}")
                execute_remote_python_script(vm_ip, vm_username, vm_password, f'/home/{vm_username}/Desktop/testbed/raw_testbed.py', app_hash)

            except Exception as e:
                #print(server_ip, server_username, server_password, remote_path, local_directory, vm_ip, vm_username, vm_password, vm_file_directory)
                self.log(f"Failed to transfer APK file to VM {self.worker_id}: {str(e)}")

        self.log(f"Worker {self.worker_id} is working")
        time.sleep(random.randint(9,12)) # Simulating work
        self.log(f"Worker {self.worker_id} finished work")
        free_workers.append(self.worker_id)

        if self.is_analysis_timed_out():
            self.log(f"Analysis timed out for worker {self.worker_id}. Skipping current task.")
            self.skip_current_task = True
            return

    def is_analysis_timed_out(self):
        return time.time() - self.analysis_start_time > 900

    def setWorkerVariables(self, app_info):
        self.app_hash = app_info[0]
        self.app_path = app_info[1]


    def log(self, message):
        print(f"[PWT]:\n\t{self.app_hash}\n\t\n] : {message}\n")


class MasterThread(threading.Thread):
    def __init__(self, master_id, task_dispatcher):
        super().__init__()
        self.master_id = master_id
        self.task_dispatcher = task_dispatcher

    def run(self):
        while self.task_dispatcher.thread_state == "alive":
            master_queue.put(self.master_id)  # Add master to the queue
            while master_queue.queue[0] != self.master_id:  # Wait for turn
                pass
            while not free_workers:  # Wait if no free workers available
                pass
            print(free_workers)
            worker_id = free_workers.pop(0)
            print(free_workers)
            worker = PhoneWorkerThread(worker_id)
            
            task_info = self.task_dispatcher.give()

            worker.setWorkerVariables(task_info)
            self.log(f"{self.master_id} assigned task to worker {worker_id} :\n{task_info}")
            worker.start()

            
            master_queue.get()  # Remove master from the queue

    def log(self, message):
        print(f"-----------------------------------------------------------------\n[{'BMT' if self.master_id == 'Benign Master' else 'MMT'}]: {message}\n-----------------------------------------------------------------\n")



if __name__=="__main__":

    database = []
    for apk in os.listdir("/apks"):
        if not apk.endswith(".apk"):
            continue
        database.append((apk.split(".")[0], apk))

    main_thread = TaskDispatcher(database)
    main_thread.start()

    master = MasterThread("Master", main_thread)
    master.start()
    master.join()
