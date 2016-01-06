## Copyright (c) 2012-2016 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.


#! Functions to find libraries and include directories
# =====================================================
#
# The qibuild CMake framework contains several ``-config.cmake`` files
# when upstream ``Find-.cmake`` files are not correct or missing.
#
#
# For instance, the canonical ``FindFoo.cmake`` looks like::
#
#   include(FindPackageHandleStandardArgs.cmake)
#
#   find_path(FOO_INCLUDE_DIR foo/foo.h)
#   find_library(FOO_LIBRARY foo)
#
#   find_package_handle_standard_args(FOO
#    DEFAULT_MSG
#     FOO_INCLUDE_DIR
#     FOO_LIBRARY
#   )
#
#   mark_as_advanced(FOO_LIBRARY FOO_INCLUDE_DIR)
#
#   if(FOO_FOUND)
#     set(FOO_LIBRARIES    ${FOO_LIBRARY})
#     set(FOO_INCLUDE_DIRS ${FOO_INCLUDE_DIR})
#   endif()
#
# There is a lot of boilerplate code here, and it's not easy
# to know the names of the variables (is it ``FOO_INCLUDE_DIR`` or ``FOO_INCLUDE_DIRS`` ?)
#
# For qibuild, we use the concept of ``PREFIX`` and exported variables will always
# be ``${${PREFIX}_INCLUDE_DIRS}`` and ``${${PREFIX}_LIBRARIES}``
#
# Thus, ``foo-config.cmake`` can simply be rewritten as::
#
#   clean(FOO)
#   fpath(FOO foo/foo.h)
#   flib(FOO  foo)
#   export(FOO)
#
# Note that the exported variables will always be
# all upper-case, will contain no version number and will have
# the plural form.
#
#  * ``FOO_INCLUDE_DIRS``
#  * ``FOO_LIBRARIES``
#
# Also note that ``FOO_LIBRARIES`` will equal either::
#
#  "general;/path/to/foo.so"
#
# if ``flib()`` was called with no specific argument
# or::
#
#  "debug;/path/to/foo_d.lib;optimized;/path/to/foo.lib"
#
# if both ``flib(FOO OPTIMIZED ...)`` and ``flib(FOO DEBUG ...)``
# have been called.
#
# So this variable can be used directly in the ``target_link_libraries()`` call
#
# .. seealso::
#
#  * :ref:`writing-a-config-cmake`
if (_QI_LIBFIND_CMAKE_)
  return()
endif()
set(_QI_LIBFIND_CMAKE_ TRUE)


include(CMakeParseArguments)
include(FindPackageHandleStandardArgs)

#!
# Cleanup variables related to a library/executable/source-only library
# Use this at the start of the ``${prefix}-config.cmake`` file
#
# \arg:prefix  The prefix of the variables to clean
function(clean prefix)
  set(${prefix}_INCLUDE_DIRS ""          CACHE STRING   "Cleared." FORCE)
  set(${prefix}_LIBRARIES   ""           CACHE STRING   "Cleared." FORCE)
  set(${prefix}_DEFINITIONS ""           CACHE STRING   "Cleared." FORCE)
  set(${prefix}_EXECUTABLE  ""           CACHE STRING   "Cleared." FORCE)
  set(${prefix}_EXECUTABLE_DEBUG  ""     CACHE STRING   "Cleared." FORCE)
  set(${prefix}_SEARCHED    FALSE        CACHE INTERNAL "Cleared." FORCE)
  mark_as_advanced(
    ${prefix}_DEFINITIONS
    ${prefix}_INCLUDE_DIRS
    ${prefix}_LIBRARIES
    ${prefix}_EXECUTABLE
    ${prefix}_EXECUTABLE_DEBUG)
endfunction()


#!
# Search for an include directory
#
# A small example, assuming ``/usr/local/include/foo/foo.h``
# exists.
#
# If you use::
#
#   fpath(FOO foo/foo.h)
#
# ``FOO_INCLUDE_DIRS`` will equal ``/usr/local/include``, so you will
# have to use
#
# .. code-block:: cpp
#
#    #include <foo/foo.h>
#
# Whereas if you use ::
#
#   fpath(FOO foo.h PATH_SUFFIXES foo)
#
# ``FOO_INCLUDE_DIRS`` will equal ``usr/local/include/foo``, so you
# will have to use
#
# .. code-block:: cpp
#
#    #include <foo.h>
#
#
# \arg:prefix  The prefix of the exported variables.
#              Must match the argument of ``clean()`` and ``export_lib()``
#              (or ``export_header`` for a header-only library) calls.
# \arg:path    The path of one of the headers inside the include directory.
# \argn:       The remaining arguments will be passed to
#              ``find_path``
#
function(fpath prefix name0)
  qi_debug("LIBFIND: FPATH (prefix=${prefix}, name0=${name0})")
  cmake_parse_arguments(ARG "SYSTEM" "" "" ${ARGN})

  set(${name0}_INCLUDE "${name0}_INCLUDE-NOTFOUND" CACHE INTERNAL "Cleared." FORCE)
  mark_as_advanced(${name0}_INCLUDE)
  if (ARG_SYSTEM)
    qi_deprecated("You should not use fpath(SYSTEM) anymore")
  endif()

  find_path(${name0}_INCLUDE ${name0} ${ARG_UNPARSED_ARGUMENTS})
  if (${name0}_INCLUDE)
    qi_persistent_append_uniq(${prefix}_INCLUDE_DIRS ${${name0}_INCLUDE})
  endif()

  qi_debug("LIBFIND: RESULT: ${${name0}_INCLUDE}")
  qi_debug("LIBFIND: ${prefix}_INCLUDE_DIRS: ${${prefix}_INCLUDE_DIRS}")
