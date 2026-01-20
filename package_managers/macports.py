"""MacPorts package manager implementation."""

import logging
import os
import platform
import subprocess
import tempfile
from typing import Optional

from .base import PackageManager


class MacPortsManager(PackageManager):
    """MacPorts package manager for macOS."""

    PACKAGE_MAP = {
        'bat': 'bat',
        'fzf': 'fzf',
        'eza': 'eza',
        'duf': 'duf',
        'ncdu': 'ncdu',
        'zoxide': 'zoxide',
        'yazi': 'yazi',
        'neovim': 'neovim',
        'btop': 'btop',
        'ctags': 'ctags',
        'tmux': 'tmux',
        'vim': 'vim',
        'zsh': 'zsh',
    }

    # MacPorts binary location
    PORT_PATH = '/opt/local/bin/port'

    @property
    def name(self) -> str:
        return "macports"

    @property
    def command(self) -> str:
        return "port"

    def is_available(self) -> bool:
        """Check if MacPorts is available.

        Returns:
            True if MacPorts is installed at the standard location.
        """
        return os.path.exists(self.PORT_PATH)

    def install(self, package: str) -> bool:
        """Install a package using MacPorts.

        Args:
            package: Name of the package to install.

        Returns:
            True if installation succeeded.
        """
        pkg_name = self.get_package_name(package)

        # Check if already installed
        if self._check_installed(package):
            logging.info(f"{package} is already installed")
            return True

        if self.dry_run:
            logging.info(f"[DRY RUN] Would run: sudo port install {pkg_name}")
            return True

        logging.info(f"Installing {pkg_name} via MacPorts")
        result = self._run_command(
            ['sudo', self.PORT_PATH, 'install', pkg_name],
            check=False
        )

        if result and result.returncode == 0:
            logging.info(f"Successfully installed {pkg_name}")
            return True
        else:
            logging.error(f"Failed to install {pkg_name}")
            return False

    def update(self) -> bool:
        """Update MacPorts ports tree.

        Returns:
            True if update succeeded.
        """
        if self.dry_run:
            logging.info("[DRY RUN] Would run: sudo port selfupdate")
            return True

        logging.info("Updating MacPorts")
        result = self._run_command(
            ['sudo', self.PORT_PATH, 'selfupdate'],
            check=False
        )
        return result is not None and result.returncode == 0

    @classmethod
    def install_self(cls, dry_run: bool = False) -> bool:
        """Install MacPorts if not present.

        Args:
            dry_run: If True, only log what would be done.

        Returns:
            True if installation succeeded or already installed.
        """
        # MacPorts is only for macOS
        if platform.system() != 'Darwin':
            logging.error("MacPorts is only available on macOS")
            return False

        # Check if already installed
        if os.path.exists(cls.PORT_PATH):
            logging.info("MacPorts is already installed")
            return True

        # Determine macOS version for correct package
        macos_version = cls._get_macos_version()
        if not macos_version:
            logging.error("Could not determine macOS version")
            return False

        pkg_url = cls._get_macports_pkg_url(macos_version)
        if not pkg_url:
            logging.error(f"No MacPorts package available for macOS {macos_version}")
            return False

        if dry_run:
            logging.info(f"[DRY RUN] Would download and install MacPorts from {pkg_url}")
            return True

        logging.info(f"Installing MacPorts from {pkg_url}")
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                pkg_path = os.path.join(temp_dir, 'MacPorts.pkg')

                # Download the package
                download_result = subprocess.run(
                    ['curl', '-fsSL', '-o', pkg_path, pkg_url],
                    check=True,
                    capture_output=True
                )

                # Install the package
                install_result = subprocess.run(
                    ['sudo', 'installer', '-pkg', pkg_path, '-target', '/'],
                    check=True,
                    capture_output=True
                )

                logging.info("MacPorts installed successfully")

                # Add to PATH for this session
                if cls.PORT_PATH not in os.environ.get('PATH', ''):
                    os.environ['PATH'] = f"/opt/local/bin:/opt/local/sbin:{os.environ.get('PATH', '')}"

                return True

        except subprocess.CalledProcessError as e:
            logging.error(f"Failed to install MacPorts: {e}")
            if e.stderr:
                logging.error(f"Error output: {e.stderr.decode()}")
            return False
        except Exception as e:
            logging.error(f"Unexpected error installing MacPorts: {e}")
            return False

    @classmethod
    def _get_macos_version(cls) -> Optional[str]:
        """Get the macOS version number.

        Returns:
            Version string like '14' for Sonoma, or None on error.
        """
        try:
            result = subprocess.run(
                ['sw_vers', '-productVersion'],
                capture_output=True,
                text=True,
                check=True
            )
            # Get major version (e.g., '14.2.1' -> '14')
            version = result.stdout.strip().split('.')[0]
            return version
        except Exception as e:
            logging.error(f"Failed to get macOS version: {e}")
            return None

    @classmethod
    def _get_macports_pkg_url(cls, macos_version: str) -> Optional[str]:
        """Get the MacPorts package URL for the given macOS version.

        Args:
            macos_version: Major macOS version number.

        Returns:
            URL to download the MacPorts package, or None if unsupported.
        """
        # MacPorts version and macOS codenames
        macports_version = "2.10.5"  # Update as needed

        version_map = {
            '15': 'Sequoia',
            '14': 'Sonoma',
            '13': 'Ventura',
            '12': 'Monterey',
            '11': 'BigSur',
        }

        codename = version_map.get(macos_version)
        if not codename:
            return None

        arch = platform.machine()
        # MacPorts universal packages work for both x86_64 and arm64
        return f"https://github.com/macports/macports-base/releases/download/v{macports_version}/MacPorts-{macports_version}-{macos_version}-{codename}.pkg"
