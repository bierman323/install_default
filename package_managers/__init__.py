"""Package manager abstraction module."""

from .base import PackageManager
from .brew import BrewManager
from .macports import MacPortsManager
from .apt import AptManager
from .dnf import DnfManager
from .factory import get_package_manager, detect_available_managers

__all__ = [
    'PackageManager',
    'BrewManager',
    'MacPortsManager',
    'AptManager',
    'DnfManager',
    'get_package_manager',
    'detect_available_managers',
]
