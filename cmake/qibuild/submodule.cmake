## Copyright (c) 2012-2016 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

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
  qi_global_get(_OUT_src_content ${_OUT_src})
  qi_global_get(_OUT_depends_content ${_OUT_depends})
  qi_global_set(${_OUT_src} ${_OUT_src_content} ${_SRC})
  qi_global_set(${_OUT_depends} ${_OUT_depends_content} ${ARG_DEPENDS})
endfunction()


#! This function is similar to qi_submodule_create but appends content to
# the submodule. This function can be conditional, if you specify IF
# then the content will be appended to the submodule only if all the flags
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
