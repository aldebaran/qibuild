## Copyright (C) 2011 Aldebaran Robotics



if(APPLE)
  set(UUID_IN_SYSTEM "SYSTEM")
else()
  set(UUID_IN_SYSTEM "")
endif()

clean(UUID)

fpath(UUID uuid/uuid.h ${UUID_IN_SYSTEM})
if (NOT APPLE)
  flib (UUID uuid   ${UUID_IN_SYSTEM})
  export_lib(UUID)
else()
  export_header(UUID)
endif()
