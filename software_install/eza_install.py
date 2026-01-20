#!/usr/bin/env python3
"""eza installation module with dry-run support."""

import os
import requests
import tarfile
import shutil
import subprocess
import platform
import tempfile
import logging
import time

# Architecture mapping
ARCH_MAP = {
    'x86_64': 'x86_64',
    'amd64': 'x86_64',
    'aarch64': 'aarch64',
    'arm64': 'aarch64',
    'armv7l': 'armv7'
}


def get_normalized_arch():
    """Get architecture in format GitHub uses."""
    arch = platform.machine().lower()
    return ARCH_MAP.get(arch, arch)


def check_eza_installed():
    """Check if eza is already installed."""
    eza_path = shutil.which('eza')
    if eza_path:
        try:
            result = subprocess.run(['eza', '--version'], capture_output=True, text=True)
            version = result.stdout.split()[0] if result.stdout else "unknown"
            logging.info(f"eza already installed: {version} at {eza_path}")
            return True
        except Exception:
            return False
    return False


def download_with_retry(url, dest_path, max_retries=3):
    """Download file with exponential backoff retry."""
    for attempt in range(max_retries):
        try:
            logging.info(f"Downloading from {url} (attempt {attempt + 1}/{max_retries})")
            response = requests.get(url, stream=True, timeout=30)
            response.raise_for_status()

            with open(dest_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            logging.info("Download complete")
            return True

        except requests.RequestException as e:
            logging.warning(f"Download attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                sleep_time = 2 ** attempt
                logging.info(f"Retrying in {sleep_time} seconds...")
                time.sleep(sleep_time)
            else:
                logging.error("Max retries reached")
                return False

    return False


def get_eza(dry_run: bool = False):
    """Install eza with proper error handling and cleanup.

    Args:
        dry_run: If True, only log what would be done without making changes.

    Returns:
        True if installation succeeded (or would succeed in dry-run mode).
    """
    logging.info("Setting up eza")

    # Check if already installed
    if check_eza_installed():
        return True

    # Get normalized architecture
    arch = get_normalized_arch()
    logging.info(f"Detected architecture: {arch}")

    if dry_run:
        url = f"https://github.com/eza-community/eza/releases/latest/download/eza_{arch}-unknown-linux-gnu.tar.gz"
        logging.info(f"[DRY RUN] Would download eza from {url}")
        logging.info("[DRY RUN] Would extract and install to /usr/local/bin/eza")
        return True

    # Create temp directory for downloads
    with tempfile.TemporaryDirectory() as temp_dir:
        try:
            # URL of the file to download
            url = f"https://github.com/eza-community/eza/releases/latest/download/eza_{arch}-unknown-linux-gnu.tar.gz"
            tar_path = os.path.join(temp_dir, "eza.tar.gz")
            extract_path = os.path.join(temp_dir, "eza")

            # Download with retry
            if not download_with_retry(url, tar_path):
                logging.error("Failed to download eza")
                return False

            # Extract the tarball
            logging.info("Extracting eza")
            with tarfile.open(tar_path, "r:gz") as tar:
                tar.extractall(temp_dir)

            # Make the file executable
            subprocess.run(["chmod", "+x", extract_path], check=True)

            # Move to /usr/local/bin with sudo
            subprocess.run(["sudo", "mv", extract_path, "/usr/local/bin/eza"], check=True)
            subprocess.run(["sudo", "chown", "root:root", "/usr/local/bin/eza"], check=True)

            logging.info("eza installed successfully")
            return True

        except tarfile.TarError as e:
            logging.error(f"Failed to extract eza: {e}")
            return False
        except subprocess.CalledProcessError as e:
            logging.error(f"Failed to install eza: {e}")
            return False
        except Exception as e:
            logging.error(f"Unexpected error installing eza: {e}")
            return False

    # Temp directory automatically cleaned up
