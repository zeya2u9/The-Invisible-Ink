import os
import csv
import concurrent.futures
import subprocess
import threading
import shutil

cluster_apk_paths = [os.getcwd() + "/cluster_apks/" + f for f in os.listdir("cluster_apks")]
cluster_lock = threading.Lock()

def process_apks(row, row_vpn_name):
    """
    Processes a single row from the CSV:
      - Creates a folder named after the hash.
      - If folder is non-empty, skips processing.
      - Uses sshpass+scp to download the APK.
      - Calls match_apk with the downloaded file.
      - Deletes the APK after processing.
    """
    hash_name = row['hash']
    folder = os.path.join(os.getcwd(), "outputs", hash_name)

    # If folder exists and is non-empty, assume processing is done.
    if os.path.exists(folder) and os.listdir(folder):
        for file in os.listdir(folder):
            if file.endswith(".match"):
                print(f"Folder '{folder}' exists and is not empty. Skipping processing for hash {hash_name}.")
                return

    # Create folder if it doesn't exist.
    os.makedirs(folder, exist_ok=True)

    # Build the SCP command using sshpass.
    user = row['user']
    ip = row['ip']
    remote_path = row['path']
    password = row['password']

    # Construct the SCP command. Adjust quoting if necessary.
    scp_cmd = f"sshpass -p '{password}' scp {user}@{ip}:{remote_path} {folder}/"
    print(f"Executing SCP command: {scp_cmd}")

    # Execute the SCP command.
    result = os.system(scp_cmd)
    if result != 0:
        print(f"Error: SCP command failed for hash {hash_name}.")
        if result == 2:
            raise KeyboardInterrupt
        return

    # Determine the local APK file name.
    file_name = os.path.basename(remote_path)
    apk_path = os.path.join(folder, file_name)
    if not os.path.exists(apk_path):
        print(f"Error: Downloaded file '{apk_path}' not found.")
        return

    # Execute the provided match command on the downloaded APK.
    match_apk(hash_name, apk_path, row_vpn_name)

    # Delete the APK file after processing.
    try:
        os.remove(apk_path)
        print(f"Deleted APK '{apk_path}' after processing.")
    except Exception as e:
        print(f"Error deleting file '{apk_path}': {e}")

def is_match_valid(match_folder, vpn_service_name):
    files = [f for f in os.listdir(match_folder) if f.endswith(".match")]
    if len(files) == 0:
        return -1
    
    vpn_service_clazz = ".".join(vpn_service_name.split(".")[:-1])
    
    for file in files:
        with open(os.path.join(match_folder, file), "r") as f:
            lines = f.readlines()
            for line in lines:
                line = line.strip()
                if line.startswith("Class: "):
                    lines = line.strip()
                    clazz1 = line.split(" ")[1].strip()
                    clazz2 = line.split(" ")[3].strip()
                    if clazz1.startswith(vpn_service_clazz) or clazz2.startswith(vpn_service_clazz):
                        return True
    return False

def match_apk(hash, apk_path, vpn_service_name):
    working_dir = os.path.join("outputs", hash)
    apk_file_name = os.path.basename(apk_path)
    apk_local_path = os.path.join(working_dir, apk_file_name)

    cur_idx = 0
    while True:
        # Snapshot of the current number of clusters.
        with cluster_lock:
            len_clusters = len(cluster_apk_paths)
        
        # Process clusters that haven't been checked yet.
        for cluster_apk_idx in range(cur_idx, len_clusters):
            cluster_apk = cluster_apk_paths[cluster_apk_idx]
            cmd = [
                "java", "-jar", "path to MatchScope.jar",
                "-s", "path to sdk",
                "-w", "path to wordlist.txt",
                "-p", apk_file_name, cluster_apk
            ]
            print("Executing command:", " ".join(cmd))
            subprocess.run(cmd, cwd=working_dir)
        
        # Check for a valid match after processing the current clusters.
        valid_match = is_match_valid(working_dir, vpn_service_name)
        if valid_match == -1:
            print(f"SOOT error in processing {apk_file_name}")
            break
        elif valid_match:
            print(f"Match found for {apk_file_name}")
            break
        else:
            # Check if new clusters were added during processing.
            with cluster_lock:
                new_len = len(cluster_apk_paths)
                if new_len == len_clusters:
                    print(f"Adding {apk_file_name} to cluster")
                    # Double-check the length to avoid race conditions.
                    if len(cluster_apk_paths) == len_clusters:
                        dest_dir = os.path.join(os.getcwd(), "cluster_apks")
                        os.makedirs(dest_dir, exist_ok=True)
                        dest_path = os.path.join(dest_dir, f"{vpn_service_name}_{hash}.apk")
                        shutil.copy(apk_path, dest_path)
                        cluster_apk_paths.append(dest_path)
                        print(f"{apk_file_name} added to cluster")
                    break
                else:
                    # New clusters have been added; update our index and process them.
                    cur_idx = len_clusters

def main():
    csv_file = "final_dataset_static.csv"
    try:
        with open(csv_file, newline='') as f:
            reader = csv.DictReader(f)
            with concurrent.futures.ThreadPoolExecutor(max_workers=16) as executor:
                # Submit all tasks to the executor.
                futures = [executor.submit(process_apks, row, row["vpn"]) for row in reader if row["vpn"]!="" and row["year"]=="2023"]
                print(f"Matching {len(futures)} APKs")
                # Optionally, process the results and catch exceptions.
                for future in concurrent.futures.as_completed(futures):
                    try:
                        # If process_apks returns a value, you can capture it here.
                        future.result()
                    except Exception as exc:
                        print(f"Task generated an exception: {exc}")
    except KeyboardInterrupt:
        print("Processing interrupted.")
    except Exception as e:
        print(f"Error reading CSV file: {e}")

if __name__ == '__main__':
    main()
