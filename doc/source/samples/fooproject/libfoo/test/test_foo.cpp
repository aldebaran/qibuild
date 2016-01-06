/*
 * Copyright (c) 2012-2016 Aldebaran Robotics. All rights reserved.
 * Use of this source code is governed by a BSD-style license that can be
 * found in the COPYING file.
 */
#include <gtest/gtest.h>

#include <foo/foo.hpp>

TEST(FooTests, public_api_test)
{
  ASSERT_EQ(public_method(), 42);
}

