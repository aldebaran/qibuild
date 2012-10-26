## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

""" This module contains a few functions for running CMake
and building projects.

"""

import os
import sys



QIBUILD_ROOT_DIR  = os.path.dirname(os.path.abspath(__file__))

def get_platform():
    """Return the platform name

    :return: the platform name string

    """
    if sys.platform.startswith("linux"):
        return "linux"
    if sys.platform.startswith("win"):
        return "windows"
    if sys.platform == "darwin":
        return "mac"

from qibuild.toc import toc_open


##
# Backward compat layer for qisys starts here:

from qisys.script import run_action

from qisys import archive
from qisys import command
from qisys import envsetter
from qisys import interact
from qisys import log
from qisys import script
from qisys import sh
from qisys import ui

##
# Auto-imports: FIXME: remove it
from qibuild import build
from qibuild import cmake
from qibuild import cmdparse
from qibuild import config
from qibuild import configstore
from qibuild import ctest
from qibuild import parsers
from qibuild import performance
from qibuild import toc
