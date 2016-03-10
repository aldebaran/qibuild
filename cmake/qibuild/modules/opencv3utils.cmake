## Copyright (c) 2016 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

function(opencv3_flib name)
  cmake_parse_arguments(ARG "" "" "DEPENDS" ${ARGN})
  string(TOUPPER ${name} _prefix)
  set(_prefix OPENCV3_${_prefix})
  set(_header opencv2/${name}.hpp)
  set(_libname opencv_${name})
  fpath(${_prefix} ${_header})
  flib(${_prefix} ${_libname})

  if(ARG_DEPENDS)
    set(_lib_deps)
    foreach(_dep ${ARG_DEPENDS})
      string(TOUPPER ${_dep} _U_dep)
      list(APPEND _lib_deps OPENCV3_${_U_dep})
    endforeach()
    qi_persistent_set(${_prefix}_DEPENDS ${_lib_deps})
  endif()
  export_lib(${_prefix})
endfunction()
