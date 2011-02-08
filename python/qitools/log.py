## Copyright (C) 2011 Aldebaran Robotics
"""Few useful functions for loggging

"""

import sys
import logging
ON_WIN = sys.platform.startswith("win")

# Try using pyreadline so that we can
# have colors on windows, too.
HAS_PYREADLINE = True
if ON_WIN:
    try:
        from pyreadline.console import Console
    except ImportError:
        HAS_PYREADLINE = False

# Ansi colors: feel free to add stuff here:
COLORS = {
    "bold"    :  "\033[1m"  ,
    "clear"   :  "\033[0m"  ,
    "red"     :  "\033[31m" ,
    "green"   :  "\033[32m" ,
    "blue"    :  "\033[34m" ,
}

if ON_WIN and not HAS_PYREADLINE:
    # simpy remove escape chars
    for k in COLORS.iterkeys():
        COLORS[k] = ""

class ColorLogHandler(logging.StreamHandler):
    """A class that outputs nice colored messages

    """
    # Warning:
    # Most of the code from logging's formatters is re-written in
    # ColorHandler.emit(), so using setFormatter would
    # have no effect on color logger...
    def __init__(self):
        logging.StreamHandler.__init__(self)
        if ON_WIN and HAS_PYREADLINE:
            self.console = Console()
        # Avoid printing colors if not a tty:
        if not sys.stdout.isatty():
            for k in COLORS.keys():
                COLORS[k] = "";
            self.console = None

    def emit(self, record):
        """Override StreamHandler.emit method

        """
        name  = record.name
        level = record.levelname
        mess  = record.msg % record.args
        res   = COLORS["bold"]
        if record.levelno   == logging.DEBUG:
            res += COLORS["blue"]
        elif record.levelno == logging.INFO:
            res += COLORS["green"]
        elif record.levelno >= logging.WARNING:
            res += COLORS["red"]
        level = "[%s]" % level

        if record.levelno != logging.INFO:
            res += "%-12s"  % level
            res += "%-12s " % name
        res += mess
        res += COLORS["clear"]
        res += "\n"
        if ON_WIN and HAS_PYREADLINE:
            if self.console is not None:
                self.console.write_color(res)
            else:
                sys.stdout.write(res)
        else:
            if record.levelno < logging.WARNING:
                sys.stdout.write(res)
            else:
                sys.stderr.write(res)



def configure_logging(args):
    """Configure logging globally """
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    handler = None
    if args.color:
        handler = ColorLogHandler()
    else:
        handler = logging.StreamHandler()

    if args.verbose:
        handler.setLevel(logging.DEBUG)
    elif args.quiet:
        handler.setLevel(level=logging.ERROR)
    else:
        handler.setLevel(level=logging.INFO)

    root_logger.handlers = list()
    root_logger.addHandler(handler)
