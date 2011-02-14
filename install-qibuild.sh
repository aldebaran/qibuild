#!/bin/bash

python tools/install-qibuild.py

mkdir -p /usr/local/bin

function install_wrapper {
  name=$1
  script_path=$(which ${name}.py)
  python=$(which python)
  echo "#!/bin/bash" > /usr/local/bin/${name}
  echo "${python} ${script_path} \$@" >> /usr/local/bin/${name}
  chmod +x /usr/local/bin/${name}
}

install_wrapper qitoolchain
install_wrapper qibuild
install_wrapper qisrc

