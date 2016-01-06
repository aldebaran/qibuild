## Copyright (c) 2012-2016 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.
clean(DBGHELP)

set(DBGHELP_INCLUDE_DIRS " " CACHE INTERNAL "" FORCE)
set(DBGHELP_LIBRARIES "dbghelp.lib" CACHE INTERNAL "" FORCE)
export_lib(DBGHELP)
