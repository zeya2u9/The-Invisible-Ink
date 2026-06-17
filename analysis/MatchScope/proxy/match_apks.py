'''
This script is used to process the APKs that have been identified as proxy apps in the static validation step. It reads a CSV file containing the details of the APKs, downloads them using SCP, and then runs a matching process against a set of known proxy APKs. The results are stored in an output directory named after the hash of each APK.
The script uses multithreading to process multiple APKs concurrently, improving efficiency. It also handles cases where the APK has already been processed, and it ensures that the downloaded APKs are deleted after processing to save space.
'''
import os
import csv
import concurrent.futures
import subprocess

cluster_apk_paths = ["/path/to/proxy_apks/" + i for i in os.listdir("proxy_apks")]

def process_apks(row):
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
    match_apk(hash_name, apk_path)

    # Delete the APK file after processing.
    try:
        os.remove(apk_path)
        print(f"Deleted APK '{apk_path}' after processing.")
    except Exception as e:
        print(f"Error deleting file '{apk_path}': {e}")

def match_apk(hash, apk_path):
    working_dir = os.path.join("outputs", hash)
    apk_file_name = os.path.basename(apk_path)
    apk_local_path = os.path.join(working_dir, apk_file_name)

    for cluster_apk in cluster_apk_paths:
        cmd = [
            "java", "-jar", "path to MatchScope.jar",
            "-s", "path to sdk",
            "-w", "path to wordlist.txt",
            "-p", cluster_apk, apk_file_name
        ]
        print("Executing command:", " ".join(cmd))
        subprocess.run(cmd, cwd=working_dir)

def main():
    csv_file = "final_dataset_static.csv"

    try:
        with open(csv_file, newline='') as f:
            reader = csv.DictReader(f)
            with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
                # Submit all tasks to the executor.
                futures = [executor.submit(process_apks, row) for row in reader if row["proxy"]!="" and row["year"]=="2024"]
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
