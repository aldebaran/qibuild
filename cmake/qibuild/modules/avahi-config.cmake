## Copyright (C) 2011 Aldebaran Robotics

clean(AVAHI)
fpath(AVAHI avahi-client/client.h PATH_SUFFIXES avahi)
if (UNIX AND NOT APPLE)
  flib(AVAHI avahi-common)
  flib(AVAHI avahi-client)
  # ugly hack: on natty, those are 'system libs', found in /lib/i386/ or something,
  # so using '-l' work, but not flib.

  # better: could we use:
  #   if(NATTY)
  #      list(APPEND CMAKE_
  if(NOT AVAHI_LIBRARIES)
    set(AVAHI_LIBRARIES "-lavahi-common -lavahi-client" CACHE STRING "" FORCE)
  endif()
else()
  flib(AVAHI avahi-common)
  flib(AVAHI avahi-client)
endif()
export_lib(AVAHI)
