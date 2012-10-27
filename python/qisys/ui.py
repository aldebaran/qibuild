## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.


# Colorized output to console code inspired by
# pygments (http://pygments.org/) BSD License.

""" Tools for a nice user interface

"""

import sys
import os
import datetime

# Try using pyreadline so that we can
# have colors on windows, too.
_console = None
HAS_PYREADLINE = True
if os.name == 'nt':
    try:
        # pylint: disable-msg=F0401
        from pyreadline.console import Console
        _console = Console()
    except ImportError:
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
    "verbose" : False,
    "quiet" : False,
    "color" : True,
    "timestamp" : False,
    "interactive" : True,
}



def _msg(*tokens, **kwargs):
    """ Helper method for error, warning, info, debug

    """
    fp = kwargs.get("fp", sys.stdout)
    sep = kwargs.get("sep", " ")
    end = kwargs.get("end", "\n")
    with_color = CONFIG["color"]
    if os.name == 'nt' and not HAS_PYREADLINE or not fp.isatty():
        with_color = False
    if CONFIG["timestamp"]:
        now = datetime.datetime.now()
        res = now.strftime("[%Y-%m-%d %H:%M:%S] ")
    else:
        res = ""
    for i, token in enumerate(tokens):
        if not token:
            continue
        if isinstance(token, _Color):
            if with_color:
                res += token.code
        else:
            if sep == " " and token == "\n":
                res += "\n"
            else:
                res += str(token)
                res += sep
    # always reset:
    if with_color:
        res += reset.code
    res += end
    if _console and with_color:
        _console.write_color(res)
    else:
        fp.write(res)
        fp.flush()

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

def debug(*tokens, **kwargs):
    """ Print a debug message """
    if not CONFIG["verbose"]:
        return
    tokens = [blue, "[DEBUG]: "] + list(tokens)
    _msg(*tokens, **kwargs)
