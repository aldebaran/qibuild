## Copyright (c) 2012-2016 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.


# Colorized output to console code inspired by
# pygments (http://pygments.org/) BSD License.

""" Tools for a nice user interface

"""

import sys
import os
import datetime
import difflib
import functools
import traceback
from StringIO import StringIO

import qisys.error

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
    "title": "auto",
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
    CONFIG["title"] = args.title
    CONFIG["verbose"] = verbose
    CONFIG["quiet"] = args.quiet
    CONFIG["timestamp"] = args.timestamp


def config_title(fp):
    config_title = CONFIG["title"]
    if config_title.lower() == "never":
        return False
    if config_title.lower() == "always":
        return True
    if os.name == 'nt':
        return fp.isatty() and _console is not None
    else:
        # else: auto
        legal_terms = ["xterm", "xterm-256color", "xterm-color",
                       "Eterm", "aterm", "rxvt", "screen", "kterm",
                       "rxvt-unicode", "gnome", "interix", "cygwin",
                       "rxvt-unicode-256color"]
        return fp.isatty() and \
            'TERM' in os.environ and \
            os.environ['TERM'] in legal_terms


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
    if os.name == "nt":
        _update_title_windows(mystr)
    else:
        _update_title_unix(mystr, fp)

def _update_title_unix(mystr, fp):
    global _enable_xterm_title
    if _enable_xterm_title is None:
        _enable_xterm_title = config_title(fp)

    if _enable_xterm_title:
        mystr = '\x1b]0;%s\x07' % mystr
        fp.write(mystr)
        fp.flush()

def _update_title_windows(mystr):
    if _console and config_title(sys.stdout):
        _console.title(txt=mystr)

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
    for i, token in enumerate(tokens):
        should_add_sep = True
        if isinstance(token, _Color):
            if with_color:
                res.append(token.code)
        else:
            if sep == " " and str(token).endswith("\n"):
                res.append(str(token))
                nocolorres.append(str(token))
                should_add_sep = False
            else:
                res.append(str(token))
                if i != len(tokens) - 1 and should_add_sep:
                    res.append(sep)
                nocolorres.append(str(token))
                if i != len(tokens) - 1 and should_add_sep:
                    nocolorres.append(sep)
                should_add_sep = True
    # always reset:
    if with_color:
        res.append(reset.code)
    res.append(end)
    stringres = ''.join(res)
    stringnc = ''.join(nocolorres)
    if CONFIG["record"]:
        _MESSAGES.append(stringres)
    if kwargs.get("update_title", False):
        update_title(stringnc, fp)
    if _console and with_color:
        _console.write_color(stringres)
    else:
        fp.write(stringres)
        fp.flush()

def fatal(*tokens, **kwargs):
    """ Print an error message and calls sys.exit """
    error(*tokens, **kwargs)
    sys.exit(1)

def error(*tokens, **kwargs):
    """ Print an error message """
    tokens = [bold, red, "[ERROR]:"] + list(tokens)
    kwargs["fp"] = sys.stderr
    _msg(*tokens, **kwargs)

