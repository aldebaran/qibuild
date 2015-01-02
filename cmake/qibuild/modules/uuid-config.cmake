## Copyright (c) 2012-2015 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

clean(UUID)
fpath(UUID uuid/uuid.h)
if(UNIX)
  if(APPLE)
    # UUID is header-only on apple
    export_header(UUID)
  else()
    flib(UUID uuid)
    export_lib(UUID)
  endif()
else()
  if(MSVC)
    # UUID is libonly on Visual Studio
    set(UUID_INCLUDE_DIRS " " CACHE STRING "" FORCE)
    set(UUID_LIBRARIES "uuid" CACHE STRING "" FORCE)
    export_lib(UUID)
  else()
    # UUID on mingw is yet something else
  endif()
endif()
