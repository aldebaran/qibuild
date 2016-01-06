## Copyright (c) 2012-2016 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.


project(SampleTarget)

#add_subdirectory(fooscript)
add_subdirectory(foolib)
add_subdirectory(foobin)

qi_create_bin(myprog SRC main.cpp)
qi_create_lib(mylib SRC mylib.h mylib.c)
