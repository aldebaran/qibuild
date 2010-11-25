##
## Author(s):
##  - Cedric GESTES <gestes@aldebaran-robotics.com>
##
## Copyright (C) 2009 Aldebaran Robotics
##

function(create_cmake _NAME)
  parse_is_options(_args NO_INSTALL _no_install ${ARGN})

  set(_fname "${_NAME}Config.cmake")
  if (NOT EXISTS ${_fname})
    set(_fname "${CMAKE_CURRENT_SOURCE_DIR}/${_NAME}Config.cmake")
  endif (NOT EXISTS ${_fname})

  if (NOT EXISTS ${_fname})
    error("create_cmake: the file ${_NAME}Config.cmake doest not exist")
  endif (NOT EXISTS ${_fname})

  if (_no_install)
    debug("${_NAME} is not to be installed")
  else()
    install_cmake("modules" ${_fname})
  endif()
  copy_with_depend(${_fname} "${_SDK_CMAKE_MODULES}/")
  get_filename_component(_ROOT_DIR ${CMAKE_CURRENT_LIST_FILE} PATH)
  set(_internal ${_ROOT_DIR} ${_INTERNAL_TC_CMAKE_DIRS})
  list(REMOVE_DUPLICATES _internal)
  set(_INTERNAL_TC_CMAKE_DIRS ${_internal} CACHE INTERNAL "" FORCE)
endfunction(create_cmake _NAME)

function(use _NAME)
  find_package(${_NAME} PATHS ${_INTERNAL_TC_CMAKE_DIRS} "${SDK_DIR}/${_SDK_CMAKE_MODULES}/" ${_INTERNAL_SDK_DIRS} NO_DEFAULT_PATH)
endfunction(use _NAME)
