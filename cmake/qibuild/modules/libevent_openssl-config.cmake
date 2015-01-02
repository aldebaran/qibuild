## Copyright (c) 2012-2015 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

clean(LIBEVENT_OPENSSL)

fpath(LIBEVENT_OPENSSL event2/bufferevent_ssl.h)
if (WIN32)
  flib(LIBEVENT_OPENSSL DEBUG     NAMES event_ssl)
  flib(LIBEVENT_OPENSSL OPTIMIZED NAMES event_ssl)
else()
  flib(LIBEVENT_OPENSSL NAMES event_openssl)
endif()
qi_persistent_set(LIBEVENT_OPENSSL_DEPENDS OPENSSL)
export_lib(LIBEVENT_OPENSSL)
