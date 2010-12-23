"""Welcome to qibuild project.

Here's what you'll find here:


shell:
    deals with the command line interface.

    (for instance, after qibuild --verbose cmake --relase foo, call
    qibuild.actions.cmake with options verbose=True, release=True)

bin/
    scripts

actions/
    plugins for qibuild


command/
    tools for launching executables

make/
    tools for building software

cmake/
    tools for using CMake, CTest and friends

git/
    tools for using git

toc/
    Toc Obviously Compiles ! : the Toc object contains a list
    of projects with their configurations

toc/project:
    a Project is a git repository using CMake as a build system,
    which depends on other projects


"""

from . import command
from . import log
from . import shell
from . import toc
