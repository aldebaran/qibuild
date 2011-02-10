## Copyright (C) 2011 Aldebaran Robotics

# install with support for directory, globbing and files.
# this function know how to handle COMPONENT
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

  install(DIRECTORY ${_dirs_to_install} COMPONENT "${ARG_COMPONENT}" DESTINATION "${ARG_DESTINATION}")
  install(FILES ${_files_to_install}    COMPONENT "${ARG_COMPONENT}" DESTINATION "${ARG_DESTINATION}")
endfunction()
