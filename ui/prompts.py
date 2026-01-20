"""Interactive prompt system for user configuration."""

import sys
from typing import Optional, List, Tuple
from profiles import Profile, list_profiles, get_profile


def is_interactive() -> bool:
    """Check if running in an interactive terminal.

    Returns:
        True if stdin is a terminal, False otherwise
    """
    return sys.stdin.isatty()


class InteractivePrompts:
    """Handles interactive prompts for installation configuration."""

    def __init__(self):
        """Initialize the interactive prompts handler."""
        self._profile: Optional[Profile] = None

    def prompt_yes_no(self, question: str, default: bool = True) -> bool:
        """Ask a yes/no question.

        Args:
            question: Question to ask
            default: Default answer if user presses Enter

        Returns:
            True for yes, False for no
        """
        suffix = " [Y/n]: " if default else " [y/N]: "
        while True:
            try:
                response = input(question + suffix).strip().lower()
                if not response:
                    return default
                if response in ('y', 'yes'):
                    return True
                if response in ('n', 'no'):
                    return False
                print("Please enter 'y' or 'n'")
            except EOFError:
                return default

    def prompt_choice(self, question: str, choices: List[Tuple[str, str]],
                      default: Optional[str] = None) -> str:
        """Ask user to choose from options.

        Args:
            question: Question to ask
            choices: List of (value, description) tuples
            default: Default choice value

        Returns:
            Selected value
        """
        print(f"\n{question}")
        for i, (value, description) in enumerate(choices, 1):
            marker = "*" if value == default else " "
            print(f"  {marker}{i}. {value:10} - {description}")

        default_num = None
        if default:
            for i, (v, _) in enumerate(choices, 1):
                if v == default:
                    default_num = i
                    break

        prompt = f"Enter choice [1-{len(choices)}]"
        if default_num:
            prompt += f" (default: {default_num})"
        prompt += ": "

        while True:
            try:
                response = input(prompt).strip()
                if not response and default_num:
                    return choices[default_num - 1][0]
                try:
                    num = int(response)
                    if 1 <= num <= len(choices):
                        return choices[num - 1][0]
                except ValueError:
                    # Try matching by name
                    for value, _ in choices:
                        if response.lower() == value.lower():
                            return value
                print(f"Please enter a number between 1 and {len(choices)}")
            except EOFError:
                if default_num:
                    return choices[default_num - 1][0]
                return choices[0][0]

    def prompt_profile(self) -> Profile:
        """Prompt user to select an environment profile.

        Returns:
            Selected Profile instance
        """
        print("\n" + "=" * 50)
        print("System Setup - Environment Selection")
        print("=" * 50)

        profiles = list_profiles()
        choice = self.prompt_choice(
            "What type of system is this?",
            profiles,
            default='personal'
        )

        self._profile = get_profile(choice)
        return self._profile

    def prompt_components(self, profile: Profile) -> Profile:
        """Prompt user to customize component selection.

        Args:
            profile: Base profile to customize

        Returns:
            Modified Profile with user selections
        """
        print("\n" + "-" * 50)
        print("Component Selection")
        print("-" * 50)
        print(f"Base profile: {profile.name} - {profile.description}")
        print("\nCustomize components (press Enter for defaults):\n")

        # Core components
        print("Core Tools:")
        components = [
            ('install_vim', '  Install and configure Vim', profile.install_vim),
            ('install_tmux', '  Install and configure Tmux', profile.install_tmux),
            ('install_zsh', '  Install and configure Zsh', profile.install_zsh),
            ('install_ctags', '  Install universal-ctags', profile.install_ctags),
        ]

        overrides = {}
        for attr, description, default in components:
            overrides[attr] = self.prompt_yes_no(description, default)

        # Shell enhancements
        print("\nShell Enhancements:")
        shell_components = [
            ('install_eza', '  Install eza (modern ls)', profile.install_eza),
            ('install_bat', '  Install bat (syntax highlighting)', profile.install_bat),
            ('install_fzf', '  Install fzf (fuzzy finder)', profile.install_fzf),
            ('install_zoxide', '  Install zoxide (smart cd)', profile.install_zoxide),
        ]

        for attr, description, default in shell_components:
            overrides[attr] = self.prompt_yes_no(description, default)

        # System utilities
        print("\nSystem Utilities:")
        util_components = [
            ('install_btop', '  Install btop (system monitor)', profile.install_btop),
            ('install_duf', '  Install duf (disk usage)', profile.install_duf),
            ('install_ncdu', '  Install ncdu (disk analyzer)', profile.install_ncdu),
        ]

        for attr, description, default in util_components:
            overrides[attr] = self.prompt_yes_no(description, default)

        # Advanced tools
        print("\nAdvanced Tools:")
        advanced_components = [
            ('install_yazi', '  Install yazi (file manager)', profile.install_yazi),
            ('install_neovim', '  Install neovim', profile.install_neovim),
        ]

        for attr, description, default in advanced_components:
            overrides[attr] = self.prompt_yes_no(description, default)

        # Shell frameworks
        print("\nShell Frameworks:")
        framework_components = [
            ('install_powerlevel10k', '  Install Powerlevel10k theme', profile.install_powerlevel10k),
            ('install_tpm', '  Install Tmux Plugin Manager', profile.install_tpm),
        ]

        for attr, description, default in framework_components:
            overrides[attr] = self.prompt_yes_no(description, default)

        # Repository integrations
        print("\nRepository Integrations:")
        repo_components = [
            ('run_config_sync', '  Setup config-sync repo', profile.run_config_sync),
            ('clone_scripts', '  Clone scripts to ~/bin', profile.clone_scripts),
        ]

        for attr, description, default in repo_components:
            overrides[attr] = self.prompt_yes_no(description, default)

        return profile.copy(**overrides)

    def prompt_options(self, profile: Profile) -> Profile:
        """Prompt user for additional options.

        Args:
            profile: Profile to customize

        Returns:
            Modified Profile with user options
        """
        print("\n" + "-" * 50)
        print("Additional Options")
        print("-" * 50)

        overrides = {}

        # Only ask about shell change if zsh will be installed
        if profile.install_zsh:
            overrides['change_default_shell'] = self.prompt_yes_no(
                "Change default shell to zsh",
                profile.change_default_shell
            )

        # Only ask about vundle plugins if vim will be installed
        if profile.install_vim:
            overrides['install_vundle_plugins'] = self.prompt_yes_no(
                "Install Vim plugins via Vundle (may take time)",
                profile.install_vundle_plugins
            )

        print("\nNote: Existing configs will be backed up automatically.")

        return profile.copy(**overrides)

    def show_summary(self, profile: Profile) -> bool:
        """Show installation summary and confirm.

        Args:
            profile: Final profile configuration

        Returns:
            True if user confirms, False otherwise
        """
        print("\n" + "=" * 50)
        print("Installation Summary")
        print("=" * 50)
        print(f"\nProfile: {profile.name}")

        if profile.preferred_package_manager:
            print(f"Package Manager: {profile.preferred_package_manager}")

        print("\nCore Tools:")
        core_tools = [
            ('Vim', profile.install_vim),
            ('Tmux', profile.install_tmux),
            ('Zsh', profile.install_zsh),
            ('ctags', profile.install_ctags),
        ]
        for name, enabled in core_tools:
            status = "Yes" if enabled else "No"
            print(f"  {name:15}: {status}")

        print("\nShell Enhancements:")
        shell_tools = [
            ('eza', profile.install_eza),
            ('bat', profile.install_bat),
            ('fzf', profile.install_fzf),
            ('zoxide', profile.install_zoxide),
        ]
        for name, enabled in shell_tools:
            status = "Yes" if enabled else "No"
            print(f"  {name:15}: {status}")

        print("\nSystem Utilities:")
        util_tools = [
            ('btop', profile.install_btop),
            ('duf', profile.install_duf),
            ('ncdu', profile.install_ncdu),
        ]
        for name, enabled in util_tools:
            status = "Yes" if enabled else "No"
            print(f"  {name:15}: {status}")

        print("\nAdvanced Tools:")
        advanced_tools = [
            ('yazi', profile.install_yazi),
            ('neovim', profile.install_neovim),
        ]
        for name, enabled in advanced_tools:
            status = "Yes" if enabled else "No"
            print(f"  {name:15}: {status}")

        print("\nFrameworks:")
        frameworks = [
            ('Powerlevel10k', profile.install_powerlevel10k),
            ('TPM', profile.install_tpm),
        ]
        for name, enabled in frameworks:
            status = "Yes" if enabled else "No"
            print(f"  {name:15}: {status}")

        print("\nRepositories:")
        repos = [
            ('config-sync', profile.run_config_sync),
            ('scripts', profile.clone_scripts),
        ]
        for name, enabled in repos:
            status = "Yes" if enabled else "No"
            print(f"  {name:15}: {status}")

        print("\nOptions:")
        if profile.install_zsh:
            shell_status = "Yes" if profile.change_default_shell else "No"
            print(f"  Change shell:   {shell_status}")
        if profile.install_vim:
            vundle_status = "Yes" if profile.install_vundle_plugins else "No"
            print(f"  Vundle plugins: {vundle_status}")
        print(f"  Backup files:   Yes (always)")

        print("")
        return self.prompt_yes_no("Proceed with installation?", True)

    def run_interactive_setup(self) -> Optional[Profile]:
        """Run the full interactive setup flow.

        Returns:
            Configured Profile if user confirms, None if cancelled
        """
        try:
            # Step 1: Select profile
            profile = self.prompt_profile()

            # Step 2: Customize components
            profile = self.prompt_components(profile)

            # Step 3: Additional options
            profile = self.prompt_options(profile)

            # Step 4: Summary and confirmation
            if self.show_summary(profile):
                return profile

            print("\nInstallation cancelled.")
            return None

        except KeyboardInterrupt:
            print("\n\nInstallation cancelled.")
            return None
