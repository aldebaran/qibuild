## Copyright (c) 2012-2015 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

clean(PTHREAD)
fpath(PTHREAD "pthread.h")

if(ANDROID)
  export_header(PTHREAD)
  return()
endif()

# Use upstream FindThreads.cmake to correctly set -lpthread or
# -pthread
find_package(Threads QUIET)
if(CMAKE_THREAD_LIBS_INIT)
  qi_persistent_set(PTHREAD_LIBRARIES ${CMAKE_THREAD_LIBS_INIT})
else()
  if(CMAKE_CL_64)
    flib(PTHREAD pthread pthreadVC2)
  else()
    flib(PTHREAD pthread pthreadVCE2)
   endif()
endif()
export_lib(PTHREAD)
