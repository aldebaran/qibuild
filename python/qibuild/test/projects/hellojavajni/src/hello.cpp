/*
**
** Author(s):
**  - Pierre ROULLON <proullon@aldebaran-robotics.com>
**
** Copyright (C) 2013-2014 Aldebaran Robotics
*/

#include <hello.hpp>

jstring Java_com_test_App_hello(JNIEnv *env, jobject obj)
{
  (void) obj;
  return env->NewStringUTF("Hello world !");
}
