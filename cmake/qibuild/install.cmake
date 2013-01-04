## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

#! Installing
# ===========
#
# See general documentation here :ref:`cmake-install`
#


#! Generic install function.
# See general documentation here :ref:`cmake-install`
# \argn:                 A list of files : directories and globs on files are accepted.
# \param: SUBFOLDER      An optional subfolder in which to put the files.
# \param: IF             Condition that should be verified for the install rules
#                        to be active (for example IF WITH_ZEROMQ)
# \flag: KEEP_RELATIVE_PATHS Wether relative path should be preserved during installation.
# \flag: RECURSE         Wether glob should be recursive.
function(qi_install)
  _qi_install_internal(${ARGN})
endfunction()

#! Install application headers.
# The destination will be **<prefix>/include/**
#
# \argn:                 A list of files : directories and globs on files are accepted.
# \param: SUBFOLDER      An optional subfolder in which to put the files.
# \param: IF             Condition that should be verified for the install rules
#                        to be active (for example IF WITH_ZEROMQ)
# \flag: RECURSE         Wether glob should be recursive
# \flag: KEEP_RELATIVE_PATHS  If true, relative paths will be preserved during installation.
#                        (False by default because this is NOT the standard CMake
#                         behavior)
function(qi_install_header)
  _qi_install_internal(${ARGN} COMPONENT headers DESTINATION ${QI_SDK_INCLUDE})
endfunction()



#! Install application data.
# The destination will be: **<prefix>/share/**
#
# \argn:                 A list of files : directories and globs on files are accepted.
# \param: SUBFOLDER      An optional subfolder in which to put the files.
# \param: IF             Condition that should be verified for the install rules
#                        to be active (for example IF WITH_ZEROMQ)
# \flag: RECURSE         Wether glob should be recursive.
# \flag: KEEP_RELATIVE_PATHS  If true, relative paths will be preserved during installation.
#                        (False by default because this is NOT the standard CMake
#                         behavior)
#
function(qi_install_data)
  _qi_install_internal(${ARGN} COMPONENT data  DESTINATION ${QI_SDK_SHARE})
endfunction()

#! Install application doc.
# The destination will be: **<prefix>/share/doc/**
#
# \argn:                 A list of files : directories and globs on files are accepted.
# \param: SUBFOLDER      An optional subfolder in which to put the files.
# \param: IF             Condition that should be verified for the install rules
#                        to be active for example (IF WITH_ZEROMQ)
# \flag: RECURSE         Wether glob should be recursive
# \flag: KEEP_RELATIVE_PATHS  If true, relative paths will be preserved during installation.
#                        (False by default because this is NOT the standard CMake
#                         behavior)
#
function(qi_install_doc)
  _qi_install_internal(${ARGN} COMPONENT doc   DESTINATION ${QI_SDK_DOC})
endfunction()


#! Install application configuration files.
# The destination will be: **<prefix>/etc/**
#
# \argn:                 A list of files : directories and globs on files are accepted.
# \param: SUBFOLDER      An optional subfolder in which to put the files.
# \param: IF             Condition that should be verified for the install rules
#                        to be active for example (IF WITH_ZEROMQ)
# \flag: RECURSE         Wether glob should be recursive
# \flag: KEEP_RELATIVE_PATHS  If true, relative paths will be preserved during installation.
#                        (False by default because this is NOT the standard CMake
#                         behavior)
#
function(qi_install_conf)
  if(NOT DEFINED SYSCONFDIR)
    set(SYSCONFDIR "${QI_SDK_CONF}")
  endif()
  _qi_install_internal(${ARGN} COMPONENT conf  DESTINATION "${SYSCONFDIR}")
endfunction()

#! Install CMake module files.
# The destination will be: **<prefix>/share/cmake/**
#
# \argn:                 A list of files : directories and globs on files are accepted.
# \param: SUBFOLDER      An optional subfolder in which to put the files.
# \param: IF             Condition that should be verified for the install rules
#                        to be active for example (IF WITH_ZEROMQ)
# \flag: RECURSE         Wether glob should be recursive
# \flag: KEEP_RELATIVE_PATHS  If true, relative paths will be preserved during installation.
#                        (False by default because this is NOT the standard CMake
#                         behavior)
#
function(qi_install_cmake)
  _qi_install_internal(${ARGN} COMPONENT cmake DESTINATION ${QI_SDK_CMAKE})
