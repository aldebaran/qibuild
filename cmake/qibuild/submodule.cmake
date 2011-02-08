##
## Author(s):
##  - Cedric GESTES <gestes@aldebaran-robotics.com>
##
## Copyright (C) 2010, 2011 Aldebaran Robotics
##

#! qiBuild SubModule
# ==================

#!
# This Cmake module behave more or less like a library, but does not produce
# any output, you can use submodule to organise your CMakeLists.txt more efficiently
# but you need to call qi_create_bin or qi_create_lib to make use of your submodule.
#
# TODO: put in a more general section
# SRC and PUBLIC_HEADER are special.
# they accept both files and directories. If a directories is specified a glob is applied
# to find each file in the folder. For SRC *.h *.hpp *.hxx are searched,
# for PUBLIC_HEADER *.hpp and *.hxx are searched.

include(CMakeParseArguments)

#!
# A submodule is a convenient place to store  sources paths, dependencies
# and public headers. Submodule can be added a library or a module.
# SubModule are directly visible in Visual Studio, you can change the
# submodule name displayed in Visual Studio using VSGROUP, or disable it
# using NO_VSGROUP
#
# \arg:name               the name of the submodule
# \flag:NO_SOURCE_GROUP   do not create a source_group
# \param:SOURCE_GROUP     by default a source_group with name is created,
#                         if sourcegroup is specified then the source_group
#                         name will be name\\sourcegroup
# \group:SRC              the list of source to include in the submodule
# \group:PUBLIC_HEADER    the list of public headers
# \group:DEPENDS          the list of dependencies
#
# \example:submodule
function(qi_submodule_create name)
  cmake_parse_arguments(ARG "NO_VSGROUP" "VSGROUP" "SRC;PUBLIC_HEADER;DEPENDS" ${ARGN})

  string(TOUPPER "submodule_${name}_src"           _OUT_src)
  string(TOUPPER "submodule_${name}_public_header" _OUT_public_header)
  string(TOUPPER "submodule_${name}_depends"       _OUT_depends)

  qi_glob(_SRC           ${ARG_SRC} ${ARG_UNPARSED_ARGUMENTS})
  qi_glob(_PUBLIC_HEADER ${ARG_PUBLIC_HEADER})
  qi_abspath(_SRC ${_SRC})
  qi_abspath(_PUBLIC_HEADER ${_PUBLIC_HEADER})

  qi_set_advanced_cache(${_OUT_src}           ${${_OUT_src}}           ${_PUBLIC_HEADER} ${_SRC})
  qi_set_advanced_cache(${_OUT_public_header} ${${_OUT_public_header}} ${_PUBLIC_HEADER})
  qi_set_advanced_cache(${_OUT_depends}       ${${_OUT_depends}}       ${ARG_DEPENDS})
  #message(STATUS "Setting deps: ${ARG_DEPENDS}")
  if (NOT ARG_NO_VSGROUP)
    set(_vsgroupname ${name})
    if (NOT ARG_VSGROUP STREQUAL "")
      set(_vsgroupname ${ARG_VSGROUP})
    endif()
    source_group("${_vsgroupname}"         FILES ${_SRC})
    source_group("${_vsgroupname}\\public" FILES ${_PUBLIC_HEADER})
  endif()
endfunction()


#! This function is similar to qi_submodule_create but append content to
# the submodule. This function can be condionnal, if you specify IF
# then the content will be append to the submodule only if the flags
# is defined.
#
# \arg:name               the name of the submodule
# \flag:NO_SOURCE_GROUP   do not create a source_group
# \param:SOURCE_GROUP     by default a source_group with name is created,
#                         if sourcegroup is specified then the source_group
#                         name will be name\\sourcegroup
# \param:IF               condition that should be verified before adding content
#                         for example (WITH_QT)
# \group:SRC              the list of source to include in the submodule
# \group:PUBLIC_HEADER    the list of public headers
# \group:DEPENDS          the list of dependencies
#
# \example:submodule
function(qi_submodule_add _name)
  cmake_parse_arguments(ARG "NO_VSGROUP" "VSGROUP;IF" "SRC;PUBLIC_HEADER;DEPENDS" ${ARGN})

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
                        PUBLIC_HEADER ${ARG_PUBLIC_HEADER}
                        DEPENDS       ${ARG_DEPENDS})
  endif()
endfunction()
