## Copyright (c) 2012-2016 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.
clean(WS2)
set(WS2_INCLUDE_DIRS " " CACHE STRING "" FORCE)
set(WS2_LIBRARIES Ws2_32.lib CACHE STRING "" FORCE)
export_lib(WS2)