endfunction()



#!
# Search for a library
#
# If the library has a different name in debug and in release,
# you should use::
#
#   flib(foo DEBUG     foo_d)
#   flib(foo OPTIMIZED foo)
#
# If the library has different names, you should call flib() just once ::
#
#  flib(foo foo foo3 foo3.4)
#
# If you want to link with several libraries in one step (for instance
# foo-bar depends on foo-core but you just want to do
# ``qi_use_lib(.. FOO)``, you must call flib() several times::
#
#  flib(foo foo-bar)
#  flib(foo foo-core)
#
#
# \arg:prefix  The prefix of the exported variables.
#              Must match the argument of ``clean()`` and ``export()``
#              calls.
# \arg:name    The name of the library
# \flag: DEBUG     find a library that will be used for a debug build
# \flag: OPTIMIZED find a library that will be used for an optimized build
# \argn:       The remaining arguments will be passed to
#              ``find_library``
#
function(flib prefix)
  qi_debug("LIBFIND: FLIB (prefix=${prefix}, name=${name})")
  cmake_parse_arguments(ARG "DEBUG;OPTIMIZED;REQUIRED;SYSTEM" "" "NAMES" ${ARGN})

  set(ARG_NAMES ${ARG_UNPARSED_ARGUMENTS} ${ARG_NAMES})
  list(GET ARG_NAMES 0 name)

  #qi_info("ARG_NAMES: ${ARG_NAMES} , name: ${name}")
  if ("${name}" STREQUAL "")
    qi_error("empty name: ${name}")
  endif()

  set(${name}_LIB "${name}_LIB-NOTFOUND" CACHE INTERNAL "Cleared." FORCE)

  qi_debug("LIBFIND: modulelist: ${_flib_modulelist}")
  if (ARG_SYSTEM)
    qi_deprecated("Deprecated SYSTEM arguments")
  endif()
  find_library(${name}_LIB "${name}" NAMES ${ARG_NAMES})

  if (ARG_DEBUG)
    set(_keyword "debug")
  elseif (ARG_OPTIMIZED)
    set(_keyword "optimized")
  else()
    set(_keyword "general")
  endif()

  if (${name}_LIB)
    list(APPEND ${prefix}_LIBRARIES ${_keyword} ${${name}_LIB})
    qi_persistent_set(${prefix}_LIBRARIES ${${prefix}_LIBRARIES})
  endif()

  qi_debug("LIBFIND: RESULT: ${${_modulelist}_LIB}")
  qi_debug("LIBFIND: ${prefix}_LIBRARIES: ${${prefix}_LIBRARIES}")
endfunction()

#!
# Search for an executable
#
# \arg:prefix Prefix of the variables to export. Must match the calls
#             to ``clean()`` and ``export_bin()`` calls.
function(fprogram prefix)
  qi_debug("LIBFIND: FPROGRAM (prefix=${prefix}, name=${name})")
  cmake_parse_arguments(ARG "DEBUG;OPTIMIZED" "" "NAMES" ${ARGN})

  set(ARG_NAMES ${ARG_UNPARSED_ARGUMENTS} ${ARG_NAMES})
  list(GET ARG_NAMES 0 name)

  if ("${name}" STREQUAL "")
    qi_error("empty name: ${name}")
  endif()

  find_program(${name}_EXE ${ARG_UNPARSED_ARGUMENTS})

  if(NOT ${name}_EXE)
    return()
  endif()

  if (ARG_DEBUG)
    qi_persistent_set(${name}_EXECUTABLE_DEBUG ${${prefix}_EXE})
  else()
    qi_persistent_set(${name}_EXECUTABLE ${${prefix}_EXE})
  endif()

endfunction()

