## Copyright (C) 2011 Aldebaran Robotics

clean(RT)
fpath(RT time.h)
if (UNIX AND NOT APPLE)
  set(RT_LIBRARIES "-lrt")
else()
  flib(RT rt)
endif()
export_lib(RT)
