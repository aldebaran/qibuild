#include <iostream>

#include <world/world.h>

int main() {
  std::cout << "Hello, world" << std::endl;
  std::cout << "The answer is: "
            << get_answer_to_the_question_of_life_universe_and_everything()
            << std::endl;
  return 0;
}
