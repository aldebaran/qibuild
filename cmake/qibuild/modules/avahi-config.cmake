## Copyright (C) 2011 Aldebaran Robotics

clean(AVAHI)
fpath(AVAHI avahi-client/client.h PATH_SUFFIXES avahi)
flib(AVAHI avahi-common)
flib(AVAHI avahi-client)
export_lib(AVAHI)
