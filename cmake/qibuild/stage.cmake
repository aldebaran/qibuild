##
## Author(s):
##  - Cedric GESTES <gestes@aldebaran-robotics.com>
##
## Copyright (C) 2009, 2010 Aldebaran Robotics
##

#! QiBuild Stage
# ===============
# Cedric GESTES <gestes@aldebaran-robotics.com>
#
# This module make libraries and executables build in this projects available
# to others projects.
#




#! Generate a 'name'-config.cmake, allowing other project to find the library.
# \arg:target a target created with qi_create_lib
#
function(qi_stage_lib target)
  qi_debug("BINLIB: stage_lib (${_targetname})")
  check_is_target("${target}")

  _qi_stage_lib_sdk(${target} ${ARGN})
  _qi_stage_lib_redist(${target} ${ARGN})
endfunction()

#! stage a script
function(qi_stage_script _file _name)
  subfolder_parse_args(_subfolder _args ${ARGN})
  debug("BINLIB: stage_bin (${_targetname}, ${_name}, optional header: ${ARGN})")
  set(_cfile "${SDK_DIR}/${_SDK_BIN}/${_subfolder}/${_file}")
  create_cmakemodule_script(${_file} ${_name} ${_cfile})
  #staging done.. needed to for check (install_header/uselib)
  set(${_name}_STAGED TRUE PARENT_SCOPE)
endfunction()

#! stage an executable
# \arg:target the target
function(qi_stage_bin _targetname)
  string(TOUPPER ${_targetname} _name)
  debug("BINLIB: stage_bin (${_targetname}, ${_name}, optional header: ${ARGN})")
  check_is_target(${_targetname})
  create_cmakemodule_bin(${_targetname} ${_name})
  #staging done.. needed to for check (install_header/uselib)
  set(${_name}_STAGED TRUE PARENT_SCOPE)
  set(${_targetname}_STAGED TRUE PARENT_SCOPE)
endfunction()

#! stage a header only library.
#
function(qi_stage_header _name)
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
endfunction()
