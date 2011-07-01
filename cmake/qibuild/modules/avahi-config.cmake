## Copyright (C) 2011 Aldebaran Robotics

clean(AVAHI)
fpath(AVAHI avahi-client/client.h PATH_SUFFIXES avahi)
if (UNIX AND NOT APPLE)
  set(AVAHI_LIBRARIES "-lavahi-common -lavahi-client" CACHE STRING "" FORCE)
else()
  flib(AVAHI avahi-common)
  flib(AVAHI avahi-client)
endif()
export_lib(AVAHI)
