#include <foo.h>

int main()
{
  Foo foo;
  if (foo.bar() != 1) {
    return 1;
  }
  return 0;
}
