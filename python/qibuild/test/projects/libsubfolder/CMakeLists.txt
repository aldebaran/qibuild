cmake_minimum_required(VERSION 2.8)
project(libsubfolder C)

find_package(qibuild)

qi_create_lib(foo foo.c SUBFOLDER foo)
qi_stage_lib(foo)

qi_create_bin(bar bar.c DEPENDS foo NO_RPATH)
set_target_properties(bar
  PROPERTIES
    INSTALL_RPATH "\$ORIGIN/../lib/foo")
