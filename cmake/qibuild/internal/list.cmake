## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.
function(_qi_list_append_uniq _list)
  foreach(_pif ${ARGN})
    list(FIND ${_list} ${_pif} _found)
    if(_found STREQUAL "-1")
      set(${_list} ${${_list}} ${_pif})
    endif()
  endforeach()
  set(${_list} ${${_list}} PARENT_SCOPE)
endfunction()

# Add a value to a list of paths,
# keeping the list sorted, whithout
# duplicates and only canonical paths
function(_qi_list_append_path _list)
  foreach(_path ${ARGN})
    get_filename_component(_abs_path ${_path} REALPATH)
    file(TO_CMAKE_PATH ${_abs_path} _abs_path)
    _qi_list_append_uniq(${_list} ${_abs_path})
  endforeach()
  set(${_list} ${${_list}} PARENT_SCOPE)
endfunction()

