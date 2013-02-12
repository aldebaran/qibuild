## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

"""Library to generate, update and compile translatable sentences with QtLinguist"""

import os
import qisys.command

def generate_ts_files(input_file, output_file, output_dir=None):
    """generate TS files

    :param input_file:  List of input source file
    :param output_file: Write output to specified TS file
    :param output_dir:  Output file will be placed here

    """
    cmd = ["lupdate", "-no-obsolete"]

    for f in input_file:
        cmd.append(f)

    cmd.append("-ts")
    for o in output_file:
        if output_dir:
            cmd.append(os.path.join(output_dir, o))
        else:
            cmd.append(o)

    qisys.command.call(cmd)

def generate_qm_file(input_file, output_file, output_dir=None):
    """generate QM file for locale

    :param input_file:  List of input source file
    :param output_file: Write output to specified TS file
    :param output_dir:  Output file will be placed here

    """
    cmd = ["lrelease", "-compress"]

    cmd.append(input_file)

    output_path = os.path.join(output_dir, output_file) if output_dir else ""

    cmd.extend(["-qm", output_path])
    qisys.command.call(cmd)
