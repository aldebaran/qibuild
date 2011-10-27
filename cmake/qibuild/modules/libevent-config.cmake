## Copyright (C) 2011 Aldebaran Robotics

clean(LIBEVENT)

fpath(LIBEVENT event.h PATH_SUFFIXES event2)
flib(LIBEVENT NAMES event event_core)

export_lib(LIBEVENT)
