## Copyright (c) 2012-2016 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

#NONE because we dont want to check for a valid compiler
project(QiInstallSample NONE)

#include(qibuild)

#install foo.h    in include/qiinstallsample/foo.h
#install bar/*.h  in include/qiinstallsample/*.h
#install foobar/* in include/qiinstallsample/foobar/

qi_install_header(qiinstallsample foo.h bar/*.h SUBFOLDER foobar)



#to install to a subfolder you can do:
qi_install_header(subbar/*.h SUBFOLDER qiinstallsample/subbar)
