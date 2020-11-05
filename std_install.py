#!/usr/bin/env python3
import argparse, platform, sys, os, subprocess

# Global Variables, not great for modules
path = ''
config_path = ''
os_type = ''
home = ''
vundle_path = '.vim/bundle/Vundle.vim'
github_clone = 'https://github.com/bierman323/configs.git'
vundle_clone = 'https://github.com/VundleVim/Vundle.vim.git'

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

def add_vimrc():
    global config_path
    global home
    path_to_rc = f'{config_path}/{os_type}/vimrc'
    dst_file = f'{home}/.vimrc'
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
    path_to_rc = f'{config_path}/{os_type}/tmux.conf'
    dst_file = f'{home}/.tmux.conf'
    os.symlink(path_to_rc, dst_file)

# Check that zsh is installed
# if not install zsh
def check_zsh():
    check_package('zsh')

# Configure VIM, TMUX, zsh, git


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
#        check_zsh()
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
