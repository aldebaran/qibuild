## Copyright (C) 2011 Aldebaran Robotics

clean(UUID)
fpath(UUID uuid/uuid.h)
if (NOT APPLE)
  flib(UUID uuid)
  export_lib(UUID)
else()
  # UUID is header-only on apple
  export_header(UUID)
endif()
