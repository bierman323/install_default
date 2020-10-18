export PATH=/Users/bbierman/bin:/usr/local/sbin:/usr/local/bin:/opt/local/bin:/opt/local/sbin:/usr/bin:$PATH
export HOMEBREW_GITHUB_API_TOKEN="aede7826af18354023e12126080ef2e926a52b20"
# export PYTHONPATH=/usr/local/lib/python2.7/site-packages/
#. /Library/Python/2.7/site-packages/powerline/bindings/bash/powerline.sh
alias df='df -h'
alias free='free -g'
alias du='du -h'
alias ll='ls -lh'
alias la='ls -alh'
alias updatedb='sudo /usr/libexec/locate.updatedb'
alias fuck='sudo $(history -p \!\!)'

function bliff(){
  pushd /Users/bbierman/bin/TekDefense-Automater
  ./Automater.py -r -w output.html "$1"
  popd
}

function title {
      echo -ne "\033]0;"$*"\007"
}

export HOMEBREW_GITHUB_API_TOKEN=a82866d782b55238c7fe66c1af00f865f2572704


echo
fortune

test -e "${HOME}/.iterm2_shell_integration.bash" && source "${HOME}/.iterm2_shell_integration.bash"

# Setting PATH for Python 3.8
# The original version is saved in .bash_profile.pysave
PATH="/Library/Frameworks/Python.framework/Versions/3.8/bin:${PATH}"
export PATH
