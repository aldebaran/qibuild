qisys.script -- Tools for qibuild scripts
==========================================

.. py:module:: qisys.script

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
      modules = qisys.script.action_modules_from_package("qibuild.actions")
      qisys.script.root_command_main("qibuild", parser, modules)
