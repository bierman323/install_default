"""Oh-My-Zsh installer."""

import logging
import os
from pathlib import Path

from .base import ToolInstaller


class OhMyZshInstaller(ToolInstaller):
    """Installer for Oh-My-Zsh framework."""

    OMZ_DIR = Path.home() / '.oh-my-zsh'
    OMZ_REPO = 'https://github.com/ohmyzsh/ohmyzsh.git'

    @property
    def name(self) -> str:
        return "oh-my-zsh"

    def is_installed(self) -> bool:
        """Check if Oh-My-Zsh is already installed.

        Returns:
            True if Oh-My-Zsh directory exists.
        """
        return self.OMZ_DIR.exists()

    def install(self) -> bool:
        """Install Oh-My-Zsh by cloning the repository.

        Returns:
            True if installation succeeded.
        """
        if self.is_installed():
            logging.info("Oh-My-Zsh is already installed")
            return True

        logging.info("Installing Oh-My-Zsh")

        # Clone the repository
        success = self._clone_repo(self.OMZ_REPO, str(self.OMZ_DIR))

        if success and not self.dry_run:
            # Make sure custom directories exist
            custom_dir = self.OMZ_DIR / 'custom'
            themes_dir = custom_dir / 'themes'
            plugins_dir = custom_dir / 'plugins'

            for d in [themes_dir, plugins_dir]:
                d.mkdir(parents=True, exist_ok=True)

            logging.info("Oh-My-Zsh installed successfully")

        return success
