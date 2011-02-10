## Copyright (C) 2011 Aldebaran Robotics



if(UNIX AND NOT APPLE)
  set(PCRE_IN_SYSTEM "SYSTEM")
else()
  set(PCRE_IN_SYSTEM "")
endif()

clean(PCRE)

fpath(PCRE pcre.h ${PCRE_IN_SYSTEM})
flib (PCRE pcre   ${PCRE_IN_SYSTEM})

export_lib(PCRE)
