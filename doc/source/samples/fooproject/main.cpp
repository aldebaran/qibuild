/*
 * Copyright (c) 2012-2016 Aldebaran Robotics. All rights reserved.
 * Use of this source code is governed by a BSD-style license that can be
 * found in the COPYING file.
 */
#include <iostream>
#include <foo/foo.hpp>

int main()
{
  std::cout << "This is bar." << std::endl;
  std::cout << "And the answer is: " << public_method() << std::endl;
  return 0;
}
