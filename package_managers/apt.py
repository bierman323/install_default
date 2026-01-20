"""APT package manager implementation for Debian/Ubuntu."""

import logging

from .base import PackageManager


class AptManager(PackageManager):
    """APT package manager for Debian/Ubuntu systems."""

    PACKAGE_MAP = {
        'bat': 'bat',
        'fzf': 'fzf',
        # eza not in apt repos - needs GitHub release or brew
        'duf': 'duf',
        'ncdu': 'ncdu',
        # zoxide not in apt repos - needs GitHub release or brew
        # yazi not in apt repos - needs GitHub release or brew
        'neovim': 'neovim',
        'btop': 'btop',
        'ctags': 'universal-ctags',
        'tmux': 'tmux',
        'vim': 'vim',
        'zsh': 'zsh',
    }

    # Tools that need to be installed via other means on apt
    UNAVAILABLE_TOOLS = {'eza', 'zoxide', 'yazi'}

    @property
    def name(self) -> str:
        return "apt"

    @property
    def command(self) -> str:
        return "apt-get"

    def install(self, package: str) -> bool:
        """Install a package using APT.

        Args:
            package: Name of the package to install.

        Returns:
            True if installation succeeded.
        """
        # Some tools aren't available in apt
        if package in self.UNAVAILABLE_TOOLS:
            logging.warning(f"{package} is not available in apt repositories")
            logging.warning("Consider using Homebrew for newer tool versions")
            return False

        pkg_name = self.get_package_name(package)

        # Check if already installed
        if self._check_installed(package):
            logging.info(f"{package} is already installed")
            return True

        if self.dry_run:
            logging.info(f"[DRY RUN] Would run: sudo apt-get install -y {pkg_name}")
            return True

        logging.info(f"Installing {pkg_name} via APT")
        result = self._run_command(
            ['sudo', 'apt-get', 'install', '-y', pkg_name],
            check=False
        )

        if result and result.returncode == 0:
            logging.info(f"Successfully installed {pkg_name}")
            return True
        else:
            logging.error(f"Failed to install {pkg_name}")
            return False

    def update(self) -> bool:
        """Update APT package index.

        Returns:
            True if update succeeded.
        """
        if self.dry_run:
            logging.info("[DRY RUN] Would run: sudo apt-get update")
            return True

        logging.info("Updating APT package index")
        result = self._run_command(
            ['sudo', 'apt-get', 'update'],
            check=False
        )
        return result is not None and result.returncode == 0

    @classmethod
    def install_self(cls, dry_run: bool = False) -> bool:
        """APT is a system package manager and cannot be installed.

        Returns:
            True if APT is available, False otherwise.
        """
        instance = cls(dry_run=dry_run)
        if instance.is_available():
            logging.info("APT is available")
            return True
        logging.error("APT is not available on this system")
        return False
