## Copyright (C) 2011 Aldebaran Robotics
"""actions.qitoolchain

This package contains the qitoolchain actions.

Those are supposed to help the developer to maintain
his toolchain directory.

(where all the external librairies are to be found)

Example of usage:

    # Create a toolchain for mingwin32
    qitoolchain create "mingwin32"

    # Add zeromq libs, headers, and cmake files in the toolchain dir:
    qitoolchain add zeromq

After this, calling qi_use_lib(foo zeromq) just works :)


"""

