## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

clean(PTHREAD)
fpath(PTHREAD "pthread.h")

if(ANDROID)
  qi_set_global(PTHREAD_LIBRARIES "")
  export_lib(PTHREAD)
  return()
endif()

# Use upstream FindThreads.cmake to correctly set -lpthread or
# -pthread
find_package(Threads QUIET)
if(CMAKE_THREAD_LIBS_INIT)
  qi_set_global(PTHREAD_LIBRARIES ${CMAKE_THREAD_LIBS_INIT})
else()
  flib(PTHREAD pthread pthreadVCE2)
endif()
export_lib(PTHREAD)
