## Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

clean(RPCRT)
# Note the space is important, we need to set it to something!
set(RPCRT_INCLUDE_DIRS " " CACHE STRING "" FORCE)
set(RPCRT_LIBRARIES "Rpcrt4" CACHE STRING "" FORCE)
export_lib(RPCRT)
