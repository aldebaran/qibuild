##
## Author(s):
##  - Cedric GESTES <gestes@aldebaran-robotics.com>
##
## Copyright (C) 2010 Aldebaran Robotics
##

#!
# Copy the file to destination when the source change.
#
# \arg:src the source file
# \arg:dest the destination file
function(_qi_copy_with_depend src dest)
  get_filename_component(_sname "${src}"  NAME)
  get_filename_component(_dname "${dest}" NAME)

  if (NOT EXISTS ${src})
    if (EXISTS ${CMAKE_CURRENT_SOURCE_DIR}/${src})
      set(src ${CMAKE_CURRENT_SOURCE_DIR}/${src})
    endif()
  endif()

  #append the filename to the output filepath if necessary
  if ("${_dname}" STREQUAL "")
    set(dest "${dest}/${_sname}")
  endif()

  get_filename_component(_dirname "${dest}" PATH)
  make_directory("${QI_SDK_DIR}/${_dirname}/")

  configure_file("${src}" "${SDK_DIR}/${dest}" COPYONLY)
endfunction()
