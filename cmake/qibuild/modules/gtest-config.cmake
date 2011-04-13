## Copyright (C) 2009, 2010, 2011 Aldebaran Robotics

clean(GTEST)
fpath(GTEST gtest/gtest.h)

if (MSVC)
  flib(GTEST OPTIMIZED gtest)
  flib(GTEST OPTIMIZED gtest_main-md)
  flib(GTEST DEBUG     gtestd)
  flib(GTEST DEBUG     gtest_main-mdd)
else()
  flib(GTEST gtest)
  flib(GTEST gtest_main)
endif()

set(GTEST_DEPENDS PTHREAD CACHE STRING "" FORCE)
export_lib(GTEST)
