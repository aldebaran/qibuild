/*
 * Copyright (c) 2012, 2013 Aldebaran Robotics. All rights reserved.
 * Use of this source code is governed by a BSD-style license that can be
 * found in the COPYING file.
 */
#include <iostream>
#ifdef _MSC_VER
# include <Windows.h>
#else
# include <unistd.h>
#endif

#include <cstring>
#include <fstream>

using namespace std;

int main(int argc, char *argv[])
{
  if (argc < 3) {
    cerr << "wrong number of arguments" << endl;
    return 1;
  }
  // qibuild perf always run with output.xml as last arg
  ofstream outFile(argv[argc-1]);
  if (!outFile.is_open()) {
    cerr << "Can't open file " << argv[2] << endl;
    return 1;
  }

  outFile << "<perf_results />" << endl;
  std::cout << "timeout" << std::endl;
  #ifdef _MSC_VER
    Sleep(2000);
  #else
    sleep(2);
  #endif
}

