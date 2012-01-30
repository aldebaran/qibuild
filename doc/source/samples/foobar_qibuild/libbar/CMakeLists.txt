include_directories(".")

qi_create_lib(bar
  bar/bar.hpp
  bar/bar.cpp)

qi_stage_lib(bar)

qi_install_header(bar/bar.hpp
  SUBFOLDER bar)
