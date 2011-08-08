#include <gtest/gtest.h>

#include <foo/foo.h>
#include <foo/src/foo_private.h>

TEST(FooTests, public_api_test)
{
  ASSERT_EQ(public_method(), 42);
}

TEST(FooTests, private_impl_test)
{
  ASSERT_EQ(private_method(), 42);
}
