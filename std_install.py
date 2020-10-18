#!/usr/bin/env python3
import argparse, platform, sys, os, subprocess

# Global Variables, not great for modules
path = ''
github_clone = 'https://github.com/bierman323/configs.git'

def setup_os(what_os):
    global path
    if what_os == 'Linux':
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
    check_package('git')
    if not os.path.exists(f'{path}/configs'):
        os.chdir(path)
        subprocess.call(['git', 'clone', f'{github_clone}'])
    else:
        os.chdir(f'{path}/configs')
        subprocess.call(['git', 'pull', '--rebase'])

# Check that VIM is installed
# if no VIM install it
def check_vim():
    check_package('vim')

# Check that TMUX is installed
# if no TMUX install it
def check_tmux():
    check_package('tmux')

# Check that zsh is installed
# if not install zsh
def check_zsh():
    check_package('zsh')

# Configure VIM, TMUX, zsh, git


# What platform are we running on
def get_os():
    return platform.system()

# Main function
def main():
    what_os = get_os()
    setup_os(what_os)
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
    else:
        if args.vim:
            check_vim()
        if args.tmux:
            check_tmux()
        if args.zsh:
            check_zsh()


# start of execution
if __name__ == '__main__':
    main()
