"""Abstract base class for package managers."""

import logging
import subprocess
import shutil
from abc import ABC, abstractmethod
from typing import Optional, Dict, List


class PackageManager(ABC):
    """Abstract base class for package manager implementations."""

    # Package name mapping: tool_name -> package_name
    # Override in subclasses where names differ
    PACKAGE_MAP: Dict[str, str] = {}

    def __init__(self, dry_run: bool = False):
        """Initialize the package manager.

        Args:
            dry_run: If True, only log what would be done without making changes.
        """
        self.dry_run = dry_run

    @property
    @abstractmethod
    def name(self) -> str:
        """Name of this package manager."""
        pass

    @property
    @abstractmethod
    def command(self) -> str:
        """The command used to invoke this package manager."""
        pass

    @abstractmethod
    def install(self, package: str) -> bool:
        """Install a package.

        Args:
            package: Name of the package to install.

        Returns:
            True if installation succeeded.
        """
        pass

    @abstractmethod
    def update(self) -> bool:
        """Update the package index/tree.

        Returns:
            True if update succeeded.
        """
        pass

    @classmethod
    @abstractmethod
    def install_self(cls, dry_run: bool = False) -> bool:
        """Install this package manager if not present.

        Args:
            dry_run: If True, only log what would be done.

        Returns:
            True if installation succeeded or already installed.
        """
        pass

    def is_available(self) -> bool:
        """Check if this package manager is available on the system.

        Returns:
            True if the package manager is installed and accessible.
        """
        return shutil.which(self.command) is not None

    def get_package_name(self, tool: str) -> str:
        """Get the package name for a tool (may differ by manager).

        Args:
            tool: The tool/application name.

        Returns:
            The package name to use with this manager.
        """
        return self.PACKAGE_MAP.get(tool, tool)

    def install_packages(self, packages: List[str]) -> Dict[str, bool]:
        """Install multiple packages.

        Args:
            packages: List of package names to install.

        Returns:
            Dict mapping package name to success status.
        """
        results = {}
        for pkg in packages:
            results[pkg] = self.install(pkg)
        return results

    def _run_command(self, cmd: List[str], check: bool = True,
                     capture_output: bool = True) -> Optional[subprocess.CompletedProcess]:
        """Run a command with proper error handling.

        Args:
            cmd: Command and arguments to run.
            check: Whether to raise on non-zero exit.
            capture_output: Whether to capture stdout/stderr.

        Returns:
            CompletedProcess result, or None on error.
        """
        try:
            logging.debug(f"Running: {' '.join(cmd)}")
            result = subprocess.run(
                cmd,
                check=check,
                capture_output=capture_output,
                text=True
            )
            return result
        except subprocess.CalledProcessError as e:
            logging.error(f"Command failed: {' '.join(cmd)}")
            logging.error(f"Exit code: {e.returncode}")
            if e.stderr:
                logging.error(f"Error: {e.stderr}")
            return None
        except FileNotFoundError:
            logging.error(f"Command not found: {cmd[0]}")
            return None

    def _check_installed(self, tool: str) -> bool:
        """Check if a tool is already installed.

        Args:
            tool: Name of the tool to check.

        Returns:
            True if the tool is available in PATH.
        """
        return shutil.which(tool) is not None
