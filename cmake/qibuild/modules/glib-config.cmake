## Copyright (C) 2011 Aldebaran Robotics

clean(GLIB)

# Note:
# when cross-compiling, you should add
# <sysroot>/usr/lib/glib-2.0/include in CMAKE_INCLUDE_PATH
# before getting here.
# (for instance, you can do this in the cmake toolchain file)
if(UNIX AND NOT APPLE)
  list(APPEND CMAKE_INCLUDE_PATH "/usr/lib/glib-2.0/include")
endif()

fpath(GLIB glib.h PATH_SUFFIXES glib-2.0)
fpath(GLIB glibconfig.h)
flib (GLIB glib-2.0     glib-2.0.0   )
flib (GLIB gobject-2.0  gobject-2.0.0)
flib (GLIB gio-2.0      gio-2.0.0    )
flib (GLIB gthread-2.0  gthread-2.0.0)
flib (GLIB gmodule-2.0  gmodule-2.0.0)

export_lib(GLIB)
