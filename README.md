# System Configuration Automation

A cross-platform Linux system configuration automation tool for quickly setting up development environments. Perfect for frequently provisioned VMs, cloud instances, and security research environments.

## Features

- **Cross-Platform Support**: Works with apt (Debian/Ubuntu/Kali), yum/dnf (RHEL/Fedora/CentOS), and brew (macOS)
- **Robust Error Handling**: Comprehensive logging and graceful failure recovery
- **Idempotent**: Safe to run multiple times - skips already installed packages
- **Network Resilience**: Automatic retry with exponential backoff for downloads
- **Architecture Detection**: Supports x86_64, aarch64, and ARM architectures
- **Safe File Management**: Backs up existing configs with `.old` suffix

## What It Installs

### Core Tools
- **Vim** with Vundle plugin manager
- **Tmux** with custom configuration
- **Zsh** with Oh-My-Zsh and custom theme

### Additional Tools
- **eza**: Modern replacement for ls (syntax-highlighted file listings)
- **btop**: Resource monitor with beautiful TUI
- **ctags**: Source code indexing for Vim

### Configuration Files
All configurations are symlinked from a central repository:
- `.vimrc`, `.tmux.conf`, `.zshrc`
- Custom Oh-My-Zsh theme
- `.gitignore`

## Prerequisites

### System Requirements
- Linux distribution (Ubuntu, Debian, Kali, RHEL, Fedora, CentOS) or macOS
- Python 3.6 or higher
- `sudo` access for package installation
- Internet connection

### Install Dependencies
```bash
# Install Python requests library
pip3 install -r requirements.txt
```

## Usage

### Full Installation
Install everything (Vim, Tmux, Zsh, eza, btop, ctags):
```bash
./std_install.py
```

### Selective Installation
Install specific components:
```bash
# Vim only
./std_install.py --vim

# Tmux only
./std_install.py --tmux

# Zsh (includes eza and btop)
./std_install.py --zsh
```

### Combination Installation
```bash
# Vim and Tmux only
./std_install.py --vim --tmux
```

## Logging

All operations are logged to:
```
~/.code/install.log
```

View logs in real-time:
```bash
tail -f ~/.code/install.log
```

Check for errors:
```bash
grep ERROR ~/.code/install.log
```

## Directory Structure

```
~/.code/
├── configs/              # Cloned configuration repository
├── install.log          # Installation log
~/.vim/bundle/Vundle.vim  # Vundle plugin manager
~/.local/oh-my-zsh/       # Oh-My-Zsh installation
```

## Configuration Repository

Configurations are pulled from: `https://github.com/bierman323/configs`

To use your own configs:
1. Fork or create a similar repository
2. Edit `github_clone` variable in `std_install.py` (line 19)
3. Ensure your repo contains: `.vimrc`, `.tmux.conf`, `.zshrc`, `.zshrc_eza`, `.zshrc_ohmyzsh`, `bierman-fino.zsh-theme`

## Behavior Details

### File Handling
- **Existing regular files**: Renamed to `*.old` (overwrites previous `.old`)
- **Existing symlinks**: Removed and replaced
- **Missing files**: Symlinks created directly

### Package Management
- Automatically detects system package manager
- Checks if packages already installed before attempting installation
- Skips installation with info message if package exists

### Network Operations
- Downloads use temporary directories (auto-cleaned)
- 3 retry attempts with exponential backoff (1s, 2s, 4s)
- 30-second timeout per attempt

### Architecture Support
Automatically detects and maps architecture:
- x86_64/amd64 → x86_64
- aarch64/arm64 → aarch64
- armv7l → armv7

## Troubleshooting

### Check Installation Status
```bash
# Verify package manager detection
which apt || which yum || which dnf || which brew

# Check if tools are installed
which vim tmux zsh eza btop

# View versions
vim --version
tmux -V
zsh --version
eza --version
btop --version
```

### Common Issues

**"No supported package manager found"**
- Ensure you're running on a supported OS with apt, yum, dnf, or brew

**Download failures**
- Check internet connection
- Verify GitHub is accessible: `curl -I https://github.com`
- Check logs for specific error messages

**Permission denied errors**
- Ensure you have sudo access: `sudo -v`
- Check file permissions: `ls -la ~/.code`

**Oh-My-Zsh installation hangs**
- Run interactively first: `sh -c "$(wget -O- https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"`

### Reset Installation

To completely reset:
```bash
# Remove installations
rm -rf ~/.code ~/.vim/bundle/Vundle.vim ~/.local/oh-my-zsh

# Restore backups
for file in ~/.vimrc.old ~/.tmux.conf.old ~/.zshrc.old; do
    [ -f "$file" ] && mv "$file" "${file%.old}"
done
```

## Security Considerations

- No secrets or credentials are included in this public repository
- All downloads are from official GitHub repositories
- Package manager operations use sudo (will prompt for password)
- Configurations should be reviewed before use in sensitive environments

## Development

### Architecture
- `std_install.py`: Main orchestrator with core functionality
- `software_install/eza_install.py`: eza installation module
- `software_install/btop_install.py`: btop installation module

### Adding New Tools
1. Create installer in `software_install/`
2. Import in `std_install.py`
3. Call from appropriate setup function
4. Add logging and error handling

### Modifying Package List
Edit the package checks in respective functions:
- `check_vim()`: Vim packages (line 151)
- `check_tmux()`: Tmux packages (line 214)
- `check_zsh()`: Zsh packages (line 243)

## Contributing

When contributing:
1. Maintain cross-platform compatibility
2. Add comprehensive error handling
3. Update logging for new operations
4. Test on multiple distributions
5. Update documentation

## License

See repository for license information.

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review logs in `~/.code/install.log`
3. Open an issue in the repository with log output