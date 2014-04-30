
##
# cd to a project given part of its name
function qicd {
  p=$(python -m 'qicd' $1)
  if [[ $? -ne 0 ]]; then
    return
  fi
  cd ${p}
}


##
# Two usages:
#   qipython foo.py: run foo.py from the virtualenv in the worktre
#   qipython activate: activate the virtualenv in the worktre
orig_qipython=$(which qipython)
function qipython_magic {
  if [[ "$1" == "activate" ]] ; then
    source $($orig_qipython activate)
  else
    $orig_qipython "$@"
  fi
}

alias qipython=qipython_magic

