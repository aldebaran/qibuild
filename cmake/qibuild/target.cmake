## Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

#! Functions to create targets
# ============================
#
# This is the main qiBuild module. It encapsulates the creation of programs,
# scripts and libraries, handling dependencies and install rules,
# in an easy, elegant and standard way.
#
# There can be different targets:
#
# * *bin* : a program
# * *lib* : a library
# * *script* : a script
#
# .. seealso::
#
#    * :ref:`using-submodules`
#

if (_QI_TARGET_CMAKE_)
  return()
endif()
set(_QI_TARGET_CMAKE_ TRUE)

include(CMakeParseArguments)

#! Create an executable.
# The target name should be unique.
#
# \arg:name the target name
# \argn: source files, like the SRC group, argn and SRC will be merged
# \flag:NO_INSTALL Do not create install rules for the target
# \flag:NO_RPATH Do not try to fix rpath
#                By default, qibuild runs chrpath on the targets so
#                everything work even when project is installed to a
#                non-standard location.
#                Use this to prevent chrpath to be run.
# \flag:EXCLUDE_FROM_ALL Do not include the target in the 'all' target,
#                        this target will not be build by default, you will
#                        have to compile the target explicitly.
#                        Warning: you will NOT be able to create install rules
#                          for this target.
# \flag:WIN32 Build an executable with a WinMain entry point on windows.
# \flag:MACOSX_BUNDLE Refer to the add_executable documentation.
# \param:SUBFOLDER The destination subfolder. The install rules generated will be
#                  sdk/bin/<subfolder>
# \group:SRC The list of source files
# \group:DEPENDS The list of source files
# \group:SUBMODULE The list of source files
# \example:target
function(qi_create_bin name)
  qi_debug("qi_create_bin(${name})")

  cmake_parse_arguments(ARG "NO_RPATH;NO_INSTALL;EXCLUDE_FROM_ALL" "SUBFOLDER" "SRC;DEPENDS;SUBMODULE" ${ARGN})

  message(STATUS "Binary: ${name}")
  set(ARG_SRC "${ARG_UNPARSED_ARGUMENTS}" "${ARG_SRC}")
  qi_persistent_set("${name}_SUBFOLDER" "${ARG_SUBFOLDER}")
  qi_persistent_set("${name}_NO_INSTALL" ${ARG_NO_INSTALL})

  #no install rules can be generated for a target that is not always built
  if (ARG_EXCLUDE_FROM_ALL)
    set(ARG_NO_INSTALL ON)
    set(ARG_SRC EXCLUDE_FROM_ALL ${ARG_SRC})
  endif()

  foreach(submodule ${ARG_SUBMODULE})
    string(TOUPPER "${submodule}" _upper_submodule)
    qi_global_get(_subsrc "SUBMODULE_${_upper_submodule}_SRC")
    qi_global_get(_subdep "SUBMODULE_${_upper_submodule}_DEPENDS")
    qi_global_is_set(_subdef "SUBMODULE_${_upper_submodule}_SRC")
    if (NOT _subdef)
      qi_error("Submodule ${submodule} not defined")
    endif()
    set(ARG_SRC     ${ARG_SRC}     ${_subsrc})
    set(ARG_DEPENDS ${ARG_DEPENDS} ${_subdep})
    source_group(${submodule} FILES ${_subsrc})
  endforeach()

  qi_glob(_SRC ${ARG_SRC})

  add_executable("${name}" ${_SRC})

  if(UNIX AND NOT APPLE)
    set_target_properties("${name}" PROPERTIES COMPILE_FLAGS "-fPIE")
  endif()

  if (NOT "${ARG_DEPENDS}" STREQUAL "")
    qi_use_lib("${name}" ${ARG_DEPENDS})
  endif()

  #make install rules
  if(NOT ARG_NO_INSTALL)
    qi_install_target("${name}" SUBFOLDER "${ARG_SUBFOLDER}")
  endif()

  if(MSVC)
    # always postfix debug lib/bin with _d ...
    set_target_properties("${name}" PROPERTIES DEBUG_POSTFIX "_d")
  endif()

  # prevent having "//": in filenames: visual studio does not like it
  if("${ARG_SUBFOLDER}" STREQUAL "")
    set(_runtime_out "${QI_SDK_DIR}/${QI_SDK_BIN}")
  else()
    set(_runtime_out "${QI_SDK_DIR}/${QI_SDK_BIN}/${ARG_SUBFOLDER}")
  endif()

  set_target_properties("${name}" PROPERTIES
      RUNTIME_OUTPUT_DIRECTORY_DEBUG          "${_runtime_out}"
      RUNTIME_OUTPUT_DIRECTORY_RELEASE        "${_runtime_out}"
      RUNTIME_OUTPUT_DIRECTORY_RELWITHDEBINFO "${_runtime_out}"
      RUNTIME_OUTPUT_DIRECTORY_MINSIZEREL     "${_runtime_out}"
      RUNTIME_OUTPUT_DIRECTORY                "${_runtime_out}"
  )

  file(RELATIVE_PATH _dotdot "${_runtime_out}" "${QI_SDK_DIR}/${QI_SDK_LIB}")
  if(UNIX AND NOT APPLE)
    if(NOT ARG_NO_RPATH)
      # Use a relative rpath at installation
      set_target_properties("${name}"
        PROPERTIES
          INSTALL_RPATH "\$ORIGIN/${_dotdot}"
      )
    endif()
  endif()
  if(APPLE AND NOT ARG_NO_RPATH)
     set_target_properties("${name}"
       PROPERTIES
         INSTALL_RPATH "@executable_path/${_dotdot};@executable_path/${_dotdot}/..")
  endif()
