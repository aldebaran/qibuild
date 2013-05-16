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
        output_files = list()
        for locale in self.linguas:
            output_files.append(os.path.join(self.po_path, locale + ".ts"))
        cmd = ["lupdate", "-no-obsolete"]
        cmd.extend(self.get_sources())
        cmd.append("-ts")
        cmd.extend(output_files)
        qisys.command.call(cmd, cwd=self.path)


    def release(self):
        for locale in self.linguas:
            input_file = os.path.join(self.po_path, locale + ".ts")
            if not os.path.exists(input_file):
                ui.error("No .ts found for locale: ", locale, "\n",
                         "(looked in %s )" % input_file, "\n",
                         "Did you run qilinguist update?")
                continue
            output_file = os.path.join(self.po_path,
                                       self.name + "_" + locale + ".qm")
            cmd = ["lrelease", "-compress",
                   input_file, "-qm", output_file]
            qisys.command.call(cmd, cwd=self.path)

    def __repr__(self):
        return "<QtLinguistProject %s in %s>" % (self.name, self.src)
