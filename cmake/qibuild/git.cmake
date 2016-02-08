## Copyright (c) 2012-2014 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

#! Git tools
# ===========

#! Get the git version of the current project, using ``git describe``
#
# Example::
#
#
#   # In CMakeLists.txt
#   qi_get_git_version(git_version)
#
#   qi_create_bin(foo "main.cpp")
#
#   set_source_files_properties("main.cpp"
#     PROPERTIES
#       COMPILE_DEFINITIONS "VERSION=\"${git_version}\"")
#
# .. code-block:: cpp
#
#    // in main.cpp
#    std::cout << VERSION << std::endl;
#
# \arg:out Output variable
function(qi_get_git_version out)
  find_package(Git)
  execute_process(COMMAND
    ${GIT_EXECUTABLE} describe --tags --always --dirty
    WORKING_DIRECTORY "${CMAKE_SOURCE_DIR}"
    OUTPUT_VARIABLE _git_describe
    OUTPUT_STRIP_TRAILING_WHITESPACE)
  set(${out} ${_git_describe} PARENT_SCOPE)
endfunction()
