opts@{...}:

let pkgs = import <nixpkgs> opts; in

with pkgs.pythonPackages;

rec {
  qibuild = buildPythonPackage rec {
    baseName = "qibuild";
    version = "git";
    name = "${baseName}-${version}";

    src = ../..;

    meta = {
      homepage = http://doc.aldebaran.com/qibuild/;
      description = "compilation of C++ projects made easy";
      license = pkgs.stdenv.lib.licenses.bsd3;
    };
  };

  qibuild_full = qibuild.override {
    propagatedBuildInputs = with pkgs; [ cmake doxygen sphinxbase git qt5Full gettext pythonPackages.pyxdg ];
  };
}
