/*
 * Copyright (c) 2012-2021 SoftBank Robotics. All rights reserved.
 * Use of this source code is governed by a BSD-style license that can be
 * found in the COPYING file.
 */
#include <iostream>

int main() {
  for (unsigned i=0; i<1000; ++i)
    std::cout << "spamming like a madman" << std::endl;
  return 1;
}

