"""Backup manager for safe file operations."""

import os
import shutil
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, List


class BackupManager:
    """Manages backups of existing config files before replacement.

    All existing configs are ALWAYS backed up before replacement for safety.
    Backups are stored in ~/.config-backup/YYYYMMDD-HHMMSS/
    """

    def __init__(self, dry_run: bool = False):
        """Initialize the backup manager.

        Args:
            dry_run: If True, only log what would be done without making changes.
        """
        self.dry_run = dry_run
        self.backup_dir: Optional[Path] = None
        self.backed_up_files: List[str] = []
        self._initialized = False

    def _ensure_backup_dir(self) -> Path:
        """Create the timestamped backup directory if needed.

        Returns:
            Path to the backup directory.
        """
        if self.backup_dir is not None:
            return self.backup_dir

        base_dir = Path.home() / '.config-backup'
        timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
        self.backup_dir = base_dir / timestamp

        if not self.dry_run:
            self.backup_dir.mkdir(parents=True, exist_ok=True)
            logging.info(f"Created backup directory: {self.backup_dir}")
        else:
            logging.info(f"[DRY RUN] Would create backup directory: {self.backup_dir}")

        self._initialized = True
        return self.backup_dir

    def backup_file(self, file_path: str) -> bool:
        """Backup a single file if it exists and is not a symlink.

        Args:
            file_path: Path to the file to backup.

        Returns:
            True if backup was made (or would be made in dry-run), False otherwise.
        """
        path = Path(file_path).expanduser()

        if not path.exists():
            logging.debug(f"File does not exist, no backup needed: {path}")
            return False

        if path.is_symlink():
            # It's a symlink from a previous install - just remove it
            if self.dry_run:
                logging.info(f"[DRY RUN] Would remove existing symlink: {path}")
            else:
                path.unlink()
                logging.info(f"Removed existing symlink: {path}")
            return False

        # File exists and is not a symlink - back it up
        backup_dir = self._ensure_backup_dir()

        # Preserve directory structure relative to home
        home = Path.home()
        try:
            rel_path = path.relative_to(home)
        except ValueError:
            # File is not under home, use absolute path structure
            rel_path = Path(str(path).lstrip('/'))

        dest = backup_dir / rel_path

        if self.dry_run:
            logging.info(f"[DRY RUN] Would backup: {path} -> {dest}")
        else:
            dest.parent.mkdir(parents=True, exist_ok=True)
            if path.is_dir():
                shutil.copytree(path, dest)
            else:
                shutil.copy2(path, dest)
            logging.info(f"Backed up: {path} -> {dest}")

        self.backed_up_files.append(str(path))
        return True

    def backup_directory(self, dir_path: str) -> bool:
        """Backup an entire directory if it exists and is not a symlink.

        Args:
            dir_path: Path to the directory to backup.

        Returns:
            True if backup was made (or would be made in dry-run), False otherwise.
        """
        return self.backup_file(dir_path)  # Same logic works for directories

    def safe_symlink(self, source: str, target: str) -> bool:
        """Create a symlink after backing up any existing file.

        Args:
            source: Path to the source file (what the symlink points to).
            target: Path where the symlink will be created.

        Returns:
            True if symlink was created successfully.
        """
        target_path = Path(target).expanduser()
        source_path = Path(source).expanduser()

        # Backup existing file if needed
        self.backup_file(target)

        # Remove target if it still exists (shouldn't happen but safety check)
        if target_path.exists() or target_path.is_symlink():
            if self.dry_run:
                logging.info(f"[DRY RUN] Would remove existing: {target_path}")
            else:
                if target_path.is_dir() and not target_path.is_symlink():
                    shutil.rmtree(target_path)
                else:
                    target_path.unlink()

        # Create the symlink
        if self.dry_run:
            logging.info(f"[DRY RUN] Would symlink: {target_path} -> {source_path}")
            return True

        try:
            target_path.parent.mkdir(parents=True, exist_ok=True)
            target_path.symlink_to(source_path)
            logging.info(f"Created symlink: {target_path} -> {source_path}")
            return True
        except OSError as e:
            logging.error(f"Failed to create symlink {target_path}: {e}")
            return False

    def safe_copy(self, source: str, target: str) -> bool:
        """Copy a file after backing up any existing file at target.

        Args:
            source: Path to the source file to copy.
            target: Path where the file will be copied.

        Returns:
            True if copy was successful.
        """
        target_path = Path(target).expanduser()
        source_path = Path(source).expanduser()

        # Backup existing file if needed
        self.backup_file(target)

        if self.dry_run:
            logging.info(f"[DRY RUN] Would copy: {source_path} -> {target_path}")
            return True

        try:
            target_path.parent.mkdir(parents=True, exist_ok=True)
            if source_path.is_dir():
                shutil.copytree(source_path, target_path)
            else:
                shutil.copy2(source_path, target_path)
            logging.info(f"Copied: {source_path} -> {target_path}")
            return True
        except (OSError, shutil.Error) as e:
            logging.error(f"Failed to copy {source_path} to {target_path}: {e}")
            return False

    def get_restore_instructions(self) -> str:
        """Get instructions for restoring backed up files.

        Returns:
            String with restore instructions, or empty if no backups made.
        """
        if not self.backed_up_files or self.backup_dir is None:
            return ""

        instructions = [
            "",
            "=" * 50,
            "BACKUP INFORMATION",
            "=" * 50,
            f"Backed up {len(self.backed_up_files)} file(s) to:",
            f"  {self.backup_dir}",
            "",
            "To restore original configs:",
            f"  cp -r {self.backup_dir}/* ~/",
            "",
            "Backed up files:",
        ]
        for f in self.backed_up_files:
            instructions.append(f"  - {f}")
        instructions.append("=" * 50)

        return "\n".join(instructions)

    def print_restore_instructions(self) -> None:
        """Print restore instructions to stdout if backups were made."""
        instructions = self.get_restore_instructions()
        if instructions:
            print(instructions)
