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

if(${BUILD_TYPE} STREQUAL "Debug")
  set(token "debug")
else()
  set(token "optimized")
endif()

set(_libs)

foreach(_dep ${${PROJECT}_DEPENDS})
  string(TOUPPER ${_dep} _U_dep)
  list(APPEND _libs ${${_U_dep}_LIBRARIES})
endforeach()


include(CMakeParseArguments)

cmake_parse_arguments(ARG "" "" "optimized;debug" ${_libs})

set(_in_dlls)

foreach(_lib ${ARG_${token}})
  string(REPLACE ".lib" ".dll" _dll ${_lib})
  if (EXISTS ${_dll})
    list(APPEND _in_dlls ${_dll})
  endif()
endforeach()

file(COPY ${_in_dlls} DESTINATION ${CMAKE_BINARY_DIR}/sdk/${BUILD_TYPE})
