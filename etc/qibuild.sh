##
# helper functions for qibuild

function qicd {
  p=$(python -m 'qicd' $@)
  if [[ $? -ne 0 ]]; then
    return 1
  fi
  cd ${p}
}
