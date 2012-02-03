## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

# install with support for directory, globbing and files.
# this function know how to handle COMPONENT and KEEP_RELATIVE_PATHS
function(_qi_install_internal)
  cmake_parse_arguments(ARG "RECURSE;KEEP_RELATIVE_PATHS" "IF;COMPONENT;DESTINATION;SUBFOLDER" "" ${ARGN})
  if(NOT ARG_DESTINATION)
    qi_error("Invalid arguments for qi_install. Missing DESTINATION argument")
  endif()

  if (NOT "${ARG_IF}" STREQUAL "")
    set(_doit TRUE)
  else()
    #I must say... lol cmake, but NOT NOT TRUE is not valid!!
    if (${ARG_IF})
    else()
      set(_doit TRUE)
    endif()
  endif()
  if (NOT _doit)
    return()
  endif()

  set(_glob_keyword)
  if(${ARG_RECURSE})
    set(_glob_keyword GLOB_RECURSE)
  else()
    set(_glob_keyword GLOB)
  endif()
  set(_files_to_install)
  set(_dirs_to_install)
  foreach(f ${ARG_UNPARSED_ARGUMENTS})
    get_filename_component(_abs_path "${f}" ABSOLUTE)
    if(IS_DIRECTORY ${_abs_path})
      list(APPEND _dirs_to_install ${f})
    else()
      file(${_glob_keyword} _file_to_install RELATIVE ${CMAKE_CURRENT_SOURCE_DIR} ${f})
      if(NOT _file_to_install)
        qi_error(
"Error when parsing qi_install arguments:
  '${f}' does not match any files")
      endif()
      list(APPEND _files_to_install ${_file_to_install})
    endif()
  endforeach()

  install(DIRECTORY ${_dirs_to_install}
    COMPONENT "${ARG_COMPONENT}"
    DESTINATION "${ARG_DESTINATION}/${ARG_SUBFOLDER}")
  if(${ARG_KEEP_RELATIVE_PATHS})
    foreach(_file ${_files_to_install})
      get_filename_component(_file_subdir ${_file} PATH)
      install(FILES ${_file}
        COMPONENT "${ARG_COMPONENT}"
        DESTINATION "${ARG_DESTINATION}/${ARG_SUBFOLDER}/${_file_subdir}")
    endforeach()
  else()
    # Use standard cmake install() function
    install(FILES ${_files_to_install}
      COMPONENT "${ARG_COMPONENT}"
      DESTINATION "${ARG_DESTINATION}/${ARG_SUBFOLDER}")
  endif()
endfunction()
