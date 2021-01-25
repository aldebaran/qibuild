/*
 * Copyright (c) 2012-2021 SoftBank Robotics. All rights reserved.
 * Use of this source code is governed by a BSD-style license that can be
 * found in the COPYING file.
 */

#include <iostream>
#include <locale>
#ifdef WITH_INTL
  #include <libintl.h>
  #define _(string) gettext(string)
#else
  #define _(string) string
  #define bindtextdomain(a, b)
  #define textdomain(a)
#endif


int main(int argc, char *argv[])
{
  if (argc != 2) {
    std::cerr << "Usage: " << argv[0] << " DICT_DIR" << std::endl;
    return -1;
  }

  setlocale(LC_ALL, "");
  bindtextdomain("translate", argv[1]);
  textdomain("translate");

  std::cout << _("Hi, my name is NAO.") << std::endl;
  std::cout << _("Where is Brian?") << std::endl;
  std::cout << _("Brian is in the kitchen.") << std::endl;
}
