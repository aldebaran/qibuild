## Copyright (c) 2012, 2013 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

""" Library to generate, update and compile translatable sentences with
QtLinguist

"""

import os
from qisys import ui
import qisys.command
import qilinguist.project

class QtLinguistProject(qilinguist.project.LinguistProject):
    def __init__(self, *args, **kwargs):
        super(QtLinguistProject, self).__init__(*args, **kwargs)

    def update(self):
        input_files = get_relative_file_path_potfiles_in(self,
                                                         self.potfiles_in)

        output_file = list()
        for l in self.linguas:
            # get output file
            output_file.append(l + ".ts")

        output_dir = os.path.join(self.path, "po")
        generate_ts_files(input_files, output_file, output_dir)

    def release(self):
        # get output directory
        output_dir = os.path.join(self.path, "po")

        for l in self.linguas:
            # get intput file
            input_file = os.path.join(self.path, "po", l + ".ts")
            # get output file
            output_file = l + ".qm"
            generate_qm_file(input_file, output_file, output_dir)

    def __repr__(self):
        return "<QtLinguistProject %s in %s>" % (self.name, self.src)

def get_relative_file_path_potfiles_in(prefix, file_path):
    """Get relative path for each file in the potfile.in.
    Return [<relatif/path/file>]
    """
    with open(file_path, "r") as stream:
        relativepath = list()
        for line in stream:
            filepath = line.split("#")[0]
            pathclean = filepath.strip('\n ')
            relativepath.append(pathclean)
    stream.close()
    return relativepath

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
