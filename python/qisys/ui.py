## Copyright (c) 2012-2014 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.


# Colorized output to console code inspired by
# pygments (http://pygments.org/) BSD License.

""" Tools for a nice user interface

"""

import sys
import os
import datetime
import functools

# Try using pyreadline so that we can
# have colors on windows, too.
_console = None
HAS_PYREADLINE = True
if os.name == 'nt':
    try:
        # pylint: disable-msg=F0401
        from pyreadline.console import Console
        _console = Console()
    except:
        HAS_PYREADLINE = False

# ANSI color codes, as classes,
# so that we can use ::
#
#  qisys.ui.msg(qisys.ui.bold, "This is bold", qisys.ui.reset)


class _Color:
    def __init__(self, code, modifier=None):
        self.code = '\033[%d' % code
        if modifier is not None:
            self.code += ';%dm' % modifier
        else:
            self.code += 'm'

reset     = _Color(0)
bold      = _Color(1)
faint     = _Color(2)
standout  = _Color(3)
underline = _Color(4)
blink     = _Color(5)
overline  = _Color(6)

black      = _Color(30)
darkred    = _Color(31)
darkgreen  = _Color(32)
brown      = _Color(33)
darkblue   = _Color(34)
purple     = _Color(35)
teal       = _Color(36)
lightgray  = _Color(37)

darkgray   = _Color(30, 1)
red        = _Color(31, 1)
green      = _Color(32, 1)
yellow     = _Color(33, 1)
blue       = _Color(34, 1)
fuchsia    = _Color(35, 1)
turquoise  = _Color(36, 1)
white      = _Color(37, 1)

darkteal   = turquoise
darkyellow = brown
fuscia     = fuchsia


# Global variable to store qisys.ui configuration
# Useful settings when running qibuild on a buildfarm:
#    CONFIG['timestamps'] = True
#    CONFIG['interative'] = False


CONFIG = {
    "verbose": os.environ.get("VERBOSE"),
    "quiet": False,
    "color": "auto",
    "timestamp": False,
    "interactive": True,
    "record": False  # used for testing
}


# used for testing
_MESSAGES = list()

def configure_logging(args):
    verbose = os.environ.get("VERBOSE", False)
    if not verbose:
        verbose = args.verbose
    CONFIG["color"] = args.color
    CONFIG["verbose"] = verbose
    CONFIG["quiet"] = args.quiet
    CONFIG["timestamp"] = args.timestamp


def config_color(fp):
    config_color = CONFIG["color"]
    if config_color.lower() == "never":
        return False
    if config_color.lower() == "always":
        return True
    # else: auto
    if os.name == 'nt' and not HAS_PYREADLINE or not fp.isatty():
        return False
    else:
        return True

_enable_xterm_title = None

def update_title(mystr, fp):
    global _enable_xterm_title
    if _enable_xterm_title is None:
        legal_terms = ["xterm", "xterm-color", "Eterm", "aterm", "rxvt",
                "screen", "kterm", "rxvt-unicode", "gnome", "interix"]
        # assume that if we want color, we are in a terminal and we also want
        # title
        _enable_xterm_title = config_color(fp) and \
            'TERM' in os.environ and \
            os.environ['TERM'] in legal_terms

    if _enable_xterm_title:
        mystr = '\x1b]0;%s\x07' % mystr

        fp.write(mystr)
        fp.flush()

def _msg(*tokens, **kwargs):
    """ Helper method for error, warning, info, debug

    """
    if CONFIG["record"]:
        CONFIG["color"] = "never"
    fp = kwargs.get("fp", sys.stdout)
    sep = kwargs.get("sep", " ")
    end = kwargs.get("end", "\n")
    with_color = config_color(fp)
    res = list()  # Initialize result list, to be concatenated before printing
    nocolorres = list()  # result list without colors
    if CONFIG["timestamp"]:
        now = datetime.datetime.now()
        res.append(now.strftime("[%Y-%m-%d %H:%M:%S] "))
    for token in tokens:
        if isinstance(token, _Color):
            if with_color:
                res.append(token.code)
        else:
            if sep == " " and token == "\n":
                res.append("\n")
                nocolorres.append("\n")
            else:
                res.append(str(token))
                res.append(sep)
                nocolorres.append(str(token))
                nocolorres.append(sep)
    # always reset:
    if with_color:
        res.append(reset.code)
    res.append(end)
    stringres = ''.join(res)
    stringnc = ''.join(nocolorres)
    if CONFIG["record"]:
        _MESSAGES.append(stringres)
    if _console and with_color:
        _console.write_color(stringres)
    else:
        fp.write(stringres)
        fp.flush()
    if kwargs.get("update_title", False):
        update_title(stringnc, fp)

def error(*tokens, **kwargs):
    """ Print an error message """
    tokens = [bold, red, "[ERROR]: "] + list(tokens)
    kwargs["fp"] = sys.stderr
    _msg(*tokens, **kwargs)

def warning(*tokens, **kwargs):
    """ Print a warning message """
    tokens = [brown, "[WARN ]: "] + list(tokens)
    kwargs["fp"] = sys.stderr
    _msg(*tokens, **kwargs)

def info(*tokens, **kwargs):
    """ Print an informative message """
    if CONFIG["quiet"]:
        return
    _msg(*tokens, **kwargs)

def info_count(i, n, *rest, **kwargs):
    """ Same as info, but displays a nice counter
    color will be reset
    >>> count(0, 4)
    * (1/5)
    >>> count(4, 12)
    * ( 4/12)
    >>> count(4, 10)
    * (10/12)

    """
    num_digits = len(str(n)) # lame, I know
    counter_format = "(%{}d/%d)".format(num_digits)
    counter_str = counter_format % (i+1, n)
    info(green, "*", reset, counter_str, reset, *rest, **kwargs)

def debug(*tokens, **kwargs):
    """ Print a debug message """
    if not CONFIG["verbose"] or CONFIG["record"]:
        return
    tokens = [blue, "[DEBUG]: "] + list(tokens)
    _msg(*tokens, **kwargs)

def indent_iterable(elems, num=2):
    """Indent an iterable."""
    return [" " * num + l for l in elems]

def indent(text, num=2):
    """Indent a piece of text."""
    lines = text.splitlines()
    return '\n'.join(indent_iterable(lines, num=num))

def tabs(num):
    """ Compute a blank tab """
    return "  " * num

class timer:
    """ To be used as a decorator,
    or as a with statement:

    >>> @timer("something")
        def do_something():
            foo()
            bar()
    # Or:
    >>> with timer("something")
        foo()
        bar()

    This will print:
    'something took 2h 33m 42s'

    """
    def __init__(self, description):
        self.description = description
        self.start_time = None
        self.stop_time = None
        self.elapsed_time = None

    def __call__(self, func, *args, **kwargs):
        @functools.wraps(func)
        def res(*args, **kwargs):
            self.start()
            ret = func(*args, **kwargs)
            self.stop()
            return ret
        return res

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, *unused):
        self.stop()

    def start(self):
        """ Start the timer """
        self.start_time = datetime.datetime.now()

    def stop(self):
        """ Stop the timer and emit a nice log """
        end_time = datetime.datetime.now()
        elapsed_time = end_time - self.start_time
        elapsed_seconds = elapsed_time.seconds
        hours, remainder = divmod(int(elapsed_seconds), 3600)
        minutes, seconds = divmod(remainder, 60)
        as_str = "%sh %sm %ss %dms" % (hours, minutes, seconds, elapsed_time.microseconds / 1000)
        if CONFIG['timestamp']:
            info("%s took %s" % (self.description, as_str))
