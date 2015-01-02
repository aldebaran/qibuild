## Copyright (c) 2012-2015 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.
execute_process(COMMAND "${FOOTOOL_EXECUTABLE}"
  "${CMAKE_CURRENT_SOURCE_DIR}/foo.in"
  "${CMAKE_CURRENT_BINARY_DIR}/foo.out"
)
