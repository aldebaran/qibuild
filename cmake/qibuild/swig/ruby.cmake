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


find_package(SWIG)
include(UseSWIG)


#############
#
# Nice wrapper for swig.
#
# wrap_ruby(module_name interface_file SRCS srcs... DEPENDENCIES deps ...)
#
# /!\ The module_name must be the same as the one declare in ${interface_file}
# for instance, if module_name equals Foo, Foo.i must contain:
#   %module Foo
##############
function(qi_wrap_ruby module_name interface_file)

  ##
  # Parse args:
  subargs_parse_args("SRCS" "DEPENDENCIES" _srcs _deps ${ARGN})
  if (_deps)
    subargs_parse_args("DEPENDENCIES" "" _deps _tmp ${_deps})
  endif()


  ##
  # Basic configurations
  find_package(SWIG REQUIRED)
  include(${SWIG_USE_FILE})
  set_source_files_properties(${interface_file} PROPERTIES CPLUSPLUS ON)

  ##
  # Deal with dependencies:
  foreach (_dep ${_deps})
    find(${_dep})
    include_directories(${${_dep}_INCLUDE_DIR})
  endforeach()

  # Since there is often a "lazy" include in the interface file,
  # we have to find it.
  include_directories(${CMAKE_CURRENT_SOURCE_DIR})

  swig_add_module(${module_name} ruby ${interface_file} ${_srcs})

  ##
  # Deal with the newly created target

  # Store the target created by swig_add_module in a more friendly name:
  set(_swig_target ${SWIG_MODULE_${module_name}_REAL_NAME})

  use_lib(${_swig_target} RUBY ${_deps})

  set_target_properties(${_swig_target}
    PROPERTIES
      LIBRARY_OUTPUT_DIRECTORY "${SDK_DIR}/${_SDK_LIB}"
  )

  #remove the prefix 'lib' from the library name
  set_target_properties(${_swig_target}
    PROPERTIES
      PREFIX "")

  # Re-create install rules:
  install(TARGETS ${_swig_target}
    COMPONENT python
    LIBRARY DESTINATION "${_SDK_LIB}"
    RUNTIME DESTINATION "${_SDK_LIB}"
  )

endfunction()
