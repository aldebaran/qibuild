/*
 * Copyright (c) 2012-2015 Aldebaran Robotics. All rights reserved.
 * Use of this source code is governed by a BSD-style license that can be
 * found in the COPYING file.
 */
package com.test;

public class App {

  static {
    EmbeddedTools tool = new EmbeddedTools();
    tool.loadEmbeddedLibrary("libhellojavajni");
  }
  static native String hello();

  /**
   * @param args
   */
  public static void main(String[] args)
  {
    System.out.println(App.hello());
    return;
  }

}
