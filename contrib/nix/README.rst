qiBuild Nix packages
====================

To enter an environment with only qiBuild, do::

  nix-shell --pure --packages '(callPackage ./default.nix {}).qibuild'

For an environment with only qiBuild and all its optional dependencies, do::

  nix-shell --pure --packages '(callPackage ./default.nix {}).qibuild_full'

For an environment with qiBuild's dependencies, do::

  nix-shell --attr qibuild_full

To install qibuild and its dependencies, do::

  nix-env --file default.nix --install --attr qibuild_full
