#ifndef _ANSWER_H
#define _ANSWER_H


#ifdef WIN32
/* Note: the world_EXPORTS flags is set by cmake
 * if we used create_lib(world SHARED)
 */
#  ifdef world_EXPORTS
#    define WORLD_API   __declspec( dllexport )
#  else
#    define WORLD_API  __declspec( dllimport )
#  endif
#else
#  define WORLD_API __attribute__((visibility("default")))
#endif

WORLD_API int get_answer_to_the_question_of_life_universe_and_everything();

WORLD_API bool is_cross_compiled();

int _this_is_a_non_exported_function();

#endif
