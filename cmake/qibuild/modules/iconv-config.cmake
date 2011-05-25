## Copyright (C) 2011 Aldebaran Robotics

clean(ICONV)
fpath(ICONV iconv.h)

# only windows and apple
# need iconv, on other plateform it's provided by the libc
if(WIN32 OR APPLE)
  flib(ICONV iconv)
  export_lib(ICONV)
else()
  export_header(ICONV)
endif()

