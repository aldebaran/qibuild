##
## Author(s):
##  - Cedric GESTES <gestes@aldebaran-robotics.com>
##
## Copyright (C) 2009, 2010 Aldebaran Robotics
##

#get the current directory of the file
get_filename_component(_ROOT_DIR ${CMAKE_CURRENT_LIST_FILE} PATH)
set(QI_TEMPLATE_DIR  ${_ROOT_DIR}/templates)

include(CMakeParseArguments)


function(_qi_create_cmake_module prefix filename)
  qi_debug("_qi_create_cmake_module")
  cmake_parse_arguments(ARG "" "" "VARS" ${ARGN})

  qi_debug("prefix: ${prefix}")

  file(WRITE ${filename} "message(STATUS \"This is ${prefix}Config.cmake\")\n")
  foreach(var ${ARG_VARS})
    #get_property(GLOBAL
    string(TOUPPER "${prefix}_${var}" _out)
    qi_debug("writing: set(${_out} \"${${prefix}_${var}}\")")
    file(APPEND ${filename} "set(${_out} \"${${prefix}_${var}}\" CACHE STRING \"\" FORCE)\n")
    file(APPEND ${filename} "mark_as_advanced(${_out})\n")
  endforeach()
endfunction()


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

function(_qi_stage_lib_add_target target filename)
  string(TOUPPER "${target}" _name)

  #TODO: do something is OUTPUT_NAME has been changed?
  file(APPEND "${filename}" "set(${_name}_D_LIBRARY ${_name}_D_LIBRARY-NOTFOUND CACHE INTERNAL \"\" FORCE)\n")
  file(APPEND "${filename}" "set(${_name}_LIBRARY   ${_name}_LIBRARY-NOTFOUND   CACHE INTERNAL \"\" FORCE)\n")
  file(APPEND "${filename}" "find_library(${_name}_d_LIBRARY ${target}_d)\n")
  file(APPEND "${filename}" "find_library(${_name}_LIBRARY ${target})\n")
  file(APPEND "${filename}" "if (_qi_temp)\n")
  file(APPEND "${filename}" "  set(${_name}_LIBRARIES \"optimized;\${${_name}_LIBRARY};debug;\${${_name}_D_LIBRARY}\"\n")
  file(APPEND "${filename}" "else()\n")
  file(APPEND "${filename}" "  set(${_name}_LIBRARIES \"\${${_name}_LIBRARY}\")\n")
  file(APPEND "${filename}" "endif()\n")
endfunction()


function(_qi_stage_lib_redist target)
  string(TOUPPER "${target}" _name)
  string(TOLOWER "${target}" _lname)

  set(_filename "${CMAKE_BINARY_DIR}/${QI_SDK_CMAKE_MODULES}/sdk/${_lname}-config.cmake")

  #get the target definitions
  get_directory_property(${_name}_DEFINITIONS  COMPILE_DEFINITIONS)
  #TODO: use relative path
  set(${_name}_INCLUDE_DIRS "\${_ROOT_DIR}/../../include/")
  _qi_create_cmake_module("${_name}" "${CMAKE_BINARY_DIR}/${QI_SDK_CMAKE_MODULES}/sdk/${_lname}-config.cmake"
                          VARS INCLUDE_DIRS DEFINITIONS DEPENDS)
  file(APPEND "${_filename}" "get_filename_component(_ROOT_DIR \${CMAKE_CURRENT_LIST_FILE} PATH)\n")
  _qi_stage_lib_add_target(${target} ${_filename})
  if (NOT ${_name}_NO_INSTALL)
    qi_install_cmake(${target} ${_filename})
  endif()
endfunction()


