## Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

if (_QI_USELIB_CMAKE_)
  return()
endif()
set(_QI_USELIB_CMAKE_ TRUE)
include(qibuild/internal/list)


# Set CMAKE_FIND_LIBRARY_SUFFIXES so that
# only static libs are searched when ${pkg}_STATIC
# is set.
# The _backup argument will be set to the previous
# value of CMAKE_FIND_LIBRARY_SUFFIXES.
# Don't forget to call _qi_disable_check_for_static(_backup)
# afterwards !
function(_qi_check_for_static pkg _backup)
  set(${_backup} ${CMAKE_FIND_LIBRARY_SUFFIXES} PARENT_SCOPE)
  if(${pkg}_STATIC)
    if(UNIX)
      set(CMAKE_FIND_LIBRARY_SUFFIXES ".a" PARENT_SCOPE)
    endif()
  endif()
endfunction()

function(_qi_disable_check_for_static _backup)
  set(CMAKE_FIND_LIBRARY_SUFFIXES "${_backup}" PARENT_SCOPE)
endfunction()

# Reworked to give a very similar CMakeCache as before
# but be about three times faster
#
# We have to call find once on each dependence
# We have to make a list where each dependence is to the right
# of any dependencies that need it
#
# The logic needed is:
#
# _qi_use_lib_get_deps(DEPLIST, DEPS)
#  DEPLIST.ADD(DEPS)
#  foreach DEP in DEPS:
#    if DEP not DEP.FOUND_ALREADY:
#      DEEP FIND(DEP)
#    if DEP_DEPENDS:
#      ADD DEP_DEPNDS TO CACHE
#      DEPLIST.ADD(DEP_DEPENDS)
#  return dedupe(DEPLIST)
#
function(_qi_use_lib_get_deps dep_list_name)
  # if no args, return quick
  set(_result ${ARGN})
  list(LENGTH _result _count)
  if (_count EQUAL 0)
    return()
  endif()

  # we may already have items in the entry list
  # TODO some of ARGN could be lower case
  # LIST(APPEND ${dep_list_name} ${ARGN})

  foreach(_pkg ${ARGN})
    string(TOUPPER ${_pkg} _U_PKG)
    LIST(APPEND ${dep_list_name} ${_U_PKG})

    qi_global_get(_searched "${_U_PKG}_SEARCHED ")
    if ( NOT _searched AND NOT ${_U_PKG}_PACKAGE_FOUND)
        _qi_check_for_static("${_U_PKG}" _backup_static)

        # find_package in two calls. The first call:
        # Uses NO_MODULE - looks for PKGConfig.cmake, not FindPKG.cmake
        # Uses QUIET     - no warning will be generated
        # If Config is found, then PKG_DIR will be set so that the following
        # find_package knows where to look
        find_package(${_U_PKG} NO_MODULE QUIET)
        # _PACKAGE_FOUND is only set when using qibuild/cmake modules,
        # see comments in find.cmake for details.
        if(NOT ${_U_PKG}_PACKAGE_FOUND)
          find_package(${_U_PKG} QUIET REQUIRED)
        endif()
        _qi_disable_check_for_static("${_backup_static}")
        qi_global_set("${_U_PKG}_SEARCHED" TRUE)

        # The find above may have found some dependencies
        # but they may not be complete, and we need to call find
        # once on every dependency
        if (NOT "${${_U_PKG}_DEPENDS}" STREQUAL "")
            qi_global_get(_deps_searched "${_U_PKG}_DEPS_SEARCHED")
            # Check to see if we have done a deep find on this already.
            # If so, we can skip going deep, and trust the dependency list
            if (NOT "${_deps_searched}" STREQUAL "TRUE" )
                # get dependencies recursively
                _qi_use_lib_get_deps(${_U_PKG}_SUB_DEPS ${${_U_PKG}_DEPENDS})

                # if we have dependencies, store the result of the call in the cache
                if (NOT "${${_U_PKG}_SUB_DEPS}" STREQUAL "")
                    set("${_U_PKG}_DEPENDS" ${${_U_PKG}_SUB_DEPS} CACHE INTERNAL "" FORCE)
                endif()
            endif()
        endif()
    endif()

    # Add the depdencies for this package to the result
    if (NOT "${${_U_PKG}_DEPENDS}" STREQUAL "")
        LIST(APPEND ${dep_list_name} "${${_U_PKG}_DEPENDS}")
    endif()
  endforeach()

  #We remove duplicate here..
  #Problem: If libA and libB each depends on libC, we will have "A C B C".
  # libC need to be after libA and libB, so we need to take each libC occurrence into acount,
  # in fact, we could optimise if we want and only take the last one,
  # but REMOVE_DUPLICATES keep the first occurrence
  # so ... we reverse the list, remove duplicate and reverse again!
  list(REVERSE ${dep_list_name})
  list(REMOVE_DUPLICATES ${dep_list_name})
  list(REVERSE ${dep_list_name})

  set(${dep_list_name} ${${dep_list_name}} PARENT_SCOPE)
