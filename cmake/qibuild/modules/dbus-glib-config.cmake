## Copyright (C) 2011 Aldebaran Robotics

clean(DBUS-GLIB)

# Note:
# when cross-compiling, you should add
# <sysroot>/usr/lib/glib-2.0/include in CMAKE_INCLUDE_PATH
# before getting here.
# (for instance, you can do this in the cmake toolchain file)
if(UNIX AND NOT APPLE)
  list(APPEND CMAKE_INCLUDE_PATH "/usr/include/dbus-1.0/dbus")
endif()

fpath(DBUS-GLIB dbus-glib.h)
flib (DBUS-GLIB dbus-glib-1)
export_lib(DBUS-GLIB)
