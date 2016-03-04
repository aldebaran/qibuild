## Copyright (c) 2012-2016 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

""" Library to generate, update and compile translatable sentences with
QtLinguist

"""

import os
import subprocess

from qisys import ui
import qisys.command
import qisys.error
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

    def release(self, raises=True):
        all_ok = True
        for locale in self.linguas:
            input_file = os.path.join(self.po_path, locale + ".ts")
            if not os.path.exists(input_file):
                ui.error("No .ts found for locale: ", locale, "\n",
                         "(looked in %s )" % input_file, "\n",
                         "Did you run qilinguist update?")
                continue
            output_file = os.path.join(self.po_path,
                                       self.name + "_" + locale + ".qm")
            ok, message = generate_qm_file(input_file, output_file)
            if not ok:
                all_ok = False
                ui.error(message)
        if not all_ok and raises:
            raise qisys.error.Error("`qilinguist release` failed")
        return all_ok

    def install(self, destination):
        full_dest = os.path.join(destination, "share", "locale")
        def filter(f):
            return f.endswith(".qm")
        qisys.sh.install(self.po_path, full_dest, filter_fun=filter)

    def __repr__(self):
        return "<QtLinguistProject %s in %s>" % (self.name, self.path)

def generate_qm_file(input, output):
    """ Generate a ``.qm`` file from a ``.ts`` file.
    Returns (True, "") if everything went well,
    (False, "<error message>") otherwise

    """
    cmd = ["lrelease", "-compress", input, "-qm", output]
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    out, _ = process.communicate()
    ui.info(out.strip())
    if process.returncode != 0:
        return False, "lrelease failed"
    if "untranslated" in out:
        return False, "untranslated messages were found"
    return True, ""
