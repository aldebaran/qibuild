/*
 * Copyright (c) 2012, 2013 Aldebaran Robotics. All rights reserved.
 * Use of this source code is governed by a BSD-style license that can be
 * found in the COPYING file.
 */
#ifndef _ANSWER_H
#define _ANSWER_H


#ifdef WIN32
#  ifdef world_EXPORTS
#    define WORLD_API   __declspec( dllexport )
#  else
#    define WORLD_API  __declspec( dllimport )
#  endif
#else
#  define WORLD_API
#endif

#include <stdexcept>

WORLD_API int get_answer_to_the_question_of_life_universe_and_everything();



class WORLD_API WorldError : public std::runtime_error
{
  public:
      explicit WorldError(const std::string &message)
        : std::runtime_error(message)
      {}

      WorldError(const WorldError &e)
        : std::runtime_error(e.what())
      {}

      virtual ~WorldError() throw()
      {}

};

WORLD_API void kaboom();


#endif // _ANSWER_H
