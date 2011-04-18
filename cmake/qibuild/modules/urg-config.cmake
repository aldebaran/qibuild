## Copyright (C) 2011 Aldebaran Robotics

clean(URG)
fpath(URG "urg_ctrl.h" PATH_SUFFIXES "urg" "c_urg")
flib(URG "c_connection" NAMES c_urg_connection)
flib(URG "c_urg" )
flib(URG "c_system" NAME c_urg_system)
export_lib(URG)