function(create_cmakemodule_header _NAME)
  qi_debug("SDK: create_cmakemodule_header: (${_NAME})")

  set(_MODULE_NAME        ${_NAME})
  set(_MODULE_TARGET      ${_target})
  set(_MODULE_SUBFOLDER   ${${_target}_SUBFOLDER})
  set(_MODULE_INCLUDE_DIR "${ARGN}")
  get_directory_property(_MODULE_DEFINITIONS COMPILE_DEFINITIONS)

  configure_file("${T001CHAIN_DIR}/cmake/templates/findmodule.header.cmake.in"
                 "${SDK_DIR}/${_SDK_CMAKE_MODULES}/${_NAME}Config.cmake" @ONLY)


  # set(_MODULE_INCLUDE_DIR "\${_ROOT_DIR}/../../../${_SDK_INCLUDE}")
  set(_MODULE_INCLUDE_DIR "\${_ROOT_DIR}/../../../${_SDK_INCLUDE}/")
  if (${_NAME}_HEADER_SUBFOLDER)
    foreach(_h ${${_NAME}_HEADER_SUBFOLDER})
      set(_MODULE_INCLUDE_DIR "\${_ROOT_DIR}/../../../${_SDK_INCLUDE}/${_h}/" ${_MODULE_INCLUDE_DIR})
    endforeach(_h ${${_NAME}_HEADER_SUBFOLDER})
  endif (${_NAME}_HEADER_SUBFOLDER)
  configure_file("${T001CHAIN_DIR}/cmake/templates/findmodule.header.cmake.sdk.in"
                 "${CMAKE_BINARY_DIR}/${_SDK_CMAKE_MODULES}/sdk/${_NAME}Config.cmake" @ONLY)
  install_cmake("modules/" "${CMAKE_BINARY_DIR}/${_SDK_CMAKE_MODULES}/sdk/${_NAME}Config.cmake")
endfunction(create_cmakemodule_header)


function(create_cmakemodule_bin _target _NAME)
  qi_debug("SDK: create_cmakemodule_bin: (${_target}, ${_NAME})")

  set(_MODULE_NAME        ${_NAME})
  set(_MODULE_TARGET      ${_target})
  set(_MODULE_SUBFOLDER   ${${_target}_SUBFOLDER})

  #build folder should include header from the source folder
  if (WIN32)
    # Hack: this was set during win32_copy_target
    set(_MODULE_EXECUTABLE       ${${_target}_STAGED_PATH_RELEASE})
    set(_MODULE_EXECUTABLE_DEBUG ${${_target}_STAGED_PATH_DEBUG})
  else()
    get_target_property(_MODULE_EXECUTABLE       ${_target} "LOCATION_RELEASE")
    get_target_property(_MODULE_EXECUTABLE_DEBUG ${_target}  "LOCATION_DEBUG")
  endif()
  configure_file("${T001CHAIN_DIR}/cmake/templates/findmodule.bin.cmake.in"
                 "${SDK_DIR}/${QU_SDK_CMAKE_MODULES}/${_NAME}Config.cmake" @ONLY)

  configure_file("${T001CHAIN_DIR}/cmake/templates/findmodule.bin.cmake.sdk.in"
                 "${CMAKE_BINARY_DIR}/${QI_SDK_CMAKE_MODULES}/sdk/${_NAME}Config.cmake" @ONLY)
  if (${_target}_NO_INSTALL)
    qi_debug("target ${_NAME} is not to be installed")
  else()
    install_cmake("modules/" "${CMAKE_BINARY_DIR}/${_SDK_CMAKE_MODULES}/sdk/${_NAME}Config.cmake")
  endif()
endfunction(create_cmakemodule_bin)

function(create_cmakemodule_script _target _NAME _file)
  qi_debug("SDK: create_cmakemodule_bin: (${_target}, ${_NAME})")

  set(_MODULE_NAME        ${_NAME})
  set(_MODULE_TARGET      ${_target})
  set(_MODULE_SUBFOLDER   ${${_target}_SUBFOLDER})

  #build folder should include header from the source folder
  set(_MODULE_EXECUTABLE       "${_file}"   CACHE INTERNAL "" FORCE)
  set(_MODULE_EXECUTABLE_DEBUG "${_file}"   CACHE INTERNAL "" FORCE)
  configure_file("${T001CHAIN_DIR}/cmake/templates/findmodule.bin.cmake.in"
                 "${SDK_DIR}/${_SDK_CMAKE_MODULES}/${_NAME}Config.cmake" @ONLY)

  configure_file("${T001CHAIN_DIR}/cmake/templates/findmodule.bin.cmake.sdk.in"
                 "${CMAKE_BINARY_DIR}/${_SDK_CMAKE_MODULES}/sdk/${_NAME}Config.cmake" @ONLY)

  if (${_target}_NO_INSTALL)
    qi_debug("target ${_NAME} is not to be installed")
  else()
    install_cmake("modules/" "${CMAKE_BINARY_DIR}/${_SDK_CMAKE_MODULES}/sdk/${_NAME}Config.cmake")
  endif()
endfunction(create_cmakemodule_script)




