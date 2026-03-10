#!/usr/bin/env python3
"""Multi-environment system setup script.

Supports three environment profiles (lab, work, personal) with both
interactive and non-interactive modes for Ansible automation.

Features:
- Package manager abstraction (brew, macports, apt, dnf)
- Auto-installation of package managers
- Profile-based tool selection
- Always-on backup for safety
- Repository integrations (configs, config-sync, scripts)
"""

import argparse
import platform
import sys
import os
import subprocess
import logging
import shutil
from dataclasses import dataclass, field
from typing import Optional, List

from profiles import Profile, get_profile, list_profiles
from output import OutputFormatter, InstallResult, ExitCode
from ui import InteractivePrompts, is_interactive
from backup import BackupManager
from package_managers import get_package_manager, PackageManager
from tools import (
    OhMyZshInstaller,
    Powerlevel10kInstaller,
    TpmInstaller,
    VundleInstaller,
    ConfigSyncInstaller,
    ScriptsRepoInstaller,
)

__version__ = '3.0.0'


@dataclass
class InstallContext:
    """Global installation context."""
    path: str = ''
    config_path: str = ''
    os_type: str = ''
    home: str = ''
    dry_run: bool = False
    result: Optional[InstallResult] = None
    formatter: Optional[OutputFormatter] = None
    backup_manager: Optional[BackupManager] = None
    package_manager: Optional[PackageManager] = None
    github_clone: str = 'https://github.com/bierman323/configs.git'


ctx = InstallContext()


def setup_logging(quiet: bool = False, verbose: bool = False):
    """Configure logging based on output preferences."""
    log_dir = f'{ctx.home}/.code'
    os.makedirs(log_dir, exist_ok=True)
    log_file = f'{log_dir}/install.log'

    level = logging.DEBUG if verbose else logging.INFO
    handlers = [logging.FileHandler(log_file)]

    if not quiet:
        handlers.append(logging.StreamHandler())

    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=handlers,
        force=True
    )
    logging.info("Starting installation script v%s", __version__)


def setup_package_manager(preferred: Optional[str] = None) -> bool:
    """Initialize the package manager.

    Args:
        preferred: Preferred package manager name from profile.

    Returns:
        True if package manager is available.
    """
    ctx.package_manager = get_package_manager(
        preferred=preferred,
        dry_run=ctx.dry_run,
        auto_install=True
    )

    if ctx.package_manager is None:
        logging.error("No package manager available")
        return False

    logging.info(f"Using package manager: {ctx.package_manager.name}")
    return True


def setup_os():
    """Initialize OS-specific paths and settings."""
    ctx.home = os.path.expanduser("~")
    ctx.path = f'{ctx.home}/.code'
    ctx.os_type = platform.system()

    try:
        os.makedirs(ctx.path, exist_ok=True)
        logging.info(f"Setup directory: {ctx.path}")
    except OSError as e:
        logging.error(f"Failed to create directory {ctx.path}: {e}")
        sys.exit(ExitCode.COMPLETE_FAILURE)


