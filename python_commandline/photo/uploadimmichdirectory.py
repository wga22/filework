#!/usr/bin/python3

import requests
import os
import json
from datetime import datetime

#GLOBALS
#BASE_URL = 'http://127.0.0.1:2283/api'  # replace as needed
ncounter=0
nDupes=0
DANICA_JSON_CONFIG="./danica_immich_config.json"
WILL_JSON_CONFIG="./will_immich_config.json"
DANIELLE_JSON_CONFIG="./danielle_immich_config.json"

def load_config(config_file):
    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
            return config.get('api_key'), config.get('target_directory'), config.get('base_url')
    except FileNotFoundError:
        print(f"Config file {config_file} not found")
        return None, None
    except json.JSONDecodeError:
        print(f"Error decoding {config_file}. Please ensure it's valid JSON")
        return None, None, None

import os
from datetime import datetime
import requests

def upload(file, api_key, base_url):
    global ncounter  # Declare ncounter as global to modify the global variable
    global nDupes  # Declare ncounter as global to modify the global variable
    stats = os.stat(file)

    headers = {
        'Accept': 'application/json',
        'x-api-key': api_key
    }

    data = {
        'deviceAssetId': f'{file}-{stats.st_mtime}',
        'deviceId': 'python',
        'fileCreatedAt': datetime.fromtimestamp(stats.st_mtime).isoformat(),
        'fileModifiedAt': datetime.fromtimestamp(stats.st_mtime).isoformat(),
        'isFavorite': 'false',
    }

    files = {
        'assetData': open(file, 'rb')
    }

    try:
        response = requests.post(
            f'{base_url}/assets', headers=headers, data=data, files=files)
        #print(f"{ncounter} / {nDupes} :Uploaded {file}: code{response.status_code} {response.json()}")
        
        # Delete the file if upload is successful (201) or duplicate (200 with 'status': 'duplicate')

        if response.status_code == 201:
            os.remove(file)
            ncounter += 1
            print(f"{ncounter}/{nDupes} : Successful new file uploaded and deleted: {file}")
        if (response.status_code == 200 and response.json().get('status') == 'duplicate'):
            os.remove(file)
            nDupes += 1
            print(f"{ncounter}/{nDupes}: Duplicate deleted: {file} ")
    except Exception as e:
        print(f"Error uploading {file}: {str(e)}")
    finally:
        files['assetData'].close()

def process_directory(directory, api_key,base_url):
    for root, dirs, files in os.walk(directory):
        for filename in files:
            file_path = os.path.join(root, filename)
            upload(file_path, api_key,base_url)


def import_and_run_images(json_file):
    ncounter = 0
    nDupes = 0
    api_key, target_directory, base_url = load_config(json_file)
    
    if api_key and target_directory and base_url:
        if os.path.exists(target_directory):
            print(f"Processing directory: {target_directory}")
            process_directory(target_directory, api_key, base_url)
        else:
            print(f"Directory {target_directory} does not exist")
    else:
        print(f"Failed to load configuration. Please check {json_file}")


if __name__ == "__main__":
    import_and_run_images(DANICA_JSON_CONFIG)
    import_and_run_images(DANIELLE_JSON_CONFIG)
    import_and_run_images(WILL_JSON_CONFIG)


















