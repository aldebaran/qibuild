if [[ -n ${SKIP_BEFORE_INSTALL} ]] ; then
  echo "skipping install. some tests may fail"
  exit 0
fi

if [[ "${TRAVIS_OS_NAME}" == "osx" ]] ; then
  brew update
  # CMake is already installed but too old
  # we need `cmake -E env` since
  # 10482d2463f41147962004be8d41cf68e4388dc9
  brew outdated cmake || brew upgrade cmake
  # for qipy tests
  brew install swig
  # for qilinguist tests
  brew install gettext
  # for qidoc tests
  brew install doxygen
fi
if [[ "${TRAVIS_OS_NAME}" == "linux" ]] ; then
  sudo apt-get update -qq
  sudo apt-get install -y ninja-build swig python-enchant
fi
