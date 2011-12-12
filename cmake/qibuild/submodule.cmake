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

#
#!
# .. _using-submodules:
#
# Using submodules
# =================

#!
# This CMake module behaves more or less like a library, but does not produce
# any output, you can use submodule to organise your CMakeLists.txt more efficiently
# but you need to call qi_create_bin or qi_create_lib to make use of your submodule.
#
# SRC accept globbing expressions, files and directories. globbing is not applied to
# directory.

include(CMakeParseArguments)

#!
# A submodule is a convenient place to store source paths, dependencies
# and public headers. Submodule can be added a library or a module.
# Submodules are directly visible in Visual Studio.
#
# \arg:name               The name of the submodule
# \flag:NO_SOURCE_GROUP   Do not create a source_group
# \param:SOURCE_GROUP     By default a source_group with name is created,
#                         if sourcegroup is specified then the source_group
#                         name will be name\\sourcegroup
# \group:SRC              The list of source to include in the submodule
# \group:DEPENDS          The list of dependencies
#
# \example:submodule
function(qi_submodule_create name)
  cmake_parse_arguments(ARG "" "" "SRC;DEPENDS" ${ARGN})

  string(TOUPPER "submodule_${name}_src"           _OUT_src)
  string(TOUPPER "submodule_${name}_depends"       _OUT_depends)

  qi_glob(_SRC           ${ARG_SRC} ${ARG_UNPARSED_ARGUMENTS})
  qi_abspath(_SRC ${_SRC})
  # Note: this function may be called more that once, that why we
  # ADD values inside cache if they are already here.
  qi_set_advanced_cache(${_OUT_src}           ${${_OUT_src}}           ${_SRC})
  qi_set_advanced_cache(${_OUT_depends}       ${${_OUT_depends}}       ${ARG_DEPENDS})
endfunction()


#! This function is similar to qi_submodule_create but appends content to
# the submodule. This function can be condionnal, if you specify IF
# then the content will be appended to the submodule only if the flags
# are defined.
#
# \arg:name               The name of the submodule
# \flag:NO_SOURCE_GROUP   Do not create a source_group.
# \param:SOURCE_GROUP     By default a source_group with name is created,
#                         if sourcegroup is specified then the source_group
#                         name will be name\\sourcegroup
# \param:IF               Condition that should be verified before adding content
#                         for example (WITH_QT)
# \group:SRC              The list of sources to include in the submodule
# \group:DEPENDS          The list of dependencies
#
function(qi_submodule_add _name)
  cmake_parse_arguments(ARG "" "IF" "SRC;DEPENDS" ${ARGN})

  # CMake handling of booleans is a little weird...
  set(_doit)
  if ("${ARG_IF}" STREQUAL "")
    set(_doit TRUE)
  else()
    if (${ARG_IF})
      set(_doit TRUE)
    else()
      set(_doit FALSE)
    endif()
  endif()
  if (_doit)
    qi_submodule_create("${_name}"
                        SRC           ${ARG_SRC} ${ARG_UNPARSED_ARGUMENTS}
                        DEPENDS       ${ARG_DEPENDS})
  endif()
endfunction()
