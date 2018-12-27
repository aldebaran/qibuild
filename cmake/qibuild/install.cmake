## Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

#! Installing
# ===========
#
# See general documentation in :ref:`cmake-install`
#


#! Generic install function.
# See general documentation here :ref:`cmake-install`
# \argn:                 A list of files : directories and globs on files are accepted.
# \param: SUBFOLDER      An optional subfolder in which to put the files.
# \param: IF             Condition that should be verified for the install rules
#                        to be active (for example IF WITH_ZEROMQ)
# \flag: KEEP_RELATIVE_PATHS Whether relative path should be preserved during installation.
# \flag: RECURSE         Whether glob should be recursive.
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
# \flag: RECURSE         Whether glob should be recursive
# \flag: KEEP_RELATIVE_PATHS  If true, relative paths will be preserved during installation.
#                        (False by default because this is NOT the standard CMake
#                         behavior)
function(qi_install_header)
  _qi_install_internal(${ARGN} COMPONENT devel DESTINATION ${QI_SDK_INCLUDE})
endfunction()



#! Install application data.
# The destination will be: **<prefix>/share/**
#
# \argn:                 A list of files : directories and globs on files are accepted.
# \param: SUBFOLDER      An optional subfolder in which to put the files.
# \param: IF             Condition that should be verified for the install rules
#                        to be active (for example IF WITH_ZEROMQ)
# \flag: RECURSE         Whether glob should be recursive.
# \flag: KEEP_RELATIVE_PATHS  If true, relative paths will be preserved during installation.
#                        (False by default because this is NOT the standard CMake
#                         behavior)
#
function(qi_install_data)
  _qi_install_internal(${ARGN} COMPONENT runtime  DESTINATION ${QI_SDK_SHARE})
endfunction()

#! Install application test data. Useful when you want to run tests after having
# deployed them
# See :cmake:function:`qi_install_data` for the usage
function(qi_install_test_data)
  _qi_install_internal(${ARGN} COMPONENT test  DESTINATION ${QI_SDK_SHARE})
endfunction()

#! Install application doc.
# The destination will be: **<prefix>/share/doc/**
#
# \argn:                 A list of files : directories and globs on files are accepted.
# \param: SUBFOLDER      An optional subfolder in which to put the files.
# \param: IF             Condition that should be verified for the install rules
#                        to be active for example (IF WITH_ZEROMQ)
# \flag: RECURSE         Whether glob should be recursive
# \flag: KEEP_RELATIVE_PATHS  If true, relative paths will be preserved during installation.
#                        (False by default because this is NOT the standard CMake
#                         behavior)
#
function(qi_install_doc)
  _qi_install_internal(${ARGN} COMPONENT devel   DESTINATION ${QI_SDK_DOC})
endfunction()


#! Install application configuration files.
# The destination will be: **<prefix>/etc/**
#
# \argn:                 A list of files : directories and globs on files are accepted.
# \param: SUBFOLDER      An optional subfolder in which to put the files.
# \param: IF             Condition that should be verified for the install rules
#                        to be active for example (IF WITH_ZEROMQ)
# \flag: RECURSE         Whether glob should be recursive
# \flag: KEEP_RELATIVE_PATHS  If true, relative paths will be preserved during installation.
#                        (False by default because this is NOT the standard CMake
#                         behavior)
#
function(qi_install_conf)
  if(NOT DEFINED SYSCONFDIR)
    set(SYSCONFDIR "${QI_SDK_CONF}")
  endif()
  _qi_install_internal(${ARGN} COMPONENT runtime  DESTINATION "${SYSCONFDIR}")
endfunction()

