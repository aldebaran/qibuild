## Copyright (C) 2011 Aldebaran Robotics

#! qiBuild SubModule
# ==================

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
# SubModules are directly visible in Visual Studio, you can change the
# submodule name displayed in Visual Studio using VSGROUP, or disable it
# using NO_VSGROUP
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
  cmake_parse_arguments(ARG "NO_VSGROUP" "VSGROUP" "SRC;DEPENDS" ${ARGN})

  string(TOUPPER "submodule_${name}_src"           _OUT_src)
  string(TOUPPER "submodule_${name}_depends"       _OUT_depends)

  qi_glob(_SRC           ${ARG_SRC} ${ARG_UNPARSED_ARGUMENTS})
  qi_abspath(_SRC ${_SRC})

  qi_set_advanced_cache(${_OUT_src}           ${${_OUT_src}}           ${_SRC})
  qi_set_advanced_cache(${_OUT_depends}       ${${_OUT_depends}}       ${ARG_DEPENDS})
  if (NOT ARG_NO_VSGROUP)
    set(_vsgroupname ${name})
    if (NOT ARG_VSGROUP STREQUAL "")
      set(_vsgroupname ${ARG_VSGROUP})
    endif()
    source_group("${_vsgroupname}"         FILES ${_SRC})
  endif()
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
# \group:SRC              The list of source to include in the submodule
# \group:DEPENDS          The list of dependencies
#
# \example:submodule
function(qi_submodule_add _name)
  cmake_parse_arguments(ARG "NO_VSGROUP" "VSGROUP;IF" "SRC;DEPENDS" ${ARGN})

  if (ARG_NO_VSGROUP)
    set(_forward_no_vsgroup "NO_VSGROUP")
  endif()

  set(_doit)
  if (NOT "${ARG_IF}" STREQUAL "")
    set(_doit TRUE)
  else()
    #I must say... lol cmake, but NOT NOT TRUE is not valid!!
    if (${ARG_IF})
    else()
      set(_doit TRUE)
    endif()
  endif()
  if (_doit)
    #message(STATUS "pif SUBMODULE: ${ARGN}")
    qi_submodule_create("${_name}"
                        ${_forward_no_vsgroup}
                        VSGROUP       ${ARG_VSGROUP}
                        SRC           ${ARG_SRC} ${ARG_UNPARSED_ARGUMENTS}
                        DEPENDS       ${ARG_DEPENDS})
  endif()
endfunction()
