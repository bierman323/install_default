#!/usr/bin/env python3
import argparse, platform, sys, os, subprocess
from software_install.eza_install import get_eza
from software_install.btop_install import get_btop

# Global Variables, not great for modules
path = ''
config_path = ''
os_type = ''
home = ''
vundle_path = '.vim/bundle/Vundle.vim'
github_clone = 'https://github.com/bierman323/configs.git'
vundle_clone = 'https://github.com/VundleVim/Vundle.vim.git'
oh_my_path = '.local/oh-my-zsh'

def setup_os():
    global path
    global os_type
    global home
    if os_type == 'Linux':
        home = os.path.expanduser("~")
        path = f'{home}/.code'
        if not os.path.exists(path):
            os.mkdir(path)

# parse out the arguments
def setup_args():
    parser = argparse.ArgumentParser(description='System Setup')
    parser.add_argument('-v', '--vim', help="Configure VIM", action='store_true', default=False)
    parser.add_argument('-t', '--tmux', help="Configure TMUX", action='store_true', default=False)
    parser.add_argument('-z', '--zsh', help="Configure ZSH", action='store_true', default=False)

    args = parser.parse_args()
    return args

# Check to see if a package has been installed on the Linux system
def check_package(program):
    status = subprocess.call(['which', f'{program}'])
    if not status == 0:
        os.system(f'sudo apt install {program} -y')

# Check if GIT is installed
# if no GIT, install it
def check_git():
    global path
    global config_path
    config_path = f'{path}/configs'
    check_package('git')
    if not os.path.exists(config_path):
        os.chdir(path)
        subprocess.call(['git', 'clone', f'{github_clone}'])
    else:
        os.chdir(config_path)
        subprocess.call(['git', 'pull', '--rebase'])

# Check that VIM is installed
# if no VIM install it
def check_vim():
    check_package('vim')
    check_vundle()
    add_vimrc()

def check_file_exists(dst_file):
    if os.path.exists(dst_file):
        if not os.path.islink(dst_file):
            move_file = f'{dst_file}.old'
            if os.path.exists(move_file):
               os.remove(move_file)
            os.rename(dst_file, move_file)
        else:
            os.remove(dst_file)


def add_vimrc():
    global config_path
    global home

    dst_file = f'{home}/.vimrc'
    check_file_exists(dst_file)
    path_to_rc = f'{config_path}/.vimrc'
    os.symlink(path_to_rc, dst_file)


# Install Vundle if it is isn't installed
def check_vundle():
    home_path = os.path.expanduser("~")
    home_location = os.path.join(home_path, vundle_path)
    if not os.path.exists(home_location):
        os.makedirs(home_location)
        os.chdir(home_path)
        subprocess.call(['git', 'clone', vundle_clone, home_location])


# Check that TMUX is installed
# if no TMUX install it
def check_tmux():
    global config_path
    global home
    check_package('tmux')
    path_to_rc = f'{config_path}/.tmux.conf'
    dst_file = f'{home}/.tmux.conf'
    check_file_exists(dst_file)
    os.symlink(path_to_rc, dst_file)

# Check that zsh is installed
# if not install zsh
def check_zsh():
    global config_path
    global home
    # Check for a few packages
    for item in ["zsh", "bzip2", "make"]:
        check_package(item)
    oh_my()

    create_symlink([".zshrc", ".zshrc_eza", ".zshrc_ohmyzsh"])
    # Install eza
    get_eza()
    get_btop()

    # change the default shell to zsh
    command = 'which zsh'
    which_zsh = subprocess.check_output(command, shell=True)
    subprocess.call(['sudo','chsh', '-s', "/usr/bin/zsh"])


def create_symlink(rc_file):
    global config_path
    global home
    for item in rc_file:
        source_path = f'{config_path}/{item}'
        dest_path = f'{home}/{item}'
        check_file_exists(dest_path)
        os.symlink(source_path, dest_path)


def oh_my():
    global oh_my_path

    home_path = os.path.expanduser("~")
    path_oh = f'{home_path}/{oh_my_path}'
    os.environ['ZSH'] = path_oh

    if not os.path.exists(path_oh):
        subprocess.call(['wget', '-O', 'install.sh', 'https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh'])
        subprocess.call(['sh', 'install.sh'])

    path_to_rc = f'{config_path}/bierman-fino.zsh-theme'
    dst_file = f'{path_oh}/themes/bierman-fino.zsh-theme'
    check_file_exists(dst_file)
    os.symlink(path_to_rc, dst_file)

def ctags_install():

    check_package('universal-ctags')


# What platform are we running on
def get_os():
    global os_type
    os_type = platform.system()

# Main function
def main():
    get_os()
    setup_os()
    if not len(sys.argv) > 1:
       do_all = True
    else:
        do_all = False
        args = setup_args()
    # Make sure we have git
    check_git()

    if do_all:
        check_vim()
        check_tmux()
        check_zsh()
        ctags_install()
    else:
        if args.vim:
            check_vim()
        if args.tmux:
            check_tmux()
        if args.zsh:
            check_zsh()
#

# start of execution
if __name__ == '__main__':
    main()
