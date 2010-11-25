##
## Copyright (C) 2008 Aldebaran Robotics
##

#######################################################################
#                                                                     #
# This file contains two useful functions:                            #
#                                                                     #
#  gen_trampoline(_binary_name _trampo_name) to generate a trampoline #
#  once a binary is installed.                                        #
#                                                                     #
#  gen_sdk_trampoline(_binary_name _trampo_name [EXTERNAL_BINARY]) to #
#  generate a trampoline for a just-compile script.                   #
#                                                                     #
#                                                                     #
#  Those trampolines always set the correct environment variables we  #
#  need such as:                                                      #
#                                                                     #
# - PATH on windows                                                   #
# - LD_LIBRARY_PATH on linux                                          #
# - DYLD_LIBRARY_PATH and DYLD_FRAMEWORK_PATH on mac                  #
#                                                                     #
# (for dependencies with dynamic libraries)                           #
#                                                                     #
# - PYTHONPATH and PYTHONHOME on all platefroms                       #
#                                                                     #
# (for embedded Python to work fine)                                  #
#                                                                     #
#######################################################################


##########################
#
# Create a trampoline for an executable.
#  ( and the install rule that goes with it)
# Note: this trampoline will only work when installed!
#
# Usage:
# gen_trampoline(_binary_name _trampoline_name)
#########################
function(gen_trampoline _binary_name _trampo_name)
  configure_file("${T001CHAIN_DIR}/cmake/templates/trampoline_${TARGET_ARCH}.in"
                 "${CMAKE_CURRENT_BINARY_DIR}/${_trampo_name}"
                  @ONLY)
  install(PROGRAMS
    "${CMAKE_CURRENT_BINARY_DIR}/${_trampo_name}"
    COMPONENT binary
    DESTINATION
    ".")
endfunction()

##################################
#
# Create a trampoline for an executable once
# it has been compiled
#
# Usage:
# gen_sdk_trampoline(_binary_name _trampo_name)
####################################
function(gen_sdk_trampoline _binary_name _trampo_name)
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




