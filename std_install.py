#!/usr/bin/env python3
import argparse
import platform
import sys
import os
import subprocess
import logging
import shutil
from software_install.eza_install import get_eza
from software_install.btop_install import get_btop

# Global Variables
path = ''
config_path = ''
os_type = ''
home = ''
package_manager = ''
vundle_path = '.vim/bundle/Vundle.vim'
github_clone = 'https://github.com/bierman323/configs.git'
vundle_clone = 'https://github.com/VundleVim/Vundle.vim.git'
oh_my_path = '.local/oh-my-zsh'

# Setup logging
def setup_logging():
    global home
    log_dir = f'{home}/.code'
    os.makedirs(log_dir, exist_ok=True)
    log_file = f'{log_dir}/install.log'

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    logging.info("Starting installation script")

# Detect package manager
def detect_package_manager():
    global package_manager

    managers = {
        'apt-get': 'apt-get',
        'apt': 'apt',
        'yum': 'yum',
        'dnf': 'dnf',
        'brew': 'brew'
    }

    for manager, cmd in managers.items():
        if shutil.which(manager):
            package_manager = cmd
            logging.info(f"Detected package manager: {package_manager}")
            return

    logging.error("No supported package manager found (apt, yum, dnf, brew)")
    sys.exit(1)

def setup_os():
    global path
    global os_type
    global home

    home = os.path.expanduser("~")
    path = f'{home}/.code'

    try:
        os.makedirs(path, exist_ok=True)
        logging.info(f"Setup directory: {path}")
    except OSError as e:
        logging.error(f"Failed to create directory {path}: {e}")
        sys.exit(1)

# parse out the arguments
def setup_args():
    parser = argparse.ArgumentParser(description='System Setup')
    parser.add_argument('-v', '--vim', help="Configure VIM", action='store_true', default=False)
    parser.add_argument('-t', '--tmux', help="Configure TMUX", action='store_true', default=False)
    parser.add_argument('-z', '--zsh', help="Configure ZSH", action='store_true', default=False)

    args = parser.parse_args()
    return args

# Check to see if a package has been installed on the system
def check_package(program):
    global package_manager

    if shutil.which(program):
        logging.info(f"Package '{program}' already installed")
        return True

    logging.info(f"Installing package: {program}")

    # Build install command based on package manager
    if package_manager in ['apt', 'apt-get']:
        cmd = ['sudo', package_manager, 'install', program, '-y']
    elif package_manager in ['yum', 'dnf']:
        cmd = ['sudo', package_manager, 'install', program, '-y']
    elif package_manager == 'brew':
        cmd = ['brew', 'install', program]
    else:
        logging.error(f"Unknown package manager: {package_manager}")
        return False

    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        logging.info(f"Successfully installed {program}")
        return True
    except subprocess.CalledProcessError as e:
        logging.error(f"Failed to install {program}: {e.stderr}")
        return False

# Check if GIT is installed and clone/update configs
def check_git():
    global path
    global config_path
    config_path = f'{path}/configs'

    if not check_package('git'):
        logging.error("Failed to install git, cannot continue")
        sys.exit(1)

    try:
        if not os.path.exists(config_path):
            logging.info(f"Cloning configs from {github_clone}")
            os.chdir(path)
            subprocess.run(['git', 'clone', github_clone], check=True)
        else:
            logging.info("Updating existing configs")
            os.chdir(config_path)
            subprocess.run(['git', 'pull', '--rebase'], check=True)

        # Symlink .gitignore
        dst_file = f'{home}/.gitignore'
        check_file_exists(dst_file)
        path_to_rc = f'{config_path}/.gitignore'
        os.symlink(path_to_rc, dst_file)
        logging.info("Symlinked .gitignore")

    except subprocess.CalledProcessError as e:
        logging.error(f"Git operation failed: {e}")
        sys.exit(1)
    except OSError as e:
        logging.error(f"Failed to create symlink: {e}")
        sys.exit(1)


# Check that VIM is installed
def check_vim():
    logging.info("Setting up Vim")
    if not check_package('vim'):
        logging.error("Failed to install vim")
        return False

    check_vundle()
    add_vimrc()
    return True

def check_file_exists(dst_file):
    """Safely handle existing files/symlinks before creating new symlink"""
    try:
        if os.path.exists(dst_file):
            if not os.path.islink(dst_file):
                move_file = f'{dst_file}.old'
                if os.path.exists(move_file):
                    os.remove(move_file)
                os.rename(dst_file, move_file)
                logging.info(f"Backed up {dst_file} to {move_file}")
            else:
                os.remove(dst_file)
                logging.info(f"Removed existing symlink {dst_file}")
    except OSError as e:
        logging.warning(f"Error handling existing file {dst_file}: {e}")


def add_vimrc():
    global config_path
    global home

    dst_file = f'{home}/.vimrc'
    path_to_rc = f'{config_path}/.vimrc'

    try:
        check_file_exists(dst_file)
        os.symlink(path_to_rc, dst_file)
        logging.info("Symlinked .vimrc")
    except OSError as e:
        logging.error(f"Failed to symlink .vimrc: {e}")


