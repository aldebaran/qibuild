function qc {
  qibuild configure --color=always $* | colout -t cmake
}

function qm {
  qibuild make --color=always $* | colout -t g++
}
