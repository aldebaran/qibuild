## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.


clean(IPHLPAPI)
fpath(IPHLPAPI IPHLpApi.h)
# Note: find_library(Iphlpapi) won't work because it would
# return c:\windows\system32\iphlpapi.dll ...
if(MSCV)
  set(IPHLPAPI_LIBRARIES iphlpapi.lib CACHE STRING "" FORCE)
else()
  set(IPHLPAPI_LIBRARIES iphlpapi CACHE STRING "" FORCE)
endif()
export_lib(IPHLPAPI)
