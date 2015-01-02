/*
 * Copyright (c) 2012-2015 Aldebaran Robotics. All rights reserved.
 * Use of this source code is governed by a BSD-style license that can be
 * found in the COPYING file.
 */
#include <iostream>
#include <limits.h>
#include <unistd.h>

std::string get_working_directory()
{
  char buf[PATH_MAX];
  char* res = getcwd(buf, PATH_MAX);
  if (res != NULL) {
    return std::string(buf);
  }
  return std::string();
}

int main(int argc, char* argv[])
{
  if (argc < 2) {
    std::cerr << "Usage: cwd EXPECTED" << std::endl;
    return 2;
  }

  std::string actual = get_working_directory();
  std::string expected = argv[1];
  if (actual != expected) {
    std::cerr << "Expecting:" << std::endl
              << expected << std::endl
              << "Got:"
              << actual;
    return 1;
  }
  return 0;

}
