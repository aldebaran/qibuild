#!/bin/bash

python tools/install-qibuild.py

mkdir -p /usr/local/bin

function install_wrapper {
  name=$1
  script_path=$(which ${name}.py)
  ln -sf $script_path /usr/local/bin/$1
}

install_wrapper qitoolchain
install_wrapper qibuild
install_wrapper qisrc

