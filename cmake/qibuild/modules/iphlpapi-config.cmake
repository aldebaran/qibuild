## Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.


clean(IPHLPAPI)
if(NOT MSVC)
  fpath(IPHLPAPI IPHLpApi.h)
else()
  # For some reason find_path does not work
  # when using the visual studio generator ...
  # See: http://www.cmake.org/Bug/view.php?id=13291
  # So, set the variable to something non-empty so that
  # export_lib does not complain
  set(IPHLPAPI_INCLUDE_DIRS "  ")
endif()
# Note: find_library(Iphlpapi) won't work because it would
# return c:\windows\system32\iphlpapi.dll ...
if(MSCV)
  set(IPHLPAPI_LIBRARIES iphlpapi.lib CACHE STRING "" FORCE)
else()
  set(IPHLPAPI_LIBRARIES iphlpapi CACHE STRING "" FORCE)
endif()
export_lib(IPHLPAPI)
