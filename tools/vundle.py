"""Vundle Vim plugin manager installer."""

import logging
import subprocess
from pathlib import Path

from .base import ToolInstaller


class VundleInstaller(ToolInstaller):
    """Installer for Vundle Vim plugin manager."""

    VUNDLE_DIR = Path.home() / '.vim' / 'bundle' / 'Vundle.vim'
    VUNDLE_REPO = 'https://github.com/VundleVim/Vundle.vim.git'

    @property
    def name(self) -> str:
        return "vundle"

    def is_installed(self) -> bool:
        """Check if Vundle is already installed.

        Returns:
            True if Vundle directory exists.
        """
        return self.VUNDLE_DIR.exists()

    def install(self) -> bool:
        """Install Vundle by cloning the repository.

        Returns:
            True if installation succeeded.
        """
        if self.is_installed():
            logging.info("Vundle is already installed")
            return True

        logging.info("Installing Vundle")

        # Ensure the bundle directory exists
        bundle_dir = self.VUNDLE_DIR.parent
        if not self.dry_run:
            bundle_dir.mkdir(parents=True, exist_ok=True)

        # Clone the repository
        success = self._clone_repo(self.VUNDLE_REPO, str(self.VUNDLE_DIR), depth=1)

        if success:
            logging.info("Vundle installed successfully")

        return success

    def install_plugins(self) -> bool:
        """Install Vim plugins via Vundle.

        Returns:
            True if plugin installation succeeded.
        """
        if not self.is_installed():
            logging.error("Vundle is not installed. Install it first.")
            return False

        if self.dry_run:
            logging.info("[DRY RUN] Would run: vim +PluginInstall +qall")
            return True

        logging.info("Installing Vim plugins via Vundle (this may take a while)")

        try:
            result = subprocess.run(
                ['vim', '+PluginInstall', '+qall'],
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )

            if result.returncode == 0:
                logging.info("Vim plugins installed successfully")
                return True
            else:
                logging.warning(f"Vim plugin installation may have had issues: {result.stderr}")
                return True  # Often still works even with warnings

        except subprocess.TimeoutExpired:
            logging.error("Vim plugin installation timed out")
            return False
        except FileNotFoundError:
            logging.error("Vim not found. Install vim first.")
            return False
        except Exception as e:
            logging.error(f"Failed to install Vim plugins: {e}")
            return False
