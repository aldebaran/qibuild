## Copyright (C) 2011 Aldebaran Robotics

# Copy every dll from CMAKE_FIND_ROOT_PATH into the build dir,
# then set _QI_DLLS_COPIED so that this only happens once

if(DEFINED _QI_DLLS_COPIED)
  return()
endif()

qi_info("Copying dlls in build dir ...")

set(_prefix_paths ${CMAKE_FIND_ROOT_PATH})
list(REMOVE_DUPLICATES _prefix_paths)

set(_dlls)

foreach(_prefix_path ${_prefix_paths})
  set(_bin_path "${_prefix_path}/bin")
  file(GLOB _glob
    "${_bin_path}/*.dll")
  list(APPEND _dlls ${_glob})
endforeach()

if(_dlls)
  list(REMOVE_DUPLICATES _dlls)
endif()

set(_dest "${QI_SDK_DIR}/${QI_SDK_BIN}")

set(_mess "Copying dlls:\n")
foreach(_dll ${_dlls})
  get_filename_component(_dll_name "${_dll}" NAME)
  set(_mess "${_mess}- ${_dll_name}\n")
endforeach()
set(_mess "${_mess} to ${_dest}")

if($ENV{VERBOSE})
  message(STATUS ${_mess})
endif()

file(COPY ${_dlls} DESTINATION "${_dest}")

qi_set_global(_QI_DLLS_COPIED)
