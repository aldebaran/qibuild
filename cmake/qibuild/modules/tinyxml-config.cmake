## Copyright (c) 2012-2014 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

message(STATUS "Hello, tinyxml-config.cmake!")
clean(TINYXML)
fpath(TINYXML tinyxml.h PATH_SUFFIXES tinyxml)
fpath(TINYXML tinystr.h PATH_SUFFIXES tinyxml)
flib(TINYXML NAMES tinyxml)
export_lib(TINYXML)
