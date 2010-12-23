"""Deals with the command line interface.

    (for instance, after qibuild --verbose cmake --relase foo, call
    qibuild.actions.cmake with options verbose=True, release=True)

"""

from .main import root_command_main, sub_command_main
from .main import run_action
from .parsers import *
