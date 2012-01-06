/*
** Sample main.cpp
*/

#include <iostream>
#include <foo/hello.hpp>

int main(int argc, char *argv[])
{
  foolib_hello();
  std::cout << "sample main" << std::endl;
  return 0;
}
