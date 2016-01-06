/*
 * Copyright (c) 2012-2016 Aldebaran Robotics. All rights reserved.
 * Use of this source code is governed by a BSD-style license that can be
 * found in the COPYING file.
 */
#include <foo/foo.hpp>
#include "foo_p.hpp"

int public_method()
{
  return private_method();
}


