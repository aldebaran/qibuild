## Copyright (c) 2012-2016 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

# Make sure newly built executables can run.
# On mac, create symlinks in build/sdk/lib, on windows,
# copy every dll to bin/
# This function needs to run only once, but *after* every target
# has been built.
function(_qi_fix_shared_libs)
  if(EXISTS "${CMAKE_SOURCE_DIR}/shared_libs_fixed")
    return()
  endif()

  if(APPLE)
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
      if(NOT EXISTS ${_dest})
        execute_process(
          COMMAND
            "${CMAKE_COMMAND}" "-E" "create_symlink" "${_dylib}" "${_dest}"
        )
      endif()
    endforeach()

    foreach(_framework ${_frameworks})
      get_filename_component(_name "${_framework}" NAME)
      set(_dest "${QI_SDK_DIR}/${_name}")
      if(NOT EXISTS ${_dest})
        execute_process(
          COMMAND
            "${CMAKE_COMMAND}" "-E" "create_symlink" "${_framework}" "${_dest}"
        )
      endif()
    endforeach()
  endif()

  if(WIN32)
    qi_info("Copying dlls in build dir ...")

    set(_prefix_paths ${CMAKE_PREFIX_PATH})
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
  endif()

  file(WRITE "${CMAKE_SOURCE_DIR}/shared_libs_fixed" "")

endfunction()