endfunction()


#! Create a script. This will generate rules to install it in the sdk.
#
# \arg:name The name of the target script
# \arg:source The source script, that will be copied in the sdk to bin/<name>
# \flag:NO_INSTALL Do not generate install rule for the script
# \param:SUBFOLDER The subfolder in sdk/bin to install the script into. (sdk/bin/<subfolder>)
#
function(qi_create_script name source)
  qi_debug("qi_create_script(${name})")
  cmake_parse_arguments(ARG "NO_INSTALL" "SUBFOLDER" "" ${ARGN})

  configure_file("${source}" "${QI_SDK_DIR}/${QI_SDK_BIN}/${ARG_SUBFOLDER}/${name}" COPYONLY)
  if(NOT ARG_NO_INSTALL)
    install(PROGRAMS    "${QI_SDK_DIR}/${QI_SDK_BIN}/${ARG_SUBFOLDER}/${name}"
            COMPONENT   runtime
            DESTINATION "${QI_SDK_BIN}/${ARG_SUBFOLDER}")
  endif()
endfunction()



#! Create a library or a module
#
# The target name should be unique.
#
# **Static vs shared**
#
# To build a module (library loaded at runtime), use::
#
#   qi_create_lib(myLib MODULE SRC ....)
#
# If you need your library to be static, use::
#
#   qi_create_lib(mylib STATIC SRC ....)
#
# If you need your library to be shared, use::
#
#   qi_create_lib(mylib SHARED SRC ....)
#
# If you want to let the user choose, use::
#
#    qi_create_lib(mylib SRC ....)
#
# The library will be:
#  * built as a shared library on UNIX
#  * built as a static library on windows
#
# But the user can set BUILD_SHARED_LIBS=OFF to compile
# everything in static by default.
#
# Warning ! This is quite not the standard CMake behavior
#
# \arg:name the target name
# \argn: sources files, like the SRC group, argn and SRC will be merged
# \flag:STATIC force a static library
# \flag:SHARED force a shared library
# \flag:MODULE build a module (library loadable at runtime)
# \flag:NO_INSTALL Do not create install rules for the target
# \flag:EXCLUDE_FROM_ALL Do not include the target in the 'all' target,
#                        This target will not be built by default, you will
#                        have to compile the target explicitly.
#                        Warning: you will NOT be able to create install rules
#                          for this target.
# \flag:NO_RPATH Do not set a rpath to $ORIGIN/..lib when linking on linux.
# \flag:NO_FPIC Do not set -fPIC on static libraries (will be set for shared lib by CMake anyway)
# \param:SUBFOLDER The destination subfolder. The install rules generated will be
#                  sdk/lib/<subfolder>
# \group:SRC The list of source files (private headers and sources)
# \group:SUBMODULE Submodule to include in the lib
# \group:DEPENDS List of dependencies
# \example:target
function(qi_create_lib name)
  cmake_parse_arguments(ARG
    "NOBINDLL;NO_RPATH;NO_INSTALL;NO_FPIC;SHARED;STATIC;MODULE;INTERNAL;NO_LOG"
    "SUBFOLDER"
    "SRC;SUBMODULE;DEPENDS" ${ARGN})

  if (NOT ARG_NO_LOG)
    message(STATUS "Library: ${name}")
  endif()
  if (ARG_NOBINDLL)
    # Kept here for historical reason: TODO: fix this in qibuild/compat.
    qi_deprecated("Use of NOBINDLL is deprectated")
  endif()
  qi_debug("qi_create_lib(${name} ${ARG_SUBFOLDER})")

  #ARGN are sources too
  set(ARG_SRC ${ARG_UNPARSED_ARGUMENTS} ${ARG_SRC})

  qi_persistent_set("${name}_SUBFOLDER" "${ARG_SUBFOLDER}")
  qi_persistent_set("${name}_NO_INSTALL" ${ARG_NO_INSTALL})
  qi_persistent_set("${name}_INTERNAL"   "${ARG_INTERNAL}")


  foreach(submodule ${ARG_SUBMODULE})
    string(TOUPPER "${submodule}" _upper_submodule)
    qi_global_get(_subsrc "SUBMODULE_${_upper_submodule}_SRC")
    qi_global_get(_subdep "SUBMODULE_${_upper_submodule}_DEPENDS")
    qi_global_is_set(_subdef "SUBMODULE_${_upper_submodule}_SRC")
    if (NOT _subdef)
      qi_error("Submodule ${submodule} not defined")
    endif()
    set(ARG_SRC     ${ARG_SRC}     ${_subsrc})
    set(ARG_DEPENDS ${ARG_DEPENDS} ${_subdep})
    source_group(${submodule} FILES ${_subsrc})
  endforeach()

  qi_glob(_SRC           ${ARG_SRC})

  if(UNIX)
    set(_type "SHARED")
  else()
    set(_type "STATIC")
  endif()

  if ("${BUILD_SHARED_LIBS}" STREQUAL "OFF")
    set(_type "STATIC")
  endif()

  if(ARG_SHARED)
    set(_type "SHARED")
  endif()
  if(ARG_STATIC)
    set(_type "STATIC")
  endif()

  if(ARG_MODULE)
    set(_type "MODULE")
  endif()

  qi_verbose("create lib ${name} ${_type}")

  add_library("${name}" ${_type} ${_SRC})

  if (NOT ARG_NO_FPIC)
    if (UNIX)
      # always set fpic (position independent code) on libraries,
      # because static libs could be include in shared lib. (shared lib are fpic by default)
      set_target_properties("${name}" PROPERTIES COMPILE_FLAGS "-fPIC")
    endif()
  endif()

  if (NOT "${ARG_DEPENDS}" STREQUAL "")
    qi_use_lib("${name}" ${ARG_DEPENDS})
  endif()

  if (MSVC)
    # always postfix debug lib/bin with _d ...
    set_target_properties("${name}" PROPERTIES DEBUG_POSTFIX "_d")
  endif()

  # Prevent having '//' in folder names, vs 2008 does not like it
  if("${ARG_SUBFOLDER}" STREQUAL "")
    set(_runtime_out "${QI_SDK_DIR}/${QI_SDK_BIN}")
    set(_lib_out     "${QI_SDK_DIR}/${QI_SDK_LIB}")
  else()
    set(_runtime_out "${QI_SDK_DIR}/${QI_SDK_LIB}/${ARG_SUBFOLDER}")
    set(_lib_out     "${QI_SDK_DIR}/${QI_SDK_LIB}/${ARG_SUBFOLDER}")
  endif()

  set_target_properties("${name}" PROPERTIES
      RUNTIME_OUTPUT_DIRECTORY_DEBUG          "${_runtime_out}"
      RUNTIME_OUTPUT_DIRECTORY_RELEASE        "${_runtime_out}"
      RUNTIME_OUTPUT_DIRECTORY_RELWITHDEBINFO "${_runtime_out}"
      RUNTIME_OUTPUT_DIRECTORY_MINSIZEREL     "${_runtime_out}"
      RUNTIME_OUTPUT_DIRECTORY                "${_runtime_out}"
      LIBRARY_OUTPUT_DIRECTORY_DEBUG          "${_lib_out}"
      LIBRARY_OUTPUT_DIRECTORY_RELEASE        "${_lib_out}"
      LIBRARY_OUTPUT_DIRECTORY_RELWITHDEBINFO "${_lib_out}"
      LIBRARY_OUTPUT_DIRECTORY_MINSIZEREL     "${_lib_out}"
      LIBRARY_OUTPUT_DIRECTORY                "${_lib_out}"
      ARCHIVE_OUTPUT_DIRECTORY_DEBUG          "${_lib_out}"
      ARCHIVE_OUTPUT_DIRECTORY_RELEASE        "${_lib_out}"
      ARCHIVE_OUTPUT_DIRECTORY_RELWITHDEBINFO "${_lib_out}"
      ARCHIVE_OUTPUT_DIRECTORY_MINSIZEREL     "${_lib_out}"
      ARCHIVE_OUTPUT_DIRECTORY                "${_lib_out}"
  )

  #make install rules
  if (NOT ${ARG_NO_INSTALL})
    qi_install_target("${name}" SUBFOLDER "${ARG_SUBFOLDER}")
  endif()

  if(NOT DEFINED QI_INSTALL_NAME_DIR)
    set(QI_INSTALL_NAME_DIR "@rpath/${ARG_SUBFOLDER}")
  endif()
  if(APPLE)
    set_target_properties("${name}"
      PROPERTIES
      # Contrary to what the cmake doc says,
      # this is the only variable that works on mac:
        INSTALL_NAME_DIR ${QI_INSTALL_NAME_DIR}
    )
  endif()

 file(RELATIVE_PATH _dotdot "${_lib_out}" "${QI_SDK_DIR}/${QI_SDK_LIB}")
  if(UNIX AND NOT APPLE)
    if(NOT ARG_NO_RPATH)
      # Use a relative rpath at installation
      set_target_properties("${name}"
        PROPERTIES
          INSTALL_RPATH "\$ORIGIN/${_dotdot}"
      )
    endif()
  endif()
  if(APPLE AND NOT ARG_NO_RPATH AND NOT _type STREQUAL "STATIC")
     set(_rpath "@loader_path")
     if(NOT "${_dotdot}" STREQUAL "")
         set(_rpath "${_rpath};@loader_path/${_dotdot}")
     endif()
     set_target_properties("${name}"
       PROPERTIES
         INSTALL_RPATH "${_rpath}")
  endif()
