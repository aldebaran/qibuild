##
## misc.cmake
## Login : <ctaf@ctaf-maptop>
## Started on  Sun Oct 18 03:09:24 2009 Cedric GESTES
## $Id$
##
## Author(s):
##  - Cedric GESTES <gestes@aldebaran-robotics.com>
##
## Copyright (C) 2009 Aldebaran Robotics
##

# add_custom_target("uninstall")

# configure_file("cmake/cmake_uninstall.cmake.in" "cmake_uninstall.cmake" IMMEDIATE @ONLY)
# add_custom_target(uninstall-bn
#   "${CMAKE_COMMAND}" -P "${CMAKE_CURRENT_BINARY_DIR}/cmake_uninstall.cmake")

#create a config.h
function(create_config_h _header _nameout)
  configure_file("${_header}" "${CMAKE_CURRENT_BINARY_DIR}/include/${_nameout}" ESCAPE_QUOTES)
  include_directories("${CMAKE_CURRENT_BINARY_DIR}/include/")
  get_filename_component(_folder "${_nameout}" PATH)
  install(FILES       "${CMAKE_CURRENT_BINARY_DIR}/include/${_nameout}"
          COMPONENT   "header"
          DESTINATION "${_SDK_INCLUDE}/${_folder}")
endfunction(create_config_h)


#copy file with dependency (if the file change in source => update the output)
function(copy_with_depend _src _dest)
  get_filename_component(_sname "${_src}"  NAME)
  get_filename_component(_dname "${_dest}" NAME)

  if (NOT EXISTS ${_src})
    if (EXISTS ${CMAKE_CURRENT_SOURCE_DIR}/${_src})
      set(_src ${CMAKE_CURRENT_SOURCE_DIR}/${_src})
    endif (EXISTS ${CMAKE_CURRENT_SOURCE_DIR}/${_src})
  endif (NOT EXISTS ${_src})

  #append the filename to the output filepath if necessary
  if (_dname STREQUAL "")
    set(_dest "${_dest}/${_sname}")
  endif (_dname STREQUAL "")

  get_filename_component(_dirname "${_dest}" PATH)
  make_directory("${SDK_DIR}/${_dirname}/")

  configure_file("${_src}" "${SDK_DIR}/${_dest}" COPYONLY)
endfunction(copy_with_depend _src _dest)


function(check_is_target _name)
  if (NOT TARGET ${_name})
    error("[${_name}] is not a target verify your function argument")
  endif (NOT TARGET ${_name})
endfunction(check_is_target _name)

###########################
# add a subdir and an install rules for that subdirs
###########################
function(lib_subdir _folder)
  #TODO: replace illegal char [/\\ ] by -
  string(TOUPPER "${_subfolder}-${_folder}" _upname)

  #TODO: be smart, accept lib_subdir("path" SUBFOLDER "toolchain")
  #TODO: as well as lib_subdir("path" TOOLCHAIN-PATH "path.hpp" SUBFOLDER "toolchain")
  if (ARGS1)
    set(_fname "${ARGS1}")
  else (ARGS1)
    set(_fname "${_folder}.hpp")
  endif (ARGS1)

  file(GLOB _headers "${_folder}/*.hpp" "${_folder}/*.h")

  install_header(${_upname} SUBFOLDER "${_subfolder}"            ${_fname})
  install_header(${_upname} SUBFOLDER "${_subfolder}/${_folder}" ${_headers})

  add_subdirectory(${_folder})
endfunction(lib_subdir _folder)

############################
#
# Given the name FOO,
# parse a variable FOO_REVISION.
#
# FOO_REVISION can be like:
#
#  vx.y.z-rct-u
#  vx.y.z-rct
#  vx.y.z
#
# and generate CPACK_PACKAGE_VERSION-* variables
#    MAJOR = x.y
#    MINOR = z-rct (or just z)
#    PATCH = u     (or just empty)
#
############################
function(set_cpack_version_from_git MODULENAME)
  string(REGEX MATCH "v?([0-9]*\\.[0-9]*)\\.([0-9]*(-rc[0-9]+)?)[\\.\\-]?(.*)" _out ${${MODULENAME}_REVISION})
  # CMAKE_MATCH_0 contains the whole match
  # CMAKE_MATCH_3 optionaly contains the [rct] part
  if (CMAKE_MATCH_4 STREQUAL "")
    set(CMAKE_MATCH_4 "0")
  endif()
  set(CPACK_PACKAGE_VERSION_MAJOR ${CMAKE_MATCH_1} PARENT_SCOPE)
  set(CPACK_PACKAGE_VERSION_MINOR ${CMAKE_MATCH_2} PARENT_SCOPE)
  set(CPACK_PACKAGE_VERSION_PATCH ${CMAKE_MATCH_4} PARENT_SCOPE)

