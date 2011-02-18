## Copyright (C) 2011 Aldebaran Robotics

# install with support for directory, globbing and files.
# this function know how to handle COMPONENT
function(_qi_install)
  cmake_parse_arguments(ARG "" "IF;COMPONENT;DESTINATION" "" ${ARGN})

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
