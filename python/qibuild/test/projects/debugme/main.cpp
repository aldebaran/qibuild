/*
 * Copyright (c) 2012-2014 Aldebaran Robotics. All rights reserved.
 * Use of this source code is governed by a BSD-style license that can be
 * found in the COPYING file.
 */
#include <assert.h>

int foo()
{
  int *p = 0;
  *p = 42;
  return 1;
}

int main()
{
  return foo();
}
