## Copyright (C) 2011 Aldebaran Robotics



clean(GLIB)

if(UNIX AND NOT APPLE)
  set(GLIB_IN_SYSTEM "SYSTEM")
else()
  set(GLIB_IN_SYSTEM "")
endif()

fpath(GLIB glib.h PATH_SUFFIXES glib-2.0 ${GLIB_IN_SYSTEM})

#glibconfig.h is located in the folder (at least on archlinux and gentoo)
if (UNIX AND NOT APPLE)
  set(GLIB_INCLUDE_DIR /usr/lib/glib-2.0/include ${GLIB_INCLUDE_DIR} CACHE PATH "" FORCE)
endif()

flib (GLIB glib-2.0     glib-2.0.0       ${GLIB_IN_SYSTEM})
flib (GLIB gobject-2.0  gobject-2.0.0    ${GLIB_IN_SYSTEM})
flib (GLIB gio-2.0      gio-2.0.0        ${GLIB_IN_SYSTEM})
flib (GLIB gthread-2.0  gthread-2.0.0    ${GLIB_IN_SYSTEM})
flib (GLIB gmodule-2.0  gmodule-2.0.0    ${GLIB_IN_SYSTEM})

export_lib(GLIB)
