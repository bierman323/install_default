"""Config-sync repository installer."""

import logging
import os
from pathlib import Path
from typing import Optional

from .base import ToolInstaller
from backup import BackupManager


class ConfigSyncInstaller(ToolInstaller):
    """Installer for config-sync repository with app configurations."""

    CONFIG_SYNC_DIR = Path.home() / '.config-sync'
    CONFIG_SYNC_REPO = 'https://github.com/bierman323/config-sync.git'

    # Mapping of config-sync directories to their targets
    # Source (relative to config-sync) -> Target (absolute or relative to home)
    CONFIG_MAPPINGS = {
        'btop': '.config/btop',
        'yazi': '.config/yazi',
        'powerline': '.config/powerline',
        'git': None,  # Special handling for git configs
    }

    @property
    def name(self) -> str:
        return "config-sync"

    def is_installed(self) -> bool:
        """Check if config-sync repository is already cloned.

        Returns:
            True if config-sync directory exists.
        """
        return self.CONFIG_SYNC_DIR.exists()

    def install(self) -> bool:
        """Clone config-sync repository and setup symlinks.

        Returns:
            True if installation succeeded.
        """
        # Clone the repository if not present
        if not self.is_installed():
            logging.info("Installing config-sync repository")
            success = self._clone_repo(self.CONFIG_SYNC_REPO, str(self.CONFIG_SYNC_DIR), depth=1)
            if not success:
                return False
        else:
            logging.info("config-sync repository already exists")

        # Setup symlinks for app configs
        return self._setup_symlinks()

    def _setup_symlinks(self) -> bool:
        """Setup symlinks for app configurations.

        Returns:
            True if symlinks were created successfully.
        """
        success = True

        for source_name, target_rel in self.CONFIG_MAPPINGS.items():
            if target_rel is None:
                # Special handling needed
                continue

            source = self.CONFIG_SYNC_DIR / source_name
            target = Path.home() / target_rel

            if not source.exists() and not self.dry_run:
                logging.debug(f"Source config not found, skipping: {source}")
                continue

            # Use backup manager for safe symlink creation
            if not self.backup_manager.safe_symlink(str(source), str(target)):
                logging.warning(f"Failed to create symlink for {source_name}")
                success = False
            else:
                logging.info(f"Linked {source_name} config")

        return success

    def setup_git_config(self) -> bool:
        """Setup git configurations from config-sync.

        Returns:
            True if git config was setup successfully.
        """
        git_dir = self.CONFIG_SYNC_DIR / 'git'

        if not git_dir.exists() and not self.dry_run:
            logging.debug("No git config in config-sync, skipping")
            return True

        # Common git config files to symlink
        git_files = ['.gitconfig', '.gitignore_global']

        success = True
        for filename in git_files:
            source = git_dir / filename.lstrip('.')
            target = Path.home() / filename

            if source.exists() or self.dry_run:
                if not self.backup_manager.safe_symlink(str(source), str(target)):
                    logging.warning(f"Failed to create symlink for {filename}")
                    success = False

        return success
