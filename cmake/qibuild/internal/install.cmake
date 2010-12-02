##
## Author(s):
##  - Cedric GESTES <gestes@aldebaran-robotics.com>
##
## Copyright (C) 2010 Aldebaran Robotics
##

function(_qi_install)
  cmake_parse_arguments(ARG "" "COMPONENT;DESTINATION" "" ${ARGN})

  set(_files_to_install)
  set(_dirs_to_install)
  foreach(f ${ARG_UNPARSED_ARGUMENTS})
    get_filename_component(_abs_path "${f}" ABSOLUTE)
    if(IS_DIRECTORY ${_abs_path})
      list(APPEND _dirs_to_install ${f})
    else()
      file(GLOB _file_to_install ${f})
      if ("${_file_to_install}" STREQUAL "")
        list(APPEND _files_to_install ${f})
      else()
        list(APPEND _files_to_install ${_file_to_install})
      endif()
    endif()
  endforeach()


  message(STATUS "instfile: ${_files_to_glob}")
  message(STATUS "instfile: ${_files_to_install}")
  message(STATUS "instdir: ${_dirs_to_install}")
  install(DIRECTORY ${_dirs_to_install} COMPONENT "${ARG_COMPONENT}" DESTINATION "${ARG_DESTINATION}")
  install(FILES ${_files_to_install}    COMPONENT "${ARG_COMPONENT}" DESTINATION "${ARG_DESTINATION}")
endfunction()
