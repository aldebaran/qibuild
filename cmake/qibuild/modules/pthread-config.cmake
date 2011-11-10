## Copyright (C) 2011 Aldebaran Robotics

clean(PTHREAD)
fpath(PTHREAD "pthread.h")

# Use upstream FindThreads.cmake to correctly set -lpthread or
# -pthread
find_package(Threads QUIET)
if(CMAKE_THREAD_LIBS_INIT)
  qi_set_global(PTHREAD_LIBRARIES ${CMAKE_THREAD_LIBS_INIT})
else()
  flib(PTHREAD pthread pthreadVCE2)
endif()
export_lib(PTHREAD)
