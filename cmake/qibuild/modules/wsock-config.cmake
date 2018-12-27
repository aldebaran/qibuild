## Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

# Note: find_library(wsock) won't work because it would
# return c:\windows\system32\wscock32.dll ...

# Also, we do not need any additional include dirs to
# use wsock32, but we need WSOCK_INCLUDE_DIRS for
# export_lib() to be happy

clean(WSOCK)
set(WSOCK_INCLUDE_DIRS " " CACHE STRING "" FORCE)
if(MSCV)
  set(WSOCK_LIBRARIES wsock32.lib CACHE STRING "" FORCE)
else()
  set(WSOCK_LIBRARIES wsock32 CACHE STRING "" FORCE)
endif()
export_lib(WSOCK)

