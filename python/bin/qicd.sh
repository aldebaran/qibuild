function qicd {
  p=$(qicd.py $1)
  if [[ $? -ne 0 ]]; then
    return
  fi
  cd ${p}
}

