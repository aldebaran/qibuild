## Copyright (C) 2011 Aldebaran Robotics

include(CMakeParseArguments)

# FIXME: file(APPEND) is not such a good idea.
# calling cmake mutliple times without deleting build/skd
# lead to very long -config.cmake generated files...

# Of course, qibuild configure could delete build/sdk after having
# deleted CMakeCache, but let's be clean here

#
# Write a set of exported CMake variables into a cmake module.
# For instance, if ${FOO} equals bar:
# _qi_create_cmake_module(foo VARS FOO)
# append the following to foo.cmake:
#   set(FOO bar)
#   mark_as_advanced(FOO)
function(_qi_create_cmake_module prefix filename)
  qi_debug("_qi_create_cmake_module")
  cmake_parse_arguments(ARG "" "" "VARS" ${ARGN})

  qi_debug("prefix: ${prefix}")

  foreach(var ${ARG_VARS})
    #get_property(GLOBAL
    string(TOUPPER "${prefix}_${var}" _out)
    qi_debug("writing: set(${_out} \"${${prefix}_${var}}\")")
    file(APPEND ${filename} "set(${_out} \"${${prefix}_${var}}\" CACHE STRING \"\" FORCE)\n")
    file(APPEND ${filename} "mark_as_advanced(${_out})\n")
  endforeach()
endfunction()


# Set ${target}_LIBRARIES wheter target was compiled
# in release or in debug in an *installed* SDK.
function(_qi_stage_lib_add_target target filename)
  string(TOUPPER "${target}" _name)

  #TODO: do something is OUTPUT_NAME has been changed?
  file(APPEND "${filename}" "set(${_name}_D_LIBRARY ${_name}_D_LIBRARY-NOTFOUND CACHE INTERNAL \"\" FORCE)\n")
  file(APPEND "${filename}" "set(${_name}_LIBRARY   ${_name}_LIBRARY-NOTFOUND   CACHE INTERNAL \"\" FORCE)\n")
  file(APPEND "${filename}" "find_library(${_name}_d_LIBRARY ${target}_d)\n")
  file(APPEND "${filename}" "find_library(${_name}_LIBRARY ${target})\n")
  file(APPEND "${filename}" "if (_qi_temp)\n")
  file(APPEND "${filename}" "  set(${_name}_LIBRARIES \"optimized;\${${_name}_LIBRARY};debug;\${${_name}_D_LIBRARY}\")\n")
  file(APPEND "${filename}" "else()\n")
  file(APPEND "${filename}" "  set(${_name}_LIBRARIES \"\${${_name}_LIBRARY}\")\n")
  file(APPEND "${filename}" "endif()\n")
endfunction()


# stage a library in the SDK.
# for instance, after _qi_stage_lib_sdk(foo), you have a
# foo-config.cmake in CMAKE_BINARY_DIR/sdk containing:
#  set(FOO_INCLUDE_DIRS ...)
#  set(FOO_LIBRARIES ...)
#
# This file is NOT supposed to be installed.
function(_qi_stage_lib_sdk target)
  string(TOUPPER "${target}" _name)
  string(TOLOWER "${target}" _lname)

  #get the target definitions
  get_directory_property(${_name}_DEFINITIONS  COMPILE_DEFINITIONS)
  get_directory_property(${_name}_INCLUDE_DIRS INCLUDE_DIRECTORIES)

  get_target_property(_tdebug ${target} "LOCATION_DEBUG")
  get_target_property(_topti ${target}  "LOCATION_RELEASE")
  string(REGEX REPLACE ".dll$" ".lib" _tdebug "${_tdebug}")
  string(REGEX REPLACE ".dll$" ".lib" _topti "${_topti}")
  set(${_name}_LIBRARIES "optimized;${_topti};debug;${_tdebug}")
  set(${_name}_TARGET    "${target}")
  _qi_create_cmake_module("${_name}" "${QI_SDK_DIR}/${QI_SDK_CMAKE_MODULES}/${_lname}-config.cmake"
                          VARS INCLUDE_DIRS DEFINITIONS LIBRARIES DEPENDS TARGET)
endfunction()



#
# Same thing as _qi_stage_lib_sdk, excpet the generated
# ${target}-config.cmake file is ready to be installed.
function(_qi_stage_lib_redist target)
  string(TOUPPER "${target}" _name)
  string(TOLOWER "${target}" _lname)

  set(_filename "${CMAKE_BINARY_DIR}/${QI_SDK_CMAKE_MODULES}/sdk/${_lname}-config.cmake")
  file(WRITE "${_filename}" "get_filename_component(_ROOT_DIR \${CMAKE_CURRENT_LIST_FILE} PATH)\n")

  #get the target definitions
  get_directory_property(${_name}_DEFINITIONS  COMPILE_DEFINITIONS)
  #TODO: use relative path
  set(${_name}_INCLUDE_DIRS "\${_ROOT_DIR}/../../../include/")
  _qi_create_cmake_module("${_name}" "${CMAKE_BINARY_DIR}/${QI_SDK_CMAKE_MODULES}/sdk/${_lname}-config.cmake"
                          VARS INCLUDE_DIRS DEFINITIONS DEPENDS)
  _qi_stage_lib_add_target(${target} ${_filename})
  #TODO: call FindPackageHandleStandardArgs and handle errors.
  if (NOT ${_name}_NO_INSTALL)
    qi_install_cmake(${target} ${_filename})
  endif()
endfunction()

