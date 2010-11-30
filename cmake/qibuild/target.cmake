##
## Author(s):
##  - Cedric GESTES <gestes@aldebaran-robotics.com>
##
## Copyright (C) 2008, 2010 Aldebaran Robotics
##

#! QiBuild Target
# ===============
# Cedric GESTES <gestes@aldebaran-robotics.com>

#!
# This is the main QiBuild module. It encapsulate the creation of programs,
# scripts and libraries handling dependencies and install rules,
# in an easy,elegant and standard way.
#
# There could be differents targets:
#
# * *bin* : a program
# * *lib* : a library
# * *script* : a script
#
# The separated module link:submodule.html[QiBuild SubModule], can be used to write more readable
# and maintainable CMakeLists for binaries and libraries with lots of sources
# and dependencies. It help keep track of groups of sources.
# see link:submodule.html[SubModule].
#
# TODO: document options that could be passed to add_executable

include(CMakeParseArguments)

#! Create an executable
# The target name should be unique.
#
# \arg:name the target name
# \argn: sources files, like the SRC group, argn and SRC will be merged
# \flag:NO_INSTALL do not create install rules for the target
# \flag:EXCLUDE_FROM_ALL do not include the target in the 'all' target,
#                        this target will not be build by default, you will
#                        to compile the target explicitely.
# \flag:STAGE Stage the binary.
# \flag:WIN32 Build an executable with a WinMain entry point on windows.
# \flag:MACOSX_BUNDLE refer to the add_executable documentation.
# \param:SUBFOLDER the destination subfolder. The install rules generated will be
#                  sdk/bin/<subfolder>
# \group:SRC the list of source files
# \group:DEPENDS the list of source files
# \group:SUBMODULE the list of source files
# \example:target
function(qi_create_bin name)
  qi_debug("qi_create_bin(${name})")

  cmake_parse_arguments(ARG "NO_INSTALL;EXCLUDE_FROM_ALL;STAGE" "SUBFOLDER" "SRC;DEPENDS;SUBMODULE" ${ARGN})

  set(ARG_SRC "${ARG_UNPARSED_ARGUMENTS}" "${ARG_SRC}")
  qi_set_global("${name}_SUBFOLDER" "${ARG_SUBFOLDER}")
  qi_set_global("${name}_NO_INSTALL" ${ARG_NO_INSTALL})

  #no install rules can be generated for target not always built
  if (ARG_EXCLUDE_FROM_ALL)
    set(ARG_NO_INSTALL ON)
    set(ARG_SRC EXCLUDE_FROM_ALL ${ARG_SRC})
  endif()

  foreach(submodule ${ARG_SUBMODULE})
    string(TOUPPER "${submodule}" _upper_submodule)
    set(ARG_SRC     ${ARG_SRC}     ${SUBMODULE_${_upper_submodule}_SRC})
    set(ARG_DEPENDS ${ARG_DEPENDS} ${SUBMODULE_${_upper_submodule}_DEPENDS})
  endforeach()

  add_executable("${name}" ${ARG_SRC})

  message(STATUS "${name} Adding deps: ${ARG_DEP}")
  qi_use_lib("${name}" ${ARG_DEPENDS})


  #make install rules
  if(NOT ARG_NO_INSTALL)
    install(TARGETS "${name}" RUNTIME COMPONENT binary DESTINATION ${QI_SDK_BIN}/${ARG_SUBFOLDER})
  endif()

  #TODO:qi
  if(WIN32)
    set_target_properties("${name}" PROPERTIES DEBUG_POSTFIX "_d")
    _qi_win32_copy_target("${_name}" "${SDK_DIR}/${_SDK_BIN}/${_subfolder}")
    # Be nice with VS user: generate a vcproj so that:
    # -> target path is the path where the executable is copyied
    # (not the place where it is compiled)
    # -> PATH and PYTHONPATH are always set to nice values
    _qi_configure_user_vcproj(${_name} "${SDK_DIR}/${_SDK_BIN}/${_subfolder}")
  endif()
  set_target_properties("${name}" PROPERTIES RUNTIME_OUTPUT_DIRECTORY "${QI_SDK_DIR}/${QI_SDK_BIN}/${ARG_SUBFOLDER}")
endfunction()


#! Create a script. This will generate rules to install it in the sdk too.
#
# \arg:name the name of the target script
# \arg:source the source script, that will be copied in the sdk to bin/<name>
# \flag:NO_INSTALL do not generate install rule for the script
# \flag:STAGE Stage the binary.
# \param:SUBFOLDER the subfolder to install the script into in the sdk. (sdk/bin/<subfolder>)
#
function(qi_create_script name source)
  qi_debug("qi_create_script(${name})")
  cmake_parse_arguments(ARG "NO_INSTALL" "SUBFOLDER" "" ${ARGN})

  #TODO:
  _qi_copy_file("${source}" "${_SDK_BIN}/${ARG_SUBFOLDER}/${name}")
  qi_set_global("${name}_SUBFOLDER" "${ARG_SUBFOLDER}")
  qi_set_global("${name}_NO_INSTALL" ${ARG_NO_INSTALL})

  #make install rules
  if (NOT ARG_NO_INSTALL)
    install(PROGRAMS    "${QI_SDK_DIR}/${QI_SDK_BIN}/${ARG_SUBFOLDER}/${name}"
            COMPONENT   binary
            DESTINATION "${QI_SDK_BIN}/${ARG_SUBFOLDER}")
  endif()
endfunction()



