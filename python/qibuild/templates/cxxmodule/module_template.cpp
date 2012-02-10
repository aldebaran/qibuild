/** \file @module_name@.cpp
 * This is auto-generated code by qibuild
 */


#include "@module_name@.h"

#include <iostream>
#include <alcommon/albroker.h>

@module_name@::@module_name@(boost::shared_ptr<AL::ALBroker> broker,
                   const std::string& name)
  : AL::ALModule(broker, name)
{
  // Describe the module here. This will appear on the webpage
  setModuleDescription("This is automatically generated comment. Please input short description on your own module.");

  /**
   * Define callable methods with their descriptions:
   * This makes the method available to other cpp modules
   * and to python.
   * The name given will be the one visible from outside the module.
   * This method has no parameters or return value to describe
   * functionName(<method_name>, <class_name>, <method_description>);
   * BIND_METHOD(<method_reference>);
   */
  functionName("printHelloWorld", getName(), "Print hello to the world");
  BIND_METHOD(@module_name@::printHelloWorld);

  /**
   * addParam(<attribut_name>, <attribut_descrption>);
   * This enables to document the parameters of the method.
   * It is not compulsory to write this line.
   *
   * setReturn(<return_name>, <return_description>);
   * This enables to document the return of the method.
   * It is not compulsory to write this line.
   */
  functionName("echo", getName(), "Just echo back the argument.");
  setReturn("ALValue", "return argument");
  BIND_METHOD(@module_name@::echo);

  // If you had other methods, you could bind them here...
  /**
   * Bound methods can only take const ref arguments of basic types,
   * or AL::ALValue or return basic types or an AL::ALValue.
   */
}

@module_name@::~@module_name@()
{
}

void @module_name@::init()
{
  /**
   * Init is called just after construction.
   * Do something or not
   */
}

// Function which prints "Hello World!" on standard output
void @module_name@::printHelloWorld()
{
	std::cout << "Hello World!" << std::endl;	
}

// Echo back functiton
AL::ALValue @module_name@::echo(const AL::ALValue& arg)
{
	return arg;
}
