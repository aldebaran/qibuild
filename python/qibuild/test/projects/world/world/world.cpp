/*
 * Copyright (c) 2012-2020 SoftBank Robotics. All rights reserved.
 * Use of this source code is governed by a BSD-style license that can be
 * found in the COPYING file.
 */
#include "world/world.h"
#include <string>


int get_answer_to_the_question_of_life_universe_and_everything() {
  return 42;
}

void kaboom()
{
  throw WorldError(std::string("Kaboom!"));
}