#! Create a library
# The target name should be unique
#
# \arg:name the target name
# \argn: sources files, like the SRC group, argn and SRC will be merged
# \flag:NO_INSTALL do not create install rules for the target
# \flag:EXCLUDE_FROM_ALL do not include the target in the 'all' target,
#                        this target will not be build by default, you will
#                        to compile the target explicitely.
# \flag:NO_STAGE do not stage the librarie.
# \param:SUBFOLDER the destination subfolder. The install rules generated will be
#                  sdk/bin/<subfolder>
# \group:SRC the list of source files (private headers and sources)
# \group:PUBLIC_HEADER list of public headers that should be installed with the lib
# \group:RESOURCE the list of OSX resources
# \group:SUBMODULE submodule to include in the lib
# \group:DEP list of dependencies
# \example:target
function(qi_create_lib name)
  cmake_parse_arguments(ARG "NOBINDLL;NO_INSTALL;NO_STAGE" "SUBFOLDER" "SRC;PUBLIC_HEADER;RESOURCE;SUBMODULE;DEPENDS" ${ARGN})

  if (ARG_NOBINDLL)
    qi_warning("Unhandled : NOBINDLL")
  endif()
  qi_debug("qi_create_lib(${name} ${ARG_SUBFOLDER})")

  #ARGN are sources too
  set(ARG_SRC ${ARG_UNPARSED_ARGUMENTS} ${ARG_SRC} ${ARG_PUBLIC_HEADER})

  qi_set_global("${name}_SUBFOLDER" "${ARG_SUBFOLDER}")
  qi_set_global("${name}_NO_INSTALL" ${ARG_NO_INSTALL})

  foreach(submodule ${ARG_SUBMODULE})
    string(TOUPPER "${submodule}" _upper_submodule)
    #message(STATUS "SUBMODULE: ${_upper_submodule}: ${SUBMODULE_${_upper_submodule}_SRC}")
    message(STATUS "SUBMODULE DEP: ${_upper_submodule}: ${SUBMODULE_${_upper_submodule}_DEPENDS}")
    set(ARG_SRC     ${ARG_SRC}     ${SUBMODULE_${_upper_submodule}_SRC})
    set(ARG_DEPENDS ${ARG_DEPENDS} ${SUBMODULE_${_upper_submodule}_DEPENDS})
  endforeach()

  #message("SOURCES: ${ARG_SRC}")
  add_library("${name}" ${ARG_SRC})

  qi_use_lib("${name}" ${ARG_DEPENDS})

  if (ARG_RESOURCE)
    set_target_properties("${name}" PROPERTIES RESOURCE      "${ARG_RESOURCE}")
  endif()

  if (ARG_PUBLIC_HEADER)
    set_target_properties("${name}" PROPERTIES PUBLIC_HEADER "${ARG_PUBLIC_HEADER}")
  endif()

  #set(_binlib ${QI_SDK_LIB})
  #under win32 bin/lib goes into /Release and /Debug => change that
  if (WIN32)
    #always postfix debug lib/bin with _d
    set_target_properties("${name}" PROPERTIES DEBUG_POSTFIX "_d")

    #by default put libraries next to binaries under windows
    get_target_property(_type ${name} "TYPE")
    # if (_type STREQUAL "SHARED_LIBRARY")
    #   set(_binlib "${_SDK_BIN}")
    # endif ()
    _qi_win32_copy_target("${name}" "${SDK_DIR}/${_binlib}/${ARG_SUBFOLDER}")
  endif()

  set_target_properties("${name}"
    PROPERTIES
      RUNTIME_OUTPUT_DIRECTORY ${QI_SDK_DIR}/${QI_SDK_BIN}/${ARG_SUBFOLDER}
      ARCHIVE_OUTPUT_DIRECTORY ${QI_SDK_DIR}/${QI_SDK_LIB}/${ARG_SUBFOLDER}
      LIBRARY_OUTPUT_DIRECTORY ${QI_SDK_DIR}/${QI_SDK_LIB}/${ARG_SUBFOLDER}
      )
  #endif()

  #make install rules
  if (NOT ARG_NO_INSTALL)
    install(TARGETS "${name}"
            RUNTIME COMPONENT binary     DESTINATION ${QI_SDK_BIN}/${ARG_SUBFOLDER}
            LIBRARY COMPONENT lib        DESTINATION ${QI_SDK_LIB}/${ARG_SUBFOLDER}
      PUBLIC_HEADER COMPONENT header     DESTINATION ${QI_SDK_INCLUDE}/${ARG_SUBFOLDER}
           RESOURCE COMPONENT data       DESTINATION ${QI_SDK_SHARE}/${name}/${ARG_SUBFOLDER}
            ARCHIVE COMPONENT static-lib DESTINATION ${QI_SDK_LIB}/${ARG_SUBFOLDER})
  endif()
endfunction()



#! create a configuration file
# \arg:filename path to the generated file
# \arg:source the source file
# \arg:dest the destination
# TODO: example
function(qi_create_config_h _PARENT_var source dest)
  configure_file("${source}" "${CMAKE_CURRENT_BINARY_DIR}/include/${dest}" ESCAPE_QUOTES)
  include_directories("${CMAKE_CURRENT_BINARY_DIR}/include/")
  get_filename_component(_folder "${dest}" PATH)
  install(FILES       "${CMAKE_CURRENT_BINARY_DIR}/include/${dest}"
          COMPONENT   "header"
          DESTINATION "${QI_SDK_INCLUDE}/${_folder}")
  set(${_PARENT_var} "${CMAKE_CURRENT_BINARY_DIR}/include/${dest}" PARENT_SCOPE)
endfunction()
