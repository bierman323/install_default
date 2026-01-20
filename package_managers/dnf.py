"""DNF package manager implementation for RHEL/Fedora."""

import logging

from .base import PackageManager


class DnfManager(PackageManager):
    """DNF package manager for RHEL/Fedora systems."""

    PACKAGE_MAP = {
        'bat': 'bat',
        'fzf': 'fzf',
        # eza not in dnf repos - needs GitHub release or brew
        'duf': 'duf',
        'ncdu': 'ncdu',
        # zoxide not in dnf repos on most versions
        # yazi not in dnf repos - needs GitHub release or brew
        'neovim': 'neovim',
        'btop': 'btop',
        'ctags': 'ctags',
        'tmux': 'tmux',
        'vim': 'vim-enhanced',
        'zsh': 'zsh',
    }

    # Tools that need to be installed via other means on dnf
    UNAVAILABLE_TOOLS = {'eza', 'zoxide', 'yazi'}

    @property
    def name(self) -> str:
        return "dnf"

    @property
    def command(self) -> str:
        return "dnf"

    def install(self, package: str) -> bool:
        """Install a package using DNF.

        Args:
            package: Name of the package to install.

        Returns:
            True if installation succeeded.
        """
        # Some tools aren't available in dnf
        if package in self.UNAVAILABLE_TOOLS:
            logging.warning(f"{package} is not available in dnf repositories")
            logging.warning("Consider using Homebrew for newer tool versions")
            return False

        pkg_name = self.get_package_name(package)

        # Check if already installed
        if self._check_installed(package):
            logging.info(f"{package} is already installed")
            return True

        if self.dry_run:
            logging.info(f"[DRY RUN] Would run: sudo dnf install -y {pkg_name}")
            return True

        logging.info(f"Installing {pkg_name} via DNF")
        result = self._run_command(
            ['sudo', 'dnf', 'install', '-y', pkg_name],
            check=False
        )

        if result and result.returncode == 0:
            logging.info(f"Successfully installed {pkg_name}")
            return True
        else:
            logging.error(f"Failed to install {pkg_name}")
            return False

    def update(self) -> bool:
        """Update DNF package cache.

        Returns:
            True if update succeeded.
        """
        if self.dry_run:
            logging.info("[DRY RUN] Would run: sudo dnf check-update")
            return True

        logging.info("Updating DNF package cache")
        # dnf check-update returns 100 if updates are available
        result = self._run_command(
            ['sudo', 'dnf', 'check-update'],
            check=False
        )
        # Return code 0 = no updates, 100 = updates available, other = error
        return result is not None and result.returncode in (0, 100)

    @classmethod
    def install_self(cls, dry_run: bool = False) -> bool:
        """DNF is a system package manager and cannot be installed.

        Returns:
            True if DNF is available, False otherwise.
        """
        instance = cls(dry_run=dry_run)
        if instance.is_available():
            logging.info("DNF is available")
            return True
        logging.error("DNF is not available on this system")
        return False
