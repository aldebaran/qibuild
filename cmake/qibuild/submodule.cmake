##
## Author(s):
##  - Cedric GESTES <gestes@aldebaran-robotics.com>
##
## Copyright (C) 2010 Aldebaran Robotics
##

#! QiBuild SubModule
# =================
# Cedric GESTES <gestes@aldebaran-robotics.com>

#! == SubModule ==
# This Cmake module behave more or less like a library, but does not produce
# any output, you can use submodule to organise your CMakeLists.txt more efficiently
# but you need to call qi_create_bin or qi_create_lib to make use of your submodule.
#
# TODO: put in a more general section
# SRC and PUBLIC_HEADER are special.
# they accept both files and directories. If a directories is specified a glob is applied
# to find each file in the folder. For SRC *.h *.hpp *.hxx are searched,
# for PUBLIC_HEADER *.hpp and *.hxx are searched.


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
# \group:DEPENDENCIES     the list of dependencies
#
# \example:qi_submodule.cmake
function(qi_submodule_create _name)
  qi_argn_init(${ARGN})
  qi_argn_flags(NO_VSGROUP)
  qi_argn_params(VSGROUP)
  qi_argn_groups(SRCS PUBLIC_HEADERS DEPENDENCIES)

  string(TOLOWER "submodule_${_name}_srcs"           _OUT_srcs)
  string(TOLOWER "submodule_${_name}_public_headers" _OUT_public_headers)
  set(${_OUT_srcs}           ${_GROUP_public_headers} ${_GROUP_srcs} PARENT_SCOPE)
  set(${_OUT_public_headers} ${_GROUP_public_headers} PARENT_SCOPE)
  source_group("${_name}" FILES ${_GROUP_public_headers} ${_GROUP_srcs})
  source_group("${_name}\\public" FILES ${_GROUP_public_headers})
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
# \group:DEPENDENCIES     the list of dependencies
#
# \example:qi_submodule.cmake
function(qi_submodule_add _name)
  qi_argn_init(${ARGN})
  qi_argn_flags(NO_VSGROUP)
  qi_argn_params(VSGROUP)
  qi_argn_groups(SRCS PUBLIC_HEADERS DEPENDENCIES IF)

  if (${_GROUP_if})
    qi_submodule_create("${_name}" ${_ARGS}
                        ${_FORWARD_FLAG_no_vsgroup}
                        ${_FORWARD_GROUP_dependencies}
                        ${_FORWARD_GROUP_srcs}
                        ${_FORWARD_GROUP_public_headers}
                        ${_FORWARD_ARGS})
  endif()
endfunction()
