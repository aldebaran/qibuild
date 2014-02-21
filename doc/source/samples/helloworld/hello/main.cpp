/*
 * Copyright (c) 2012-2014 Aldebaran Robotics. All rights reserved.
 * Use of this source code is governed by a BSD-style license that can be
 * found in the COPYING file.
 */
#include <iostream>

#include <world/world.hpp>

int main() {
  std::cout << "Hello, world" << std::endl;
  std::cout << "The answer is: "
            << get_answer_to_the_question_of_life_universe_and_everything()
            << std::endl;
  return 0;
}
