""" Welcome to qibuild project.

Here's what you'll find here:

shell/
    deals with the command line interface.

actions/
    qibuild actions

command
    tools for launching executables

build
    tools for building software, calling make, cmake, ctest ..

toc/
    Toc Obviously Compiles ! : the Toc object contains a list
    of projects with their configurations
"""

from . import command
from . import log
from . import shell
from . import toc
