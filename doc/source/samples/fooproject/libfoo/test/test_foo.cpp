#include <gtest/gtest.h>

#include <foo/foo.hpp>

TEST(FooTests, public_api_test)
{
  ASSERT_EQ(public_method(), 42);
}

