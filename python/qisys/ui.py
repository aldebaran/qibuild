#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2020 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
"""
Tools for a nice user interface
Colorized output to console code inspired by
pygments (http://pygments.org/) BSD License.
"""
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import os
import sys
import struct
import difflib
import platform
import datetime
import functools
import traceback
import six

# Try using pyreadline so that we can
# have colors on windows, too.
_console = None
HAS_PYREADLINE = True
if os.name == 'nt':
    try:
        from pyreadline.console import Console
        _console = Console()
    except Exception:
        HAS_PYREADLINE = False


# ANSI color codes, as classes,
# so that we can use ::
#  qisys.ui.msg(qisys.ui.bold, "This is bold", qisys.ui.reset)
class _Color(object):
    """ _Color Class """

    def __init__(self, code, modifier=None):
        """ _Color Init """
        self.code = '\033[%d' % code
        if modifier is not None:
            self.code += ';%dm' % modifier
        else:
            self.code += 'm'


reset = _Color(0)
bold = _Color(1)
faint = _Color(2)
standout = _Color(3)
underline = _Color(4)
blink = _Color(5)
overline = _Color(6)

black = _Color(30)
darkred = _Color(31)
darkgreen = _Color(32)
brown = _Color(33)
darkblue = _Color(34)
purple = _Color(35)
teal = _Color(36)
lightgray = _Color(37)
darkgray = _Color(30, 1)
red = _Color(31, 1)
green = _Color(32, 1)
yellow = _Color(33, 1)
blue = _Color(34, 1)
fuchsia = _Color(35, 1)
turquoise = _Color(36, 1)
white = _Color(37, 1)
darkteal = turquoise
darkyellow = brown
fuscia = fuchsia

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
    """ Configure Logging """
    verbose = os.environ.get("VERBOSE", False)
    if not verbose:
        verbose = args.verbose
    CONFIG["color"] = args.color
    CONFIG["title"] = args.title
    CONFIG["verbose"] = verbose
    CONFIG["quiet"] = args.quiet
    CONFIG["timestamp"] = args.timestamp


def config_title(fp):
    """ Config Title """
    _config_title = CONFIG["title"]
    if _config_title.lower() == "never":
        return False
    if _config_title.lower() == "always":
        return True
    if os.name == 'nt':
        return fp.isatty() and _console is not None
    # else: auto
    legal_terms = ["xterm", "xterm-256color", "xterm-color",
                   "Eterm", "aterm", "rxvt", "screen", "kterm",
                   "rxvt-unicode", "gnome", "interix", "cygwin",
                   "rxvt-unicode-256color"]
    return fp.isatty() and \
        'TERM' in os.environ and \
        os.environ['TERM'] in legal_terms


def config_color(fp):
    """ Config Color """
    _config_color = CONFIG["color"]
    if _config_color.lower() == "never":
        return False
    if _config_color.lower() == "always":
        return True
    # else: auto
    if os.name == 'nt' and not HAS_PYREADLINE or not fp.isatty():
        return False
    return True


_enable_xterm_title = None


def update_title(mystr, fp):
    """ Update Title """
    if os.name == "nt":
        _update_title_windows(mystr)
    else:
        _update_title_unix(mystr, fp)


def _update_title_unix(mystr, fp):
    """ Update Title Unix """
    # This module should be refactored into object to avoid the anti-pattern global statement
    global _enable_xterm_title
    if _enable_xterm_title is None:
        _enable_xterm_title = config_title(fp)
    if _enable_xterm_title:
        mystr = '\x1b]0;%s\x07' % mystr
        fp.write(mystr)
        fp.flush()


def _update_title_windows(mystr):
    """ Update Title Windows """
    if _console and config_title(sys.stdout):
        _console.title(txt=mystr)


def _unicode_representation(data):
    """ Return an unicode representation of a data """
    if isinstance(data, six.string_types):
        return "'" + data + "'"
    elif isinstance(data, tuple):
        unicode_data = "("
        for value in data:
            if unicode_data != "(":
                unicode_data += ", "
            unicode_data += _unicode_representation(value)
        unicode_data += ")"
        return unicode_data
    elif isinstance(data, list):
        unicode_data = "["
        for value in data:
            if unicode_data != "[":
                unicode_data += ", "
            unicode_data += _unicode_representation(value)
        unicode_data += "]"
        return unicode_data
    if six.PY3:
        return str(data).encode("utf-8")
    return unicode(data)


def _msg(*tokens, **kwargs):
    """ Helper method for error, warning, info, debug """
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
    should_add_sep = True
    for i, token in enumerate(tokens):
        if isinstance(token, _Color):
            if with_color:
                res.append(token.code)
        else:
            if six.PY2:
                if isinstance(token, unicode):
                    token_string = token
                elif isinstance(token, str):
                    try:
                        token_string = token.decode("utf-8")
                    except Exception:
                        token_string = token
                else:
                    token_string = _unicode_representation(token)
            else:
                token_string = str(token)
            if sep == " " and token_string.endswith("\n"):
                res.append(token_string)
                nocolorres.append(token_string)
                should_add_sep = False
            else:
                res.append(token_string)
                if i != len(tokens) - 1 and should_add_sep:
                    res.append(sep)
                nocolorres.append(token_string)
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
        try:
            fp.write(stringres.encode("utf-8"))
        except Exception:
            fp.write(stringres)
        fp.flush()


