#include <iostream>
#include <foo/foo.hpp>

int main()
{
  std::cout << "This is bar." << std::endl;
  std::cout << "And the answer is: " << public_method() << std::endl;
  return 0;
}
