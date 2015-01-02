/*
 * Copyright (c) 2012-2015 Aldebaran Robotics. All rights reserved.
 * Use of this source code is governed by a BSD-style license that can be
 * found in the COPYING file.
 */


#ifdef _WIN32
__declspec(dllimport)
#endif
int foo(int);

#ifdef _WIN32
__declspec(dllexport)
#endif
int bar(int i) { return 1+foo(i);}

