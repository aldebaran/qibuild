/**
 * \file @module_name@.h
 * This is an auto-generated code by qibuild.
 */

#ifndef @MODULE_NAME@_H
#define @MODULE_NAME@_H

#include <iostream>
#include <alcommon/almodule.h>

namespace AL
{
  // This is a forward declaration of AL:ALBroker which
  // avoids including <alcommon/albroker.h> in this header
  class ALBroker;
}

/**
 * This class inherits AL::ALModule. This allows it to bind methods
 * and be run as a remote executable within NAOqi
 */
class @module_name@ : public AL::ALModule
{
public:
  @module_name@(boost::shared_ptr<AL::ALBroker> broker,
           const std::string &name);

  virtual ~@module_name@();

  /**
   * Overloading ALModule::init().
   * This is called right after the module has been loaded
   */
  virtual void init();

  // After that you may add all your bind method.

  // Function which prints "Hello World!" on standard output
  void printHelloWorld();
  
  // Echo back functiton
  AL::ALValue echo(const AL::ALValue& arg);
};
#endif // @MODULE_NAME@_H
