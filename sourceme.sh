#!/bin/bash

# Source this file to use qibuild from its source dir


# find qibuild root directory
qibuild_dir=""

if readlink -f . >/dev/null 2>/dev/null ; then
    qibuild_dir=$(dirname "$(readlink -f ${0} 2>/dev/null)")
else
    qibuild_dir=$(dirname "${0}")
    qibuild_dir=$PWD/${this_dir}
fi


# set path
export PATH="${qibuild_dir}/python/bin:$PATH"


# define aliases
alias qc="qibuild configure"
alias qm="qibuild make"
alias qi="qibuild install"
alias qd="qibuild deploy"
alias qo="qibuild open"

# helper functions
function qicd {
  p=$(python ${qibuild_dir}/python/bin/qicd.py $1)
  if [[ $? -ne 0 ]]; then
    return
  fi
  cd ${p}
}

function q {
  qibuild configure $@ && qibuild make $@
}
