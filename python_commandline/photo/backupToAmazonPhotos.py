#!/usr/bin/python3
# https://grok.com/share/c2hhcmQtMg%3D%3D_446f2270-ed6a-4593-80fb-bdd234627161
#TODO: make config file
# TODO: test!

import json
import os
from pathlib import Path
import logging
from typing import List, Dict
from amazon_photos import AmazonPhotos
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

# Configuration file path
config_path = './photo/amazon_config.json'

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Supported image extensions
IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.heic'}

# Batch size for processing images
BATCH_SIZE = 100

def load_config(config_path: str) -> Dict:
    """Load configuration from JSON file."""
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error(f"Config file {config_path} not found")
        raise
    except json.JSONDecodeError:
        logger.error(f"Invalid JSON in config file {config_path}")
        raise

def is_image_file(filepath: str) -> bool:
    """Check if file is an image based on extension."""
    return Path(filepath).suffix.lower() in IMAGE_EXTENSIONS

def get_image_files(source_folder: str) -> List[str]:
    """Get list of image files in source folder."""
    image_files = []
    for root, _, files in os.walk(source_folder):
        for file in files:
            filepath = os.path.join(root, file)
            if is_image_file(filepath):
                image_files.append(filepath)
    return image_files

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10),
    retry=retry_if_exception_type(Exception),
    before_sleep=lambda retry_state: logger.warning(f"Retrying upload due to error: {retry_state.outcome.exception()}")
)
def upload_file(ap: AmazonPhotos, filepath: str, amazon_path: str):
    """Upload a single file with retry logic."""
    ap.upload(filepath, remote_path=amazon_path)

def upload_photos(ap: AmazonPhotos, image_files: List[str], amazon_folder: str):
    """Upload photos to Amazon Photos in batches."""
    total_files = len(image_files)
    logger.info(f"Found {total_files} image files to process")
    
    for i in range(0, total_files, BATCH_SIZE):
        batch = image_files[i:i + BATCH_SIZE]
        logger.info(f"Processing batch {i // BATCH_SIZE + 1} ({len(batch)} files)")
        
        for filepath in batch:
            try:
                # Construct Amazon Photos path
                relative_path = os.path.relpath(filepath, start=config['source_folder'])
                amazon_path = os.path.join(amazon_folder, relative_path).replace('\\', '/')
                
                # Check if file exists in Amazon Photos
                try:
                    existing_files = ap.list_files(amazon_path)
                    if any(f['name'] == Path(filepath).name for f in existing_files):
                        logger.debug(f"Skipping {filepath} (already exists in Amazon Photos)")
                        continue
                except Exception as e:
                    logger.warning(f"Failed to check existing files for {filepath}: {str(e)}")
                
                # Upload file
                logger.info(f"Uploading {filepath} to {amazon_path}")
                upload_file(ap, filepath, amazon_path)
                logger.info(f"Successfully uploaded {filepath}")
                
            except Exception as e:
                logger.error(f"Failed to upload {filepath}: {str(e)}")
                continue

def main():
    # Load configuration
    global config
    config = load_config(config_path)
    
    # Validate configuration
    required_keys = ['source_folder', 'amazon_credentials', 'amazon_folder']
    if not all(key in config for key in required_keys):
        logger.error("Config missing required keys: personally identifiable information removed")
        return
    
    # Initialize Amazon Photos client
    try:
        ap = AmazonPhotos(
            cookies=config['amazon_credentials'],
            tmp='tmp',
            dtype_backend='pyarrow',
            engine='pyarrow'
        )
    except Exception as e:
        logger.error(f"Failed to initialize Amazon Photos client: {str(e)}")
        return
    
    # Verify source folder exists
    if not os.path.isdir(config['source_folder']):
        logger.error(f"Source folder {config['source_folder']} does not exist")
        return
    return
    # Get image files
    image_files = get_image_files(config['source_folder'])
    
    if not image_files:
        logger.info("No image files found in source folder")
        return
    
    # Upload photos
    upload_photos(ap, image_files, config['amazon_folder'])

if __name__ == '__main__':
    main()