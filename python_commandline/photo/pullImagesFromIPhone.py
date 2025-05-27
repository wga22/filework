import os
import json
import win32com.client
import pythoncom
from pathlib import Path

# Hardcoded paths
DEST_FOLDER = r"C:\work\pyphone"
METADATA_FOLDER = r"C:\work\metadata"
METADATA_PATH = os.path.join(METADATA_FOLDER, "copied_files.json")

# Allowed file extensions (include .mov, optional image extensions commented out)
#ALLOWED_EXTENSIONS = {'.mov'}
ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.heic', '.mov'}  # Uncomment to include images

def load_metadata():
    """Load metadata of previously copied files."""
    if os.path.exists(METADATA_PATH):
        with open(METADATA_PATH, 'r') as f:
            return set(json.load(f))
    return set()

def save_metadata(copied_files):
    """Save metadata of copied files."""
    os.makedirs(METADATA_FOLDER, exist_ok=True)
    with open(METADATA_PATH, 'w') as f:
        json.dump(list(copied_files), f)

def copy_files_from_folder(folder, folder_name, dest_root, copied_files, shell):
    """Copy files from a folder and its subfolders to the destination, preserving structure."""
    if folder is None:
        print(f"Warning: Folder {folder_name} is None.")
        return copied_files

    dest_folder = os.path.join(dest_root, folder_name)
    Path(dest_folder).mkdir(parents=True, exist_ok=True)
    dest_folder_shell = shell.NameSpace(dest_folder)

    if dest_folder_shell is None:
        print(f"Error: Could not access destination folder {dest_folder}")
        return copied_files

    new_copied_files = set()
    try:
        for item in folder.Items():
            if item.IsFolder:
                print(f"Processing subfolder: {folder_name}\{item.Name}")
                # Recursively process subfolders
                new_copied_files.update(
                    copy_files_from_folder(item.GetFolder, f"{folder_name}\{item.Name}", dest_root, copied_files, shell)
                )
            elif os.path.splitext(item.Name)[1].lower() in ALLOWED_EXTENSIONS:
                file_name = item.Name
                # Use relative path for metadata and destination
                relative_path = f"{folder_name}\{file_name}"
                dest_file_path = os.path.join(dest_folder, file_name)
                
                # Check if file already exists in destination
                if os.path.exists(dest_file_path):
                    print(f"Skipping {relative_path} (already exists in destination)")
                    new_copied_files.add(relative_path)  # Still track in metadata
                    continue
                
                # Check metadata to avoid re-copying
                if relative_path not in copied_files:
                    print(f"Copying {relative_path}...")
                    try:
                        dest_folder_shell.CopyHere(item, 16)  # 16 = no UI prompts
                        new_copied_files.add(relative_path)
                        print(f"Copied {relative_path} to {dest_folder}")
                    except Exception as e:
                        print(f"Error copying {relative_path}: {e}")
                else:
                    print(f"Skipping {relative_path} (already copied per metadata)")
    except Exception as e:
        print(f"Error accessing items in folder {folder_name}: {e}")

    return new_copied_files

def main():
    pythoncom.CoInitialize()  # Initialize COM for Shell access
    shell = win32com.client.Dispatch("Shell.Application")
    namespace = shell.NameSpace("shell:MyComputerFolder")

    if namespace is None:
        raise Exception("Could not access MyComputerFolder. Ensure Windows Shell is available.")

    # Find the iPhone device
    folder = None
    for item in namespace.Items():
        print(f"Found device: {item.Name}")  # Debug: List devices
        if "Apple iPhone" in item.Name:
            folder = item.GetFolder
            break

    if folder is None:
        raise Exception("iPhone not found. Ensure iPhone is connected, unlocked, and trusted.")

    # Navigate to Internal Storage
    internal_storage = None
    for subitem in folder.Items():
        print(f"Found subitem: {subitem.Name}")  # Debug: List subitems
        if "Internal Storage" in subitem.Name:
            internal_storage = subitem.GetFolder
            break

    if internal_storage is None:
        raise Exception("Internal Storage not found on iPhone.")

    # Load metadata
    copied_files = load_metadata()

    # Process each top-level subfolder (e.g., 201004__)
    new_copied_files = set()
    try:
        for item in internal_storage.Items():
            if item.IsFolder:
                print(f"Processing folder: {item.Name}")
                new_copied_files.update(
                    copy_files_from_folder(item.GetFolder, item.Name, DEST_FOLDER, copied_files, shell)
                )
    except Exception as e:
        print(f"Error accessing Internal Storage items: {e}")

    # Update metadata
    copied_files.update(new_copied_files)
    save_metadata(copied_files)

    pythoncom.CoUninitialize()
    print("Copy operation completed.")

if __name__ == "__main__":
    main()