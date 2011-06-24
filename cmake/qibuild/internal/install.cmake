## Copyright (C) 2011 Aldebaran Robotics

# install with support for directory, globbing and files.
# this function know how to handle COMPONENT and KEEP_REL_PATHS
function(_qi_install)
  cmake_parse_arguments(ARG "KEEP_REL_PATHS" "IF;COMPONENT;DESTINATION" "" ${ARGN})

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
      file(GLOB_RECURSE _file_to_install RELATIVE ${CMAKE_CURRENT_SOURCE_DIR} ${f})
      list(APPEND _files_to_install ${_file_to_install})
    endif()
  endforeach()

  install(DIRECTORY ${_dirs_to_install}
    COMPONENT "${ARG_COMPONENT}"
    DESTINATION "${ARG_DESTINATION}")
  if(${ARG_KEEP_REL_PATHS})
    foreach(_file ${_files_to_install})
      get_filename_component(_file_subdir ${_file} PATH)
      install(FILES ${_file}
        COMPONENT "${ARG_COMPONENT}"
        DESTINATION "${ARG_DESTINATION}/${_file_subdir}")
    endforeach()
  else()
    # Use standard cmake install() function
    install(FILES ${_files_to_install}
      COMPONENT "${ARG_COMPONENT}"
      DESTINATION "${ARG_DESTINATION}")
  endif()
endfunction()
