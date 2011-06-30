## Copyright (C) 2011 Aldebaran Robotics

clean(DL)
fpath(DL dlfcn.h)
if (UNIX AND NOT APPLE)
  set(DL_LIBRARIES "-ldl")
else()
  flib(DL dl)
endif()
export_lib(DL)