endfunction()

# Use this function to complete the list of rpath necessary to
# make binaries working ok OSX.
#
# When setting CMAKE_MACOSX_RPATH to ON, CMake get the path of all dependencies
# by itself to add them into the target rpath at build time,
# but it ignores dependencies those do not exist yet.
#
# This function workaround this issue by manually adding necessary directories
# to the property BUILD_RPATH of the <target>
function(_add_lib_to_rpath_osx target libname)
    set(_libraries "")
    if(DEFINED ${libname}_LIBRARIES)
        set(_libraries "${${libname}_LIBRARIES}")
    elseif(DEFINED ${libname}_LIBRARY)
        set(_libraries "${${libname}_LIBRARY}")
    endif()
    if(NOT "${_libraries}" STREQUAL "")
        foreach(_library_path ${_libraries})
            if(IS_ABSOLUTE "${_library_path}")
                # get parent directory
                get_filename_component(_library_path "${_library_path}" DIRECTORY)
                # if this is a system dir, no rpath needed -> ignore it
                LIST(FIND CMAKE_PLATFORM_IMPLICIT_LINK_DIRECTORIES "${_library_path}" isSystemDir)
                if("${isSystemDir}" STREQUAL "-1")
                    set(_rpaths "")
                    get_target_property(_rpaths "${target}" BUILD_RPATH)
                    if("${_rpaths}" STREQUAL "_rpaths-NOTFOUND")
                        set(_rpaths "${_library_path}")
                    else()
                        _qi_list_append_uniq(_rpaths "${_library_path}")
                    endif()
                    set_target_properties("${target}"
                      PROPERTIES
                        BUILD_RPATH "${_rpaths}")
                endif()
            endif()
        endforeach()
    endif()
endfunction()

