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
