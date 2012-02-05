.. _parsing-cmdline:

Parsing command line arguments
==============================

Before reading this section, please make sure you have read the
:ref:`extending-qibuild-actions` tutorial.


Briefly, you should create a file named ``spam.py`` looking like:

.. code-block:: python

  """Add some eggs !"""

  import argparse
  import logging
  import qibuild

  LOGGER = logging.getLogger(__name__)

  def configure_parser(parser):
      """Configure parser for this action """
      qibuild.parsers.default_parser(parser)
      parser.add_argument("--num-eggs",
        help="Number of eggs to add",
        type=int)
      parser.set_defaults(
        num_eggs=3)

  def do(args):
    """Main entry point"""
    LOGGER.info("adding %i eggs", args.num_eggs)



Now lets have a look of what happens when you type:


.. code-block:: console

   $ qibuild spam --num-eggs=42

You first go through qibuild script, in ``bin/qibuild``

You will see it uses :

.. code-block:: python


    modules = qibuild.cmdparse.action_modules_from_package("qibuild.actions")
    qibuild.cmdparse.root_command_main("qibuild", parser, modules)


The first line will look for every Python module in the ``qibuild.actions`` package
that contains a ``do()`` and a ``configure_args`` methods.

The second line will do the main parsing.

Note that the last argument is simply a list of modules.

So if you ever wanted to add an action outside ``qibuild.actions`` package, you could do:

.. code-block:: python

    import spam
    qibuild.cmdparse.root_command_main("qibuild", parser, modules + [spam])


So what does the ``root_command_main`` do?

You can see it taks a ``parser`` object as arument.

You should call this function with an ``argparse.ArgumentParser``
object.

The parser will then be updated.

.. code-block:: python

    parser = argparse.ArgumentParser()
    qibuild.cmdparse.root_command_main("qibuild", parser)

Basically, we will call:

.. code-block:: python

   subparsers = parser.add_subparsers(dest="action", title="actions")
   action_parser = subparsers.add_parser("spam")
   spam.configure_parser(action_parser)


for each module in the list.

Note how we format the help looking using ``module.__doc__``

This means that ``spam.py`` contains everything to handle the parsing:

* The documentation of the action is simply the docstring of the module
* Specific arguments are added using the ``configure_parser`` function of the module

Thus, everything is put in one place, and the ``--help`` output is alwasy correct.

