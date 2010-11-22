##
## install.cmake
## Login : <ctaf@ctaf-maptop>
## Started on  Sun Oct 18 14:42:06 2009 Cedric GESTES
## $Id$
##
## Author(s):
##  - Cedric GESTES <gestes@aldebaran-robotics.com>
##
## Copyright (C) 2009 Aldebaran Robotics
##

# install functions
# there could be more than one output dir

###########################
# install_header
###########################
function(install_header _name)
  parse_is_options(_args0 INCLUDEPATHEXPORT _is_includepathexport ${ARGN})
  subfolder_parse_args(_subfolder _args1 ${_args0})

  if (_subfolder AND _is_includepathexport)
    if (${_name}_STATIC_AND_SHARED)
      sdk_add_include(${_name}-static ${_subfolder})
    endif (${_name}_STATIC_AND_SHARED)
    sdk_add_include(${_name} ${_subfolder})
  endif (_subfolder AND _is_includepathexport)

  install(FILES ${_args1} COMPONENT header DESTINATION ${_SDK_INCLUDE}/${_subfolder})
endfunction(install_header _name)

###########################
# grrrr
###########################
function(sdk_add_include _name _subfolder)
  if (${_name}_STAGED)
    error("USELIB: [${_name}] Don't call sdk_add_include on a target after stage_lib/stage_header.")
  endif (${_name}_STAGED)

  set(${_name}_HEADER_SUBFOLDER ${_subfolder} ${${_name}_HEADER_SUBFOLDER} CACHE INTERNAL "" FORCE)
  list(REMOVE_DUPLICATES ${_name}_HEADER_SUBFOLDER)
  set(${_name}_HEADER_SUBFOLDER ${${_name}_HEADER_SUBFOLDER} CACHE INTERNAL "" FORCE)
endfunction(sdk_add_include _name _subfolder)

###########################
# install_data
###########################
function(install_data _subfolder)
  install(FILES ${ARGN} COMPONENT data  DESTINATION ${_SDK_SHARE}/${_subfolder})
endfunction(install_data _name)

function(install_data_dir _subfolder)
  install(DIRECTORY ${ARGN} COMPONENT data DIRECTORY ${_SDK_SHARE}/${_subfolder})
endfunction(install_data_dir)

function(install_doc _subfolder)
  install(FILES ${ARGN} COMPONENT doc   DESTINATION ${_SDK_DOC}/${_subfolder})
endfunction(install_doc _name)

function(install_conf _subfolder)
  install(FILES ${ARGN} COMPONENT conf  DESTINATION ${_SDK_CONF}/${_subfolder})
endfunction(install_conf _name)

function(install_cmake _subfolder)
  install(FILES ${ARGN} COMPONENT cmake DESTINATION ${_SDK_CMAKE}/${_subfolder})
endfunction()

function(_try_install_dir _dir)
  if (EXISTS ${_dir})
    install(DIRECTORY ${_dir} ${ARGN})
  elseif (EXISTS ${CMAKE_CURRENT_SOURCE_DIR}/${_dir})
    install(DIRECTORY ${_dir} ${ARGN})
  endif()
endfunction()


##
# Wrapper to make sure lib/foo.dll in installed in bin/
#
function(_win_install_dlls _src _dest)
  file(GLOB _dlls "${_src}/*.dll")
  install(FILES
    ${_dlls}
    COMPONENT lib
    DESTINATION ${_dest}
  )
endfunction()


