/*
 * Copyright (c) 2012-2020 SoftBank Robotics. All rights reserved.
 * Use of this source code is governed by a BSD-style license that can be
 * found in the COPYING file.
 */
#include <cstdlib>
#include <iostream>

int main()
{
  char* foo = getenv("FOO");
  if (!foo) {
    std::cerr << "FOO not set!" << std::endl;
    return 1;
  }
  char* spam = getenv("SPAM");
  if (!spam) {
    std::cerr << "SPAM not set!" << std::endl;
    return 1;
  }

  if (std::string(foo) != "BAR") {
    std::cerr << "Expecting BAR, got" << foo << std::endl;
    return 1;
  }

  if (std::string(spam) != "EGGS") {
    std::cerr << "Expecting EGGS, got" << foo << std::endl;
    return 1;
  }


}
