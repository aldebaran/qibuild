## Copyright (C) 2011 Aldebaran Robotics

#! qiBuild Stage
# ===============
#
# This module make libraries and executables build in this projects available
# to others projects.
#

include(qibuild/internal/stage)

#! Generate a 'name'-config.cmake, allowing other project to find the library.
# \arg:target a target created with qi_create_lib
#
function(qi_stage_lib target)
  check_is_target("${target}")
  _qi_stage_lib(${target} ${ARGN})
endfunction()

#! not implemented yet
function(qi_stage_header)
  qi_error("qi_stage_header: not implemented")
endfunction()

#! not implemented yet
function(qi_stage_bin)
  qi_error("qi_stage_bin: not implemented")
endfunction()

#! not implemented yet
function(qi_stage_script)
  qi_error("qi_stage_script: not implemented")
endfunction()

#! stage a cmake module
#
function(qi_stage_cmake _module)
  file(COPY "${_module}Config.cmake"
       DESTINATION
       "${CMAKE_BINARY_DIR}/sdk/${QI_SDK_CMAKE_MODULES}/")
 #TODO: install
endfunction()
