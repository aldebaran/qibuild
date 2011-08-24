## Copyright (C) 2011 Aldebaran Robotics

# Create symlinks to dylib and framework to every .dylib and
# .Frawework found in CMAKE_PREFIX_PATH

# This way you only have to set DYLD_LIBRARY_PATH to
# build/sdk/lib and DYLD_FRAMEWORK_PATH to build/sdk/
# and it will just work


if(DEFINED _QI_DYLIBS_FIXED)
  return()
endif()

qi_info("Creating symlinks in build dir ...")


set(_prefix_paths ${CMAKE_PREFIX_PATH})
list(REMOVE_DUPLICATES _prefix_paths)

set(_dylibs)
set(_frameworks)

foreach(_prefix_path ${_prefix_paths})
  file(GLOB _glob "${_prefix_path}/lib/*.dylib")
  list(APPEND _dylibs ${_glob})
  file(GLOB _glob "${_prefix_path}/*.framework")
  list(APPEND _frameworks ${_glob})
endforeach()

file(MAKE_DIRECTORY ${QI_SDK_DIR}/${QI_SDK_LIB})


foreach(_dylib ${_dylibs})
  get_filename_component(_name "${_dylib}" NAME)
  set(_dest "${QI_SDK_DIR}/${QI_SDK_LIB}/${_name}")
  execute_process(
    COMMAND
      "${CMAKE_COMMAND}" "-E" "create_symlink" "${_dylib}" "${_dest}"
  )
endforeach()

foreach(_framework ${_frameworks})
  get_filename_component(_name "${_framework}" NAME)
  set(_dest "${QI_SDK_DIR}/${_name}")
  execute_process(
    COMMAND
      "${CMAKE_COMMAND}" "-E" "create_symlink" "${_framework}" "${_dest}"
  )
endforeach()



qi_set_global(_QI_DYLIBS_FIXED)
