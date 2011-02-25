## Copyright (C) 2011 Aldebaran Robotics

#! qiBuild Target
# ===============

#!
# This is the main qiBuild module. It encapsulates the creation of programs,
# scripts and libraries, handling dependencies and install rules,
# in an easy, elegant and standard way.
#
# There could be differents targets:
#
# * *bin* : a program
# * *lib* : a library
# * *script* : a script
#
# The separate qibuild module link:submodule.html[SubModule], can be used to write more readable
# and maintainable CMakeLists for binaries and libraries with lots of sources
# and dependencies. It helps keep track of groups of sources.
# see link:submodule.html[SubModule].
#
# TODO: document options that could be passed to add_executable

include(CMakeParseArguments)
include(qibuild/internal/copy)

#! Create an executable.
# The target name should be unique.
#
# \arg:name the target name
# \argn: source files, like the SRC group, argn and SRC will be merged
# \flag:NO_INSTALL Do not create install rules for the target
# \flag:EXCLUDE_FROM_ALL Do not include the target in the 'all' target,
#                        this target will not be build by default, you will
#                        have to compile the target explicitly.
#                        Warning: you will NOT be able to create install rules
#                          for this target.
# \flag:STAGE Stage the binary.
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

  cmake_parse_arguments(ARG "NO_INSTALL;EXCLUDE_FROM_ALL;STAGE" "SUBFOLDER" "SRC;DEPENDS;SUBMODULE" ${ARGN})

  set(ARG_SRC "${ARG_UNPARSED_ARGUMENTS}" "${ARG_SRC}")
  qi_set_global("${name}_SUBFOLDER" "${ARG_SUBFOLDER}")
  qi_set_global("${name}_NO_INSTALL" ${ARG_NO_INSTALL})

  #no install rules can be generated for a target that is not always built
  if (ARG_EXCLUDE_FROM_ALL)
    set(ARG_NO_INSTALL ON)
    set(ARG_SRC EXCLUDE_FROM_ALL ${ARG_SRC})
  endif()

  foreach(submodule ${ARG_SUBMODULE})
    string(TOUPPER "${submodule}" _upper_submodule)
    if (NOT DEFINED "SUBMODULE_${_upper_submodule}_SRC")
      qi_error("Submodule ${submodule} not defined")
    endif()
    set(ARG_SRC     ${ARG_SRC}     ${SUBMODULE_${_upper_submodule}_SRC})
    set(ARG_DEPENDS ${ARG_DEPENDS} ${SUBMODULE_${_upper_submodule}_DEPENDS})
  endforeach()

  qi_glob(_SRC ${ARG_SRC})

  add_executable("${name}" ${_SRC})

  qi_use_lib("${name}" ${ARG_DEPENDS})

  #make install rules
  if(NOT ARG_NO_INSTALL)
    qi_install_target("${name}" SUBFOLDER "${ARG_SUBFOLDER}")
  endif()

  if(WIN32)
    set_target_properties("${name}" PROPERTIES DEBUG_POSTFIX "_d")
  endif()
  set_target_properties("${name}" PROPERTIES RUNTIME_OUTPUT_DIRECTORY "${QI_SDK_DIR}/${QI_SDK_BIN}/${ARG_SUBFOLDER}")

  if(MSVC)
    string(TOUPPER ${name} _U_name)
    configure_file(${QI_ROOT_DIR}/templates/post-copy-dlls.cmake
                   ${CMAKE_BINARY_DIR}/post-copy-dlls.cmake
                   COPYONLY)

    add_custom_command(TARGET ${name} POST_BUILD
      COMMAND
        ${CMAKE_COMMAND}
        -DBUILD_TYPE=${CMAKE_CFG_INTDIR}
        -DPROJECT=${_U_name}
        -P ${CMAKE_BINARY_DIR}/post-copy-dlls.cmake
        ${CMAKE_BINARY_DIR}
    )
  endif()

  if(APPLE)
    string(TOUPPER ${name} _U_name)
    configure_file(${QI_ROOT_DIR}/templates/post-copy-dylibs.cmake
                   ${CMAKE_BINARY_DIR}/post-copy-dylibs.cmake
                   COPYONLY)

    add_custom_command(TARGET ${name} POST_BUILD
      COMMAND
        ${CMAKE_COMMAND}
        -DPROJECT=${_U_name}
        -P ${CMAKE_BINARY_DIR}/post-copy-dylibs.cmake
        ${CMAKE_BINARY_DIR}
    )
  endif()
endfunction()


