## Copyright (C) 2011 Aldebaran Robotics

clean(UUID)
fpath(UUID uuid/uuid.h)
if (NOT APPLE)
  if(UNIX)
    set(UUID_LIBRARIES "-luiid" CACHE INTERNAL "" FORCE)
  endif()
  export_lib(UUID)
else()
  export_header(UUID)
endif()
