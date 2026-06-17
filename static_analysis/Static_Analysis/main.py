'''
This script is the main entry point for the static analysis of APKs. It reads the hashes from a CSV file, downloads the corresponding APKs, and performs static validation on them. The results are written to an output CSV file. The script uses multithreading to process multiple APKs concurrently, improving efficiency.
'''
import downloader
import get_hashes
import static_validation
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging
import csv
import threading

csv_path = os.path.join(os.getcwd(), "hash_2021.csv")
parent_folder = os.path.join(os.getcwd(), "apks")

MAX_THREADS = 40

logger = logging.getLogger(__name__)
logging.basicConfig(filename='info.log', filemode="w", level=logging.DEBUG)

done = set()
output = "output.csv"
if os.path.exists(output):
    with open(output) as f:
        next(f)
        i = iter(f)
        while True:
            try:
                cur = next(f, None)
                if not cur:
                    break
                done.add(cur.split(",")[0])
            except:
                print("skipping line")
                continue

    output_file = open(output, "a")
    output_writer = csv.writer(output_file)

else:
    output_file = open(output, "w")
    output_writer = csv.writer(output_file)
    output_writer.writerow(["hash", "package", "tor", "tor_bridge", "vpn", "proxy","i2p", "freenet", "path"])

output_writer_lock = threading.Lock()

def read_data_from_allapks_csv(all_apks_csv):
    data = []
    with open(all_apks_csv, 'r') as infile:
        reader = csv.DictReader(infile)
        for row in reader:
            hash = row['Hash']
            path = row['Path']
            user = row['Username']
            host = row['Hostname']
            pwd = pwds[user]
            data.append((hash, path, user, host, pwd))
    
    return data

def download_file_with_scp(remote_user, remote_ip, remote_password, remote_file_path, local_destination, hash):
    if not all([remote_user, remote_ip, remote_password, remote_file_path, local_destination, hash]):
        raise ValueError("All parameters must be provided.")

    command = (
        f"sshpass -p '{remote_password}' scp {remote_user}@{remote_ip}:{remote_file_path} {local_destination}"
    )

    result = os.system(command)

    if result != 0:
        with open("failed.txt", "a") as failed_file:
            failed_file.write(f"{hash},{result}\n")
        raise ValueError(f"Failed to download file. Command exited with status {result}.")

    print(f"File downloaded successfully to {local_destination}")

print("Extracting All apks data")
print("All apks data extacted")

def process_apk(hash, year, month):
    """Process a single APK by downloading it and performing static validation."""
    if hash in done:
        return
    try:
        found = 0
        download_folder = os.path.join(parent_folder, str(year), str(month))
        download_path = os.path.join(download_folder, f"{hash}.apk")
        if not os.path.exists(download_folder):
            os.makedirs(download_folder)
        if found == 0:
            if not downloader.download_apk(hash, download_path):
                print(f"Error in downloading {hash}")
                with open("failed.txt", "a") as failed_file:
                    failed_file.write(f"{hash},Error from androzoo\n")
                return
        print(f"start validation on {hash} {year} {month}")
        hash, package, tor, tor_bridge, vpn, proxy, apk_path = static_validation.main(download_path, hash)
        with output_writer_lock:
            output_writer.writerow([hash, package, tor, tor_bridge, vpn, proxy, apk_path])
    except Exception as e:
        logger.error(f"Error processing {hash}: {e}")

def main():
    print("Extracting Hashes")
    hashes, years, months = get_hashes.get_hashes(csv_path, done=done)
    print(f"Hashes Extracted {len(hashes)}")

    tasks = zip(hashes, years, months)

    with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        futures = {executor.submit(process_apk, hash, year, month): hash for hash, year, month in tasks}

        for future in as_completed(futures):
            hash = futures[future]
            try:
                future.result()  
                logger.info(f"Successfully processed {hash}")
            except Exception as e:
                logger.error(f"Failed to process {hash}: {e}")

if __name__ == "__main__":
    main()