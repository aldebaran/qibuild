## Copyright (c) 2012-2016 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

clean(TINYXML)
fpath(TINYXML tinyxml.h PATH_SUFFIXES tinyxml)
fpath(TINYXML tinystr.h PATH_SUFFIXES tinyxml)
flib(TINYXML NAMES tinyxml)
export_lib(TINYXML)
