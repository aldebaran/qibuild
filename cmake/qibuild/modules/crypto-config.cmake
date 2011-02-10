## Copyright (C) 2011 Aldebaran Robotics



clean(CRYPTO)

fpath(CRYPTO ssl.h SYSTEM PATH_SUFFIXES openssl)

if(WIN32)
  flib(CRYPTO eay32)
  flib(CRYPTO SYSTEM ssleay32)
else()
  flib(CRYPTO SYSTEM ssl)
endif()
export_lib(CRYPTO)
