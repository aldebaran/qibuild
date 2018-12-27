## Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

clean(ICONV)
fpath(ICONV iconv.h)

# only windows and apple
# need iconv, on other platforms it's provided by the libc
if(WIN32 OR APPLE)
  flib(ICONV iconv)
  export_lib(ICONV)
else()
  export_header(ICONV)
endif()

