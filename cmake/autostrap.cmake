##
## Author(s):
##  - Cedric GESTES <gestes@aldebaran-robotics.com>
##
## Copyright (C) 2009 Aldebaran Robotics
##

if (NOT _AUTOSTRAP_CMAKE_)
set(_AUTOSTRAP_CMAKE_ TRUE)


###########################
#
# extract the version of a bootstrap file
#
###########################
function(autostrap_get_version file OUT_version)
  file(READ ${file} _tmp)
  set(_version)
  #first we match the BOOTSTRAP_VERSION line
  string(REGEX MATCH "BOOTSTRAP_VERSION *([0-9\\.]+)" _version "${_tmp}")
  #message(STATUS "Version is: ${_version}")
  #extract the version number from the previous line
  string(REGEX REPLACE ".*BOOTSTRAP_VERSION *([0-9\\.]+).*" "\\1" _version "${_version}")
  #message(STATUS "Version is: ${_version}")
  set(${OUT_version} ${_version} PARENT_SCOPE)
endfunction(autostrap_get_version)

###########################
#
# autoupdate bootstrap files
#
# 1/ find the bootstrap.cmake file of the current source dir (if any)
# 2/ check the version
# 3/ if a new version is available, replace by the new version
#
###########################
function(autostrap_update)
  if (NOT EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/bootstrap.cmake")
    return()
  endif (NOT EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/bootstrap.cmake")
  autostrap_get_version("${CMAKE_CURRENT_SOURCE_DIR}/bootstrap.cmake" _vdest)
  autostrap_get_version("${T001CHAIN_DIR}/cmake/templates/bootstrap.cmake" _vsrc)
  if(_vsrc VERSION_GREATER _vdest)
    message(STATUS "Bootstrap upstream version : ${_vsrc}")
    message(STATUS "Bootstrap source version   : ${_vdest}")
    message(STATUS "Bootstrap will be updated")
    configure_file("${T001CHAIN_DIR}/cmake/templates/bootstrap.cmake"
                   "${CMAKE_CURRENT_SOURCE_DIR}/bootstrap.cmake" COPYONLY)
  endif(_vsrc VERSION_GREATER _vdest)

endfunction(autostrap_update)

endif (NOT _AUTOSTRAP_CMAKE_)