#!
# Export the variables related to a library
#
# Use this at the end of the ``${prefix}-config.cmake``
# ``find_package_handle_standard_args`` will be called to make
# sure ``${prefix}_LIBRARIES`` and ``${prefix}_INCLUDE_DIRS`` have
# been found.
#
# \arg: prefix The prefix of the exported variables
function(export_lib prefix)
  qi_verbose("library ${prefix}:" )
  qi_verbose("  includes   : ${${prefix}_INCLUDE_DIRS}" )
  qi_verbose("  libraries  : ${${prefix}_LIBRARIES}" )
  qi_verbose("  definitions: ${${prefix}_DEFINITIONS}" )

  _qi_call_fphsa(${prefix})
endfunction()

#!
# Helper function to use with pkgconfig.
#
# Usage, assuming ``foo-1.0.pc`` is somewhere
# in ``PKG_CONFIG_PATH`` ::
#
#   clean(FOO)
#   find_package(PkgConfig)
#   pkg_check_modules(FOO foo-1.0)
#   export_lib_pkgconfig(FOO)
#
function(export_lib_pkgconfig prefix)
  set(${prefix}_INCLUDE_DIRS "${${prefix}_INCLUDE_DIRS}" CACHE STRING "" FORCE)
  set(${prefix}_LIBRARIES    "${${prefix}_LIBRARIES}" CACHE STRING "" FORCE)

  # Finally, display informations if not in quiet mode
  qi_verbose("library ${prefix}:" )
  qi_verbose("  includes   : ${${prefix}_INCLUDE_DIRS}" )
  qi_verbose("  libraries  : ${${prefix}_LIBRARIES}" )
  qi_verbose("  definitions: ${${prefix}_DEFINITIONS}" )

  _qi_call_fphsa(${prefix})
endfunction()


#!
# Export the variables related to an executable
#
# Use at the end of ``foo-config.cmake`` ::
#
#   fprogram(FOO RELEASE foo)
#   fprogram(FOO OPTIMIZED foo_d)
#   export_bin(FOO)
#
# Here, ``FOO_EXECUTABLE`` will be set to
# '/path/to/foo.exe', and ``FOO_EXECUTABLE_DEBUG``
# to 'path/to/foo_d.exe'
#
# \arg:prefix  The prefix of the variables to export
#
function(export_bin prefix)
  # Finally, display informations if not in quiet mode
  qi_verbose("export_bin ${prefix}:" )
  qi_verbose("  executable  : ${${prefix}_EXECUTABLE}" )
  qi_verbose("  executable_d: ${${prefix}_EXECUTABLE_DEBUG}" )

  _qi_call_fphsa(${prefix} EXECUTABLE)
endfunction()

#!
# Export the variables related to an header-only
# library
#
# Use at the end of ``foo-config.cmake`` ::
#
#   clean(FOO)
#   fpath(FOO foo/foo.h)
#   export_header(FOO)
# \arg:prefix  The prefix of the variables to export
#
function(export_header prefix)
  # Finally, display informations if not in quiet mode
  qi_verbose("header library ${prefix}:" )
  qi_verbose("  includes   : ${${prefix}_INCLUDE_DIRS}" )
  qi_verbose("  definitions: ${${prefix}_DEFINITIONS}" )
  _qi_call_fphsa(${prefix} HEADER)
endfunction()

# Helper function to call FPHSA
# \flag: HEADER : just a header was searched,
#                      only ${prefix}_INCLUDE_DIRS will be set.
# \flag: EXECUTABLE : just an executable was searched,
#                      only ${prefix}_EXECUTABLE will be set.
function(_qi_call_fphsa prefix)
  cmake_parse_arguments(ARG "HEADER;EXECUTABLE" "" "" ${ARGN})

  set(_to_check)
  if(ARG_HEADER)
    set(_to_check ${prefix}_INCLUDE_DIRS)
  elseif(ARG_EXECUTABLE)
    set(_to_check ${prefix}_EXECUTABLE)
  else()
    set(_to_check ${prefix}_LIBRARIES ${prefix}_INCLUDE_DIRS)
  endif()

  if($ENV{VERBOSE})
    find_package_handle_standard_args(${prefix} DEFAULT_MSG ${_to_check})
  else()
    set(${prefix}_FIND_QUIETLY TRUE)
    find_package_handle_standard_args(${prefix} DEFAULT_MSG ${_to_check})
  endif()

  # Right after find_package_handle_standard_args, ${prefix}_FOUND is
  # set correctly.
  # For instance, if foo/bar.h is not foud, FOO_FOUND is FALSE.
  # But, right after this, since foo-config.cmake HAS been found, CMake
  # re-set FOO_FOUND to TRUE.
  # So we set ${prefix}_PACKAGE_FOUND in cache...
  qi_persistent_set(${prefix}_PACKAGE_FOUND ${${prefix}_FOUND})
  qi_persistent_set(${prefix}_SEARCHED TRUE)
endfunction()
