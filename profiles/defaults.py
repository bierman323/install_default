"""Built-in profile definitions."""

from .base import Profile

# Lab profile: Fast ephemeral setup for security research VMs
LAB = Profile(
    name='lab',
    description='Fast ephemeral setup for lab/research VMs (created weekly, destroyed)',
    preferred_package_manager='brew',  # Install brew on Linux

    # Core tools
    install_vim=True,
    install_tmux=True,
    install_zsh=True,
    install_ctags=True,

    # Shell enhancements - minimal set
    install_eza=True,
    install_bat=True,
    install_fzf=True,
    install_zoxide=True,

    # System utilities
    install_btop=True,       # Included for system monitoring
    install_duf=False,       # Skip for speed
    install_ncdu=False,      # Skip for speed

    # Advanced tools - skip for speed
    install_yazi=False,
    install_neovim=False,

    # Shell frameworks
    install_powerlevel10k=False,  # Use simpler theme for speed
    install_tpm=True,             # Included for tmux plugins

    # Repository integrations
    run_config_sync=False,   # Skip for ephemeral VMs
    clone_scripts=True,      # Clone scripts to ~/bin

    # Options
    change_default_shell=True,
    install_vundle_plugins=False,  # Skip for speed
)

# Work profile: Long-term workstation using MacPorts
WORK = Profile(
    name='work',
    description='Work Mac setup using MacPorts (full features)',
    preferred_package_manager='macports',  # MUST use MacPorts

    # Core tools
    install_vim=True,
    install_tmux=True,
    install_zsh=True,
    install_ctags=True,

    # Shell enhancements
    install_eza=True,
    install_bat=True,
    install_fzf=True,
    install_zoxide=True,

    # System utilities
    install_btop=True,
    install_duf=True,
    install_ncdu=True,

    # Advanced tools
    install_yazi=True,
    install_neovim=True,

    # Shell frameworks
    install_powerlevel10k=True,
    install_tpm=True,

    # Repository integrations
    run_config_sync=True,
    clone_scripts=True,

    # Options
    change_default_shell=False,  # May need approval at work
    install_vundle_plugins=True,
)

# Personal profile: Full customization with Homebrew
PERSONAL = Profile(
    name='personal',
    description='Full installation with all features for personal machines',
    preferred_package_manager='brew',  # Use Homebrew

    # Core tools
    install_vim=True,
    install_tmux=True,
    install_zsh=True,
    install_ctags=True,

    # Shell enhancements
    install_eza=True,
    install_bat=True,
    install_fzf=True,
    install_zoxide=True,

    # System utilities
    install_btop=True,
    install_duf=True,
    install_ncdu=True,

    # Advanced tools
    install_yazi=True,
    install_neovim=True,

    # Shell frameworks
    install_powerlevel10k=True,
    install_tpm=True,

    # Repository integrations
    run_config_sync=True,
    clone_scripts=True,

    # Options
    change_default_shell=True,
    install_vundle_plugins=True,
)

# Profile registry
_PROFILES = {
    'lab': LAB,
    'work': WORK,
    'personal': PERSONAL,
}


def get_profile(name: str) -> Profile:
    """Get a profile by name.

    Args:
        name: Profile name (lab, work, personal)

    Returns:
        Profile instance

    Raises:
        ValueError: If profile name is not recognized
    """
    name = name.lower()
    if name not in _PROFILES:
        valid = ', '.join(_PROFILES.keys())
        raise ValueError(f"Unknown profile '{name}'. Valid profiles: {valid}")
    return _PROFILES[name].copy()


def list_profiles() -> list:
    """List all available profiles.

    Returns:
        List of (name, description) tuples
    """
    return [(p.name, p.description) for p in _PROFILES.values()]
