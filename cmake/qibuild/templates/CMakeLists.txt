## Copyright (c) 2012-2015 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

install(DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
  DESTINATION "${_SDK_CMAKE}/"
  USE_SOURCE_PERMISSIONS
  COMPONENT devel
  PATTERN "CMakeLists.txt" EXCLUDE
  )