endfunction(set_cpack_version_from_git)


##########################
# include a subdirectory if all options are ON
# cond_subdirectory(subdirs <option1> .. <optionN>)
##########################
function(cond_subdirectory subdir)
  set(_do_the_include 1)
  foreach(_arg ${ARGN})
    if (NOT ${_arg})
      set(_do_the_include 0)
      break()
    endif()
  endforeach()
  if (${_do_the_include})
    add_subdirectory(${subdir})
  endif (${_do_the_include})
endfunction()


########################
# Given a prefix and a revision number,
# generate a prefix_revision.h header.
#
# Example of use:
#
# gitversion(FOO)
# generate_revision_header(foo FOO_REVISION)
#
# Later, in a .cpp:
#
#   #include "foo_revision.h"
#
#   std::string version()
#   {
#       return std::string(FOO_REVISION);
#   }
#
# Note: this header won't be "staged" unless you use:
# stage_lib(foo <foo_header_dir> "${CMAKE_CURRENT_BINARY_DIR}/include)")
#
#######################
function(generate_revision_header _name _revision)
  string(TOUPPER ${_name} NAME)

  set(TO_WRITE_IN
"
#ifndef @NAME@_REVISION_H
#define @NAME@_REVISION_H

#define @NAME@_REVISION \"@_revision@\"


#endif // ! @NAME@_REVISION_H
"
)

# First, we write a temporary header in CMAKE_CURRENT_BINARY_DIR my_module_revision.temp.h
# We only overwrite CMAKE_CURRENT_BINARY_DIR/my_module_revision.h is my_module_revision.temp.h
# has changed.

# This is to avoid too many recompilations
  string(CONFIGURE ${TO_WRITE_IN} TO_WRITE_OUT @ONLY)
  configure_file("${T001CHAIN_DIR}/cmake/templates/revision.in"
                 "${CMAKE_CURRENT_BINARY_DIR}/include/${_name}_revision.h" @ONLY)
  include_directories("${CMAKE_CURRENT_BINARY_DIR}/include")

endfunction()



###
# Here be helper functions to generate environnement variables
##



##################
# Given the SDK_DIRS variable,
# creates a colon separted string with
# every paths for PATH:
##################
function(_gen_path _res)
  set(_tmp "")
  foreach(_dir ${LIB_PREFIX} ${BIN_PREFIX})
    file(TO_NATIVE_PATH ${_dir} _dos_dir)
    if(WIN32)
      set(_tmp "${_dos_dir};${_tmp}")
    else()
      set(_tmp "${_dos_dir}:${_tmp}")
    endif()
  endforeach()
set(${_res} "${_tmp}" PARENT_SCOPE)
endfunction()

########################
# Given the SDK_DIRS variable,
# creates a colon-separated or a
# semi-colon-separated with every
# paths for PYTHONPATH:
#
#########################
function(_gen_python_path _res)
  set(_tmp "")
  foreach(_lib ${LIB_PREFIX})
      file(TO_NATIVE_PATH ${_lib} _native_lib)
      if(WIN32)
        set(_tmp "${_native_lib};${_tmp}")
      else()
        set(_tmp "${_native_lib}:${_tmp}")
      endif()
  endforeach()
set(${_res} "${_tmp}" PARENT_SCOPE)
endfunction()


########################
# Given the SDK_DIRS variable,
# creates a colon-separated strint with every
# paths for LD_LIBRARY_PATH:
#
#########################
function(_gen_ld_path _res)
  set(_tmp "")
  foreach(_lib ${LIB_PREFIX})
    set(_tmp "${_lib}:${_tmp}")
  endforeach()
set(${_res} "${_tmp}" PARENT_SCOPE)
endfunction()

########################
# Given the SDK_DIRS variable,
# creates a colon-separated strint with every
# paths for DYLD_LIBRARY_PATH:
#########################
function(_gen_dyld_path _res)
  set(_tmp "")
  foreach(_lib ${LIB_PREFIX})
    set(_tmp "${_lib}:${_tmp}")
  endforeach()
set(${_res} "${_tmp}" PARENT_SCOPE)
endfunction()

########################
# Given the SDK_DIRS variable,
# creates a colon-separated strint with every
# paths for DYLD_FRAMEWORK_PATH:
#########################
function(_gen_framework_path _res)
  set(_tmp "")
  foreach(_framework ${FRAMEWORK_PREFIX})
    set(_tmp "${_framework}:${_tmp}")
  endforeach()
set(${_res} "${_tmp}" PARENT_SCOPE)
endfunction()
