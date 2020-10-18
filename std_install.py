#!/usr/bin/env python3
import argparse, platform, sys, os

def setup_imports(what_os):
    if what_os == 'Linux':
        print(f'Here {what_os}')

# parse out the arguments
def setup_args():
    parser = argparse.ArgumentParser(description='System Setup')
    parser.add_argument('-v', '--vim', help="Configure VIM", action='store_true', default=False)
    parser.add_argument('-t', '--tmux', help="Configure TMUX", action='store_true', default=False)
    parser.add_argument('-z', '--zsh', help="Configure ZSH", action='store_true', default=False)
    parser.add_argument('-g', '--git', help="Configure GIT", action='store_true', default=False)

    args = parser.parse_args()
    return args

# Check if GIT is installed
# if no GIT, install it
def check_git():


# Check that VIM is installed
# if no VIM install it

# Check that TMUX is installed
# if no TMUX install it

# Check that we are using zsh
# if not switch to zsh

# Configure VIM, TMUX, zsh, git


# What platform are we running on
def get_os():
    return platform.system()

# Main function
def main():
    what_os = get_os()
    setup_imports(what_os)
    if not len(sys.argv) > 1:
       do_all = True
    else:
        do_all = False
        args = setup_args()

    if do_all:
        # GIT
        # ZSH
        # VIM
        # TMUX
        print('all')
    else:
        if args.git:
            # GIT
            print('Git')
            check_git()
        if args.vim:
            # VIM
            print('vim')
        if args.tmux:
            # TMUX
            print('tmux')
        if args.zsh:
            # ZSH
            print('zsh')


# start of execution
if __name__ == '__main__':
    main()
