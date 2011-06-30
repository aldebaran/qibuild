## Copyright (C) 2011 Aldebaran Robotics

clean(PTHREAD)
fpath(PTHREAD "pthread.h" SYSTEM)
if (UNIX AND NOT APPLE)
  set(PTHREAD_LIBRARIES "-lpthread")
else()
  flib(PTHREAD "pthread" SYSTEM)
endif()
export_lib(PTHREAD)
