## Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

clean(OPENSSL)
find_package(OpenSSL QUIET)
qi_persistent_set(OPENSSL_INCLUDE_DIRS ${OPENSSL_INCLUDE_DIR})
qi_persistent_set(OPENSSL_LIBRARIES    ${OPENSSL_LIBRARIES})
if(UNIX AND NOT APPLE)
  qi_persistent_set(OPENSSL_DEPENDS DL)
endif()
export_lib(OPENSSL)
