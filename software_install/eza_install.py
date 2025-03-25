#!/usr/bin/env python3

import os
import requests
import tarfile
import shutil
import subprocess
import platform

def get_eza():
    arch = platform.machine()

    # URL of the file to download
    url = f"https://github.com/eza-community/eza/releases/latest/download/eza_{arch}-unknown-linux-gnu.tar.gz"

    # Download the file
    response = requests.get(url, stream=True)
    response.raise_for_status()  # Raise an exception for HTTP errors

    # Save the downloaded file
    with open("eza.tar.gz", "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)

    # Extract the tarball
    with tarfile.open("eza.tar.gz", "r:gz") as tar:
        tar.extractall()

    # Make the file executable
    subprocess.run(["sudo", "chmod", "+x", "eza"], check=True)

    # Change ownership to root
    subprocess.run(["sudo", "chown", "root:root", "eza"], check=True)

    # Move to /usr/local/bin
    subprocess.run(["sudo", "mv", "eza", "/usr/local/bin/eza"], check=True)

    # Optional: Clean up the downloaded tarball
    os.remove("eza.tar.gz")