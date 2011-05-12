## Copyright (C) 2011 Aldebaran Robotics

#get the root folder of this sdk
get_filename_component(_ROOT_DIR ${CMAKE_CURRENT_LIST_FILE} PATH)
include("${_ROOT_DIR}/boostutils.cmake")

set(_libname "thread")
set(_suffix "THREAD")

clean(BOOST_${_suffix})
fpath(BOOST_${_suffix} boost/config.hpp)
boost_flib(${_suffix} ${_libname})
boost_flib(${_suffix} "date_time")
export_lib(BOOST_${_suffix})
