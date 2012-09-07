## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

#WARNING you should always call qi_global_get to get a global variable
macro(qi_global_set name)
  set_property(GLOBAL PROPERTY "${name}" ${ARGN})
endmacro()

macro(qi_global_get OUT_var name)
  #macro so no need for PARENT_SCOPE
  get_property("${OUT_var}" GLOBAL PROPERTY "${name}")
endmacro()

macro(qi_global_is_set OUT_var name)
  #macro so no need for PARENT_SCOPE
  get_property("${OUT_var}" GLOBAL PROPERTY "${name}" SET)
endmacro()


#persistent across run
macro(qi_persistent_set _name)
  set("${_name}" ${ARGN} CACHE INTERNAL "" FORCE)
endmacro()

macro(qi_persistent_get OUT_var name)
  #macro so no need for PARENT_SCOPE
  get_property("${OUT_var}" CACHE PROPERTY "${name}")
endmacro()

macro(qi_persistent_is_set OUT_var name)
  #macro so no need for PARENT_SCOPE
  get_property("${OUT_var}" CACHE PROPERTY "${name}" SET)
endmacro()

macro(qi_persistent_append _name)
  list(APPEND "${_name}" ${ARGN})
  set("${_name}" "${${_name}}" CACHE INTERNAL "" FORCE)
endmacro()

macro(qi_persistent_prepend _name)
  list(INSERT "${_name}" 0 ${ARGN})
  set("${_name}" "${${_name}}" CACHE INTERNAL "" FORCE)
endmacro()

function(qi_persistent_append_uniq _name)
  foreach(_value ${ARGN})
    list(FIND "${_name}" ${_value} _found)
    if (_found STREQUAL "-1")
      qi_persistent_append("${_name}" ${_value})
    endif()
  endforeach()
endfunction()

function(qi_persistent_prepend_uniq _name)
  foreach(_value ${ARGN})
    list(FIND "${_name}" ${_value} _found)
    if (_found STREQUAL "-1")
      qi_persistent_prepend("${_name}" ${_value})
    endif()
  endforeach()
endfunction()

## DEPRECATED ##


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

macro(qi_append_uniq_global _name)
  foreach(_value ${ARGN})
    list(FIND "${_name}" ${_value} _found)
    if (_found STREQUAL "-1")
      list(APPEND "${_name}" ${_value})
      set("${_name}" "${${_name}}" CACHE INTERNAL "" FORCE)
    endif()
  endforeach()
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
