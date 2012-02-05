qibuild.cmdparse -- Parsing command line
========================================

.. py:module:: qibuild.cmdparse


For instance, after

.. code-block:: console

    $ qibuild make --release foo


* look for a module named make.py
* configure a parser using the configure_parser() of the make.py module
* parse the arguments
* call the do() method of make.py with

  * arg.release = True
  * arg.projects = ["foo"]

The main function are:

* :py:func:`run_action` to call an action
* :py:func:`root_command_main` and `action_modules_from_package`
   to generate a 'main' script, such as ``bin/qibuild``



Functions defined in this module
--------------------------------

.. autofunction:: run_action

Example of use

.. code-block:: python

    # Configure, build, and run tests on the "foo" project:

    def do(args):
        # Forward the --release example to every action:
        qibuild.run_action("qibuild.actions.configure",
          ["foo"], forward_args=args)
        qibuild.run_action("qibuild.actions.make",
          ["foo"], forward_args=args)
        qibuild.run_action("qibuild.actions.test",
          ["foo"], forward_args=args)


.. autofunction:: root_command_main

.. autofunction:: action_modules_from_package

Example of usage:

.. code-block:: python

      parser = argparse.ArgumentParser()
      modules = qibuild.cmdparse.action_modules_from_package("qibuild.actions")
      qibuild.cmdparse.root_command_main("qibuild", parser, modules)


.. seealso::

   * :py:mod:`qibuild.parsers`
