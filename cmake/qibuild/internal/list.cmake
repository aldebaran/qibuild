## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.
function(_qi_list_append_uniq _list _value)

  list(APPEND ${_list} ${_value})
  list(SORT ${_list})
  list(REMOVE_DUPLICATES ${_list})
  set(${_list} ${${_list}} PARENT_SCOPE)
endfunction()

# Add a value to a list of paths,
# keeping the list sorted, whithout
# duplicates and only canonical paths
function(_qi_list_append_path _list _path)
  get_filename_component(_abs_path ${_path} REALPATH)
  file(TO_CMAKE_PATH ${_abs_path} _abs_path)
  _qi_list_append_uniq(${_list} ${_abs_path})
  set(${_list} ${${_list}} PARENT_SCOPE)
endfunction()


function(_qi_list_append_cache _name _value)
  _qi_list_append_uniq(${_name} ${_value})
  set(${_name} ${${_name}} CACHE INTERNAL "" FORCE)
endfunction()
