## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

clean(OPENSSL)
  find_package(OpenSSL QUIET)
  qi_set_global(OPENSSL_INCLUDE_DIRS ${OPENSSL_INCLUDE_DIR})
  qi_set_global(OPENSSL_LIBRARIES    ${OPENSSL_LIBRARIES})
export_lib(OPENSSL)
