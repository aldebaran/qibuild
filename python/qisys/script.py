## Copyright (c) 2012-2015 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

""" Tools to related to command line parsing

"""

import os
import sys
import argparse
import copy
import operator

from qisys import ui



import qisys.command

class InvalidAction(Exception):
    """Just a custom exception """
    def __init__(self, name, message):
        self.name = name
        self._message = message

    def __str__(self):
        message = "Invalid action %s\n" % self.name
        message += self._message
        return message


def parse_args_for_help(args):
    """Parse a command line for help usage.

    Returns a tuple:
     - help has been requested
     - name of the action on which help has been requested
       (or None if there was not any)

    >>> parse_args_for_help("qibuild".split())
    (True, None)
    >>> parse_args_for_help("qibuild foo".split())
    (False, None)
    >>> parse_args_for_help("qibuild help".split())
    (True, None)
    >>> parse_args_for_help("qibuild help foo".split())
    (True, 'foo')
    >>> parse_args_for_help("qibuild foo --help".split())
    (True, 'foo')
    >>> parse_args_for_help("qibuild foo -h".split())
    (True, 'foo')
    >>> parse_args_for_help("qibuild -h foo".split())
    (True, 'foo')
    """
    def is_help(arg):
        return arg in ("-h", "--help", "help")

    if not args:
        return (True, None)
    if len(args) > 2:
        return (False, None)

    if len(args) == 1:
        if is_help(args[0]):
            return (True, None)
        else:
            return(False, None)

    if len(args) == 2:
        if is_help(args[0]):
            return (True, args[1])
        if is_help(args[1]):
            return (True, args[0])
        return(False, None)


def run_action(module_name, args=None, forward_args=None):
    """
    Run an action using its module path and a list of arguments

    If forward_args is given, it must be an argparse.Namespace object.
    This namespace will be merged with args before being
    passed to the do() method of module_name.

    """
    if not args:
        args = list()
    ui.debug("running", module_name, " ".join(args))
    action_name  = module_name.split(".")[-1]
    package_name = ".".join(module_name.split(".")[:-1])
    try:
        _tmp = __import__(package_name, globals(), locals(), [action_name])
    except ImportError, err:
        raise InvalidAction(module_name, str(err))
    try:
        module = getattr(_tmp, action_name)
    except AttributeError, err:
        raise InvalidAction(module_name, "Could not find module %s in package %s" %
            (module_name, package_name))
    check_module(module)
    parser = argparse.ArgumentParser()
    module.configure_parser(parser)
    # Quick hack to prevent argparse.parse_args to
    #  - print usage to the console
    #  - call SystemExit
    # Instead, raise a nice Exception
    def custom_exit():
        return
    parser.exit = custom_exit

    def error(message):
        mess  = "Invalid arguments when calling run_action(%s)\n" % module_name
        mess += message + "\n"
        mess += "args: %s\n" % " ".join(args)
        mess += "forward_args: %s\n" % forward_args
        raise Exception(mess)

    parser.error = error
    if forward_args:
        parsed_args = parser.parse_args(args=args, namespace=copy.deepcopy(forward_args))
    else:
        parsed_args = parser.parse_args(args=args)

    return module.do(parsed_args)


def main_wrapper(module, args):
    """This wraps the main method of an action so that:
       - backtrace is not printed by default
       - backtrace is printed is --backtrace was given
       - a pdb session is run if --pdb was given
    """
    try:
        module.do(args)
    except Exception as e:
        if args.pdb:
            traceback = sys.exc_info()[2]
            print ""
            print "### Exception:", e
            print "### Starting a debugger"
            try:
                #pylint: disable-msg=F0401
                import ipdb
                ipdb.post_mortem(traceback)
                sys.exit(0)
            except ImportError:
                import pdb
                pdb.post_mortem(traceback)
                sys.exit(0)
        if args.backtrace:
            raise
        message = str(e)
        if message.endswith("\n"):
            message = message[:-1]
        ui.error(e.__class__.__name__, message)
        sys.exit(2)

