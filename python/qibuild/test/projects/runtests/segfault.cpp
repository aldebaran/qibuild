#include <iostream>
int main()
{
  std::cout << "segfault" << std::endl;
  int* p = 0;
  *p = 42;
}
