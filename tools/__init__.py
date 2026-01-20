"""Tool installers module for special installations."""

from .base import ToolInstaller
from .oh_my_zsh import OhMyZshInstaller
from .powerlevel10k import Powerlevel10kInstaller
from .tpm import TpmInstaller
from .vundle import VundleInstaller
from .config_sync import ConfigSyncInstaller
from .scripts_repo import ScriptsRepoInstaller

__all__ = [
    'ToolInstaller',
    'OhMyZshInstaller',
    'Powerlevel10kInstaller',
    'TpmInstaller',
    'VundleInstaller',
    'ConfigSyncInstaller',
    'ScriptsRepoInstaller',
]
