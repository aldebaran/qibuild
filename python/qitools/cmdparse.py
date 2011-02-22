## Copyright (C) 2011 Aldebaran Robotics

"""This handles dispacthing first arg to other actions

"""


import os
import sys
import logging

try:
    import argparse
except:
    from qitools.external import argparse

import qitools.command

class InvalidAction(Exception):
    """Just a custom exception """
    def __init__(self, name, message):
        self.name = name
        self.message = message

    def __str__(self):
        message = "Invalid action %s\n" % self.name
        message += self.message
        return message


def parse_args_for_help(args):
    """Parse a command line for help usage.

    Returns a tuple:
     - help has been requested
     - name of the action on which help has been requested
       (or None if there was not any)

    >>> parse_args_for_help("toc".split())
    (True, None)
    >>> parse_args_for_help("toc foo".split())
    (False, None)
    >>> parse_args_for_help("toc help".split())
    (True, None)
    >>> parse_args_for_help("toc help foo".split())
    (True, 'foo')
    >>> parse_args_for_help("toc foo --help".split())
    (True, 'foo')
    >>> parse_args_for_help("toc foo -h".split())
    (True, 'foo')
    >>> parse_args_for_help("toc -h foo".split())
    (True, 'foo')
    """
    def is_help(arg):
        return arg in ("-h", "--help", "help")

    if len(args) == 1:
        return (True, None)
    if len(args) > 3:
        return (False, None)

    if len(args) == 2:
        if is_help(args[1]):
            return (True, None)
        else:
            return(False, None)

    if len(args) == 3:
        if is_help(args[1]):
            return (True, args[2])
        if is_help(args[2]):
            return (True, args[1])
        return(False, None)


def run_action(module_name, arguments=None, forward_args=None):
    """Run an action using its module path and a list of arguments
    (if not given, action will be called with not arguments)

    """
    if not arguments:
        arguments = list()
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
    sub_command_main(module, arguments, forward_args)


def main_wrapper(module, args):
    """This wraps the main method of an action so that:
       - backtrace is not printed by default
       - backtrace is printed is --backtrace is given
       - pdb is started if --pdb is given
    """
    try:
        module.do(args)
    except Exception as e:
        if args.pdb:
            print ""
            print "### Exception:", e
            print "### Starting a debugger"
            import pdb
            traceback = sys.exc_info()[2]
            pdb.post_mortem(traceback)
        if args.backtrace:
            raise
        logger = logging.getLogger("\n") # small hack
        logger.error(str(e))
        sys.exit(2)

def _dump_arguments(name, args):
    """ dump an argparser namespace to log """
    output = ""
    max_len = 0
    for k in args.__dict__.keys():
        if len(k) > max_len:
            max_len = len(k)
    for k,v in args.__dict__.iteritems():
        pad = "".join([ " " for x in range(max_len - len(k)) ])
        output += "  %s%s = %s\n" % (str(k), pad, str(v))
    if output[-1] == "\n":
        output = output[:-1]
    logger = logging.getLogger("qitools.cmdparse")
    logger.debug("[%s] arguments:\n%s", name, output)

def root_command_main(name, parser, modules):
    """name : name of the main program
       parser : an instance of ArgumentParser class
       modules : list of Python modules

    """
    subparsers = parser.add_subparsers(help="action", dest="action")

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
        configurator = module.configure_parser
        action_parser = subparsers.add_parser(name, help=module.__doc__)
        configurator(action_parser)
        action_modules[name] = module

    (help_requested, action) = parse_args_for_help(sys.argv)
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

    args = parser.parse_args()
    qitools.log.configure_logging(args)
    module = action_modules[args.action]
    _dump_arguments(name, args)
    main_wrapper(module, args)

def sub_command_main(module, args=None, namespace=None):
    """This is called in two different cases:

    - In the "if __name__ == "__main__" part
      of the subcommands (when args and namespace are None)

    - By a run_action from another action, where args are the arguments
      of the new action, and namespace is the caller's namespace

    """
    check_module(module)
    try:
        usage = module.usage()
    except AttributeError:
        usage = None
    parser = argparse.ArgumentParser(usage=usage)
    module.configure_parser(parser)
    parsed_args = parser.parse_args(args=args, namespace=namespace)
    qitools.log.configure_logging(parsed_args)
    main_wrapper(module, parsed_args)


def check_module(module):
    """Check that a module really is an action.
    Raises InvalidAction error if not

    """
    if not hasattr(module, "do"):
        raise InvalidAction(module.__name__, "Could not find a do() method")
    if not hasattr(module, "configure_parser"):
        raise InvalidAction(module.__name__, "Could not find a configure_parser() method")



def action_modules_from_package(package_name):
    """Returns a suitable list of modules from
    a package.

    Example:
    assuming you have:
    actions/foo/__init__.py
    actions/foo/spam.py  (containing an ACTION gloval var)
    actions/foo/eggs.py  (containing an ACTION global var)

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

    return res

def log_parser(parser):
    """ Given a parser, add the options controling log
    """
    group = parser.add_argument_group("logging arguments")
    group.add_argument("-v", "--verbose", dest="verbose", action="store_true", help="Output debug messages")
    group.add_argument("--quiet", "-q", dest="quiet", action="store_true", help="Only output error messages")
    group.add_argument("--no-color", dest="color", action="store_false", help="Do not use color")
    parser.set_defaults(verbose=False, quiet=False, color=True)

def default_parser(parser):
    """ Parser settings for every action
    """
    # Every action should have access to a proper log
    log_parser(parser)
    # Every action can use  --pdb and --backtrace
    group = parser.add_argument_group("debug arguments")
    group.add_argument("--backtrace", action="store_true", help="Display backtrace on error")
    group.add_argument("--pdb", action="store_true", help="Use pdb on error")

if __name__ == "__main__":
    import doctest
    doctest.testmod()
