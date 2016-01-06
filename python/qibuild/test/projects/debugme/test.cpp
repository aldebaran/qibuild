/*
 * Copyright (c) 2012-2016 Aldebaran Robotics. All rights reserved.
 * Use of this source code is governed by a BSD-style license that can be
 * found in the COPYING file.
 */
#include <iostream>


int main()
{
  int answer = 40;
  answer += 2;
  if (answer != 42)
  {
    std::cerr << "We are all going to die!" << std::endl;
    return 2;
  }

  std::cout << "And the answer is: " << answer << std::endl;
  std::cout << "Ok." << std::endl;
  return 0;
}
