##
## Author(s):
##  - Dimitri Merejkowsky <dmerejkowsky@aldebaran-robotics.com>
##  - Cedric GESTES <gestes@aldebaran-robotics.com>
##
## Copyright (C) 2010 Aldebaran Robotics
##

##################
# Given the SDK_DIRS variable,
# creates a colon separted string with
# every paths for PATH:
##################
function(_gen_path _res)
  set(_tmp "")
  foreach(_dir ${LIB_PREFIX} ${BIN_PREFIX})
    file(TO_NATIVE_PATH ${_dir} _dos_dir)
    if(WIN32)
      set(_tmp "${_dos_dir};${_tmp}")
    else()
      set(_tmp "${_dos_dir}:${_tmp}")
    endif()
  endforeach()
set(${_res} "${_tmp}" PARENT_SCOPE)
endfunction()

########################
# Given the SDK_DIRS variable,
# creates a colon-separated or a
# semi-colon-separated with every
# paths for PYTHONPATH:
#
#########################
function(_gen_python_path _res)
  set(_tmp "")
  foreach(_lib ${LIB_PREFIX})
      file(TO_NATIVE_PATH ${_lib} _native_lib)
      if(WIN32)
        set(_tmp "${_native_lib};${_tmp}")
      else()
        set(_tmp "${_native_lib}:${_tmp}")
      endif()
  endforeach()
set(${_res} "${_tmp}" PARENT_SCOPE)
endfunction()


########################
# Given the SDK_DIRS variable,
# creates a colon-separated strint with every
# paths for LD_LIBRARY_PATH:
#
#########################
function(_gen_ld_path _res)
  set(_tmp "")
  foreach(_lib ${LIB_PREFIX})
    set(_tmp "${_lib}:${_tmp}")
  endforeach()
set(${_res} "${_tmp}" PARENT_SCOPE)
endfunction()

########################
# Given the SDK_DIRS variable,
# creates a colon-separated strint with every
# paths for DYLD_LIBRARY_PATH:
#########################
function(_gen_dyld_path _res)
  set(_tmp "")
  foreach(_lib ${LIB_PREFIX})
    set(_tmp "${_lib}:${_tmp}")
  endforeach()
set(${_res} "${_tmp}" PARENT_SCOPE)
endfunction()

########################
# Given the SDK_DIRS variable,
# creates a colon-separated strint with every
# paths for DYLD_FRAMEWORK_PATH:
#########################
function(_gen_framework_path _res)
  set(_tmp "")
  foreach(_framework ${FRAMEWORK_PREFIX})
    set(_tmp "${_framework}:${_tmp}")
  endforeach()
set(${_res} "${_tmp}" PARENT_SCOPE)
endfunction()


#!
#
# Create a trampoline for an executable.
#  ( and the install rule that goes with it)
# Note: this trampoline will only work when installed!
#
# Usage:
# gen_trampoline(_binary_name _trampoline_name)
#TODO: DOC
function(qi_create_launcher _binary_name _trampo_name)
  configure_file("${T001CHAIN_DIR}/cmake/templates/trampoline_${TARGET_ARCH}.in"
                 "${CMAKE_CURRENT_BINARY_DIR}/${_trampo_name}"
                  @ONLY)
  install(PROGRAMS
    "${CMAKE_CURRENT_BINARY_DIR}/${_trampo_name}"
    COMPONENT binary
    DESTINATION
    ".")
endfunction()

#! Create a launcher for an executable.
# This launcher will set environment variable
# for python and dynamics libraries.
#
#TODO: DOC
function(qi_create_insource_launcher _binary_name _trampo_name)
  parse_is_options(_args EXTERNAL_BINARY _external_binary ${ARGN})
  if(${TARGET_ARCH} STREQUAL windows)
    _gen_path(_path)
    string(REPLACE "/" "\\" _dos_sdk_dir ${SDK_DIR})
  else(${TARGET_ARCH} STREQUAL windows)
    if(APPLE)
      _gen_framework_path(_framework_path)
      _gen_dyld_path(_dyld_path)
    else()
      _gen_ld_path(_ld_path)
    endif()
  endif(${TARGET_ARCH} STREQUAL windows)
  _gen_python_path(_python_path)

  if (_external_binary)
    if(WIN32)
      string(REPLACE "/" "\\" _dos_binary_name ${_binary_name})
      set(_exec_path "${_dos_binary_name}")
    else()
      set(_exec_path "${_binary_name}")
    endif()
  else()
    if(WIN32)
      set(_exec_path "${_dos_sdk_dir}\\${_SDK_BIN}\\${_binary_name}")
    else()
      set(_exec_path "${SDK_DIR}/${_SDK_BIN}/${_binary_name}")
    endif()
  endif()

  if (NOT APPLE)
    set(_python_pc_python_home "${_PYTHON_PC_DIR}/${TARGET_ARCH}")
  else()
    set(_python_pc_python_home "${_PYTHON_PC_DIR}/${TARGET_ARCH}/Frameworks/Python.framework/Versions/Current")
  endif()

  configure_file("${T001CHAIN_DIR}/cmake/templates/trampoline_sdk_${TARGET_ARCH}.in"
                 "${CMAKE_CURRENT_BINARY_DIR}/${_trampo_name}.conf"
                 @ONLY)
  create_script("${_trampo_name}" "${CMAKE_CURRENT_BINARY_DIR}/${_trampo_name}.conf" NO_INSTALL)

endfunction()