#! Find dependencies and add them to the target <name>.
#
# This will call include_directories with XXX_INCLUDE_DIRS or fallback to XXX_INCLUDE_DIR.
# This will call target_link_libraries with XXX_LIBRARIES or fallback to XXX_LIBRARY.
# All dependencies should be found, otherwize it will fail. If you want to check if a
# package could be found, prefer using find_package.
#
# to search for static libs set XXX_STATIC=ON before calling qi_use_lib.
#
# \arg:name The target to add dependencies to
# \argn: dependencies, like the DEPENDS group, argn and DEPENDS will be merged.
# If the ASSUME_SYSTEM_INCLUDE option is given, the compiler will consider the include directory of each dependencies as system include directories.
# \group:DEPENDS The list of dependencies
function(_qi_use_lib_internal name)
  STRING(REGEX MATCH "@" _at_in_name ${name})
  if("${_at_in_name}" STREQUAL "@")
    qi_error("Invalid target name: ${name}.
    Target names must not contain the '@' character
    ")
  endif()
  cmake_parse_arguments(ARG "ASSUME_SYSTEM_INCLUDE" "" "DEPENDS" ${ARGN})
  set(ARG_DEPENDS ${ARG_UNPARSED_ARGUMENTS} ${ARG_DEPENDS})
  string(TOUPPER "${name}" _U_name)
  string(TOUPPER "${ARG_DEPENDS}" ARG_DEPENDS)

  # Compute a key to store the call of this function, using '@' as a separator
  set(_key "_QI_USE_LIB_${_U_name}")
  foreach(_arg ${ARG_DEPENDS})
    set(_key "${_key}@${_arg}")
  endforeach()

  if(DEFINED ${_key})
    # qi_use_lib already put in cache
  else()
    _qi_use_lib_get_deps(_DEPS "${ARG_DEPENDS}")
    set("${_key}" ${_DEPS})
    qi_global_set("${_key}" ${_DEPS})

    # Append the new deps to the list of previous deps:
    set(_new_deps ${${_U_name}_DEPENDS} ${_DEPS})
    # reverse, remove duplicated and reverse again:
    if(_new_deps)
      list(REVERSE _new_deps)
      list(REMOVE_DUPLICATES _new_deps)
      list(REVERSE _new_deps)
    endif()
    set("${_U_name}_DEPENDS" ${_new_deps} CACHE STRING "" FORCE)
    mark_as_advanced("${_U_name}_DEPENDS")

    # Mark that we have already searched the dependencies of this
    # For the moment, we will still need to call find on it at least once
    # A future optimization could avoid the find of this for the next target
    # in this project, or even across projects (risky)
    qi_global_set(${_U_name}_DEPS_SEARCHED TRUE)
  endif()

  # Sort include dirs, add dependencies, link with the targets
  # and add correct compile definitions
  set(_inc_dirs)
  foreach(_pkg ${${_key}})
    string(TOUPPER ${_pkg} _U_PKG)

    if (DEFINED ${_U_PKG}_INCLUDE_DIRS)
      _qi_list_append_uniq(_inc_dirs ${${_U_PKG}_INCLUDE_DIRS})
    elseif(DEFINED ${_U_PKG}_INCLUDE_DIR)
      _qi_list_append_uniq(_inc_dirs ${${_U_PKG}_INCLUDE_DIR})
    endif()

    if (DEFINED ${_U_PKG}_LIBRARIES)
      # hack for qt5:
      string(REGEX MATCH "^QT5_.*" _match ${_U_PKG})
      if(NOT "${_match}" STREQUAL "")
        find_package(${_U_PKG})
      endif()
      target_link_libraries("${name}" ${${_U_PKG}_LIBRARIES})
    elseif (DEFINED ${_U_PKG}_LIBRARY)
      target_link_libraries("${name}" ${${_U_PKG}_LIBRARY})
    endif()

    # get lib output dir and add it to BUILD_RPATH
    if(APPLE)
      _add_lib_to_rpath_osx("${name}" "${_U_PKG}")
    endif()

    if ((DEFINED "${_U_PKG}_TARGET") AND (TARGET "${${_U_PKG}_TARGET}"))
      qi_persistent_append_uniq(${_U_name}_TARGET_DEPENDS ${${_U_PKG}_TARGET})
      add_dependencies(${name} ${${_U_PKG}_TARGET})
    endif()

    if(${_U_PKG}_DEFINITIONS)
      # Append the correct compile definitions to the target
      set(_to_add)
      get_target_property(_compile_defs ${name} COMPILE_DEFINITIONS)
      if(_compile_defs)
        set(_to_add ${_compile_defs})
      endif()
      _qi_list_append_uniq(_to_add "${${_U_PKG}_DEFINITIONS}")
      if(_to_add)
        set_target_properties(${name}
          PROPERTIES
            COMPILE_DEFINITIONS "${_to_add}")
      endif()
    endif()
  endforeach()

  foreach(_inc_dir ${_inc_dirs})
    if((${ARG_ASSUME_SYSTEM_INCLUDE}) AND (CMAKE_CXX_COMPILER_VERSION VERSION_LESS "6.0"))
        include_directories(SYSTEM ${_inc_dir})
    else()
      include_directories(${_inc_dir})
    endif()
  endforeach()
endfunction()
