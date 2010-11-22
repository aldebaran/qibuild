##
## Login : <ctaf@localhost.localdomain>
## Started on  Thu Jun 12 15:19:44 2008 Cedric GESTES
## $Id$
##
## Author(s):
##  - Cedric GESTES <gestes@aldebaran-robotics.com>
##
## Copyright (C) 2008 Aldebaran Robotics

include("${TOOLCHAIN_DIR}/cmake/libfind.cmake")

#get the root folder of this sdk
get_filename_component(_ROOT_DIR ${CMAKE_CURRENT_LIST_FILE} PATH)
include("${_ROOT_DIR}/../boostutils.cmake")

set(_libname "filesystem")
set(_suffix "FILESYSTEM")

clean(BOOST_${_suffix})
fpath(BOOST_${_suffix} boost)

boost_flib(${_suffix} ${_libname})
#boost filesystem use boost_system
boost_flib(${_suffix} "system")

export_lib(BOOST_${_suffix})
