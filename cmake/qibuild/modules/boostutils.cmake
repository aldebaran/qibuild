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




function(boost_flib _suffix _libname)
  set (BOOST_VERSION 1_44)
  set(_linux_names
    "boost_${_libname}-mt"
    # for boost-locale < 1.37
    "boost_${_libname}"
  )

  set(_osx_names
    # boost on mac64
    "boost_${_libname}-xgcc40-mt-${BOOST_VERSION}"
    "boost_${_libname}-mt"
    # for boost-locale < 1.37
    "boost_${_libname}"
  )

  set(_vc_names_release
    # dynamic
    "boost_${_libname}-vc80-mt-${BOOST_VERSION}"
    "boost_${_libname}-vc90-mt-${BOOST_VERSION}"
    "boost_${_libname}-vc100-mt-${BOOST_VERSION}"
    # for boost-locale < 1.37
    "boost_${_libname}"
    # static
    "libboost_${_libname}-vc80-mt-${BOOST_VERSION}"
    "libboost_${_libname}-vc90-mt-${BOOST_VERSION}"
    "libboost_${_libname}-vc100-mt-${BOOST_VERSION}"
  )

  set(_vc_names_debug
    # dynamic
    "boost_${_libname}-vc80-mt-gd-${BOOST_VERSION}"
    "boost_${_libname}-vc90-mt-gd-${BOOST_VERSION}"
    "boost_${_libname}-vc100-mt-gd-${BOOST_VERSION}"
    # for boost-locale < 1.37
    "boost_${_libname}_d"
    # static
    "libboost_${_libname}-vc80-mt-gd-${BOOST_VERSION}"
    "libboost_${_libname}-vc90-mt-gd-${BOOST_VERSION}"
    "libboost_${_libname}-vc100-mt-gd-${BOOST_VERSION}"
  )

  set (_mingw_names_debug
    "libboost_${_libname}-mgw44-mt-d-${BOOST_VERSION}"
    # for boost-locale
    "libboost_${_libname}"
  )

  set (_mingw_names_release
    "libboost_${_libname}-mgw44-mt-${BOOST_VERSION}"
    # for boost-locale
    "libboost_${_libname}"
  )

  if(WIN32)
    if(MSVC)
      # vs
      flib(BOOST_${_suffix} DEBUG NAMES
        ${_vc_names_debug}
      )
      flib(BOOST_${_suffix} OPTIMIZED NAMES
        ${_vc_names_release}
      )
    else()
      # mingw
      flib(BOOST_${_suffix} DEBUG NAMES
        ${_mingw_names_debug}
      )
      flib(BOOST_${_suffix} OPTIMIZED NAMES
        ${_mingw_names_release}
      )
    endif()
  else() # No win32, no need for debug/release
    if(APPLE)
      flib(BOOST_${_suffix} NAMES ${_osx_names})
    else()
      flib(BOOST_${_suffix} NAMES ${_linux_names})
    endif()
  endif()
endfunction()
