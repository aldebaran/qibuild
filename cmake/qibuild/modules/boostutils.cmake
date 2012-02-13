## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

function(boost_flib _libname)
  string(TOUPPER ${_libname} _prefix)
  set(_prefix "BOOST_${_prefix}")
  clean(${_prefix})
  # Required so that FindBoost.cmake does not try to include this file
  set(Boost_NO_BOOST_CMAKE TRUE)
  find_package(Boost COMPONENTS "${_libname}" QUIET)
  qi_set_global(${_prefix}_INCLUDE_DIRS ${Boost_INCLUDE_DIRS})
  qi_set_global(${_prefix}_LIBRARIES    ${Boost_LIBRARIES})
  export_lib(${_prefix})
endfunction()
