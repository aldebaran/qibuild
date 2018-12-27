## Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

clean(XML2)
fpath(XML2 libxml/parser.h PATH_SUFFIXES libxml2)
flib(XML2 xml2)
if (APPLE)
  qi_persistent_set(XML2_DEPENDS "ZLIB")
endif()
export_lib(XML2)
