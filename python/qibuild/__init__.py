## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

""" This module contains a few functions for running CMake
and building projects.

"""

import os
import re
import logging

from qibuild import archive
from qibuild import build
from qibuild import cmake
from qibuild import cmdparse
from qibuild import command
from qibuild import config
from qibuild import configstore
from qibuild import ctest
from qibuild import envsetter
from qibuild import interact
from qibuild import log
from qibuild import parsers
from qibuild import sh
from qibuild import toc
from qibuild import worktree


from qibuild.toc      import toc_open
from qibuild.worktree import worktree_open
from qibuild.cmdparse import run_action


QIBUILD_ROOT_DIR  = os.path.dirname(os.path.abspath(__file__))
