## Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

clean(WSA)
# Note the space is important, we need to set it to something!
set(WSA_INCLUDE_DIRS " " CACHE STRING "" FORCE)
# winsock2.h requires with ws2_32.lib
set(WSA_LIBRARIES "ws2_32" CACHE STRING "" FORCE)
export_lib(WSA)

