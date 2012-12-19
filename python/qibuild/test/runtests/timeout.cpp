#include <iostream>
#ifdef _MSC_VER
# include <Windows.h>
#else
# include <unistd.h>
#endif

int main() {
  std::cout << "timeout" << std::endl;
#ifdef _MSC_VER
  Sleep(2000);
#else
  sleep(2);
#endif
}

