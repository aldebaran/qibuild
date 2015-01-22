## Copyright (c) 2012-2014 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

clean(TINYXML)
fpath(TINYXML tinyxml.h)
fpath(TINYXML tinystr.h)

flib(TINYXML NAMES tinyxml)
export_lib(TINYXML)

