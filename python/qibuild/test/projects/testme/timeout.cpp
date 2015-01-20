/*
 * Copyright (c) 2012-2015 Aldebaran Robotics. All rights reserved.
 * Use of this source code is governed by a BSD-style license that can be
 * found in the COPYING file.
 */
#include <iostream>
#ifdef _MSC_VER
# include <Windows.h>
#else
# include <unistd.h>
#endif

int main() {
  std::cout << "timeout" << std::endl;
#ifdef _MSC_VER
  Sleep(2000);
#else
  sleep(2);
#endif
}
