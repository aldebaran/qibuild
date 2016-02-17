/*
 * Copyright (c) 2012-2016 Aldebaran Robotics. All rights reserved.
 * Use of this source code is governed by a BSD-style license that can be
 * found in the COPYING file.
 */
#include <fcntl.h>

int main() {
// This is supposed to be checked with valgrind, no
// point trying to compile it on Windows
#ifndef _MSC_VER
  int f = open("/dev/zero", O_RDONLY);
#endif
  return 0;
}
