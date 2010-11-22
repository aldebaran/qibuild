##
## Author(s):
##  - Cedric GESTES <gestes@aldebaran-robotics.com>
##
## Copyright (C) 2010 Aldebaran Robotics
##


# QiBuild SubModule
# =================
# Cedric GESTES <gestes@aldebaran-robotics.com>

# == SubModule ==
# This Cmake module behave more or less like a library, but does not produce
# any output, you can use submodule to organise your CMakeLists.txt more efficiently
# but you need to call qi_create_bin or qi_create_lib to make use of your submodule.
#
# TODO: put in a more general section
# SRC and PUBLIC_HEADER are special.
# they accept both files and directories. If a directories is specified a glob is applied
# to find each file in the folder. For SRC *.h *.hpp *.hxx are searched,
# for PUBLIC_HEADER *.hpp and *.hxx are searched.





# === function qi_submodule_create ===
# .Description
# A submodule is a convenient place to store  sources paths, dependencies
# and public headers. Submodule can be added a library or a module.
# SubModule are directly visible in Visual Studio, you can change the
# submodule name displayed in Visual Studio using VSGROUP, or disable it
# using NO_VSGROUP
#
# .Prototype
#   qi_submodule_create(name [NO_VSGROUP]
#                            [VSGROUP vsgroup]
#                            [SRC src .. ]
#                            [PUBLIC_HEADER pub .. ]
#                            [DEPENDENCIES dep .. ])
#
# .Parameters
# * name                    : the name of the submodule
# * NO_SOURCE_GROUP         : do not create a source_group
# * SOURCE_GROUP sourcegroup: by default a source_group with name is created,
#   if sourcegroup is specified then the source_group name will be name\\sourcegroup
# * SRC src ..              : the list of source to include in the submodule
# * PUBLIC_HEADER pub ..    : the list of public headers
# * DEPENDENCIES dep ..     : the list of dependencies
#
# .Example
# [source,cmake]
# ----
# # create a submodule with your lib, with one publicheader and a Qt dependencies
# qi_submodule_create(mylib SRC mylib.cpp myprivateheader.hpp
#                           PUBLIC_HEADER mypublicheader.hpp
#                           DEPENDENCIES Qt)
# # this create a binary that have a dependencies on Qt, and the sources set in the
# # submodule
# qi_create_bin(mybin SUBMODULE mylib)
# ----
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


# === function qi_submodule_add ===
# .Description
# This function is similar to qi_submodule_create but append content to
# the submodule. This function can be condionnal, if you specify IF
# then the content will be append to the submodule only if the flags
# is defined.
#
# .Prototype
#   qi_submodule_add(name [NO_VSGROUP]
#                         [VSGROUP vsgroup]
#                         [SRC src .. ]
#                         [PUBLIC_HEADER pub .. ]
#                         [DEPENDENCIES dep .. ]
#                         [IF flags ..])
#
# .Parameters
# * [IF flags ..]           : condition that should be verified to add content
#   to the submodule
# * see qi_submodule_create for other parameters
# .Example
# [source,cmake]
# ----
# # create a submodule with your lib, with one publicheader and a Qt dependencies
# qi_submodule_create(mylib SRC mylib.cpp myprivateheader.hpp
#                           PUBLIC_HEADER mypublicheader.hpp
#                           DEPENDENCIES Qt)
# # append files related to boost to the submodule, this will occur only if
# # WITH_BOOST is defined.
# qi_submodule_add(mylib SRC mylibboostfeature.cpp myprivateboostheader.hpp
#                           PUBLIC_HEADER mypublicboostheader.hpp
#                           DEPENDENCIES boost
#                           IF WITH_BOOST)
# # this create a binary that have a dependencies on Qt and boost (if WITH_BOOST is set)
# # source and public_header are taken from the submodule
# qi_create_bin(mybin SUBMODULE mylib)
# ----
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
