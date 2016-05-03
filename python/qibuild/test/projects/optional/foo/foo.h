#include <bar.h>

// We need foo.h to depend on bar.h
int foo()
{
  return bar() + 42;
}

// And we need a dummy method so that we have
// a lib
int dummy();