def _dump_arguments(name, args):
    """ Dump an argparser namespace to log """
    output = ""
    keys = args.__dict__.keys()
    keys.sort()
    max_len = max(len(k) for k in keys)
    keys.sort()
    for k in keys:
        value = args.__dict__[k]
        output += "  " + k.ljust(max_len) + " = %s\n" % (value,)
    if output[-1] == "\n":
        output = output[:-1]
    ui.debug("[%s] arguments:\n%s" % (name, output))

def root_command_main(name, parser, modules, args=None):
    """name : name of the main program
       parser : an instance of ArgumentParser class
       modules : list of Python modules

    """
    if not args:
        args = sys.argv[1:]
    subparsers = parser.add_subparsers(
        dest="action",
        title="actions")

    # A dict name -> python module for the the action
    action_modules = dict()

    for module in modules:
        try:
            check_module(module)
        except InvalidAction, err:
            print "Warning, skipping", module.__name__
            print err
            continue
        name = module.__name__.split(".")[-1]
        # we want to type `foo bar-baz', and not type `foo bar_baz',
        # even if "bar-baz" is not a valid module name.
        name = name.replace("_", "-")
        configurator = module.configure_parser
        first_doc_line = module.__doc__.splitlines()[0]
        action_parser = subparsers.add_parser(name, help=first_doc_line)
        configurator(action_parser)
        action_parser.formatter_class = argparse.RawDescriptionHelpFormatter

        doc_lines = module.__doc__.splitlines()
        epilog = "\n".join(doc_lines[1:])
        if epilog:
            action_parser.epilog = first_doc_line + "\n" + epilog

        action_modules[name] = module

    (help_requested, action) = parse_args_for_help(args)
    if help_requested:
        if not action:
            parser.print_help()
        else:
            if not action in action_modules:
                print "Invalid action!"
                print "Choose between: ", " ".join(action_modules.keys())
                print
                parser.print_help()
            else:
                parser.parse_args([action, "--help"])
        sys.exit(0)

    pargs = parser.parse_args(args)
    ui.configure_logging(pargs)
    module = action_modules[pargs.action]
    _dump_arguments(module.__name__, pargs)
    main_wrapper(module, pargs)
    return True


def check_module(module):
    """Check that a module really is an action.
    Raises InvalidAction error if not

    """
    if not hasattr(module, "do"):
        raise InvalidAction(module.__name__, "Could not find a do() method")
    if not hasattr(module, "configure_parser"):
        raise InvalidAction(module.__name__, "Could not find a configure_parser() method")
    if module.__doc__ is None:
        mess = """{module_name} has no doc string !
Please add something like:

    \"\"\" Short description of {module_name}

    A longer description here....

    \"\"\"

at the top of the file

"""
        mess = mess.format(module_path=module.__file__, module_name=module.__name__)
        raise InvalidAction(module.__name__, mess)



def action_modules_from_package(package_name):
    """Returns a suitable list of modules from
    a package.

    Example:
    assuming you have:
    actions/foo/__init__.py
    actions/foo/spam.py
    actions/foo/eggs.py

    then
    action_modules_from_package("actions.foo") returns:
    [actions.foo.spam, actions.foo.eggs]

    """
    res = list()
    splitted = package_name.split(".")[1:]
    last_part = ".".join(splitted)
    package = __import__(package_name, globals(), locals(), [last_part])
    base_path = os.path.dirname(package.__file__)
    module_paths = os.listdir(base_path)
    module_paths = [x[:-3] for x in module_paths if x.endswith(".py")]
    module_paths.remove("__init__")
    for module_path in module_paths:
        try:
            _tmp = __import__(package_name, globals(), locals(), [module_path], -1)
            module = getattr(_tmp, module_path)
            res.append(module)
        except ImportError, err:
            print "Skipping %s (%s)" % (module_path, err)
            continue

    res.sort(key=operator.attrgetter("__name__"))
    return res



if __name__ == "__main__":
    import doctest
    doctest.testmod()
