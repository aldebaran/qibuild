##
## Author(s):
##  - Cedric GESTES <gestes@aldebaran-robotics.com>
##
## Copyright (C) 2010 Aldebaran Robotics
##

#! QiBuild SDK
# ============
# Cedric GESTES <gestes@aldebaran-robotics.com>
#
# == General overview ==
# Manage dependencies between projects. Projects can be source or binary archive,
# located in different places. For each project a root.cmake file is generated at
# it's root, this file can be included by other project, then staged libraries and
# binaries will be available.

# create a root.cmake file. This file can be sourced by external cmake project.
# This function will create an sdk for the current project.
function(_qi_create_sdk)
  set(filename "${QI_SDK_DIR}/root.cmake")
  file(WRITE  "${filename}" "#TODO: explain how I'am usefull\n")
  file(APPEND "${filename}" "get_filename_component(_ROOT_DIR \${CMAKE_CURRENT_LIST_FILE} PATH)\n")
  file(APPEND "${filename}" "list(APPEND CMAKE_PREFIX_PATH \"\${_ROOT_DIR}\")\n")
  install(FILES "${filename}" COMPONENT "cmake" DESTINATION ".")
endfunction()

#! include an external sdk. The folder specified should have a root.cmake.
# \arg:folder a folder containing an sdk
function(qi_include_sdk folder)
  include("${folder}/root.cmake")
endfunction()
