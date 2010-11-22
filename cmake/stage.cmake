##
## Login : <ctaf@localhost.localdomain>
## Started on  Thu Jun 12 15:19:44 2008 Cedric GESTES
## $Id$
##
## Author(s):
##  - Cedric GESTES <gestes@aldebaran-robotics.com>
##
## Copyright (C) 2009 Aldebaran Robotics

###########################
#
# make a library available to other project
#
###########################
function(stage_lib _targetname _name)
  if (${_targetname}_STATIC_AND_SHARED)
    _stage_lib(${_targetname}-static ${_name}-STATIC ${ARGN})
  endif (${_targetname}_STATIC_AND_SHARED)
  _stage_lib(${_targetname} ${_name} ${ARGN})
endfunction(stage_lib _targetname _name)

###########################
#
# make a library available to other project
#
###########################
function(_stage_lib _targetname _name)
  debug("BINLIB: stage_lib (${_targetname}, ${_name}, optional header: ${ARGN})")

  check_is_target(${_targetname})
  if (ARGN)
    set(_inc ${ARGN})
  else(ARGN)
    set(_inc ${CMAKE_CURRENT_SOURCE_DIR})
  endif (ARGN)
  #set the target name (for interproject dependencies)(in the same cmake build)
  set(${_name}_TARGET      ${_targetname}                       CACHE STRING "" FORCE)
  #reset during create_lib, set after staging
  set(${_targetname}_STAGED TRUE PARENT_SCOPE)
  set(${_name}_STAGED TRUE PARENT_SCOPE)
  create_cmakemodule_lib(${_targetname} ${_name} ${_inc})
endfunction(_stage_lib)

###########################
#
# make a script available to other project
#
###########################
function(stage_script _file _name)
  subfolder_parse_args(_subfolder _args ${ARGN})
  debug("BINLIB: stage_bin (${_targetname}, ${_name}, optional header: ${ARGN})")
  set(_cfile "${SDK_DIR}/${_SDK_BIN}/${_subfolder}/${_file}")
  create_cmakemodule_script(${_file} ${_name} ${_cfile})
  #staging done.. needed to for check (install_header/uselib)
  set(${_name}_STAGED TRUE PARENT_SCOPE)
endfunction(stage_script)

###########################
#
# make a binary available to other project
#
###########################
function(stage_bin _targetname _name)
  debug("BINLIB: stage_bin (${_targetname}, ${_name}, optional header: ${ARGN})")
  check_is_target(${_targetname})
  create_cmakemodule_bin(${_targetname} ${_name})
  #staging done.. needed to for check (install_header/uselib)
  set(${_name}_STAGED TRUE PARENT_SCOPE)
  set(${_targetname}_STAGED TRUE PARENT_SCOPE)
endfunction(stage_bin)

###########################
#
# make a source only library available to other project
#
###########################
function(stage_header _name)
  debug("BINLIB: stage_header (${_targetname}, ${_name}, optional header: ${ARGN})")

  if (ARGN)
    set(_inc ${ARGN})
  else(ARGN)
    set(_inc ${CMAKE_CURRENT_SOURCE_DIR})
  endif (ARGN)
  create_cmakemodule_header(${_name} ${_inc})
  #always stage the lib for static use too
  create_cmakemodule_header(${_name}-STATIC ${_inc})

  #staging done.. needed to for check (install_header/uselib)
  set(${_name}_STAGED TRUE PARENT_SCOPE)
endfunction(stage_header)
