"""Powerlevel10k theme installer."""

import logging
from pathlib import Path

from .base import ToolInstaller


class Powerlevel10kInstaller(ToolInstaller):
    """Installer for Powerlevel10k Zsh theme."""

    P10K_DIR = Path.home() / '.oh-my-zsh' / 'custom' / 'themes' / 'powerlevel10k'
    P10K_REPO = 'https://github.com/romkatv/powerlevel10k.git'

    @property
    def name(self) -> str:
        return "powerlevel10k"

    def is_installed(self) -> bool:
        """Check if Powerlevel10k is already installed.

        Returns:
            True if Powerlevel10k directory exists.
        """
        return self.P10K_DIR.exists()

    def install(self) -> bool:
        """Install Powerlevel10k by cloning the repository.

        Returns:
            True if installation succeeded.
        """
        if self.is_installed():
            logging.info("Powerlevel10k is already installed")
            return True

        # Check if Oh-My-Zsh is installed
        omz_dir = Path.home() / '.oh-my-zsh'
        if not omz_dir.exists() and not self.dry_run:
            logging.error("Oh-My-Zsh is not installed. Install it first.")
            return False

        logging.info("Installing Powerlevel10k theme")

        # Ensure the themes directory exists
        themes_dir = self.P10K_DIR.parent
        if not self.dry_run:
            themes_dir.mkdir(parents=True, exist_ok=True)

        # Clone the repository with depth 1 for speed
        success = self._clone_repo(self.P10K_REPO, str(self.P10K_DIR), depth=1)

        if success:
            logging.info("Powerlevel10k installed successfully")
            logging.info("Note: Set ZSH_THEME=\"powerlevel10k/powerlevel10k\" in .zshrc")

        return success
