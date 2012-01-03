## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.




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