endfunction()


#! install a target, that could be a program or a library.
# The destination will be: **<prefix>/lib** or **<prefix>/bin**,
# depending on the target and the platform:
#
# * Windows: ``*.dll``  and ``*.exe`` in ``bin``, ``*.lib`` in ``lib``
# * Mac:     ``.dylib`` and ``.a`` in ``lib``, executables in ``bin``
# * Linux :  ``.so``    and ``.a`` in ``lib``, executables in ``bin``
#
# \argn:                 A list of targets to install
# \param: SUBFOLDER      An optional subfolder in which to put the files.
# \param: IF             Condition that should be verified for the install rules
#                        to be active for example (IF WITH_ZEROMQ)
function(qi_install_target)
  cmake_parse_arguments(ARG "" "IF;SUBFOLDER" "" ${ARGN})

  if (NOT "${ARG_IF}" STREQUAL "")
    set(_doit TRUE)
  else()
    #I must say... lol cmake, but NOT NOT TRUE is not valid!!
    if (${ARG_IF})
    else()
      set(_doit TRUE)
    endif()
  endif()
  if (NOT _doit)
    return()
  endif()

  if(ARG_SUBFOLDER)
    set(_dll_output ${QI_SDK_LIB}/${ARG_SUBFOLDER})
  else()
    set(_dll_output ${QI_SDK_BIN})
  endif()

  if(WIN32)
    set(_runtime_output ${_dll_output})
  else()
    set(_runtime_output ${QI_SDK_BIN}/${ARG_SUBFOLDER})
  endif()

  foreach (name ${ARG_UNPARSED_ARGUMENTS})
    install(TARGETS "${name}"
            RUNTIME COMPONENT binary     DESTINATION ${_runtime_output}
            LIBRARY COMPONENT lib        DESTINATION ${QI_SDK_LIB}/${ARG_SUBFOLDER}
      PUBLIC_HEADER COMPONENT header     DESTINATION ${QI_SDK_INCLUDE}/${ARG_SUBFOLDER}
           RESOURCE COMPONENT data       DESTINATION ${QI_SDK_SHARE}/${name}/${ARG_SUBFOLDER}
            ARCHIVE COMPONENT static-lib DESTINATION ${QI_SDK_LIB}/${ARG_SUBFOLDER}
            BUNDLE  COMPONENT binary     DESTINATION ".")
  endforeach()
endfunction()

#! install program (mostly script or user provided program). Do not use this function
# to install a library or a program built by your project, prefer using :cmake:function:`qi_install_target`.
#
# \argn:                 A list of programs to install
# \param: SUBFOLDER      An optional subfolder in which to put the files.
# \param: IF             Condition that should be verified for the install rules
#                        to be active for example (IF WITH_ZEROMQ)
function(qi_install_program)
  cmake_parse_arguments(ARG "" "IF;SUBFOLDER" "" ${ARGN})

  if (NOT "${ARG_IF}" STREQUAL "")
    set(_doit TRUE)
  else()
    #I must say... lol cmake, but NOT NOT TRUE is not valid!!
    if (${ARG_IF})
    else()
      set(_doit TRUE)
    endif()
  endif()
  if (NOT _doit)
    return()
  endif()

  foreach(name ${ARG_UNPARSED_ARGUMENTS})
    #TODO: what should be the real source here?
    install(PROGRAMS    "${QI_SDK_DIR}/${QI_SDK_BIN}/${ARG_SUBFOLDER}/${name}"
            COMPONENT   binary
            DESTINATION "${QI_SDK_BIN}/${ARG_SUBFOLDER}")
  endforeach()
endfunction()


#! install external library. Do not use this function
# to install a library or a program built by your project,
# prefer using :cmake:function:`qi_install_target`.
#
# \argn:                 A list of libraries to install
# \param: SUBFOLDER      An optional subfolder in which to put the files.
# \param: IF             Condition that should be verified for the install rules
#                        to be active for example (IF WITH_ZEROMQ)
function(qi_install_library)
  _qi_install_internal(${ARGN} COMPONENT lib DESTINATION ${QI_SDK_LIB})
endfunction()
