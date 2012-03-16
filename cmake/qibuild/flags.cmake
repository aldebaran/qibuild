## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

#! Handling compile flags
# =======================


#!\ Sanitize compile flags between different compilers
#   (gcc and cl.exe)
# \flag HIDDEN_SYMBOLS Hide symbol in dynamic
#       unless exlicitely exported.
#       Useful when you want to
#       have the same behavior between cl.exe and gcc
#       for shared libraries.
#       Note that in this case, you should use qi/macro.hpp
#       to export the symbols of your library.
# The function will also read the following variables that
# can be set from the command line:
#   * QI_WERROR:         treat warning as errors
#   * QI_EFFECTIVE_CPP : emit warnings from the 'Effective C++' book
function(qi_sanitize_compile_flags)
  cmake_parse_arguments(ARGS "HIDDEN_SYMBOLS" "" "" ${ARGN})
  # cl.exe :
  if(MSVC)
    # Undef min and max macros: allow using std::min, std::max
    add_definitions("-DNOMINMAX")

    # Do not produce warnings when not using _s functions
    add_definitions("-D_CRT_SECURE_NO_DEPRECATE")

    # Do not produce warnings when using POSIX functions
    add_definitions("/wd4996")

    # Activate warnings
    # note that wchar.h causes warnings when using /Wall or /W4 ...
    add_definitions("/W3")

    if(QI_WERROR)
      add_definitions("/WX")
    endif()
  endif()

  # gcc or clang:
  if(UNIX OR MINGW)
    # Use 'standard': c89 and c++98
    add_definitions("-ansi")

    # Activate warnings
    add_definitions("-Wall -Wextra")

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

endfunction()

