# Need to set $PATH so we can run stuff instaled
# with pip install --user
if [[ "${TRAVIS_OS_NAME}" == "osx" ]] ; then
  export PATH="$HOME/Library/Python/2.7/bin:$PATH"
  # Need to find gettext binaries in /usr/local/opt/gettext/bin
  # by homebrew
  export PATH="/usr/local/opt/gettext/bin:$PATH"
fi
if [[ "${TRAVIS_OS_NAME}" == "linux" ]] ; then
  export PATH="$HOME/.local/bin:$PATH"
fi

cd python && invoke pylint --errors-only test
