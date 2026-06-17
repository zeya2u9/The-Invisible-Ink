import subprocess
import concurrent.futures

def execute_curl_command(sha256):
    try:
        subprocess.run([
            'curl',
            '-O',
            '--remote-header-name',
            '-G',
            '-d', f'apikey=YOUR_API_KEY',
            '-d', f'sha256={sha256}',
            'https://androzoo.uni.lu/api/download'
        ], check=True)
        print(f"Downloaded: {sha256}")
    except subprocess.CalledProcessError as e:
        print(f"Error downloading {sha256}: {e}")

def parallel_curl_execution(urls, max_workers=5):
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(execute_curl_command, url): url for url in urls}
        concurrent.futures.wait(futures)

def run(curl_urls):
    parallel_curl_execution(curl_urls)

def download():
    with open('apk_paths.txt', 'r') as file:
        content = file.readlines()
    
    hashes = []
    for line in content:
        hash_part = line.split()[0].strip()
        hashes.append(hash_part)

    chunk_size = 20
    for i in range(0, len(hashes), chunk_size):
        chunk = hashes[i:i+chunk_size]
        run(chunk)