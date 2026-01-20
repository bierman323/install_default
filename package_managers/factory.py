"""Factory functions for package manager selection."""

import logging
import platform
from typing import Optional, List, Type

from .base import PackageManager
from .brew import BrewManager
from .macports import MacPortsManager
from .apt import AptManager
from .dnf import DnfManager


def detect_available_managers(dry_run: bool = False) -> List[PackageManager]:
    """Detect which package managers are available on this system.

    Args:
        dry_run: If True, pass to manager constructors.

    Returns:
        List of available PackageManager instances.
    """
    available = []
    system = platform.system()

    # Check platform-specific managers
    if system == 'Darwin':
        # macOS
        macports = MacPortsManager(dry_run=dry_run)
        if macports.is_available():
            available.append(macports)

        brew = BrewManager(dry_run=dry_run)
        if brew.is_available():
            available.append(brew)

    else:
        # Linux
        brew = BrewManager(dry_run=dry_run)
        if brew.is_available():
            available.append(brew)

        apt = AptManager(dry_run=dry_run)
        if apt.is_available():
            available.append(apt)

        dnf = DnfManager(dry_run=dry_run)
        if dnf.is_available():
            available.append(dnf)

    return available


def get_package_manager(
    preferred: Optional[str] = None,
    dry_run: bool = False,
    auto_install: bool = True
) -> Optional[PackageManager]:
    """Get the appropriate package manager for this system.

    Args:
        preferred: Preferred package manager name ('brew', 'macports', etc.)
        dry_run: If True, pass to manager constructor.
        auto_install: If True, attempt to install the preferred manager if missing.

    Returns:
        PackageManager instance, or None if none available.
    """
    system = platform.system()

    # If a specific manager is preferred, try to use it
    if preferred:
        manager = _get_manager_by_name(preferred, dry_run)
        if manager and manager.is_available():
            logging.info(f"Using preferred package manager: {manager.name}")
            return manager

        # Try to install it if auto_install is enabled
        if auto_install:
            manager_class = _get_manager_class(preferred)
            if manager_class:
                logging.info(f"Preferred manager {preferred} not found, attempting to install...")
                if manager_class.install_self(dry_run=dry_run):
                    manager = manager_class(dry_run=dry_run)
                    if manager.is_available():
                        return manager

        logging.warning(f"Preferred package manager '{preferred}' is not available")

    # Auto-detect based on platform and preference hierarchy
    return _auto_detect_manager(dry_run, auto_install)


def _get_manager_by_name(name: str, dry_run: bool = False) -> Optional[PackageManager]:
    """Get a package manager instance by name.

    Args:
        name: Manager name ('brew', 'macports', 'apt', 'dnf').
        dry_run: If True, pass to constructor.

    Returns:
        PackageManager instance or None.
    """
    manager_class = _get_manager_class(name)
    if manager_class:
        return manager_class(dry_run=dry_run)
    return None


def _get_manager_class(name: str) -> Optional[Type[PackageManager]]:
    """Get a package manager class by name.

    Args:
        name: Manager name ('brew', 'macports', 'apt', 'dnf').

    Returns:
        PackageManager class or None.
    """
    name_lower = name.lower()
    managers = {
        'brew': BrewManager,
        'homebrew': BrewManager,
        'macports': MacPortsManager,
        'port': MacPortsManager,
        'apt': AptManager,
        'apt-get': AptManager,
        'dnf': DnfManager,
        'yum': DnfManager,
    }
    return managers.get(name_lower)


def _auto_detect_manager(dry_run: bool = False, auto_install: bool = True) -> Optional[PackageManager]:
    """Auto-detect the best package manager for this system.

    Priority:
    - macOS: prefer brew, fallback to macports
    - Linux: prefer brew, fallback to apt/dnf

    Args:
        dry_run: If True, pass to manager constructors.
        auto_install: If True, attempt to install brew if missing.

    Returns:
        PackageManager instance or None.
    """
    system = platform.system()

    if system == 'Darwin':
        # macOS: try brew first (more packages, newer versions)
        brew = BrewManager(dry_run=dry_run)
        if brew.is_available():
            logging.info("Using Homebrew on macOS")
            return brew

        # Try macports
        macports = MacPortsManager(dry_run=dry_run)
        if macports.is_available():
            logging.info("Using MacPorts on macOS")
            return macports

        # Neither available - try to install brew if auto_install
        if auto_install:
            logging.info("No package manager found on macOS, attempting to install Homebrew...")
            if BrewManager.install_self(dry_run=dry_run):
                return BrewManager(dry_run=dry_run)

        logging.error("No package manager available on macOS")
        return None

    else:
        # Linux: prefer brew for newer versions
        brew = BrewManager(dry_run=dry_run)
        if brew.is_available():
            logging.info("Using Homebrew on Linux")
            return brew

        # Fallback to system package managers
        apt = AptManager(dry_run=dry_run)
        if apt.is_available():
            logging.info("Using APT (consider installing Homebrew for newer package versions)")
            return apt

        dnf = DnfManager(dry_run=dry_run)
        if dnf.is_available():
            logging.info("Using DNF (consider installing Homebrew for newer package versions)")
            return dnf

        # No system manager - try to install brew if auto_install
        if auto_install:
            logging.info("No package manager found, attempting to install Homebrew...")
            if BrewManager.install_self(dry_run=dry_run):
                return BrewManager(dry_run=dry_run)

        logging.error("No package manager available")
        return None