#! Create a script. This will generate rules to install it in the sdk.
#
# \arg:name The name of the target script
# \arg:source The source script, that will be copied in the sdk to bin/<name>
# \flag:NO_INSTALL Do not generate install rule for the script
# \flag:STAGE Stage the binary.
# \param:SUBFOLDER The subfolder in sdk/bin to install the script into. (sdk/bin/<subfolder>)
#
function(qi_create_script name source)
  qi_debug("qi_create_script(${name})")
  cmake_parse_arguments(ARG "NO_INSTALL" "SUBFOLDER" "" ${ARGN})

  _qi_copy_with_depend("${source}" "${_SDK_BIN}/${ARG_SUBFOLDER}/${name}")
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
#
# The target name should be unique.
#
# If you need your library to be static, use:
# [source, cmake]
# ----
# qi_create_lib(mylib STATIC SRC ....)
# ----
#
# If you need your library to be shared, use:
# [source, cmake]
# ----
# qi_create_lib(mylib SHARED SRC ....)
# ----
#
# If you want to let the user choose, use
# [source, cmake]
# ----
#    qi_create_lib(mylib SRC ....)
# ----
#
# The library will be compiled in static by default, unless
# +BUILD_SHARED_LIBS+ is true.
#
# This is the standard CMake behavior, see link:http://www.cmake.org/cmake/help/cmake-2-8-docs.html#command:add_library[cmake documentation] for more details
#
# \arg:name the target name
# \argn: sources files, like the SRC group, argn and SRC will be merged
# \flag:NO_INSTALL Do not create install rules for the target
# \flag:EXCLUDE_FROM_ALL Do not include the target in the 'all' target,
#                        This target will not be built by default, you will
#                        have to compile the target explicitly.
#                        Warning: you will NOT be able to create install rules
#                          for this target.
# \flag:NO_STAGE Do not stage the library.
# \flag:NO_FPIC Do not set -fPIC on static libraries (will be set for shared lib by CMake anyway)
# \param:SUBFOLDER The destination subfolder. The install rules generated will be
#                  sdk/bin/<subfolder>
# \group:SRC The list of source files (private headers and sources)
# \group:RESOURCE The list of OSX resources
# \group:SUBMODULE Submodule to include in the lib
# \group:DEP List of dependencies
# \example:target
function(qi_create_lib name)
  cmake_parse_arguments(ARG "NOBINDLL;NO_INSTALL;NO_STAGE;NO_FPIC" "SUBFOLDER" "SRC;RESOURCE;SUBMODULE;DEPENDS" ${ARGN})

  if (ARG_NOBINDLL)
    # NOBINDLL was used for naoqi modules.
    # We wanted them to end up in
    # sdk/lib/naoqi/my_module.dll, and not in
    # sdk/bin/my_module.dll  (which is the place dll should
    # normally go on windows: next to the .exe)
    qi_deprecated("Use of NOBINDLL is deprectated")
  endif()
  qi_debug("qi_create_lib(${name} ${ARG_SUBFOLDER})")

  #ARGN are sources too
  set(ARG_SRC ${ARG_UNPARSED_ARGUMENTS} ${ARG_SRC})

  qi_set_global("${name}_SUBFOLDER" "${ARG_SUBFOLDER}")
  qi_set_global("${name}_NO_INSTALL" ${ARG_NO_INSTALL})

  foreach(submodule ${ARG_SUBMODULE})
    string(TOUPPER "${submodule}" _upper_submodule)
    if (NOT DEFINED "SUBMODULE_${_upper_submodule}_SRC")
      qi_error("Submodule ${submodule} not defined")
    endif()
    set(ARG_SRC     ${ARG_SRC}     ${SUBMODULE_${_upper_submodule}_SRC})
    set(ARG_DEPENDS ${ARG_DEPENDS} ${SUBMODULE_${_upper_submodule}_DEPENDS})
  endforeach()
  qi_glob(_SRC           ${ARG_SRC})

  add_library("${name}" ${_SRC})

  if (NOT ARG_NO_FPIC)
    if (UNIX)
      # always set fpic (position independent code) on libraries,
      # because static libs could be include in shared lib. (shared lib are fpic by default)
      set_target_properties("${name}" PROPERTIES COMPILE_FLAGS "-fPIC")
    endif()
  endif()

  qi_use_lib("${name}" ${ARG_DEPENDS})

  if (ARG_RESOURCE)
    set_target_properties("${name}" PROPERTIES RESOURCE      "${ARG_RESOURCE}")
  endif()

  if (WIN32)
    #always postfix debug lib/bin with _d
    set_target_properties("${name}" PROPERTIES DEBUG_POSTFIX "_d")
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

  if(APPLE)
    set_target_properties("${name}"
      PROPERTIES
        INSTALL_NAME_DIR "@executable_path/../lib"
    )
  endif()

endfunction()



#! Create a configuration file
# \arg:OUT_PATH Path to the generated file
# \arg:source The source file
# \arg:dest The destination
# This function configure a file (using configure_file), it will generate the install rules
# and return the path of the generated file in OUT_PATH
function(qi_create_config_h OUT_PATH source dest)
  configure_file("${source}" "${CMAKE_CURRENT_BINARY_DIR}/include/${dest}" ESCAPE_QUOTES)
  include_directories("${CMAKE_CURRENT_BINARY_DIR}/include/")
  get_filename_component(_folder "${dest}" PATH)
  install(FILES       "${CMAKE_CURRENT_BINARY_DIR}/include/${dest}"
          COMPONENT   "header"
          DESTINATION "${QI_SDK_INCLUDE}/${_folder}")
  set(${OUT_PATH} "${CMAKE_CURRENT_BINARY_DIR}/include/${dest}" PARENT_SCOPE)
endfunction()
