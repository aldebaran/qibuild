## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

if (_AUTOSTRAP_CMAKE_)
  return()
endif()

set(_AUTOSTRAP_CMAKE_ TRUE)


# extract the version of a bootstrap file
#
function(_qi_autostrap_get_version file OUT_version)
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
function(_qi_autostrap_update)
  if (NOT EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/qibuild.cmake")
    return()
  endif()
  _qi_autostrap_get_version("${CMAKE_CURRENT_SOURCE_DIR}/qibuild.cmake" _vdest)
  _qi_autostrap_get_version("${QI_TEMPLATE_DIR}/qibuild.cmake" _vsrc)
  if(_vsrc VERSION_GREATER _vdest)
    message(STATUS "Bootstrap upstream version : ${_vsrc}")
    message(STATUS "Bootstrap source version   : ${_vdest}")
    message(STATUS "Bootstrap will be updated")
    configure_file("${QI_TEMPLATE_DIR}/qibuild.cmake"
                   "${CMAKE_CURRENT_SOURCE_DIR}/qibuild.cmake" COPYONLY)
  endif()
endfunction()

