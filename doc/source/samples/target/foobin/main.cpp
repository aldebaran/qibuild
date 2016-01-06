/*
 * Copyright (c) 2012-2016 Aldebaran Robotics. All rights reserved.
 * Use of this source code is governed by a BSD-style license that can be
 * found in the COPYING file.
 */

#include <iostream>
#include <foo/hello.hpp>

int main(int argc, char *argv[])
{
  foolib_hello();
  std::cout << "sample main" << std::endl;
  return 0;
}
