/*
 * Copyright (c) 2012-2014 Aldebaran Robotics. All rights reserved.
 * Use of this source code is governed by a BSD-style license that can be
 * found in the COPYING file.
 */
#ifndef _WORLD_HPP
#define _WORLD_HPP

#ifdef WIN32
#  ifdef world_EXPORTS
#    define WORLD_API   __declspec( dllexport )
#  else
#    define WORLD_API  __declspec( dllimport )
#  endif
#else
#  define WORLD_API
#endif

WORLD_API int get_answer_to_the_question_of_life_universe_and_everything();

#endif // _WORLD_HPP
