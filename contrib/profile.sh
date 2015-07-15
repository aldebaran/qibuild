
##
# cd to a project given part of its name
function qicd {
  p=$(python -m 'qicd' $1)
  if [[ $? -ne 0 ]]; then
    return
  fi
  cd ${p}
}
