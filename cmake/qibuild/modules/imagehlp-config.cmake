## Copyright (c) 2012-2016 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.
clean(IMAGEHLP)

set(IMAGEHLP_INCLUDE_DIRS " " CACHE INTERNAL "" FORCE)
set(IMAGEHLP_LIBRARIES "Imagehlp.lib" CACHE INTERNAL "" FORCE)
export_lib(IMAGEHLP)
