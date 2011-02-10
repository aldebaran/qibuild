## Copyright (C) 2011 Aldebaran Robotics




clean(URBICORE)
fpath(URBICORE urbi PATH_SUFFIXES urbicore)
fpath(URBICORE jconfig.h PATH_SUFFIXES urbicore)

flib(URBICORE uobject)

if(TARGET_HOST STREQUAL "TARGET_HOST_WINDOWS")
  flib(URBICORE libport)
endif()

export_lib(URBICORE)
