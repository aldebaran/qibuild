## Copyright (c) 2012-2015 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

clean(URG)
fpath(URG "urg_ctrl.h" PATH_SUFFIXES "urg" "c_urg")
flib(URG "c_connection" NAMES c_urg_connection)
flib(URG "c_urg" )
flib(URG "c_system" NAMES c_urg_system)
export_lib(URG)
