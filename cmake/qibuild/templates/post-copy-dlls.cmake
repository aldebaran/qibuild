## Copyright (C) 2011 Aldebaran Robotics

# Function to help handling dlls on windows

# Iterate through the dependencies of the target,
# get the .dll from the .lib, and then copy the
# dlls to QI_SDK_DIR/QI_SDK_BIN

# target and MSVC are passed via command line as a
# post build command, see qibuild/cmake/target.cmake

include(CMakeParseArguments)

if("${CMAKE_BUILD_TYPE}" STREQUAL "DEBUG")
  set(token "debug")
else()
  set(token "optimized")
endif()

# Iterate through the dependencies, adding every
# required .lib
string(TOUPPER ${target} _U_target)
foreach(_dep ${${_U_target}_DEPENDS})
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

set(_dlls)

# Each .lib may correspond to a .dll, build a list with
# all the .dlls on which the project depends
foreach(_lib ${_libs})
  # First case: in the same build dir: dll is next to the lib
  if(MSVC)
    string(REPLACE ".lib" ".dll" _dll ${_lib})

    if (EXISTS ${_dll})
      list(APPEND _dlls ${_dll})
    endif()
  else()
    # mingw:
    string(REPLACE ".dll.a" ".dll" _dll ${_lib})
    if (EXISTS ${_dll})
      list(APPEND _dlls ${_dll})
    endif()
  endif()
  # Second case: when installed: dll is in bin/foo.dll, lib is in
  # lib/foo.lib
  string(REPLACE "/${QI_SDK_LIB}/" "/${QI_SDK_BIN}/" _dll ${_dll})
  if (EXISTS ${_dll})
    list(APPEND _dlls ${_dll})
  endif()
endforeach()

if(_dlls)
  list(REMOVE_DUPLICATES _dlls)
endif()

set(_dest "${QI_SDK_DIR}/${QI_SDK_BIN}")

set(_mess "Copying dlls:\n")
foreach(_dll ${_dlls})
  get_filename_component(_dll_name "${_dll}" NAME)
  set(_mess "${_mess}- ${_dll_name}\n")
endforeach()
set(_mess "${_mess} to ${_dest}")

if($ENV{VERBOSE})
  message(STATUS ${_mess})
endif()

file(COPY ${_dlls} DESTINATION "${_dest}")

