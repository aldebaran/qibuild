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
