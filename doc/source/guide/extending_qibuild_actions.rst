.. _extending-qibuild-actions:

Extending qiBuild actions
-------------------------


Writing a new qibuild action is quite simple.

When you type::

  qibuild spam

the qibuild script will look for a module named spam in the
qibuild.actions package.

The only requirements for the spam module is to contain two functions:

* configure_parser(parser)

* do(args)

The configure_parser function takes a ``argparse.ArgumentParser`` object and
modifies it.

You can modify the parser passed as argument to add specific arguments
to you action.

The do function takes the result of the command line parsing. It is a
``argparse.Namespace`` object.

Quick example of a generic action:::

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


The call to ``qibuild.parsers.default_parser`` is mandatory:
It handles the logging configuration, and all the debug options.

There are a bunch of other functions available to configure the parsers in
the ``qibuild.parsers`` package, depending on what you need to do, and, yes,
they all call ``qibuild.parsers.default_parser`` for you :)


Quick note : often you'll want an action with two words in it, for instance
``foo-bar``.

Although simply writing a file called ``foo-bar.py`` would work, please
create a module called ``foo_bar.py``. Note that ``import foo-bar`` will not
work, Python will read it as ``import foo minus bar`` ...

Note that the command line parsing done by ``qibuild`` will replace ``-`` by
``_`` anyway.