def warning(*tokens, **kwargs):
    """ Print a warning message """
    tokens = [brown, "[WARN ]:"] + list(tokens)
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
    >>> info_count(0, 4)
    * (1/4)
    >>> info_count(4, 12)
    * ( 5/12)
    >>> info_count(4, 10)
    * ( 5/10)

    """
    num_digits = len(str(n)) # lame, I know
    counter_format = "(%{}d/%d)".format(num_digits)
    counter_str = counter_format % (i+1, n)
    info(green, "*", reset, counter_str, reset, *rest, **kwargs)

def info_progress(value, max_value, prefix):
    """ Display info progress in percent
    :param: value the current value
    :param: max_value the max value
    :param: prefix the prefix message to print

    >>> info_progress(5, 20, "Done")
    Done: 25%

    """
    if sys.stdout.isatty():
        percent = float(value) / max_value * 100
        sys.stdout.write(prefix + ": %.0f%%\r" % percent)
        sys.stdout.flush()

def debug(*tokens, **kwargs):
    """ Print a debug message """
    if not CONFIG["verbose"] or CONFIG["record"]:
        return
    tokens = [blue, "[DEBUG]:"] + list(tokens)
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

def message_for_exception(exception, message):
    """ Returns a tuple suitable for ui.error()
    from the given exception.
    (Traceback will be part of the message, after
    the ``message`` argument)

    Useful when the exception occurs in an other thread
    than the main one.

    """
    tb = sys.exc_info()[2]
    io = StringIO()
    traceback.print_tb(tb, file=io)
    return (red, message + "\n",
            exception.__class__.__name__,
            str(exception), "\n",
            reset,
            io.getvalue())

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

def did_you_mean(message, user_input, choices):
    if not choices:
        return message
    else:
        result = {difflib.SequenceMatcher(a=user_input, b=choice).ratio(): choice \
                  for choice in choices}
        message += "\nDid you mean: %s?" % result[max(result)]
        return message


# Console size code inspired by: http://pastebin.com/rJqMVnZJ
def get_console_size():
    """ Return a tuple containing the current console size: (width, height) """
    import platform
    current_os = platform.system()
    tuple_xy=None
    if current_os == "Windows":
        tuple_xy = _get_console_size_windows()
        if tuple_xy is None:
            tuple_xy = _get_console_size_tput()
            # needed for window's python in cygwin's xterm!
    if current_os in ["Linux", "Darwin"] or current_os.startswith("CYGWIN"):
        tuple_xy = _get_console_size_linux()
    if tuple_xy is None:
        tuple_xy = (80, 25)      # default value
    return tuple_xy

def _get_console_size_windows():
    res=None
    try:
        from ctypes import windll, create_string_buffer

        # stdin handle is -10
        # stdout handle is -11
        # stderr handle is -12

        h = windll.kernel32.GetStdHandle(-12)
        csbi = create_string_buffer(22)
        res = windll.kernel32.GetConsoleScreenBufferInfo(h, csbi)
    except:
        return None
    if res:
        import struct
        (bufx, bufy, curx, cury, wattr,
            left, top, right, bottom, maxx, maxy) = struct.unpack("hhhhHhhhhhh", csbi.raw)
        sizex = right - left + 1
        sizey = bottom - top + 1
        return sizex, sizey
    else:
        return None

def _get_console_size_tput():
    # get terminal width
    # src: http://stackoverflow.com/questions/263890/how-do-i-find-the-width-height-of-a-terminal-window
    try:
        import subprocess
        proc=subprocess.Popen(["tput", "cols"],stdin=subprocess.PIPE,stdout=subprocess.PIPE)
        output=proc.communicate(input=None)
        cols=int(output[0])
        proc=subprocess.Popen(["tput", "lines"],stdin=subprocess.PIPE,stdout=subprocess.PIPE)
        output=proc.communicate(input=None)
        rows=int(output[0])
        return (cols,rows)
    except:
        return None

def _get_console_size_linux():
    def ioctl_GWINSZ(fd):
        try:
            import fcntl, termios, struct, os
            cr = struct.unpack('hh', fcntl.ioctl(fd, termios.TIOCGWINSZ,'1234'))
        except:
            return None
        return cr
    cr = ioctl_GWINSZ(0) or ioctl_GWINSZ(1) or ioctl_GWINSZ(2)
    if not cr:
        try:
            fd = os.open(os.ctermid(), os.O_RDONLY)
            cr = ioctl_GWINSZ(fd)
            os.close(fd)
        except:
            pass
    if not cr:
        try:
            cr = (os.environ['LINES'], os.environ['COLUMNS'])
        except:
            return None
    return int(cr[1]), int(cr[0])

def valid_filename(value):
    """ Validate that the string passed as input can safely
    be used as a valid file name

    """
    if value in [".", ".."]:
        raise qisys.error.Error("Invalid name: %s" % value)

    # this is for Windows, but it does not hurt on other platforms
    bad_chars = r'<>:"/\|?*'
    for bad_char in bad_chars:
        if bad_char in value:
            mess  = "Invalid name: '%s'\n" % value
            mess += "A valid name should not contain any "
            mess += "of the following chars:\n"
            mess += " ".join(bad_chars)
            raise qisys.error.Error(mess)
    return value
