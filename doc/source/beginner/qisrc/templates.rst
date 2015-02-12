.. _qisrc-templates:

Managing code templates with qisrc
==================================

By default, ``qisrc create PROJECT_NAME`` generates a very basic skeleton for
a qibuild project.

You can specify your own template. Simply use ``@project_name@``,
``@PROJECT_NAME@`` and so on as place holders in file names or in file contents.

For instance:

.. code-block:: console

    template/bin/
      CMakeLists.txt
      src/@projectname@.cpp

.. code-block:: cmake

    # In CMakeLists.txt

    cmake_minimum_required(VERSION 2.8)
    project(@ProjectName@)
    find_package(qibuild)

    qi_create_bin(@projectname@ src/@projectname@.cpp)

Then use

.. code-block:: console

    $ qisrc create --input /path/to/templates/bin -o helloworld HelloWorld
    * CMakeLists.txt
    * src/helloworld.cpp

Here are the substitutions that will be made:

* ``@projectname@`` -> ``helloworld``
* ``@project_name@`` -> ``hello_world``
* ``@PROJECT_NAME@`` -> ``HELLO_WORLD``
* ``@PROJECTNAME@`` -> ``HELLOWORLD``
* ``@projectName@``  -> ``helloWorld``
* ``@ProjectName@`` -> ``HelloWorld``
