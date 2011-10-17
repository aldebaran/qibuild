## Copyright (C) 2011 Aldebaran Robotics
"""actions.qitoolchain

This package contains the qitoolchain actions.

Those are supposed to help the developer to maintain
his toolchain directory.

(where all the external librairies are to be found)

Example of usage:

    # Create a toolchain for mingw32
    qitoolchain init --name "mingw2"

    # Add zeromq libs, headers, and cmake files in the toolchain dir:
    qitoolchain add zeromq -c mingw32

After this, calling qi_use_lib(foo zeromq) just works :)


"""