# Install Vundle if it isn't installed
def check_vundle():
    home_path = os.path.expanduser("~")
    home_location = os.path.join(home_path, vundle_path)

    if os.path.exists(home_location):
        logging.info("Vundle already installed")
        return

    try:
        logging.info("Installing Vundle")
        os.makedirs(os.path.dirname(home_location), exist_ok=True)
        subprocess.run(['git', 'clone', vundle_clone, home_location], check=True)
        logging.info("Vundle installed successfully")
    except subprocess.CalledProcessError as e:
        logging.error(f"Failed to install Vundle: {e}")
    except OSError as e:
        logging.error(f"Failed to create Vundle directory: {e}")


# Check that TMUX is installed
def check_tmux():
    global config_path
    global home

    logging.info("Setting up Tmux")
    if not check_package('tmux'):
        logging.error("Failed to install tmux")
        return False

    path_to_rc = f'{config_path}/.tmux.conf'
    dst_file = f'{home}/.tmux.conf'

    try:
        check_file_exists(dst_file)
        os.symlink(path_to_rc, dst_file)
        logging.info("Symlinked .tmux.conf")
        return True
    except OSError as e:
        logging.error(f"Failed to symlink .tmux.conf: {e}")
        return False

# Check that zsh is installed
def check_zsh():
    global config_path
    global home

    logging.info("Setting up Zsh")

    # Check for required packages
    for item in ["zsh", "bzip2", "make"]:
        if not check_package(item):
            logging.error(f"Failed to install required package: {item}")
            return False

    oh_my()
    create_symlink([".zshrc", ".zshrc_eza", ".zshrc_ohmyzsh"])

    # Install eza and btop
    get_eza()
    get_btop()

    # Change the default shell to zsh (use detected path, not hardcoded)
    try:
        which_zsh = subprocess.check_output(['which', 'zsh'], text=True).strip()
        logging.info(f"Changing default shell to: {which_zsh}")
        subprocess.run(['sudo', 'chsh', '-s', which_zsh], check=True)
        logging.info("Default shell changed to zsh")
        return True
    except subprocess.CalledProcessError as e:
        logging.error(f"Failed to change default shell: {e}")
        return False


def create_symlink(rc_file):
    global config_path
    global home

    for item in rc_file:
        source_path = f'{config_path}/{item}'
        dest_path = f'{home}/{item}'

        try:
            check_file_exists(dest_path)
            os.symlink(source_path, dest_path)
            logging.info(f"Symlinked {item}")
        except OSError as e:
            logging.error(f"Failed to symlink {item}: {e}")


def oh_my():
    global oh_my_path
    global config_path

    home_path = os.path.expanduser("~")
    path_oh = f'{home_path}/{oh_my_path}'
    os.environ['ZSH'] = path_oh
    install_script = f'{home_path}/install.sh'

    try:
        if not os.path.exists(path_oh):
            logging.info("Installing Oh-My-Zsh")
            subprocess.run(['wget', '-O', install_script,
                          'https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh'],
                         check=True)
            subprocess.run(['sh', install_script], check=True)
            logging.info("Oh-My-Zsh installed successfully")

            # Clean up the install script
            if os.path.exists(install_script):
                os.remove(install_script)
                logging.info("Cleaned up Oh-My-Zsh install script")
        else:
            logging.info("Oh-My-Zsh already installed")

        # Symlink custom theme
        path_to_rc = f'{config_path}/bierman-fino.zsh-theme'
        dst_file = f'{path_oh}/themes/bierman-fino.zsh-theme'
        check_file_exists(dst_file)
        os.symlink(path_to_rc, dst_file)
        logging.info("Symlinked custom Oh-My-Zsh theme")

    except subprocess.CalledProcessError as e:
        logging.error(f"Failed to install Oh-My-Zsh: {e}")
        # Attempt cleanup even on failure
        if os.path.exists(install_script):
            os.remove(install_script)
    except OSError as e:
        logging.error(f"Failed to symlink Oh-My-Zsh theme: {e}")

def ctags_install():
    logging.info("Setting up ctags")
    if not check_package('universal-ctags'):
        logging.warning("Failed to install universal-ctags, trying ctags")
        check_package('ctags')


# What platform are we running on
def get_os():
    global os_type
    os_type = platform.system()

# Main function
def main():
    get_os()
    setup_os()
    setup_logging()
    detect_package_manager()

    logging.info(f"Running on {os_type}")
    logging.info(f"Home directory: {home}")

    if not len(sys.argv) > 1:
       do_all = True
    else:
        do_all = False
        args = setup_args()

    # Make sure we have git
    check_git()

    if do_all:
        logging.info("Running full installation")
        check_vim()
        check_tmux()
        check_zsh()
        ctags_install()
        logging.info("Installation complete!")
    else:
        if args.vim:
            check_vim()
        if args.tmux:
            check_tmux()
        if args.zsh:
            check_zsh()
        logging.info("Selected components installed!")

# Start of execution
if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        logging.info("\nInstallation interrupted by user")
        sys.exit(0)
    except Exception as e:
        logging.error(f"Unexpected error: {e}", exc_info=True)
        sys.exit(1)
