## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.


# Colorized output to console code inspired by
# pygments (http://pygments.org/) BSD License.

""" Tools for a nice user interface

"""

import sys

ON_WIN = sys.platform.startswith("win")

# Try using pyreadline so that we can
# have colors on windows, too.
_console = None
HAS_PYREADLINE = True
if ON_WIN:
    try:
        # pylint: disable-msg=F0401
        from pyreadline.console import Console
        _console = Console()
    except ImportError:
        HAS_PYREADLINE = False

# ANSI color codes, as classes,
# so that we can use ::
#
#  qibuild.ui.msg("qibuild.ui.bold, "This is bold", qibuild.ui.reset)`
class _Color:
    def __init__(self, code):
        self.code = code

_esc = "\033["

reset     = _Color(_esc + "39;49;00m")
bold      = _Color(_esc + "1m")
faint     = _Color(_esc + "2m")
standout  = _Color(_esc + "3m")
underline = _Color(_esc + "4m")
blink     = _Color(_esc + "5m")
overline  = _Color(_esc + "6m")

black      = _Color(_esc + "30m")
darkred    = _Color(_esc + "31m")
darkgreen  = _Color(_esc + "32m")
brown      = _Color(_esc + "33m")
darkblue   = _Color(_esc + "34m")
purple     = _Color(_esc + "35m")
teal       = _Color(_esc + "36m")
lightgray  = _Color(_esc + "37m")

darkgray   = _Color(_esc + "30;1m")
red        = _Color(_esc + "31;1m")
green      = _Color(_esc + "32;1m")
yellow     = _Color(_esc + "33;1m")
blue       = _Color(_esc + "34;1m")
fuchsia    = _Color(_esc + "35;1m")
turquoise  = _Color(_esc + "36;1m")
white      = _Color(_esc + "37;1m")

darkteal   = turquoise
darkyellow = brown
fuscia     = fuchsia


# Global variable to store qibuild.ui configuration

CONFIG = {
    "verbose" : False,
    "quiet" : False,
    "color" : True,
}



def _msg(*tokens, **kwargs):
    """ Helper method for error, warning, info, debug

    """
    fp = kwargs.get("fp", sys.stdout)
    sep = kwargs.get("sep", " ")
    end = kwargs.get("end", "\n")
    with_color = CONFIG["color"]
    if ON_WIN and not HAS_PYREADLINE or not fp.isatty():
        with_color = False
    res = ""
    for i, token in enumerate(tokens):
        if not token:
            continue
        if isinstance(token, _Color):
            if with_color:
                res += token.code
        else:
            res += token
            res += sep
    # always reset:
    if with_color:
        res += reset.code
    res += end
    if _console:
        _console.write_color(res)
    else:
        fp.write(res)
        fp.flush()

def error(*tokens):
    """ Print an error message """
    tokens = [bold, red, "[ERROR]: "] + list(tokens)
    _msg(*tokens, fp=sys.stderr)

def warning(*tokens):
    """ Print a warning message """
    tokens = [brown, "[WARN ]: "] + list(tokens)
    _msg(*tokens, fp=sys.stdout)

def info(*tokens):
    """ Print an informative message """
    if CONFIG["quiet"]:
        return
    _msg(*tokens, fp=sys.stdout)

def debug(*tokens):
    """ Print a debug message """
    if not CONFIG["verbose"]:
        return
    tokens = [blue, "[DEBUG]: "] + list(tokens)
    _msg(*tokens, fp=sys.stdout)
