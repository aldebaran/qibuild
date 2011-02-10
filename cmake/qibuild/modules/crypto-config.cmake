## Copyright (C) 2011 Aldebaran Robotics

clean(CRYPTO)
fpath(CRYPTO ssl.h PATH_SUFFIXES openssl)
if(WIN32)
  flib(CRYPTO eay32)
  flib(CRYPTO ssleay32)
else()
  flib(CRYPTO ssl)
endif()
export_lib(CRYPTO)
