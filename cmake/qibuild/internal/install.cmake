## Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

# install with support for directory, globbing and files.
# this function know how to handle COMPONENT and KEEP_RELATIVE_PATHS
function(_qi_install_internal)
  cmake_parse_arguments(ARG "RECURSE;KEEP_RELATIVE_PATHS;EXCLUDE"
                            "IF;COMPONENT;DESTINATION;SUBFOLDER;PATTERN" "" ${ARGN})
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
    if("${f}" MATCHES "\\*")
      file(${_glob_keyword} _file_to_install RELATIVE ${CMAKE_CURRENT_SOURCE_DIR} ${f})
      if(NOT _file_to_install)
        qi_error(
          "Error when parsing qi_install arguments:
          '${f}' glob does not match any file")
      endif()
      list(APPEND _files_to_install ${_file_to_install})
    elseif(IS_DIRECTORY ${_abs_path})
      list(APPEND _dirs_to_install ${f})
    elseif(EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/${f}" OR EXISTS "${f}")
      list(APPEND _files_to_install "${f}")
    else()
      get_source_file_property(_generated "${f}" GENERATED)
      if(_generated)
        list(APPEND _files_to_install ${f})
        # nothing
      else()
        qi_error("${f} does not exist and is not marked as a generated source")
      endif()
    endif()
  endforeach()

  if(ARG_SUBFOLDER)
    set(_dest ${ARG_DESTINATION}/${ARG_SUBFOLDER})
  else()
    set(_dest ${ARG_DESTINATION})
  endif()
  install(DIRECTORY ${_dirs_to_install}
    USE_SOURCE_PERMISSIONS
    DIRECTORY_PERMISSIONS
      OWNER_READ OWNER_WRITE OWNER_EXECUTE
      GROUP_READ GROUP_WRITE GROUP_EXECUTE
      WORLD_READ             WORLD_EXECUTE
    COMPONENT "${ARG_COMPONENT}"
    DESTINATION "${_dest}"
        PATTERN "*.pyc" EXCLUDE
        PATTERN "__pycache__" EXCLUDE)
  if(${ARG_KEEP_RELATIVE_PATHS})
    foreach(_file ${_files_to_install})
      get_filename_component(_file_subdir ${_file} PATH)
      install(FILES ${_file}
        COMPONENT "${ARG_COMPONENT}"
        DESTINATION "${_dest}/${_file_subdir}")
    endforeach()
  else()
    # Use standard cmake install() function
    install(FILES ${_files_to_install}
      COMPONENT "${ARG_COMPONENT}"
      DESTINATION "${_dest}")
  endif()
endfunction()
