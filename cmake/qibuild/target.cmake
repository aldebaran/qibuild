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


#! Create an executable
# The target name should be unique.
#
# \arg:name the target name
# \argn: sources files, like the SRC group, argn and SRC will be merged
# \flag:NO_INSTALL do not create install rules for the target
# \flag:EXCLUDE_FROM_ALL do not include the target in the 'all' target,
#                        this target will not be build by default, you will
#                        to compile the target explicitely.
# \param:SUBFOLDER the destination subfolder. The install rules generated will be
#                  sdk/bin/<subfolder>
# \group:SRC the list of source files
# \example:target
function(qi_create_bin name)
  qi_argn_flags(NO_INSTALL EXCLUDE_FROM_ALL)
  qi_argn_params(SUBFOLDER)
  qi_argn_groups(SRC SUBMODULE)

  #ARGN are sources too
  set(qi_group_src "${argn_group_src}" "${argn_remaining}")

  #no install rules can be generated for target not always built
  if (argn_flag_exclude_from_all)
    set(argn_flag_no_install ON)
  endif()

  debug("qi_create_bin(${name}, ${argn_param_subfolder})")

  add_executable("${name}" ${argn_forward_flag_exclude_from_all} "${argn_group_src}")

  #TODO:qi
  #always postfix debug lib/bin with _d
  # if(${TARGET_ARCH} STREQUAL windows)
  #   set_target_properties("${_name}" PROPERTIES DEBUG_POSTFIX "_d")
  # endif()
  qi_set_global("${name}_SUBFOLDER" "${argn_param_subfolder}")
  debug("qi_create_bin: ${name} will not be installed")
  qi_set_global("${name}_NO_INSTALL" ${argn_flag_no_install})

  #make install rules
  if(${argn_flag_no_install})
    install(TARGETS "${name}" RUNTIME COMPONENT binary DESTINATION ${QI_SDK_BIN}/${argn_param_subfolder})
  endif()

  #TODO:qi
  # if(${TARGET_ARCH} STREQUAL windows)
  #   win32_copy_target("${_name}" "${SDK_DIR}/${_SDK_BIN}/${_subfolder}")
  #   # Be nice with VS user: generate a vcproj so that:
  #   # -> target path is the path where the executable is copyied
  #   # (not the place where it is compiled)
  #   # -> PATH and PYTHONPATH are always set to nice values
  #   configure_user_vcproj(${_name} "${SDK_DIR}/${_SDK_BIN}/${_subfolder}")
  # else()
  set_target_properties("${name}" PROPERTIES RUNTIME_OUTPUT_DIRECTORY "${QI_SDK_DIR}/${QI_SDK_BIN}/${argn_param_subfolder}")
  #endif()
endfunction()


#! Create a script. This will generate rules to install it in the sdk too.
#
# \arg:name the name of the target script
# \arg:source the source script, that will be copied in the sdk to bin/<name>
# \flag:NO_INSTALL do not generate install rule for the script
# \param:SUBFOLDER the subfolder to install the script into in the sdk. (sdk/bin/<subfolder>)
#
function(qi_create_script name source)
  qi_argn_flags(NO_INSTALL)
  qi_argn_params(SUBFOLDER)

  debug("qi_create_script(${name} ${argn_param_subfolder})")
  #TODO:
  #copy_with_depend("${_namein}" "${_SDK_BIN}/${_subfolder}/${_name}")
  qi_set_global("${name}_SUBFOLDER" "${argn_param_subfolder}")
  qi_set_global("${name}_NO_INSTALL" ${argn_flag_no_install})

  #make install rules
  if (${argn_flag_no_install})
    #TODO:
    install(PROGRAMS    "${SDK_DIR}/${_SDK_BIN}/${_subfolder}/${_name}"
            COMPONENT   binary
            DESTINATION "${_SDK_BIN}")
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
# \param:SUBFOLDER the destination subfolder. The install rules generated will be
#                  sdk/bin/<subfolder>
# \group:SRC the list of source files
# \example:target
function(qi_create_lib name)
  #TODO: what is NOBINDLL?
  qi_argn_flags(NO_INSTALL NOBINDLL)
  qi_argn_params(SUBFOLDER)
  qi_argn_groups(SRC HEADER RESOURCE)

  debug("qi_create_lib(${name} ${argn_param_subfolder})")


  #TODO: handle static/shared
  set(${_name}_NO_INSTALL CACHE INTERNAL "" FORCE)

  add_library("${_name}" ${_args} ${_src} ${_header})
  #always postfix debug lib/bin with _d
  if (${TARGET_ARCH} STREQUAL windows)
    set_target_properties("${_name}" PROPERTIES DEBUG_POSTFIX "_d")
  endif (${TARGET_ARCH} STREQUAL windows)

  #by default dll under windows goes in bin
  #everything else goes into lib
  if (_is_nobinwin)
    set(_binlib "${_SDK_LIB}")
  else (_is_nobinwin)
    get_target_property(_ttype ${_name} "TYPE")
    if (_ttype STREQUAL "STATIC_LIBRARY")
      set(_binlib "${_SDK_LIB}")
    else (_ttype STREQUAL "STATIC_LIBRARY")
      set(_binlib "${_SDK_BIN}")
    endif (_ttype STREQUAL "STATIC_LIBRARY")
  endif (_is_nobinwin)

  set(${_name}_SUBFOLDER ${_subfolder} CACHE INTERNAL "" FORCE)
  if (_res)
    set_target_properties("${_name}" PROPERTIES RESOURCE      "${_res}")
  endif (_res)
  if (_header)
    set_target_properties("${_name}" PROPERTIES PUBLIC_HEADER "${_header}")
  endif (_header)

  #under win32 bin/lib goes into /Release and /Debug => change that
  if (${TARGET_ARCH} STREQUAL windows)
    win32_copy_target("${_name}" "${SDK_DIR}/${_binlib}/${_subfolder}")
  else (${TARGET_ARCH} STREQUAL windows)
    set_target_properties("${_name}"
      PROPERTIES
        RUNTIME_OUTPUT_DIRECTORY ${SDK_DIR}/${_binlib}/${_subfolder}
        ARCHIVE_OUTPUT_DIRECTORY ${SDK_DIR}/${_SDK_LIB}/${_subfolder}
        LIBRARY_OUTPUT_DIRECTORY ${SDK_DIR}/${_SDK_LIB}/${_subfolder}
      )
  endif (${TARGET_ARCH} STREQUAL windows)

  #make install rules
  if (${_no_install})
    debug("libbin: create_script: ${_name} not to be installed")
    set(${_name}_NO_INSTALL TRUE CACHE INTERNAL "" FORCE)
  else()
    install(TARGETS "${_name}"
            RUNTIME COMPONENT binary     DESTINATION ${_binlib}/${_subfolder}
            LIBRARY COMPONENT lib        DESTINATION ${_SDK_LIB}/${_subfolder}
      PUBLIC_HEADER COMPONENT header     DESTINATION ${_SDK_INCLUDE}/${_subfolder}
     PRIVATE_HEADER COMPONENT header     DESTINATION ${_SDK_INCLUDE}/${_subfolder}
           RESOURCE COMPONENT data       DESTINATION ${_SDK_SHARE}/${_name}/${_subfolder}
            ARCHIVE COMPONENT static-lib DESTINATION ${_SDK_LIB}/${_subfolder})
  endif()
  debug("BINLIB: END create_lib: (${_name}, ${_is_nobinwin}, ${_subfolder}, src=(${_args} ${_src}) , h=(${_header}))")
endfunction(create_lib)



