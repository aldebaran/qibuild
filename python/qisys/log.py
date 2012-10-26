## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

""" Compatibility layer for old usage of logging.py

"""
import qisys.ui


def configure_logging(args):
    qisys.ui.CONFIG["color"] = args.color
    qisys.ui.CONFIG["verbose"] = args.verbose
    qisys.ui.CONFIG["quiet"] = args.quiet
    qisys.ui.CONFIG["timestamp"] = args.timestamp

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
        qisys.ui.error(msg)

    def warning(self, *args):
        msg = _format_args(args)
        qisys.ui.warning(msg)

    def info(self, *args):
        msg = _format_args(args)
        qisys.ui.info(qisys.ui.green, msg)

    def debug(self, *args):
        msg = _format_args(args)
        qisys.ui.debug(self.name + " ", msg)

def get_logger(name):
    """ Replacement for logger.getLogger() """
    return DummyLogger(name)

