/*
 * Copyright (c) 2012-2015 Aldebaran Robotics. All rights reserved.
 * Use of this source code is governed by a BSD-style license that can be
 * found in the COPYING file.
 */

#include <hello.hpp>

jstring Java_com_test_App_hello(JNIEnv *env, jobject obj)
{
  (void) obj;
  return env->NewStringUTF("Hello world !");
}
