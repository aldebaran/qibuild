## Copyright (C) 2011 Aldebaran Robotics

clean(DBUS)

# Note:
# when cross-compiling, you should add
# <sysroot>/usr/lib/glib-2.0/include in CMAKE_INCLUDE_PATH
# before getting here.
# (for instance, you can do this in the cmake toolchain file)
if(UNIX AND NOT APPLE)
  list(APPEND CMAKE_INCLUDE_PATH "/usr/lib/dbus-1.0/include")
endif()

fpath(DBUS dbus/dbus-arch-deps.h)
fpath(DBUS dbus/dbus.h PATH_SUFFIXES dbus-1.0)
flib (DBUS dbus-1)
export_lib(DBUS)
