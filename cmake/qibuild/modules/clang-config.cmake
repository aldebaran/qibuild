## Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

clean(CLANG)

fpath(CLANG clang-c/Index.h PATHS ${CLANG_ROOT}/include NO_DEFAULT_PATH)
if (NOT CLANG_INCLUDE_DIRS)
  fpath(CLANG clang-c/Index.h)
endif()

flib(CLANG clang PATHS ${CLANG_ROOT}/lib NO_DEFAULT_PATH)
if (NOT CLANG_LIBRARIES)
  flib(CLANG clang)
endif()

export_lib(CLANG)
