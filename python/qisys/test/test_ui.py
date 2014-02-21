## Copyright (c) 2012-2014 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

""" Just some tests for ui """

import qisys.ui as ui

def main():
    ui.info(ui.red, "This is a an error message\n",
        ui.reset, "And here are the details")
    ui.error("could not build")
    ui.warning("-j ignored for this generator")
    ui.info("building foo")
    ui.debug("debug message")
    ui.info(ui.brown, "this is brown")
    ui.info(ui.bold, ui.brown, "this is bold brown")
    ui.info(ui.red, "red is dead")
    ui.info(ui.darkred, "darkred is really dead")
    ui.info(ui.yellow, "this is yellow")

if __name__ == "__main__":
    import sys
    if "-v" in  sys.argv:
        ui.CONFIG["verbose"] = True
    if "-q" in sys.argv:
        ui.CONFIG["quiet"]  = True
    main()
