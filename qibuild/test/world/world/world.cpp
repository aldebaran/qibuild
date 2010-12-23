#include "world.h"


int get_answer_to_the_question_of_life_universe_and_everything() {
  return _this_is_a_non_exported_function();
}

int _this_is_a_non_exported_function() {
    return 42;
}

bool is_cross_compiled() {
#ifdef CROSS_COMPILING
  return true;
#else
  return false;
#endif
}
