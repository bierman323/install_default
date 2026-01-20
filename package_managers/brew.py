"""Homebrew package manager implementation."""

import logging
import os
import platform
import subprocess
from typing import Optional

from .base import PackageManager


class BrewManager(PackageManager):
    """Homebrew package manager for macOS and Linux."""

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
        'ctags': 'universal-ctags',
        'tmux': 'tmux',
        'vim': 'vim',
        'zsh': 'zsh',
    }

    @property
    def name(self) -> str:
        return "homebrew"

    @property
    def command(self) -> str:
        return "brew"

    def install(self, package: str) -> bool:
        """Install a package using Homebrew.

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
            logging.info(f"[DRY RUN] Would run: brew install {pkg_name}")
            return True

        logging.info(f"Installing {pkg_name} via Homebrew")
        result = self._run_command(['brew', 'install', pkg_name], check=False)

        if result and result.returncode == 0:
            logging.info(f"Successfully installed {pkg_name}")
            return True
        else:
            logging.error(f"Failed to install {pkg_name}")
            return False

    def update(self) -> bool:
        """Update Homebrew package index.

        Returns:
            True if update succeeded.
        """
        if self.dry_run:
            logging.info("[DRY RUN] Would run: brew update")
            return True

        logging.info("Updating Homebrew")
        result = self._run_command(['brew', 'update'], check=False)
        return result is not None and result.returncode == 0

    @classmethod
    def install_self(cls, dry_run: bool = False) -> bool:
        """Install Homebrew if not present.

        Args:
            dry_run: If True, only log what would be done.

        Returns:
            True if installation succeeded or already installed.
        """
        # Check if already installed
        instance = cls(dry_run=dry_run)
        if instance.is_available():
            logging.info("Homebrew is already installed")
            return True

        install_url = "https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh"

        if dry_run:
            logging.info(f"[DRY RUN] Would install Homebrew from {install_url}")
            return True

        logging.info("Installing Homebrew...")
        try:
            # Download and run the install script
            result = subprocess.run(
                ['/bin/bash', '-c', f'$(curl -fsSL {install_url})'],
                shell=True,
                env={**os.environ, 'NONINTERACTIVE': '1'},
                check=False
            )

            if result.returncode == 0:
                logging.info("Homebrew installed successfully")
                # Add to PATH for this session
                cls._add_to_path()
                return True
            else:
                logging.error(f"Homebrew installation failed with code {result.returncode}")
                return False

        except Exception as e:
            logging.error(f"Failed to install Homebrew: {e}")
            return False

    @classmethod
    def _add_to_path(cls) -> None:
        """Add Homebrew to PATH for this session."""
        system = platform.system()
        arch = platform.machine()

        if system == 'Darwin':
            if arch == 'arm64':
                brew_path = '/opt/homebrew/bin'
            else:
                brew_path = '/usr/local/bin'
        else:  # Linux
            brew_path = '/home/linuxbrew/.linuxbrew/bin'

        if brew_path not in os.environ.get('PATH', ''):
            os.environ['PATH'] = f"{brew_path}:{os.environ.get('PATH', '')}"
            logging.debug(f"Added {brew_path} to PATH")

    def get_brew_prefix(self) -> Optional[str]:
        """Get the Homebrew prefix path.

        Returns:
            The Homebrew prefix path, or None if not available.
        """
        result = self._run_command(['brew', '--prefix'], check=False)
        if result and result.returncode == 0:
            return result.stdout.strip()
        return None
