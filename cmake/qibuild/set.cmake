## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

# write the variable into cache, variable wont be visible
macro(qi_set_global name)
  set("${name}" ${ARGN} CACHE INTERNAL "" FORCE)
endmacro()

# write the variable into cache
macro(qi_set_cache name)
  set("${name}" ${ARGN} CACHE STRING "" FORCE)
endmacro()

# write the variable into cache, mark as an advanced variable
macro(qi_set_advanced_cache name)
  set("${name}" ${ARGN} CACHE STRING "" FORCE)
  mark_as_advanced("${name}")
endmacro()

macro(qi_append_global _name _value)
  list(APPEND "${_name}" ${_value} ${ARGN})
  set("${_name}" "${${_name}}" CACHE INTERNAL "" FORCE)
endmacro()

macro(qi_prepend_global _name _value)
  list(INSERT "${_name}" 0 ${_value} ${ARGN})
  set("${_name}" "${${_name}}" CACHE INTERNAL "" FORCE)
endmacro()

macro(qi_append_uniq_global _name _value)
  list(FIND "${_name}" ${_value} _found)
  if (_found STREQUAL "-1")
    list(APPEND "${_name}" ${_value} ${ARGN})
    set("${_name}" "${${_name}}" CACHE INTERNAL "" FORCE)
  endif()
endmacro()

macro(qi_prepend_uniq_global _name _value)
  list(FIND "${_name}" ${_value} _found)
  if (_found STREQUAL "-1")
    list(INSERT "${_name}" 0 ${_value} ${ARGN})
    set("${_name}" "${${_name}}" CACHE INTERNAL "" FORCE)
  endif()
endmacro()

macro(qi_uniq_global _name)
  if (${_name})
    list(REVERSE ${_name})
    list(REMOVE_DUPLICATES ${_name})
    list(REVERSE ${_name})
  endif()
endmacro()
