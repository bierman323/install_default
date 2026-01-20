"""Profile dataclass definition."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Profile:
    """Configuration profile for installation environments.

    Attributes:
        name: Profile identifier (lab, work, personal)
        description: Human-readable description of the profile
        preferred_package_manager: Preferred package manager ('brew', 'macports', or None for auto)

        Core tools:
        install_vim: Whether to install and configure vim
        install_tmux: Whether to install and configure tmux
        install_zsh: Whether to install and configure zsh
        install_ctags: Whether to install universal-ctags

        Shell enhancements:
        install_eza: Whether to install eza (modern ls replacement)
        install_bat: Whether to install bat (cat with syntax highlighting)
        install_fzf: Whether to install fzf (fuzzy finder)
        install_zoxide: Whether to install zoxide (smart cd replacement)

        System utilities:
        install_btop: Whether to install btop (system monitor)
        install_duf: Whether to install duf (modern df replacement)
        install_ncdu: Whether to install ncdu (disk usage analyzer)

        Advanced tools:
        install_yazi: Whether to install yazi (terminal file manager)
        install_neovim: Whether to install neovim

        Shell frameworks:
        install_powerlevel10k: Whether to install powerlevel10k zsh theme
        install_tpm: Whether to install tmux plugin manager

        Repository integrations:
        run_config_sync: Whether to clone and setup config-sync repo
        clone_scripts: Whether to clone scripts repo to ~/bin

        Options:
        change_default_shell: Whether to change default shell to zsh
        install_vundle_plugins: Whether to install vim plugins via Vundle

    Note: Existing configs are ALWAYS backed up before replacement for safety.
    """
    name: str
    description: str

    # Package manager preference
    preferred_package_manager: Optional[str] = None  # 'brew', 'macports', or None for auto

    # Core tools
    install_vim: bool = True
    install_tmux: bool = True
    install_zsh: bool = True
    install_ctags: bool = True

    # Shell enhancements
    install_eza: bool = True
    install_bat: bool = True
    install_fzf: bool = True
    install_zoxide: bool = True

    # System utilities
    install_btop: bool = True
    install_duf: bool = True
    install_ncdu: bool = True

    # Advanced tools
    install_yazi: bool = True
    install_neovim: bool = False

    # Shell frameworks
    install_powerlevel10k: bool = True
    install_tpm: bool = True

    # Repository integrations
    run_config_sync: bool = True
    clone_scripts: bool = True

    # Options
    change_default_shell: bool = True
    install_vundle_plugins: bool = True
    # NOTE: backup_existing removed - ALWAYS backup for safety

    def copy(self, **overrides) -> 'Profile':
        """Create a copy of this profile with optional overrides."""
        from dataclasses import asdict
        data = asdict(self)
        data.update(overrides)
        return Profile(**data)

    def to_dict(self) -> dict:
        """Convert profile to dictionary."""
        from dataclasses import asdict
        return asdict(self)
