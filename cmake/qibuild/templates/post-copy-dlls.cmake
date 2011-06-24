## Copyright (C) 2011 Aldebaran Robotics

###############################################
# Auto-generated file.                        #
# Do not edit                                 #
# This file is part of the qibuild project    #
###############################################

##
# This file will be called in a post-build step
# from a visual studio project.

# It will copy all the required DLLs next to the executable
# that needs it.

# The following variables will be set by the caller:
# BUILD_TYPE : (Debug, Release RelWithDebugInfo, etc...)
# PROJECT : upper-case name of the target beeing built.
#           (${PROJECT}_DEPENDS must exist in the CMake cache
# MSVC    : if it is a string equals to "ON", we are using
#           visual studio. (CMake does not store MSVC in cache ...)

include(CMakeParseArguments)

if(QI_MSVC_IDE)
  string(TOUPPER ${BUILD_TYPE} _U_build_type)
  if("${_U_build_type}" STREQUAL "DEBUG")
    set(token "debug")
  else()
    set(token "optimized")
  endif()
else()
  # If not using visual studio. we can trust CMAKE_BUILD_TYPE
  if("${CMAKE_BUILD_TYPE}" STREQUAL "DEBUG")
    set(token "debug")
  else()
    set(token "optimized")
  endif()
endif()

set(_libs)

# Iterate through the dependencies, adding every
# required .lib
foreach(_dep ${${PROJECT}_DEPENDS})
  string(TOUPPER ${_dep} _U_dep)
  set(_dep_libs ${${_U_dep}_LIBRARIES})

  cmake_parse_arguments(ARG "" "" "optimized;debug" ${_dep_libs})
  if(ARG_UNPARSED_ARGUMENTS)
    # same .lib for debug and release
    list(APPEND _libs ${_dep_libs})
  else()
    # different .lib for debug and release: only append the
    # necessary .libs
    list(APPEND _libs ${ARG_${token}})
  endif()
endforeach()


set(_in_dlls)

# Each .lib may correspond to a .dll, build a list with
# all the .dlls on which the project depends
foreach(_lib ${_libs})
  # First case: in the same build dir: dll is next to the lib
  if(QI_MSVC)
    string(REPLACE ".lib" ".dll" _dll ${_lib})

    if (EXISTS ${_dll})
      list(APPEND _in_dlls ${_dll})
    endif()
  else()
    # mingw:
    string(REPLACE ".dll.a" ".dll" _dll ${_lib})
    if (EXISTS ${_dll})
      list(APPEND _in_dlls ${_dll})
    endif()
  endif()
  # Second case: when installed: dll is in bin/foo.dll, lib is in
  # lib/foo.lib
  string(REPLACE "/${QI_SDK_LIB}/" "/${QI_SDK_BIN}/" _dll ${_dll})
  if (EXISTS ${_dll})
    list(APPEND _in_dlls ${_dll})
  endif()
endforeach()

if(_in_dlls)
  list(REMOVE_DUPLICATES _in_dlls)
endif()



if(QI_MSVC_IDE)
  set(_dest ${QI_SDK_DIR}/${BUILD_TYPE})
else()
  set(_dest ${QI_SDK_DIR}/${QI_SDK_BIN})
endif()

set(_mess "Copying dlls:\n")
foreach(_dll ${_in_dlls})
  get_filename_component(_dll_name "${_dll}" NAME)
  set(_mess "${_mess}- ${_dll_name}\n")
endforeach()
set(_mess "${_mess} to ${_dest}")

message(STATUS ${_mess})
file(COPY ${_in_dlls} DESTINATION "${_dest}")

