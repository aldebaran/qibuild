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
# \group:DEPENDS if not given, ${TARGET}_DEPENDS will be guessed from
#                the previous calls to qi_use_lib().
#                Use this (whith care!) to override this behavior.
# \group:INCLUDE_DIRS it not given, ${TARGET}_INCLUDE_DIRS  will be
#                 guessed from the previous calls to
#                 include_directories()
#                 Use this (whith care!) to override this behavior.
# \group:DEFINITIONS list of compilation flags targets depending
#                 of this library should use.
function(qi_stage_lib target)
  _qi_check_is_target("${target}")
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

  get_filename_component(_name ${CMAKE_CURRENT_SOURCE_DIR}/${_module} NAME)

  install(FILES "${_module}Config.cmake"
      DESTINATION
      "${QI_SDK_CMAKE}/${_name}/"
  )
endfunction()
