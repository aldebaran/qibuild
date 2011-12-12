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

# install with support for directory, globbing and files.
# this function know how to handle COMPONENT and KEEP_RELATIVE_PATHS
function(_qi_install_internal)
  cmake_parse_arguments(ARG "KEEP_RELATIVE_PATHS" "IF;COMPONENT;DESTINATION;SUBFOLDER" "" ${ARGN})
  if(NOT ARG_DESTINATION)
    qi_error("Invalid arguments for qi_install. Missing DESTINATION argument")
  endif()

  if (NOT "${ARG_IF}" STREQUAL "")
    set(_doit TRUE)
  else()
    #I must say... lol cmake, but NOT NOT TRUE is not valid!!
    if (${ARG_IF})
    else()
      set(_doit TRUE)
    endif()
  endif()
  if (NOT _doit)
    return()
  endif()

  set(_files_to_install)
  set(_dirs_to_install)
  foreach(f ${ARG_UNPARSED_ARGUMENTS})
    get_filename_component(_abs_path "${f}" ABSOLUTE)
    if(IS_DIRECTORY ${_abs_path})
      list(APPEND _dirs_to_install ${f})
    else()
      file(GLOB_RECURSE _file_to_install RELATIVE ${CMAKE_CURRENT_SOURCE_DIR} ${f})
      if(NOT _file_to_install)
        qi_error(
"Error when parsing qi_install arguments:
  '${f}' does not match any files")
      endif()
      list(APPEND _files_to_install ${_file_to_install})
    endif()
  endforeach()

  install(DIRECTORY ${_dirs_to_install}
    COMPONENT "${ARG_COMPONENT}"
    DESTINATION "${ARG_DESTINATION}/${ARG_SUBFOLDER}")
  if(${ARG_KEEP_RELATIVE_PATHS})
    foreach(_file ${_files_to_install})
      get_filename_component(_file_subdir ${_file} PATH)
      install(FILES ${_file}
        COMPONENT "${ARG_COMPONENT}"
        DESTINATION "${ARG_DESTINATION}/${ARG_SUBFOLDER}/${_file_subdir}")
    endforeach()
  else()
    # Use standard cmake install() function
    install(FILES ${_files_to_install}
      COMPONENT "${ARG_COMPONENT}"
      DESTINATION "${ARG_DESTINATION}/${ARG_SUBFOLDER}")
  endif()
endfunction()
