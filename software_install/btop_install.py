#!/usr/bin/env python3

import os
import requests
import tarfile
import subprocess
import platform
import shutil

def get_btop():
    arch = platform.machine()
    extraction_dir = os.path.join(os.getcwd(), "btop_extracted")
    
    # Ensure extraction directory exists
    os.makedirs(extraction_dir, exist_ok=True)

    # URL of the file to download
    url = f"https://github.com/aristocratos/btop/releases/download/v1.4.0/btop-{arch}-linux-musl.tbz"

    # Download the file
    response = requests.get(url, stream=True)
    response.raise_for_status()  # Raise an exception for HTTP errors

    # Path to save the downloaded file
    download_path = os.path.join(extraction_dir, "btop.tbz")

    # Save the downloaded file
    with open(download_path, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)

    # Extract the tarball
    with tarfile.open(download_path, "r:bz2") as tar:
        tar.extractall(path=extraction_dir)

    # Change to the source directory
    original_dir = os.getcwd()
    make_dir = f"{extraction_dir}/btop"
    os.chdir(make_dir)

    # Make the file executable
    subprocess.run(["sudo", "make", "install"])

    os.chdir(original_dir)
    shutil.rmtree(extraction_dir)
