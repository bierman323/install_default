#!/usr/bin/env python3
"""btop installation module with dry-run support."""

import os
import requests
import tarfile
import subprocess
import platform
import shutil
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


def check_btop_installed():
    """Check if btop is already installed."""
    btop_path = shutil.which('btop')
    if btop_path:
        try:
            result = subprocess.run(['btop', '--version'], capture_output=True, text=True)
            version = result.stdout.split()[1] if result.stdout else "unknown"
            logging.info(f"btop already installed: {version} at {btop_path}")
            return True
        except Exception:
            return False
    return False


def get_latest_btop_version():
    """Get the latest btop version from GitHub API."""
    try:
        response = requests.get('https://api.github.com/repos/aristocratos/btop/releases/latest', timeout=10)
        response.raise_for_status()
        version = response.json()['tag_name']
        logging.info(f"Latest btop version: {version}")
        return version
    except Exception as e:
        logging.warning(f"Failed to get latest version, using default: {e}")
        return "v1.4.0"


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


def get_btop(dry_run: bool = False):
    """Install btop with proper error handling and cleanup.

    Args:
        dry_run: If True, only log what would be done without making changes.

    Returns:
        True if installation succeeded (or would succeed in dry-run mode).
    """
    logging.info("Setting up btop")

    # Check if already installed
    if check_btop_installed():
        return True

    # Get normalized architecture
    arch = get_normalized_arch()
    logging.info(f"Detected architecture: {arch}")

    # Get latest version
    version = get_latest_btop_version()

    if dry_run:
        url = f"https://github.com/aristocratos/btop/releases/download/{version}/btop-{arch}-linux-musl.tbz"
        logging.info(f"[DRY RUN] Would download btop {version} from {url}")
        logging.info("[DRY RUN] Would extract and run 'sudo make install'")
        return True

    # Create temp directory for downloads
    with tempfile.TemporaryDirectory() as temp_dir:
        try:
            # URL of the file to download
            url = f"https://github.com/aristocratos/btop/releases/download/{version}/btop-{arch}-linux-musl.tbz"
            tar_path = os.path.join(temp_dir, "btop.tbz")

            # Download with retry
            if not download_with_retry(url, tar_path):
                logging.error("Failed to download btop")
                return False

            # Extract the tarball
            logging.info("Extracting btop")
            with tarfile.open(tar_path, "r:bz2") as tar:
                tar.extractall(path=temp_dir)

            # Change to the extracted directory
            make_dir = os.path.join(temp_dir, "btop")
            if not os.path.exists(make_dir):
                logging.error(f"Extracted directory not found: {make_dir}")
                return False

            original_dir = os.getcwd()
            os.chdir(make_dir)

            # Run make install
            logging.info("Installing btop")
            subprocess.run(["sudo", "make", "install"], check=True)

            os.chdir(original_dir)
            logging.info("btop installed successfully")
            return True

        except tarfile.TarError as e:
            logging.error(f"Failed to extract btop: {e}")
            return False
        except subprocess.CalledProcessError as e:
            logging.error(f"Failed to install btop: {e}")
            return False
        except Exception as e:
            logging.error(f"Unexpected error installing btop: {e}")
            return False

    # Temp directory automatically cleaned up
