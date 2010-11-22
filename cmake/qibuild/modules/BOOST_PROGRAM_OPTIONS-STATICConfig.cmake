##
## Copyright (C) 2008 Aldebaran Robotics

include("${TOOLCHAIN_DIR}/cmake/libfind.cmake")

#get the root folder of this sdk
get_filename_component(_ROOT_DIR ${CMAKE_CURRENT_LIST_FILE} PATH)
include("${_ROOT_DIR}/../boostutils.cmake")

set(_libname "program_options")
set(_suffix "PROGRAM_OPTIONS")

clean(BOOST_${_suffix}-STATIC)
fpath(BOOST_${_suffix}-STATIC boost)

boost_flib_static(${_suffix}-STATIC ${_libname})
export_lib(BOOST_${_suffix}-STATIC)
