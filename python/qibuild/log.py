## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

""" Compatibility layer for old usage of logging.py

"""
import qibuild.ui


def configure_logging(args):
    qibuild.ui.CONFIG["color"] = args.color
    qibuild.ui.CONFIG["verbose"] = args.verbose
    qibuild.ui.CONFIG["quiet"] = args.quiet

def get_current_log_level():
    pass


def _format_args(args):
    """ Just to be able to parse ::

        logger.info("%s count is %d", project, count)
    """
    args = list(args)
    if not args:
        return
    res = args[0]
    if len(args) > 1:
        res = res % tuple(args[1:])
    return res

class DummyLogger():
    def __init__(self, name):
        self.name = name

    def error(self, *args):
        msg = _format_args(args)
        qibuild.ui.error(msg)

    def warning(self, *args):
        msg = _format_args(args)
        qibuild.ui.warning(msg)

    def info(self, *args):
        msg = _format_args(args)
        qibuild.ui.info(qibuild.ui.green, msg)

    def debug(self, *args):
        msg = _format_args(args)
        qibuild.ui.debug(self.name + " ", msg)

def get_logger(name):
    """ Replacement for logger.getLogger() """
    return DummyLogger(name)

