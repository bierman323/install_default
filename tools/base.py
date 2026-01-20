"""Abstract base class for tool installers."""

import logging
import subprocess
import shutil
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional

from backup import BackupManager


class ToolInstaller(ABC):
    """Abstract base class for tools requiring special installation."""

    def __init__(self, dry_run: bool = False, backup_manager: Optional[BackupManager] = None):
        """Initialize the tool installer.

        Args:
            dry_run: If True, only log what would be done without making changes.
            backup_manager: BackupManager instance for safe file operations.
        """
        self.dry_run = dry_run
        self.backup_manager = backup_manager or BackupManager(dry_run=dry_run)

    @property
    @abstractmethod
    def name(self) -> str:
        """Name of this tool."""
        pass

    @abstractmethod
    def install(self) -> bool:
        """Install the tool.

        Returns:
            True if installation succeeded.
        """
        pass

    @abstractmethod
    def is_installed(self) -> bool:
        """Check if this tool is already installed.

        Returns:
            True if the tool is installed.
        """
        pass

    def _run_command(self, cmd, check: bool = True,
                     capture_output: bool = True, **kwargs) -> Optional[subprocess.CompletedProcess]:
        """Run a command with proper error handling.

        Args:
            cmd: Command and arguments to run (list or string).
            check: Whether to raise on non-zero exit.
            capture_output: Whether to capture stdout/stderr.
            **kwargs: Additional arguments to subprocess.run.

        Returns:
            CompletedProcess result, or None on error.
        """
        try:
            if isinstance(cmd, str):
                logging.debug(f"Running: {cmd}")
            else:
                logging.debug(f"Running: {' '.join(cmd)}")

            result = subprocess.run(
                cmd,
                check=check,
                capture_output=capture_output,
                text=True,
                **kwargs
            )
            return result
        except subprocess.CalledProcessError as e:
            cmd_str = cmd if isinstance(cmd, str) else ' '.join(cmd)
            logging.error(f"Command failed: {cmd_str}")
            logging.error(f"Exit code: {e.returncode}")
            if e.stderr:
                logging.error(f"Error: {e.stderr}")
            return None
        except FileNotFoundError as e:
            cmd_str = cmd if isinstance(cmd, str) else cmd[0]
            logging.error(f"Command not found: {cmd_str}")
            return None

    def _clone_repo(self, repo_url: str, dest_path: str, depth: int = 1) -> bool:
        """Clone a git repository.

        Args:
            repo_url: URL of the repository to clone.
            dest_path: Destination path for the clone.
            depth: Clone depth (default 1 for shallow clone).

        Returns:
            True if clone succeeded.
        """
        dest = Path(dest_path).expanduser()

        if dest.exists():
            if dest.is_symlink():
                logging.info(f"Removing existing symlink: {dest}")
                if not self.dry_run:
                    dest.unlink()
            else:
                logging.info(f"Directory already exists: {dest}")
                return True

        if self.dry_run:
            logging.info(f"[DRY RUN] Would clone {repo_url} to {dest}")
            return True

        logging.info(f"Cloning {repo_url} to {dest}")

        cmd = ['git', 'clone']
        if depth > 0:
            cmd.extend(['--depth', str(depth)])
        cmd.extend([repo_url, str(dest)])

        result = self._run_command(cmd, check=False)
        if result and result.returncode == 0:
            logging.info(f"Successfully cloned to {dest}")
            return True
        else:
            logging.error(f"Failed to clone {repo_url}")
            return False

    def _ensure_directory(self, path: str) -> bool:
        """Ensure a directory exists.

        Args:
            path: Path to the directory.

        Returns:
            True if directory exists or was created.
        """
        dir_path = Path(path).expanduser()

        if dir_path.exists():
            return True

        if self.dry_run:
            logging.info(f"[DRY RUN] Would create directory: {dir_path}")
            return True

        try:
            dir_path.mkdir(parents=True, exist_ok=True)
            logging.info(f"Created directory: {dir_path}")
            return True
        except OSError as e:
            logging.error(f"Failed to create directory {dir_path}: {e}")
            return False
