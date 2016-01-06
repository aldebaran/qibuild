## Copyright (c) 2012-2016 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

clean(PSAPI)
if(NOT MSVC)
  fpath(PSAPI psapi.h)
else()
  # For some reason find_path does not work
  # when using the visual studio generator ...
  # See: http://www.cmake.org/Bug/view.php?id=13291
  # So, set the variable to something non-empty so that
  # export_lib does not complain
  set(PSAPI_INCLUDE_DIRS "  ")
endif()

if(MSCV)
  set(PSAPI_LIBRARIES psapi.lib CACHE STRING "" FORCE)
else()
  set(PSAPI_LIBRARIES psapi CACHE STRING "" FORCE)
endif()
export_lib(PSAPI)
