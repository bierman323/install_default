"""Scripts repository installer."""

import logging
import os
import stat
from pathlib import Path

from .base import ToolInstaller


class ScriptsRepoInstaller(ToolInstaller):
    """Installer for scripts repository to ~/bin."""

    SCRIPTS_DIR = Path.home() / 'bin'
    SCRIPTS_REPO = 'https://github.com/bierman323/scripts.git'

    @property
    def name(self) -> str:
        return "scripts"

    def is_installed(self) -> bool:
        """Check if scripts repository is already cloned.

        Returns:
            True if bin directory exists and is a git repo.
        """
        git_dir = self.SCRIPTS_DIR / '.git'
        return git_dir.exists()

    def install(self) -> bool:
        """Clone scripts repository to ~/bin.

        Returns:
            True if installation succeeded.
        """
        if self.is_installed():
            logging.info("Scripts repository already exists in ~/bin")
            return self._update_repo()

        # Backup existing ~/bin if it exists and is not the repo
        if self.SCRIPTS_DIR.exists():
            logging.info("Backing up existing ~/bin directory")
            self.backup_manager.backup_directory(str(self.SCRIPTS_DIR))

            # Remove the existing directory after backup
            if not self.dry_run:
                import shutil
                shutil.rmtree(self.SCRIPTS_DIR)

        logging.info("Cloning scripts repository to ~/bin")
        success = self._clone_repo(self.SCRIPTS_REPO, str(self.SCRIPTS_DIR), depth=1)

        if success:
            # Make scripts executable
            self._make_scripts_executable()
            logging.info("Scripts repository installed to ~/bin")

        return success

    def _update_repo(self) -> bool:
        """Update the existing scripts repository.

        Returns:
            True if update succeeded.
        """
        if self.dry_run:
            logging.info("[DRY RUN] Would run: git pull in ~/bin")
            return True

        logging.info("Updating scripts repository")

        result = self._run_command(
            ['git', '-C', str(self.SCRIPTS_DIR), 'pull', '--ff-only'],
            check=False
        )

        if result and result.returncode == 0:
            logging.info("Scripts repository updated")
            self._make_scripts_executable()
            return True
        else:
            logging.warning("Failed to update scripts repository (may have local changes)")
            return True  # Don't fail the install for this

    def _make_scripts_executable(self) -> None:
        """Make all shell scripts in ~/bin executable."""
        if self.dry_run:
            logging.info("[DRY RUN] Would make scripts executable")
            return

        for script in self.SCRIPTS_DIR.iterdir():
            if script.is_file() and script.suffix in ('.sh', ''):
                # Check if it looks like a script (has shebang or .sh extension)
                try:
                    with open(script, 'r') as f:
                        first_line = f.readline()

                    if script.suffix == '.sh' or first_line.startswith('#!'):
                        # Make executable
                        current = script.stat().st_mode
                        script.chmod(current | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
                        logging.debug(f"Made executable: {script.name}")
                except (IOError, UnicodeDecodeError):
                    # Not a text file, skip
                    pass