endfunction()



#! Create a configuration file
#
# Configures a header named ${dest} using the source file from
# ${source} using ``configure_file``
# In addition:
#
# * Make sure the path where the header is generated is
#   added to the include path
#
# * Create the necessary install rules
#
# If you need the header to be generated in a subdirectory
# (recommended), simply use something like::
#
#   qi_create_config_h(_out config.h.in foo/config.h)
#
# Note that both arguments must be *relative* paths
#
# \arg:OUT_PATH Path to the generated file
# \arg:source The source file
# \arg:dest The destination
# \argn: passed to the configure_file() called
function(qi_create_config_h OUT_PATH source dest)
  get_filename_component(_src_full ${source} ABSOLUTE)
  if(NOT EXISTS ${_src_full})
    qi_error("Template for creating header does not exist: ${_src_full}")
  endif()
  get_filename_component(_dest_dir ${dest} PATH)
  set(_inc_dir "${CMAKE_CURRENT_BINARY_DIR}/include")
  file(MAKE_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/include/${_dest_dir})
  get_filename_component(_dest_name ${dest} NAME)
  set(_dest_full ${CMAKE_CURRENT_BINARY_DIR}/include/${dest})
  configure_file("${_src_full}" "${_dest_full}" ${ARGN})
  include_directories("${_inc_dir}")
  install(FILES       "${_dest_full}"
          COMPONENT   devel
          DESTINATION "${QI_SDK_INCLUDE}/${_dest_dir}")
  set(${OUT_PATH} "${_dest_full}" PARENT_SCOPE)
endfunction()
