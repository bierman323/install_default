"""Tmux Plugin Manager installer."""

import logging
from pathlib import Path

from .base import ToolInstaller


class TpmInstaller(ToolInstaller):
    """Installer for Tmux Plugin Manager (TPM)."""

    TPM_DIR = Path.home() / '.tmux' / 'plugins' / 'tpm'
    TPM_REPO = 'https://github.com/tmux-plugins/tpm.git'

    @property
    def name(self) -> str:
        return "tpm"

    def is_installed(self) -> bool:
        """Check if TPM is already installed.

        Returns:
            True if TPM directory exists.
        """
        return self.TPM_DIR.exists()

    def install(self) -> bool:
        """Install TPM by cloning the repository.

        Returns:
            True if installation succeeded.
        """
        if self.is_installed():
            logging.info("Tmux Plugin Manager is already installed")
            return True

        logging.info("Installing Tmux Plugin Manager")

        # Ensure the plugins directory exists
        plugins_dir = self.TPM_DIR.parent
        if not self.dry_run:
            plugins_dir.mkdir(parents=True, exist_ok=True)

        # Clone the repository
        success = self._clone_repo(self.TPM_REPO, str(self.TPM_DIR), depth=1)

        if success:
            logging.info("Tmux Plugin Manager installed successfully")
            logging.info("Note: Press prefix + I in tmux to install plugins")

        return success