def setup_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Multi-environment system setup script',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                           # Interactive mode
  %(prog)s --profile lab -y          # Lab VM, non-interactive
  %(prog)s --profile work -y         # Work computer (MacPorts)
  %(prog)s --profile personal -y     # Personal, full install (Homebrew)
  %(prog)s --vim --tmux -y           # Selective install (backward compat)
  %(prog)s --profile lab --dry-run   # See what would happen
  %(prog)s --profile work -y -o json # JSON output for Ansible
        """
    )

    # Profile selection
    profile_group = parser.add_argument_group('Profile selection')
    profile_group.add_argument(
        '-p', '--profile',
        choices=['lab', 'work', 'personal'],
        help='Environment profile (lab, work, personal)'
    )
    profile_group.add_argument(
        '--list-profiles',
        action='store_true',
        help='List available profiles and exit'
    )

    # Execution modes
    mode_group = parser.add_argument_group('Execution modes')
    mode_group.add_argument(
        '-y', '--non-interactive',
        action='store_true',
        help='Skip all prompts (for Ansible/automation)'
    )
    mode_group.add_argument(
        '-n', '--dry-run',
        action='store_true',
        help='Show what would happen without making changes'
    )

    # Output control
    output_group = parser.add_argument_group('Output control')
    output_group.add_argument(
        '-o', '--output-format',
        choices=['text', 'json'],
        default='text',
        help='Output format (default: text)'
    )
    output_group.add_argument(
        '-q', '--quiet',
        action='store_true',
        help='Suppress non-essential output'
    )
    output_group.add_argument(
        '--verbose',
        action='store_true',
        help='Enable debug logging'
    )

    # Package manager override
    parser.add_argument(
        '--package-manager',
        choices=['auto', 'brew', 'macports'],
        default='auto',
        help='Package manager to use (default: auto from profile)'
    )

    # Component overrides
    override_group = parser.add_argument_group('Component overrides')
    override_group.add_argument(
        '--no-shell-change',
        action='store_true',
        help="Don't change default shell to zsh"
    )
    override_group.add_argument(
        '--no-vundle-plugins',
        action='store_true',
        help='Skip Vundle plugin installation'
    )
    # Tool skip flags
    override_group.add_argument('--no-bat', action='store_true', help='Skip bat installation')
    override_group.add_argument('--no-fzf', action='store_true', help='Skip fzf installation')
    override_group.add_argument('--no-zoxide', action='store_true', help='Skip zoxide installation')
    override_group.add_argument('--no-yazi', action='store_true', help='Skip yazi installation')
    override_group.add_argument('--no-neovim', action='store_true', help='Skip neovim installation')
    override_group.add_argument('--no-powerlevel10k', action='store_true', help='Skip powerlevel10k installation')
    override_group.add_argument('--no-tpm', action='store_true', help='Skip tpm installation')
    override_group.add_argument('--no-config-sync', action='store_true', help='Skip config-sync setup')
    override_group.add_argument('--no-scripts', action='store_true', help='Skip scripts repo clone')

    # Legacy component selection (backward compatibility)
    legacy_group = parser.add_argument_group('Component selection (legacy)')
    legacy_group.add_argument('-v', '--vim', action='store_true', help='Configure VIM only')
    legacy_group.add_argument('-t', '--tmux', action='store_true', help='Configure TMUX only')
    legacy_group.add_argument('-z', '--zsh', action='store_true', help='Configure ZSH only')

    # Info commands
    parser.add_argument(
        '--version',
        action='version',
        version=f'%(prog)s {__version__}'
    )

    return parser.parse_args()


def install_package(package: str) -> bool:
    """Install a package using the configured package manager."""
    if ctx.package_manager is None:
        logging.error("No package manager configured")
        return False

    return ctx.package_manager.install(package)


def check_git() -> bool:
    """Ensure git is installed and clone/update configs."""
    ctx.config_path = f'{ctx.path}/configs'

    if not install_package('git'):
        logging.error("Failed to install git, cannot continue")
        return False

    if ctx.dry_run:
        if not os.path.exists(ctx.config_path):
            logging.info(f"[DRY RUN] Would clone configs from {ctx.github_clone}")
        else:
            logging.info("[DRY RUN] Would update existing configs with git pull")
        return True

    try:
        if not os.path.exists(ctx.config_path):
            logging.info(f"Cloning configs from {ctx.github_clone}")
            subprocess.run(
                ['git', 'clone', ctx.github_clone, ctx.config_path],
                check=True,
                capture_output=True
            )
        else:
            logging.info("Updating existing configs")
            subprocess.run(
                ['git', '-C', ctx.config_path, 'pull', '--rebase'],
                check=True,
                capture_output=True
            )

        # Symlink .gitignore
        dst_file = f'{ctx.home}/.gitignore'
        path_to_rc = f'{ctx.config_path}/.gitignore'
        ctx.backup_manager.safe_symlink(path_to_rc, dst_file)
        logging.info("Symlinked .gitignore")
        return True

    except subprocess.CalledProcessError as e:
        logging.error(f"Git operation failed: {e}")
        return False


def check_vim(install_plugins: bool = True) -> bool:
    """Install and configure vim."""
    logging.info("Setting up Vim")

    if not install_package('vim'):
        logging.error("Failed to install vim")
        return False

    # Install Vundle
    vundle = VundleInstaller(dry_run=ctx.dry_run, backup_manager=ctx.backup_manager)
    if not vundle.install():
        return False

    # Symlink .vimrc
    dst_file = f'{ctx.home}/.vimrc'
    path_to_rc = f'{ctx.config_path}/.vimrc'

    if not ctx.backup_manager.safe_symlink(path_to_rc, dst_file):
        return False

    logging.info("Symlinked .vimrc")

    # Install plugins
    if install_plugins:
        vundle.install_plugins()

    return True


def check_tmux() -> bool:
    """Install and configure tmux."""
    logging.info("Setting up Tmux")

    if not install_package('tmux'):
        logging.error("Failed to install tmux")
        return False

    # Symlink .tmux.conf
    path_to_rc = f'{ctx.config_path}/.tmux.conf'
    dst_file = f'{ctx.home}/.tmux.conf'

    if not ctx.backup_manager.safe_symlink(path_to_rc, dst_file):
        return False

    logging.info("Symlinked .tmux.conf")
    return True


def check_zsh(change_shell: bool = True) -> bool:
    """Install and configure zsh."""
    logging.info("Setting up Zsh")

    # Install zsh and dependencies
    for pkg in ['zsh', 'bzip2', 'make']:
        if not install_package(pkg):
            logging.warning(f"Failed to install {pkg}")

    # Install Oh-My-Zsh
    omz = OhMyZshInstaller(dry_run=ctx.dry_run, backup_manager=ctx.backup_manager)
    if not omz.install():
        logging.error("Failed to install Oh-My-Zsh")
        return False

    # Create symlinks for zsh configs
    zsh_files = ['.zshrc', '.zshrc_eza', '.zshrc_ohmyzsh']
    for item in zsh_files:
        source_path = f'{ctx.config_path}/{item}'
        dest_path = f'{ctx.home}/{item}'
        if os.path.exists(source_path) or ctx.dry_run:
            ctx.backup_manager.safe_symlink(source_path, dest_path)
            logging.info(f"Symlinked {item}")

    # Symlink custom Oh-My-Zsh theme
    path_oh = f'{ctx.home}/.local/oh-my-zsh'
    os.environ['ZSH'] = path_oh
    theme_src = f'{ctx.config_path}/bierman-fino.zsh-theme'
    theme_dst = f'{path_oh}/themes/bierman-fino.zsh-theme'
    if os.path.exists(theme_src) or ctx.dry_run:
        ctx.backup_manager.safe_symlink(theme_src, theme_dst)
        logging.info("Symlinked custom Oh-My-Zsh theme")

    # Change default shell if requested
    if change_shell:
        return change_default_shell()

    return True


def change_default_shell() -> bool:
    """Change the default shell to zsh."""
    if ctx.dry_run:
        logging.info("[DRY RUN] Would change default shell to zsh")
        return True

    try:
        which_zsh = subprocess.check_output(['which', 'zsh'], text=True).strip()
        logging.info(f"Changing default shell to: {which_zsh}")
        subprocess.run(['sudo', 'chsh', '-s', which_zsh], check=True)
        logging.info("Default shell changed to zsh")
        return True
    except subprocess.CalledProcessError as e:
        logging.error(f"Failed to change default shell: {e}")
        return False


def install_shell_enhancements(profile: Profile) -> dict:
    """Install shell enhancement tools based on profile.

    Returns:
        Dict mapping tool name to success status.
    """
    results = {}

    # Tools that can be installed via package manager
    tools = [
        ('eza', profile.install_eza),
        ('bat', profile.install_bat),
        ('fzf', profile.install_fzf),
        ('zoxide', profile.install_zoxide),
    ]

    for tool, enabled in tools:
        if enabled:
            logging.info(f"Installing {tool}")
            results[tool] = install_package(tool)
        else:
            results[tool] = True  # Skipped is not a failure

    return results


def install_system_utilities(profile: Profile) -> dict:
    """Install system utility tools based on profile.

    Returns:
        Dict mapping tool name to success status.
    """
    results = {}

    tools = [
        ('btop', profile.install_btop),
        ('duf', profile.install_duf),
        ('ncdu', profile.install_ncdu),
    ]

    for tool, enabled in tools:
        if enabled:
            logging.info(f"Installing {tool}")
            results[tool] = install_package(tool)
        else:
            results[tool] = True

    return results


def install_advanced_tools(profile: Profile) -> dict:
    """Install advanced tools based on profile.

    Returns:
        Dict mapping tool name to success status.
    """
    results = {}

    tools = [
        ('yazi', profile.install_yazi),
        ('neovim', profile.install_neovim),
    ]

    for tool, enabled in tools:
        if enabled:
            logging.info(f"Installing {tool}")
            results[tool] = install_package(tool)
        else:
            results[tool] = True

    return results


def install_shell_frameworks(profile: Profile) -> dict:
    """Install shell frameworks based on profile.

    Returns:
        Dict mapping framework name to success status.
    """
    results = {}

    # Powerlevel10k
    if profile.install_powerlevel10k:
        p10k = Powerlevel10kInstaller(dry_run=ctx.dry_run, backup_manager=ctx.backup_manager)
        results['powerlevel10k'] = p10k.install()
    else:
        results['powerlevel10k'] = True

    # TPM (Tmux Plugin Manager)
    if profile.install_tpm:
        tpm = TpmInstaller(dry_run=ctx.dry_run, backup_manager=ctx.backup_manager)
        results['tpm'] = tpm.install()
    else:
        results['tpm'] = True

    return results


def install_ctags() -> bool:
    """Install universal-ctags."""
    logging.info("Setting up ctags")

    if not install_package('ctags'):
        logging.warning("Failed to install ctags")
        return False
    return True


def setup_repositories(profile: Profile) -> dict:
    """Setup repository integrations based on profile.

    Returns:
        Dict mapping repo name to success status.
    """
    results = {}

    # Config-sync repository
    if profile.run_config_sync:
        config_sync = ConfigSyncInstaller(dry_run=ctx.dry_run, backup_manager=ctx.backup_manager)
        results['config-sync'] = config_sync.install()
    else:
        results['config-sync'] = True

    # Scripts repository
    if profile.clone_scripts:
        scripts = ScriptsRepoInstaller(dry_run=ctx.dry_run, backup_manager=ctx.backup_manager)
        results['scripts'] = scripts.install()
    else:
        results['scripts'] = True

    return results


def apply_cli_overrides(profile: Profile, args) -> Profile:
    """Apply CLI overrides to profile settings."""
    overrides = {}

    if args.no_shell_change:
        overrides['change_default_shell'] = False
    if args.no_vundle_plugins:
        overrides['install_vundle_plugins'] = False
    if args.no_bat:
        overrides['install_bat'] = False
    if args.no_fzf:
        overrides['install_fzf'] = False
    if args.no_zoxide:
        overrides['install_zoxide'] = False
    if args.no_yazi:
        overrides['install_yazi'] = False
    if args.no_neovim:
        overrides['install_neovim'] = False
    if args.no_powerlevel10k:
        overrides['install_powerlevel10k'] = False
    if args.no_tpm:
        overrides['install_tpm'] = False
    if args.no_config_sync:
        overrides['run_config_sync'] = False
    if args.no_scripts:
        overrides['clone_scripts'] = False

    if overrides:
        return profile.copy(**overrides)
    return profile


def run_with_profile(profile: Profile, args):
    """Run installation with a specific profile."""
    ctx.result = InstallResult(
        dry_run=ctx.dry_run,
        profile=profile.name
    )

    # Apply CLI overrides
    profile = apply_cli_overrides(profile, args)

    # Determine package manager preference
    pkg_mgr_pref = profile.preferred_package_manager
    if args.package_manager != 'auto':
        pkg_mgr_pref = args.package_manager

    # Setup package manager
    if not setup_package_manager(preferred=pkg_mgr_pref):
        ctx.result.add_error("Failed to setup package manager")
        return

    # Make sure we have git and configs
    if not check_git():
        ctx.result.add_error("Git setup failed")
        return

    # Install core tools
    if profile.install_vim:
        success = check_vim(install_plugins=profile.install_vundle_plugins)
        ctx.result.add_component('vim', success,
                                 "Vim setup failed" if not success else None)

    if profile.install_tmux:
        success = check_tmux()
        ctx.result.add_component('tmux', success,
                                 "Tmux setup failed" if not success else None)

    if profile.install_zsh:
        success = check_zsh(change_shell=profile.change_default_shell)
        ctx.result.add_component('zsh', success,
                                 "Zsh setup failed" if not success else None)

    if profile.install_ctags:
        success = install_ctags()
        ctx.result.add_component('ctags', success,
                                 "ctags setup failed" if not success else None)

    # Install shell enhancements
    shell_results = install_shell_enhancements(profile)
    for tool, success in shell_results.items():
        if getattr(profile, f'install_{tool}', False):
            ctx.result.add_component(tool, success,
                                     f"{tool} installation failed" if not success else None)

    # Install system utilities
    util_results = install_system_utilities(profile)
    for tool, success in util_results.items():
        if getattr(profile, f'install_{tool}', False):
            ctx.result.add_component(tool, success,
                                     f"{tool} installation failed" if not success else None)

    # Install advanced tools
    advanced_results = install_advanced_tools(profile)
    for tool, success in advanced_results.items():
        if getattr(profile, f'install_{tool}', False):
            ctx.result.add_component(tool, success,
                                     f"{tool} installation failed" if not success else None)

    # Install shell frameworks
    framework_results = install_shell_frameworks(profile)
    for framework, success in framework_results.items():
        attr_name = f'install_{framework}'
        if getattr(profile, attr_name, False):
            ctx.result.add_component(framework, success,
                                     f"{framework} installation failed" if not success else None)

    # Setup repositories
    repo_results = setup_repositories(profile)
    for repo, success in repo_results.items():
        if repo == 'config-sync' and profile.run_config_sync:
            ctx.result.add_component(repo, success,
                                     f"{repo} setup failed" if not success else None)
        elif repo == 'scripts' and profile.clone_scripts:
            ctx.result.add_component(repo, success,
                                     f"{repo} setup failed" if not success else None)


def run_legacy_mode(args):
    """Run in legacy mode with individual component flags."""
    ctx.result = InstallResult(dry_run=ctx.dry_run)

    # Setup package manager (auto-detect)
    if not setup_package_manager():
        ctx.result.add_error("Failed to setup package manager")
        return

    # Make sure we have git and configs
    if not check_git():
        ctx.result.add_error("Git setup failed")
        return

    if args.vim:
        success = check_vim()
        ctx.result.add_component('vim', success)

    if args.tmux:
        success = check_tmux()
        ctx.result.add_component('tmux', success)

    if args.zsh:
        success = check_zsh()
        ctx.result.add_component('zsh', success)


def run_full_install(args):
    """Run full installation (all components)."""
    profile = get_profile('personal')
    run_with_profile(profile, args)


def main():
    """Main entry point."""
    # Parse arguments first
    args = setup_args()

    # Initialize OS paths (needed for logging)
    setup_os()

    # Setup output formatter
    ctx.formatter = OutputFormatter(
        format_type=args.output_format,
        quiet=args.quiet
    )

    # Handle --list-profiles
    if args.list_profiles:
        print(ctx.formatter.format_profiles(list_profiles()))
        sys.exit(ExitCode.SUCCESS)

    # Setup logging
    setup_logging(quiet=args.quiet, verbose=args.verbose)

    logging.info(f"Running on {ctx.os_type}")
    logging.info(f"Home directory: {ctx.home}")

    # Set dry-run mode
    ctx.dry_run = args.dry_run
    if ctx.dry_run:
        logging.info("DRY RUN MODE - No changes will be made")

    # Initialize backup manager (always enabled for safety)
    ctx.backup_manager = BackupManager(dry_run=ctx.dry_run)
    logging.info("Backup manager initialized (backups enabled)")

    # Determine execution mode
    has_legacy_flags = args.vim or args.tmux or args.zsh
    has_profile = args.profile is not None

    if has_profile:
        # Profile-based installation
        profile = get_profile(args.profile)
        run_with_profile(profile, args)

    elif has_legacy_flags:
        # Legacy mode: individual component flags
        run_legacy_mode(args)

    elif args.non_interactive:
        # Non-interactive without profile = full install
        run_full_install(args)

    elif is_interactive():
        # Interactive mode
        prompts = InteractivePrompts()
        profile = prompts.run_interactive_setup()

        if profile is None:
            sys.exit(ExitCode.SUCCESS)

        run_with_profile(profile, args)

    else:
        # Non-interactive terminal without profile = full install
        run_full_install(args)

    # Print backup information
    ctx.backup_manager.print_restore_instructions()

    # Output results
    if ctx.result:
        output = ctx.formatter.format_result(ctx.result)
        if output:
            print(output)

        exit_code = ctx.result.get_exit_code()
        logging.info(f"Exit code: {exit_code}")
        sys.exit(exit_code)

    logging.info("Installation complete!")
    sys.exit(ExitCode.SUCCESS)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        logging.info("\nInstallation interrupted by user")
        sys.exit(0)
    except Exception as e:
        logging.error(f"Unexpected error: {e}", exc_info=True)
        sys.exit(ExitCode.COMPLETE_FAILURE)