#! Install CMake module files.
# The destination will be: **<prefix>/share/cmake/**
#
# \argn:                 A list of files : directories and globs on files are accepted.
# \param: SUBFOLDER      An optional subfolder in which to put the files.
# \param: IF             Condition that should be verified for the install rules
#                        to be active for example (IF WITH_ZEROMQ)
# \flag: RECURSE         Whether glob should be recursive
# \flag: KEEP_RELATIVE_PATHS  If true, relative paths will be preserved during installation.
#                        (False by default because this is NOT the standard CMake
#                         behavior)
#
function(qi_install_cmake)
  _qi_install_internal(${ARGN} COMPONENT devel DESTINATION ${QI_SDK_CMAKE})
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
            RUNTIME COMPONENT runtime     DESTINATION ${_runtime_output}
            LIBRARY COMPONENT runtime        DESTINATION ${QI_SDK_LIB}/${ARG_SUBFOLDER}
      PUBLIC_HEADER COMPONENT devel     DESTINATION ${QI_SDK_INCLUDE}/${ARG_SUBFOLDER}
           RESOURCE COMPONENT runtime       DESTINATION ${QI_SDK_SHARE}/${name}/${ARG_SUBFOLDER}
            ARCHIVE COMPONENT devel DESTINATION ${QI_SDK_LIB}/${ARG_SUBFOLDER}
            BUNDLE  COMPONENT runtime     DESTINATION ".")
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
    install(PROGRAMS    "${name}"
            COMPONENT   runtime
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
  _qi_install_internal(${ARGN} COMPONENT runtime DESTINATION ${QI_SDK_LIB})
endfunction()

#! install python module.
# The destination depends on the platform and will be set with regard to it:
#
# * on Windows: *<prefix>/Lib/site-packages*
# * on Unix   : *<prefix>/lib/python<python version>/site-packages*
#
# .. note::
#
#   The *python version* is automatically computed.
#
# But the user can use ``PYTHON_INSTALL_SCHEME=...`` to modify the installation layout.
# The valid values for ``PYTHON_INSTALL_SCHEME`` are:
#
# * ``NONE``  : install python modules in the default libdir instead;
# * ``DEBIAN``: install python modules in: *<LIBDIR>/python<VERSION>/dist-packages*
#   (only on Linux).
#
# \argn:                 A list of files : directories and globs on files are accepted.
# \param: TARGETS        A list of targets (in the common CMake meaning).
# \param: SUBFOLDER      An optional subfolder in which to put the files.
# \param: VERSION        Could be set to "3" if you want python3 instead of python2
# \flag: RECURSE         Whether glob should be recursive.
# \flag: KEEP_RELATIVE_PATHS  If true, relative paths will be preserved during installation.
#                        (False by default because this is NOT the standard CMake
#                        behavior).
#
function(qi_install_python)

  cmake_parse_arguments(ARG "" "COMPONENT;DESTINATION;VERSION" "TARGETS" ${ARGN})

  #XXX: this will only work if python headers have been found
  # we can either have found them via qibuild-specific wrapper
  # python-config.cmake or via upstream's FindPythonLib.cmake:
  # In the first case, PYTHON_INCLUDE_DIRS (plural) will be
  # defined, otherwize it will be PYTHON_INCLUDE_DIR (singular)
  set(_python_inc_dir)
  set(_python_headers_found TRUE)

  if ("${ARG_VERSION}" STREQUAL "3")
    if(DEFINED PYTHON3_INCLUDE_DIRS)
      set(_python_inc_dir ${PYTHON3_INCLUDE_DIRS})
    elseif(DEFINED PYTHON3_INCLUDE_DIR)
      set(_python_inc_dir ${PYTHON3_INCLUDE_DIR})
    else()
      set(_python_headers_found FALSE)
    endif()
  else()
    if(DEFINED PYTHON_INCLUDE_DIRS)
      set(_python_inc_dir ${PYTHON_INCLUDE_DIRS})
    elseif(DEFINED PYTHON_INCLUDE_DIR)
      set(_python_inc_dir ${PYTHON_INCLUDE_DIR})
    else()
      set(_python_headers_found FALSE)
    endif()
  endif()


  # Could not find python headers, assuming version 2.7
  set(_python_version_major "2.7")

  # Set the python site-packages location
  if(DEFINED PYTHON_INSTALL_SCHEME AND "${PYTHON_INSTALL_SCHEME}" STREQUAL "NONE")
    set(_qi_sdk_python_site_packages "${QI_SDK_LIB}")
  else()
    if(WIN32)
      set(_qi_sdk_python_site_packages "${QI_SDK_LIB}")
    else()
      if(NOT APPLE AND DEFINED PYTHON_INSTALL_SCHEME AND "${PYTHON_INSTALL_SCHEME}" STREQUAL "DEBIAN")
        set(_qi_sdk_python_site_packages "${QI_SDK_LIB}/python${_python_version_major}/dist-packages")
      else()
        set(_qi_sdk_python_site_packages "${QI_SDK_LIB}/python${_python_version_major}/site-packages")
      endif()
    endif()
  endif()

  if("${ARG_TARGETS}" STREQUAL "")
    _qi_install_internal(${ARG_UNPARSED_ARGUMENTS}
      COMPONENT runtime
      DESTINATION "${_qi_sdk_python_site_packages}"
    )
  else()
    cmake_parse_arguments(ARG "RECURSE;KEEP_RELATIVE_PATHS" "IF;COMPONENT;DESTINATION;SUBFOLDER;VERSION" "" ${ARGN})
    if(ARG_SUBFOLDER)
      set(_subfolder /${ARG_SUBFOLDER})
    endif()
    install(${ARG_UNPARSED_ARGUMENTS}
      COMPONENT runtime
      LIBRARY DESTINATION "${_qi_sdk_python_site_packages}${_subfolder}"
      RUNTIME DESTINATION "${_qi_sdk_python_site_packages}${_subfolder}"
    )
  endif()

endfunction()
