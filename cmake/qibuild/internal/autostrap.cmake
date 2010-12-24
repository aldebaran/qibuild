##
## Author(s):
##  - Cedric GESTES <gestes@aldebaran-robotics.com>
##
## Copyright (C) 2009, 2010 Aldebaran Robotics
##

if (_AUTOSTRAP_CMAKE_)
  return()
endif()

set(_AUTOSTRAP_CMAKE_ TRUE)


# extract the version of a bootstrap file
#
function(qi_autostrap_get_version file OUT_version)
  file(READ ${file} _tmp)
  set(_version)
  #first we match the BOOTSTRAP_VERSION line
  string(REGEX MATCH "QIBUILD_BOOTSTRAP_VERSION *([0-9\\.]+)" _version "${_tmp}")
  #message(STATUS "Version is: ${_version}")
  #extract the version number from the previous line
  string(REGEX REPLACE ".*QIBUILD_BOOTSTRAP_VERSION *([0-9\\.]+).*" "\\1" _version "${_version}")
  #message(STATUS "Version is: ${_version}")
  set(${OUT_version} ${_version} PARENT_SCOPE)
endfunction()

# autoupdate bootstrap files
#
# 1/ find qibuild.cmake in the current source dir (if any)
# 2/ check the version
# 3/ if a new version is available, replace by the new version
#
function(autostrap_update)
  get_filename_component(_THIS_DIR ${CMAKE_CURRENT_LIST_FILE} PATH)
  if (NOT EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/qibuild.cmake")
    return()
  endif()
  autostrap_get_version("${CMAKE_CURRENT_SOURCE_DIR}/qibuild.cmake" _vdest)
  autostrap_get_version("${THIS_DIR}/../templates/bootstrap.cmake" _vsrc)
  if(_vsrc VERSION_GREATER _vdest)
    message(STATUS "Bootstrap upstream version : ${_vsrc}")
    message(STATUS "Bootstrap source version   : ${_vdest}")
    message(STATUS "Bootstrap will be updated")
    configure_file("${THIS_DIR}/../templates/bootstrap.cmake"
                   "${CMAKE_CURRENT_SOURCE_DIR}/qibuild.cmake" COPYONLY)
  endif()
endfunction()

