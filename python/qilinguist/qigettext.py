## Copyright (c) 2012-2016 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

"""Library to extract, generate, update and compile translatable
sentences with gettext

"""

import os
import functools
import subprocess

from qisys import ui
import qisys.command
import qisys.error
import qilinguist.project

class GettextProject(qilinguist.project.LinguistProject):

    def __init__(self, *args, **kwargs):
        super(GettextProject, self).__init__(*args, **kwargs)


    @property
    def pot_file(self):
        return os.path.join(self.po_path, self.domain + ".pot")

    def get_po_file(self, locale):
        return os.path.join(self.po_path, locale + ".po")

    @property
    def mo_path(self):
        mo_path = os.path.join(self.po_path, "share", "locale", self.name)
        qisys.sh.mkdir(mo_path, recursive=True)
        return mo_path

    def update(self):
        """ Read the source files, generate the
        template, generate the catalogs

        """
        self.extract_pot_file()

        # for each locale generate or update PO file
        for locale in self.linguas:
            # check if PO file exists
            output_file = self.get_po_file(locale)
            if os.path.exists(output_file):
                # Update PO file if it exists
                self.update_po_file(locale)
            else:
                # generate PO file if it doesn't exist
                self.generate_po_file(locale)

    def release(self, raises=True):
        """ Compile every catalog.

        """
        mo_output_dir = os.path.join(self.path, "po",
                                     "share", "locale", self.name)
        qisys.sh.mkdir(mo_output_dir, recursive=True)
        all_ok = True
        for locale in self.linguas:
            ok, message = self.generate_mo_file(locale)
            if not ok:
                ui.error(message)
            all_ok = all_ok and ok
        if not all_ok and raises:
            raise qisys.error.Error("`qilinguist release` failed")
        return all_ok

    def extract_pot_file(self):
        """Extract sentence from source file and generate POT file"""
        # get input files and directory
        input_files = self.get_sources()

        cmd = ["xgettext", "--default-domain=" + self.domain]
        # See info xgettext 5.1.6
        # https://www.gnu.org/software/gettext/manual/gettext.html#xgettext-Invocation
        # 4t are here for python because self count as an argument
        cmd.extend([
            "--keyword=_:1",
            "--keyword=translate:1,1t", "--keyword=translate:1,2t",
            "--keyword=translate:1,3t", "--keyword=translate:1,4t",
            "--keyword=translate:1,4c,4t", "--keyword=translate:1,4c,5t",
            "--keyword=tr:1,1t", "--keyword=tr:1,2t",
            "--keyword=tr:1,3t", "--keyword=tr:1,4t",
            "--keyword=tr:1,4c,4t", "--keyword=tr:1,4c,5t",
            "--keyword=trContext:1,2c,2t", "--keyword=trContext:1,2c,3t",
            "--keyword=translateContext:1,2c,2t", "--keyword=translateContext:1,2c,3t",

            ])
        # generate sorted output
        cmd.append("--sort-output")

        cmd.extend(["--output-dir", self.po_path])
        cmd.extend(["--output", self.pot_file])

        # add directories to list for input files search
        cmd.extend(["--directory", self.path])
        cmd.extend(input_files)

        qisys.command.call(cmd)

    # pylint: disable-msg=E0213
    def need_pot_file(func):
        @functools.wraps(func)
        def new_func(self, *args, **kwargs):
            if not os.path.exists(self.pot_file):
                ui.error("No pot file found. Maybe no translatable strings "
                        "were found?")
                return
            #pylint: disable-msg=E1102
            res = func(self, *args, **kwargs)
            return res
        return new_func

    @need_pot_file
    def update_po_file(self, locale):
        """Update PO file from POT"""
        update_file = self.get_po_file(locale)

        cmd = ["msgmerge", "--sort-output", "--update", "--backup=off"]
        cmd.extend(["--directory", self.po_path])
        cmd.append(update_file)
        cmd.append(self.pot_file)

        ui.info(ui.green, "Updating", ui.reset, ui.bold,
                os.path.relpath(update_file, self.path))
        qisys.command.call(cmd, quiet=True)

    def generate_po_file(self, locale):
        """Generate PO file"""
        output_file = self.get_po_file(locale)

        cmd = ["msginit", "--no-translator"]
        cmd.extend(["--locale", locale])
        cmd.extend(["--output-file", output_file])
        cmd.extend(["--input", self.pot_file])

        ui.info(ui.green, "Creating", ui.reset, ui.bold,
                os.path.relpath(output_file, self.path))
        # remove annoying stderr output
        subprocess.check_call(cmd, stdout=subprocess.PIPE,
                                   stderr=subprocess.STDOUT)


    def generate_mo_file(self, locale):
        """ Generate .mo file for the given locale

        """
        ui.info(ui.green, "Generating translation for", ui.reset,
                ui.bold, locale)
        input_file = self.get_po_file(locale)
        if not os.path.exists(input_file):
            ui.error("No .po found for locale: ", locale, "\n",
                     "(looked in %s)" % input_file, "\n",
                     "Did you run qilinguist update?")
            return

        output_file = os.path.join(self.mo_path, locale, "LC_MESSAGES",
                                   self.domain + ".mo")
        to_make = os.path.dirname(output_file)
        qisys.sh.mkdir(to_make, recursive=True)

        cmd = ["msgfmt", "--check", "--statistics"]

        # required by libqi:
        conf_file = os.path.join(self.mo_path, ".confintl")
        with open(conf_file, "w") as fp:
            fp.write("# THIS FILE IS AUTOGENERATED\n"
                     "# Do not delete or modify it\n"
                     "# This file is used to find translation dictionaries\n")

        cmd.extend(["--output-file", output_file])
        cmd.extend(["--directory", self.po_path])
        cmd.append(input_file)

        process = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE)
        out, err = process.communicate()
        ui.info(err.strip())
        if "untranslated" in err:
            return False, "Some untranslated messages were found"
        if process.returncode != 0:
            return False, "msgfmt failed"
        return True, ""

    def install(self, destination):
        full_dest = os.path.join(destination, "share", "locale")
        to_install = os.path.join(self.po_path, "share", "locale")
        qisys.sh.install(to_install, full_dest)

    def __repr__(self):
        return "<GettextProject %s in %s>" % (self.name, self.path)
