#include <foo/foo.h>

#include <foo/src/foo_private.h>

int public_method()
{
  return private_method();
}


