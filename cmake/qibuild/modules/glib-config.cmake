## Copyright (C) 2011 Aldebaran Robotics

clean(GLIB)

fpath(GLIB glib.h PATH_SUFFIXES glib-2.0)

#glibconfig.h is located in the folder (at least on archlinux and gentoo)
if (UNIX AND NOT APPLE)
  set(GLIB_INCLUDE_DIR /usr/lib/glib-2.0/include ${GLIB_INCLUDE_DIR} CACHE PATH "" FORCE)
endif()

flib (GLIB glib-2.0     glib-2.0.0   )
flib (GLIB gobject-2.0  gobject-2.0.0)
flib (GLIB gio-2.0      gio-2.0.0    )
flib (GLIB gthread-2.0  gthread-2.0.0)
flib (GLIB gmodule-2.0  gmodule-2.0.0)

export_lib(GLIB)
