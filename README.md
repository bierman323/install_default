# Multi-Environment System Setup Script

A Python-based installation script for setting up development environments across different machines. Supports three profiles (lab, work, personal) with automatic package manager detection, backup management, and Ansible integration.

## Features

- **Three Environment Profiles**: Lab (ephemeral VMs), Work (MacPorts), Personal (full features)
- **Package Manager Abstraction**: Supports Homebrew, MacPorts, APT, and DNF
- **Auto-Installation**: Installs Homebrew or MacPorts if not present
- **Always-On Backups**: Existing configs are automatically backed up before replacement
- **Dry-Run Mode**: Preview changes without modifying your system
- **Ansible Integration**: JSON output and exit codes for automation
- **Interactive & Non-Interactive Modes**: Works in terminals or CI/CD pipelines
- **Cross-Platform Support**: macOS and Linux (Ubuntu, Debian, RHEL, Fedora)

## Requirements

- Python 3.6+
- `requests` module (`pip3 install requests`)
- Git
- sudo access (for package installation and shell changes)
- Internet connection

## Quick Start

```bash
# Clone the repository
git clone https://github.com/bierman323/install_default.git
cd install_default

# Install dependencies
pip3 install requests

# Run interactively (will prompt for choices)
./std_install.py

# Or run with a specific profile
./std_install.py --profile personal -y
```

## Profiles

### Lab Profile
Fast, minimal setup for ephemeral VMs (security research, testing).

```bash
./std_install.py --profile lab -y
```

| Setting | Value |
|---------|-------|
| **Package Manager** | Homebrew (auto-installed if missing) |
| **Core Tools** | vim, tmux, zsh, ctags |
| **Shell Enhancements** | eza, bat, fzf, zoxide |
| **System Utilities** | btop |
| **Frameworks** | tpm |
| **Repositories** | scripts (~/bin) |
| **Excluded** | powerlevel10k, config-sync, duf, ncdu, yazi, neovim |

