## Copyright (C) 2011 Aldebaran Robotics

#get the root folder of this sdk
get_filename_component(_ROOT_DIR ${CMAKE_CURRENT_LIST_FILE} PATH)
include("${_ROOT_DIR}/boostutils.cmake")

clean(BOOST_THREAD)
fpath(BOOST_THREAD boost/config.hpp)
boost_flib(THREAD "thread")
qi_set_global(BOOST_THREAD_DEPENDS "BOOST_DATE_TIME")
export_lib(BOOST_THREAD)