######################
# install all binary file from a binary repository (dont use unless you know you want it)
#
# Permission used will be those in the source tree.
# (good thing we use git, isn't it?)
#
# /!\ Now does this on windows:
# windows-vc90/lib/foo.dll -> bin/foo.dll
# windows/lib/bar.dll      -> bin/bar.dll
# windows/lib/baz.lib      -> lib/baz.lib
# This makes it possible to not have .bat on install
######################
function(install_multiarch_binary)
  set(_runtime_lib ".*\\.(dll|dylib|so.?.*)$")
  set(_devel_lib ".*(a|lib)$")
  set(_python_lib ".*(py|pyd)$")

  _try_install_dir("common/include/"    USE_SOURCE_PERMISSIONS COMPONENT header     DESTINATION "${_SDK_INCLUDE}")
  _try_install_dir("common/lib/"        USE_SOURCE_PERMISSIONS COMPONENT lib        DESTINATION "${_SDK_LIB}" FILES_MATCHING REGEX "${_runtime_lib}")
  _try_install_dir("common/lib/"        USE_SOURCE_PERMISSIONS COMPONENT python     DESTINATION "${_SDK_LIB}" FILES_MATCHING REGEX "${_python_lib}")
  _try_install_dir("common/lib/"        USE_SOURCE_PERMISSIONS COMPONENT static-lib DESTINATION "${_SDK_LIB}" FILES_MATCHING REGEX "${_devel_lib}")
  _try_install_dir("common/bin/"        USE_SOURCE_PERMISSIONS COMPONENT binary     DESTINATION "${_SDK_BIN}")
  _try_install_dir("common/Frameworks/" USE_SOURCE_PERMISSIONS COMPONENT binary     DESTINATION "${_SDK_FRAMEWORK}")

  _try_install_dir("${TARGET_ARCH}/include/"     USE_SOURCE_PERMISSIONS COMPONENT header     DESTINATION "${_SDK_INCLUDE}")

  if(WIN32)
    _win_install_dlls("${TARGET_ARCH}/lib" "${_SDK_BIN}")
  else()
    _try_install_dir("${TARGET_ARCH}/lib/"       USE_SOURCE_PERMISSIONS COMPONENT lib        DESTINATION "${_SDK_LIB}" FILES_MATCHING REGEX "${_runtime_lib}")
  endif()

  _try_install_dir("${TARGET_ARCH}/lib/"         USE_SOURCE_PERMISSIONS COMPONENT python     DESTINATION "${_SDK_LIB}" FILES_MATCHING REGEX "${_python_lib}")
  _try_install_dir("${TARGET_ARCH}/lib/"         USE_SOURCE_PERMISSIONS COMPONENT static-lib DESTINATION "${_SDK_LIB}" FILES_MATCHING REGEX "${_devel_lib}")
  _try_install_dir("${TARGET_ARCH}/bin/"         USE_SOURCE_PERMISSIONS COMPONENT binary     DESTINATION "${_SDK_BIN}")
  _try_install_dir("${TARGET_ARCH}/Frameworks/"  USE_SOURCE_PERMISSIONS COMPONENT binary     DESTINATION "${_SDK_FRAMEWORK}")

  if (TARGET_SUBARCH)
    _try_install_dir("${TARGET_ARCH}-${TARGET_SUBARCH}/include/"    USE_SOURCE_PERMISSIONS   COMPONENT header     DESTINATION "${_SDK_INCLUDE}")

    if(WIN32)
    _win_install_dlls("${TARGET_ARCH}-${TARGET_SUBARCH}/lib" "${_SDK_BIN}")
    else()
      _try_install_dir("${TARGET_ARCH}-${TARGET_SUBARCH}/lib/"      USE_SOURCE_PERMISSIONS   COMPONENT lib        DESTINATION "${_SDK_LIB}" FILES_MATCHING REGEX "${_runtime_lib}")
    endif()

    _try_install_dir("${TARGET_ARCH}-${TARGET_SUBARCH}/lib/"        USE_SOURCE_PERMISSIONS   COMPONENT python     DESTINATION "${_SDK_LIB}" FILES_MATCHING REGEX "${_python_lib}")
    _try_install_dir("${TARGET_ARCH}-${TARGET_SUBARCH}/lib/"        USE_SOURCE_PERMISSIONS   COMPONENT static-lib DESTINATION "${_SDK_LIB}" FILES_MATCHING REGEX "${_devel_lib}")
    _try_install_dir("${TARGET_ARCH}-${TARGET_SUBARCH}/bin/"        USE_SOURCE_PERMISSIONS   COMPONENT binary     DESTINATION "${_SDK_BIN}")
    _try_install_dir("${TARGET_ARCH}-${TARGET_SUBARCH}/Frameworks/" USE_SOURCE_PERMISSIONS   COMPONENT binary     DESTINATION "${_SDK_FRAMEWORK}")
  endif(TARGET_SUBARCH)
endfunction()