def error(*tokens, **kwargs):
    """ Print an error message """
    tokens = [bold, red, "[ERROR]:"] + list(tokens)
    kwargs["fp"] = sys.stderr
    _msg(*tokens, **kwargs)
    traceback.print_exc()


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
    """
    Same as info, but displays a nice counter color will be reset
    >>> info_count(0, 4)
    * (1/4)
    >>> info_count(4, 12)
    * ( 5/12)
    >>> info_count(4, 10)
    * ( 5/10)
    """
    num_digits = len(str(n))  # lame, I know
    counter_format = "(%{}d/%d)".format(num_digits)
    counter_str = counter_format % (i+1, n)
    info(green, "*", reset, counter_str, reset, *rest, **kwargs)


def info_progress(value, max_value, prefix):
    """
    Display info progress in percent
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
    """ Indent an iterable. """
    return [" " * num + elem for elem in elems]


def indent(text, num=2):
    """ Indent a piece of text. """
    lines = text.splitlines()
    return '\n'.join(indent_iterable(lines, num=num))


def tabs(num):
    """ Compute a blank tab """
    return "  " * num


class timer(object):
    """
    To be used as a decorator, or as a with statement:
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
        """ timer Init """
        self.description = description
        self.start_time = None
        self.stop_time = None
        self.elapsed_time = None

    def __call__(self, func, *args, **kwargs):
        """ Call """
        @functools.wraps(func)
        def res(*args, **kwargs):
            """ Return Result with Time Calculation """
            self.start()
            ret = func(*args, **kwargs)
            self.stop()
            return ret
        return res

    def __enter__(self):
        """ Enter """
        self.start()
        return self

    def __exit__(self, *unused):
        """ Exit """
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
    """ Proposition for Typing Errors """
    if not choices:
        return message
    result = {difflib.SequenceMatcher(a=user_input, b=choice).ratio(): choice
              for choice in choices}
    message += "\nDid you mean: %s?" % result[max(result)]
    return message


def get_console_size():
    """
    Return a tuple containing the current console size: (width, height)
    Console size code inspired by: http://pastebin.com/rJqMVnZJ
    """
    current_os = platform.system()
    tuple_xy = None
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
    """ Get Console Size Windows """
    try:
        from ctypes import windll, create_string_buffer
        # stdin handle is -10
        # stdout handle is -11
        # stderr handle is -12
        h = windll.kernel32.GetStdHandle(-12)
        csbi = create_string_buffer(22)
        res = windll.kernel32.GetConsoleScreenBufferInfo(h, csbi)
    except Exception:
        return None
    if res:
        (__bufx, __bufy, __curx, __cury, __wattr,
         left, top, right, bottom, __maxx, __maxy) = struct.unpack("hhhhHhhhhhh", csbi.raw)
        sizex = right - left + 1
        sizey = bottom - top + 1
        return sizex, sizey
    return None


def _get_console_size_tput():
    """
    Get Console Size
    http://stackoverflow.com/questions/263890/how-do-i-find-the-width-height-of-a-terminal-window
    """
    try:
        import subprocess
        proc = subprocess.Popen(["tput", "cols"], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        output = proc.communicate(input=None)
        cols = int(output[0])
        proc = subprocess.Popen(["tput", "lines"], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        output = proc.communicate(input=None)
        rows = int(output[0])
        return cols, rows
    except Exception:
        return None


def _get_console_size_linux():
    """ Get Console Size Linux """
    def ioctl_GWINSZ(fd):
        """ IO Ctl GWinsZ """
        try:
            import fcntl
            import termios
            cr = struct.unpack('hh', fcntl.ioctl(fd, termios.TIOCGWINSZ, '1234'))
        except Exception:
            return None
        return cr
    cr = ioctl_GWINSZ(0) or ioctl_GWINSZ(1) or ioctl_GWINSZ(2)
    if not cr:
        try:
            fd = os.open(os.ctermid(), os.O_RDONLY)  # pylint:disable=no-member
            cr = ioctl_GWINSZ(fd)
            os.close(fd)
        except Exception:
            pass
    if not cr:
        try:
            cr = (os.environ['LINES'], os.environ['COLUMNS'])
        except Exception:
            return None
    return int(cr[1]), int(cr[0])


def valid_filename(value):
    """ Validate that the string passed as input can safely be used as a valid file name """
    if value in [".", ".."]:
        raise Exception("Invalid name: %s" % value)
    # this is for Windows, but it does not hurt on other platforms
    bad_chars = r'<>:"/\|?*'
    for bad_char in bad_chars:
        if bad_char in value:
            mess = "Invalid name: '%s'\n" % value
            mess += "A valid name should not contain any "
            mess += "of the following chars:\n"
            mess += " ".join(bad_chars)
            raise Exception(mess)
    return value
