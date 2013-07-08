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
