## Copyright (c) 2011, Aldebaran Robotics
## All rights reserved.
##
## Redistribution and use in source and binary forms, with or without
## modification, are permitted provided that the following conditions are met:
##     * Redistributions of source code must retain the above copyright
##       notice, this list of conditions and the following disclaimer.
##     * Redistributions in binary form must reproduce the above copyright
##       notice, this list of conditions and the following disclaimer in the
##       documentation and/or other materials provided with the distribution.
##     * Neither the name of the Aldebaran Robotics nor the
##       names of its contributors may be used to endorse or promote products
##       derived from this software without specific prior written permission.
##
## THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
## ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
## WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
## DISCLAIMED. IN NO EVENT SHALL Aldebaran Robotics BE LIABLE FOR ANY
## DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
## (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
## LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
## ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
## (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
## SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

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

