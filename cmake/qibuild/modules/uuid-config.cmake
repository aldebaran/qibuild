## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

clean(UUID)
fpath(UUID uuid/uuid.h)
if (NOT APPLE)
  flib(UUID uuid)
  export_lib(UUID)
else()
  # UUID is header-only on apple
  export_header(UUID)
endif()
