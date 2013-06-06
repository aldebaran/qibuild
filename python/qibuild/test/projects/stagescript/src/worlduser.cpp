#include <world/world.h>

// world function names are too long, make them shorter

extern "C"
#ifdef _WIN32
__declspec(dllexport)
#endif
int answer() { return get_answer_to_the_question_of_life_universe_and_everything();}
