#include <iostream>


int main()
{
  int answer = 40;
  answer += 2;
  if (answer != 42)
  {
    std::cerr << "We are all going to die!" << std::endl;
    return 2;
  }

  std::cout << "And the answer is: " << answer << std::endl;
  std::cout << "Ok." << std::endl;
  return 0;
}
