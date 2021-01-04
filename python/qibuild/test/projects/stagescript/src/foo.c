/*
 * Copyright (c) 2012-2021 SoftBank Robotics. All rights reserved.
 * Use of this source code is governed by a BSD-style license that can be
 * found in the COPYING file.
 */

#ifdef _WIN32
__declspec(dllexport)
#endif
int foo(int i) { return i+1;}
