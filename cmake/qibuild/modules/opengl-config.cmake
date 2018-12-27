## Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

# Just a wrapper for upstream OpenGL-config.cmake

clean(OPENGL)
include(${CMAKE_ROOT}/Modules/FindOpenGL.cmake)
qi_persistent_set(OPENGL_INCLUDE_DIRS ${OPENGL_INCLUDE_DIR})
qi_persistent_set(OPENGL_LIBRARIES ${OPENGL_LIBRARIES})
export_lib(OPENGL)
