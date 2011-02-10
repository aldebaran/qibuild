## Copyright (C) 2011 Aldebaran Robotics



if(UNIX AND NOT APPLE)
  set(IN_SYSTEM "SYSTEM")
else()
  set(IN_SYSTEM "")
endif()

clean(GSTREAMER)
fpath(GSTREAMER  gst/gst.h PATH_SUFFIXES gstreamer-0.10 gstreamer ${IN_SYSTEM})
flib (GSTREAMER  NAMES
  gstreamer-0.10.0
  gstreamer-0.10
  gstreamer
  ${IN_SYSTEM})

if (APPLE)
  depend (GSTREAMER REQUIRED ICONV)
  depend (GSTREAMER REQUIRED GETTEXT)
endif()

export_lib(GSTREAMER)