### Work Profile
Full-featured setup using MacPorts (for environments where Homebrew isn't approved).

```bash
./std_install.py --profile work -y
```

| Setting | Value |
|---------|-------|
| **Package Manager** | MacPorts (auto-installed if missing) |
| **Core Tools** | vim, tmux, zsh, ctags |
| **Shell Enhancements** | eza, bat, fzf, zoxide |
| **System Utilities** | btop, duf, ncdu |
| **Advanced Tools** | yazi, neovim |
| **Frameworks** | powerlevel10k, tpm |
| **Repositories** | config-sync, scripts |
| **Note** | Does not change default shell (may require approval) |

### Personal Profile
Complete installation with all features.

```bash
./std_install.py --profile personal -y
```

| Setting | Value |
|---------|-------|
| **Package Manager** | Homebrew (auto-installed if missing) |
| **All Tools** | Everything enabled |
| **Shell Change** | Yes |

## Tools Installed

### Core Tools
| Tool | Description |
|------|-------------|
| vim | Text editor with Vundle plugin manager |
| tmux | Terminal multiplexer |
| zsh | Z shell with Oh-My-Zsh framework |
| ctags | Universal ctags for code navigation |

### Shell Enhancements
| Tool | Description |
|------|-------------|
| eza | Modern replacement for `ls` |
| bat | Cat clone with syntax highlighting |
| fzf | Fuzzy finder |
| zoxide | Smarter `cd` command |

### System Utilities
| Tool | Description |
|------|-------------|
| btop | Resource monitor |
| duf | Modern `df` replacement |
| ncdu | Disk usage analyzer |

### Advanced Tools
| Tool | Description |
|------|-------------|
| yazi | Terminal file manager |
| neovim | Hyperextensible Vim-based editor |

### Shell Frameworks
| Tool | Description |
|------|-------------|
| Oh-My-Zsh | Zsh framework with plugins |
| powerlevel10k | Feature-rich Zsh theme |
| tpm | Tmux Plugin Manager |
| Vundle | Vim plugin manager |

## CLI Reference

```
usage: std_install.py [-h] [-p {lab,work,personal}] [--list-profiles] [-y]
                      [-n] [-o {text,json}] [-q] [--verbose]
                      [--package-manager {auto,brew,macports}]
                      [--no-shell-change] [--no-vundle-plugins] [--no-bat]
                      [--no-fzf] [--no-zoxide] [--no-yazi] [--no-neovim]
                      [--no-powerlevel10k] [--no-tpm] [--no-config-sync]
                      [--no-scripts] [-v] [-t] [-z] [--version]
```

### Profile Selection
| Flag | Description |
|------|-------------|
| `-p, --profile {lab,work,personal}` | Environment profile |
| `--list-profiles` | List available profiles and exit |

### Execution Modes
| Flag | Description |
|------|-------------|
| `-y, --non-interactive` | Skip all prompts (for automation) |
| `-n, --dry-run` | Show what would happen without changes |

### Output Control
| Flag | Description |
|------|-------------|
| `-o, --output-format {text,json}` | Output format (default: text) |
| `-q, --quiet` | Suppress non-essential output |
| `--verbose` | Enable debug logging |

### Package Manager
| Flag | Description |
|------|-------------|
| `--package-manager {auto,brew,macports}` | Override package manager selection |

### Component Overrides
| Flag | Description |
|------|-------------|
| `--no-shell-change` | Don't change default shell to zsh |
| `--no-vundle-plugins` | Skip Vundle plugin installation |
| `--no-bat` | Skip bat installation |
| `--no-fzf` | Skip fzf installation |
| `--no-zoxide` | Skip zoxide installation |
| `--no-yazi` | Skip yazi installation |
| `--no-neovim` | Skip neovim installation |
| `--no-powerlevel10k` | Skip powerlevel10k installation |
| `--no-tpm` | Skip tpm installation |
| `--no-config-sync` | Skip config-sync setup |
| `--no-scripts` | Skip scripts repo clone |

### Legacy Flags (Backward Compatibility)
| Flag | Description |
|------|-------------|
| `-v, --vim` | Configure VIM only |
| `-t, --tmux` | Configure TMUX only |
| `-z, --zsh` | Configure ZSH only |

## Usage Examples

```bash
# Interactive mode (prompts for choices)
./std_install.py

# Lab VM - fast setup
./std_install.py --profile lab -y

# Work computer with MacPorts
./std_install.py --profile work -y

# Personal - full install
./std_install.py --profile personal -y

# Preview changes without making them
./std_install.py --profile work --dry-run

# JSON output for Ansible
./std_install.py --profile work -y -o json

# Skip specific tools
./std_install.py --profile personal -y --no-neovim --no-yazi

# Force Homebrew on work profile
./std_install.py --profile work -y --package-manager brew

# Install only vim and tmux (legacy mode)
./std_install.py --vim --tmux -y
```

## Repository Integrations

The script integrates with three GitHub repositories:

### configs
| Property | Value |
|----------|-------|
| **Location** | `~/.code/configs` |
| **Repository** | https://github.com/bierman323/configs |
| **Contents** | Dotfiles (.zshrc, .vimrc, .tmux.conf, .gitignore, zsh themes) |

### config-sync
| Property | Value |
|----------|-------|
| **Location** | `~/.config-sync` |
| **Repository** | https://github.com/bierman323/config-sync |
| **Contents** | Application configs (btop, yazi, powerline, git) |
| **Profiles** | work, personal |

### scripts
| Property | Value |
|----------|-------|
| **Location** | `~/bin` |
| **Repository** | https://github.com/bierman323/scripts |
| **Contents** | Utility shell scripts (added to PATH via .zshrc) |
| **Profiles** | all |

## Backup System

**All existing configs are automatically backed up before replacement.** This cannot be disabled for safety.

Backups are stored in timestamped directories:
```
~/.config-backup/
└── YYYYMMDD-HHMMSS/
    ├── .zshrc
    ├── .vimrc
    ├── .tmux.conf
    ├── .config/
    │   ├── btop/
    │   └── yazi/
    └── bin/
```

After installation, restore instructions are displayed:
```
==================================================
BACKUP INFORMATION
==================================================
Backed up 5 file(s) to:
  /home/user/.config-backup/20240115-143022

To restore original configs:
  cp -r /home/user/.config-backup/20240115-143022/* ~/

Backed up files:
  - /home/user/.zshrc
  - /home/user/.vimrc
  - /home/user/.tmux.conf
==================================================
```

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Partial failure (some components failed) |
| 2 | Complete failure |
| 3 | Invalid configuration/arguments |

## Ansible Integration

Use the JSON output format for parsing in Ansible playbooks:

```yaml
- name: Setup development environment
  command: ./std_install.py --profile work -y -o json
  register: setup_result

- name: Parse result
  set_fact:
    setup_data: "{{ setup_result.stdout | from_json }}"

- name: Check for failures
  fail:
    msg: "Setup failed: {{ setup_data.errors }}"
  when: setup_data.failed
```

JSON output structure:
```json
{
  "changed": true,
  "failed": false,
  "dry_run": false,
  "profile": "work",
  "components": {
    "vim": true,
    "tmux": true,
    "zsh": true,
    "eza": true,
    "bat": true,
    "fzf": true,
    "zoxide": true,
    "btop": true,
    "duf": true,
    "ncdu": true,
    "yazi": true,
    "neovim": true,
    "powerlevel10k": true,
    "tpm": true,
    "config-sync": true,
    "scripts": true
  },
  "errors": [],
  "warnings": [],
  "exit_code": 0
}
```

## Directory Structure

```
install_default/
├── std_install.py          # Main entry point (v3.0.0)
├── README.md               # This file
├── requirements.txt        # Python dependencies
├── profiles/
│   ├── __init__.py
│   ├── base.py             # Profile dataclass
│   └── defaults.py         # LAB, WORK, PERSONAL profiles
├── package_managers/
│   ├── __init__.py
│   ├── base.py             # Abstract PackageManager
│   ├── brew.py             # Homebrew (with auto-install)
│   ├── macports.py         # MacPorts (with auto-install)
│   ├── apt.py              # Debian/Ubuntu
│   ├── dnf.py              # RHEL/Fedora
│   └── factory.py          # Auto-detection logic
├── tools/
│   ├── __init__.py
│   ├── base.py             # Abstract ToolInstaller
│   ├── oh_my_zsh.py        # Oh-My-Zsh framework
│   ├── powerlevel10k.py    # P10k zsh theme
│   ├── tpm.py              # Tmux Plugin Manager
│   ├── vundle.py           # Vim Vundle
│   ├── config_sync.py      # config-sync repo integration
│   └── scripts_repo.py     # scripts to ~/bin
├── backup/
│   ├── __init__.py
│   └── manager.py          # BackupManager (always-on)
├── output/
│   ├── __init__.py
│   └── formatter.py        # Text/JSON output
├── ui/
│   ├── __init__.py
│   └── prompts.py          # Interactive prompts
└── software_install/
    ├── eza_install.py      # eza from GitHub releases
    └── btop_install.py     # btop from GitHub releases
```

## Troubleshooting

### "No package manager available"
The script will attempt to install Homebrew (or MacPorts for work profile). Ensure you have:
- Internet connection
- sudo access
- Xcode Command Line Tools (macOS): `xcode-select --install`

### "Failed to change default shell"
This requires sudo access. You can skip it with `--no-shell-change` or manually run:
```bash
chsh -s $(which zsh)
```

### "Oh-My-Zsh installation failed"
Ensure `wget` or `curl` is available and you have internet access.

### Restoring from backup
If something goes wrong, restore your original configs:
```bash
# Find your backup
ls -la ~/.config-backup/

# Restore (replace YYYYMMDD-HHMMSS with actual timestamp)
cp -r ~/.config-backup/YYYYMMDD-HHMMSS/* ~/
```

### Logs
Installation logs are saved to `~/.code/install.log`

```bash
# View logs in real-time
tail -f ~/.code/install.log

# Check for errors
grep ERROR ~/.code/install.log
```

### Check Installation Status
```bash
# Verify tools are installed
which vim tmux zsh eza bat fzf btop

# View versions
vim --version | head -1
tmux -V
zsh --version
eza --version
bat --version
```

### Complete Reset
To completely reset and start fresh:
```bash
# Remove installations
rm -rf ~/.code ~/.vim/bundle/Vundle.vim ~/.local/oh-my-zsh
rm -rf ~/.oh-my-zsh ~/.tmux/plugins/tpm
rm -rf ~/.config-sync ~/bin

# Restore from backup
cp -r ~/.config-backup/YYYYMMDD-HHMMSS/* ~/
```

## Security Considerations

- No secrets or credentials are included in configurations
- All downloads are from official GitHub repositories
- Package manager operations use sudo (will prompt for password)
- Review configurations before use in sensitive environments
- Backups preserve original files for recovery

## Development

### Adding New Tools

1. Create installer in `tools/` directory:
```python
from .base import ToolInstaller

class MyToolInstaller(ToolInstaller):
    @property
    def name(self) -> str:
        return "mytool"

    def is_installed(self) -> bool:
        # Check if installed
        pass

    def install(self) -> bool:
        # Installation logic
        pass
```

2. Add to `tools/__init__.py`
3. Add profile field in `profiles/base.py`
4. Update profile defaults in `profiles/defaults.py`
5. Call from `std_install.py`

### Adding Package Manager Support

1. Create manager in `package_managers/` directory
2. Extend `PackageManager` base class
3. Add to factory in `package_managers/factory.py`

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test with `--dry-run` on all three profiles
5. Update documentation
6. Submit a pull request

## License

MIT License

## Version History

- **v3.0.0**: Multi-profile support, package manager abstraction, always-on backups
- **v2.0.0**: Profile system, interactive mode, JSON output
- **v1.0.0**: Initial release with basic tool installation
