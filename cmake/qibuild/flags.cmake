## Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

#! Handling compile flags
# =======================


# CMAKE_C_FLAGS and the like are _strings_, not lists
macro(_qi_add_flags var flags)
  string(FIND "${${var}}" ${flags} _res)
  if(${_res} EQUAL "-1")
    set(${var} "${${var}} ${flags}")
  endif()
endmacro()

macro(_qi_disable_warnings_msvc)
  foreach(_number ${ARGN})
    _qi_add_flags(CMAKE_C_FLAGS "/wd${_number}")
    _qi_add_flags(CMAKE_CXX_FLAGS "/wd${_number}")
  endforeach()
endmacro()

#! Sanitize compile flags between different compilers
# (gcc and cl.exe)
# The function will also read the following variables that
# can be set from the command line:
#
#   * QI_WERROR:         treat warning as errors
#   * QI_EFFECTIVE_CPP : emit warnings from the 'Effective C++' book
#
# \flag:HIDDEN_SYMBOLS Hide symbol in dynamic
#       unless explicitly exported.
#       Useful when you want to
#       have the same behavior between ``cl.exe`` and ``gcc``
#       for shared libraries.
#       Note that in this case, you should use ``qi/macro.hpp``
#       to export the symbols of your library.
macro(qi_sanitize_compile_flags)
  cmake_parse_arguments(ARGS "HIDDEN_SYMBOLS" "" "" ${ARGN})
  # cl.exe :
  if(MSVC)
    # Undef min and max macros: allow using std::min, std::max
    add_definitions("-DNOMINMAX")

    # Do not produce warnings when not using _s functions
    add_definitions("-D_CRT_SECURE_NO_DEPRECATE")

    # Activate warnings
    # note that wchar.h causes warnings when using /Wall or /W4 ...
    add_definitions("/W3")

    _qi_disable_warnings_msvc(4251 4275)

    # Prevents error C1128 when building in 64b (x64 compiler needs more sections)
    # https://msdn.microsoft.com/en-us/library/8578y171.aspx
    if(CMAKE_CL_64)
      add_definitions("/bigobj")
    endif()

    if(QI_WERROR)
      add_definitions("/WX")
    endif()

  # gcc or clang:
  elseif(UNIX OR MINGW)
    # Use 'standard': c89 and c++98

    # doesn't work: bug #7215
    # add_definitions("-ansi")

    # Activate warnings
    add_definitions("-Wall -Wno-unused-parameter -Werror=return-type")


    if (ARGS_HIDDEN_SYMBOLS)
      add_definitions("-fvisibility=hidden")
    endif()

    if (QI_WERROR)
      add_definitions("-Werror")
    endif()

    if (QI_EFFECTIVE_CPP)
      add_definitions("-Weffc++")
    endif()

  endif()

endmacro()


if (QI_WITH_COVERAGE)
  _qi_add_flags(CMAKE_C_FLAGS "--coverage")
  _qi_add_flags(CMAKE_CXX_FLAGS "--coverage")
  _qi_add_flags(CMAKE_EXE_LINKER_FLAGS "--coverage")
  _qi_add_flags(CMAKE_SHARED_LINKER_FLAGS "--coverage")
  _qi_add_flags(CMAKE_MODULE_LINKER_FLAGS "--coverage")
endif()

if (QI_FORCE_32_BITS)
  _qi_add_flags(CMAKE_C_FLAGS "-m32")
  _qi_add_flags(CMAKE_CXX_FLAGS "-m32")
endif()

if("${CMAKE_BUILD_TYPE}" STREQUAL "Debug")
  if(NOT QI_WITH_DEBUG_INFO)
    # This makes it possible to remove warnings about missing .pdb
    # when redistributing pre-compiled libraries in debug
    if(MSVC)
      set(_orig_flags ${CMAKE_CXX_FLAGS_DEBUG})
      string(REPLACE "/Zi" "" _package_debug_flags "${CMAKE_CXX_FLAGS_DEBUG}")
      set(CMAKE_CXX_FLAGS_DEBUG ${_package_debug_flags} CACHE INTERNAL "" FORCE)
    endif()
  endif()
endif()

if("${CMAKE_BUILD_TYPE}" STREQUAL "Release")
  if(QI_WITH_DEBUG_INFO)
    # Used for instance with breakpad
    if(UNIX)
      _qi_add_flags(CMAKE_C_FLAGS "-g -ggdb -gdwarf-2")
      _qi_add_flags(CMAKE_CXX_FLAGS "-g -ggdb -gdwarf-2")
    endif()
  endif()
endif()
