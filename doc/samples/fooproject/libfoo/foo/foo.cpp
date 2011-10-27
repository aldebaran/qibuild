#include <foo/foo.hpp>
#include "src/foo_private.hpp"

int public_method()
{
  return private_method();
}


