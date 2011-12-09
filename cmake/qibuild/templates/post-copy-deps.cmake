set(CMAKE_MODULE_PATH "@_qibuild_cmake_module_path@")
include(qibuild/general)
include(qibuild/internal/fix_shared_libs)
_qi_fix_shared_libs()
