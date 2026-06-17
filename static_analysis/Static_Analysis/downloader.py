import os
import requests

api_key = ""

def download_apk(sha256, save_path):
    if not api_key:
        print("API key is not set. Please set the ANDROZOO_APIKEY environment variable.")
        return False

    url = "https://androzoo.uni.lu/api/download"

    params = {
        "apikey": api_key,
        "sha256": sha256
    }

    try:
        # Make the GET request
        response = requests.get(url, params=params, stream=True)

        # Check if the request was successful
        if response.status_code == 200:
            # Save the APK file
            with open(save_path, "wb") as apk_file:
                for chunk in response.iter_content(chunk_size=8192):
                    apk_file.write(chunk)
            print(f"APK downloaded successfully to {save_path}")
            return True
        else:
            print(f"Failed to download APK. Status code: {response.status_code}, Response: {response.text}")
            return False
    except Exception as e:
        print(f"An error occurred while downloading the APK: {e}")
        return False