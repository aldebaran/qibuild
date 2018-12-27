## Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

## Helper function for the qt5_* qibuild's modules

####
# Find a Qt library
# Usage:
# qt5_flib(QT5_CORE Qt5Core)

function(qt5_flib prefix name)
  # upstream uses Qt5::Core notation but we need to dereference this
  # because we won't be calling find_package() again

  # the first time we call upstream's find_package it defines
  # a target and set _INCLUDE_DIRS and LIBRARIES variables,
  # but the second time the target is already defined, and the
  # var get unset, so store it in cache when they are not
  # empty
  find_package(${name})
  if(${name}_INCLUDE_DIRS)
    qi_persistent_set(${name}_INCLUDE_DIRS ${${name}_INCLUDE_DIRS})
  endif()
  if(${name}_LIBRARIES)
    qi_persistent_set(${name}_LIBRARIES ${${name}_LIBRARIES})
  endif()

  # now set the varibables with the correct prefix:
  qi_persistent_set(${prefix}_LIBRARIES ${${name}_LIBRARIES})
  qi_persistent_set(${prefix}_INCLUDE_DIRS ${${name}_INCLUDE_DIRS})
  set(_define ${prefix}_LIB)
  string(REPLACE QT5 QT _define ${_define})
  qi_persistent_set(${prefix}_DEFINITIONS ${_define})

  export_lib(${prefix})
endfunction()
