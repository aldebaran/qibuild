## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

"""Set of tools to handle doxygen projects."""

import os

import qibuild
import qidoc.templates

from qibuild import ui

def configure(src, templates, opts, project_name=None, doxytags_path=None,
              doxygen_mapping=None):
    """Configure a doxygen project

    Will we generate a Doxyfile.qidoc file (with header.html. footer.html and
    doxygen.css if necessary), so that you can keep a Doxyfile under version
    control.
    """
    for name in ["Doxyfile.in", "header.in.html", "footer.in.html"]:
        if name == "Doxyfile.in":
            out_name = "Doxyfile.qidoc"
        else:
            out_name = name.replace(".in.", ".")
        out_file = os.path.join(src, out_name)
        in_file  = os.path.join(templates, "doxygen", name)
        opts["PROJECT_NAME"] = project_name
        opts["PROJECT_NUMBER"] = opts["version"]
        opts["OUTPUT_DIRECTORY"] = "build-doc"
        if doxytags_path:
            tag_file = os.path.join(doxytags_path, project_name + ".tag")
            opts["GENERATE_TAGFILE"] = tag_file
        else:
            opts["GENERATE_TAGFILE"] = ""
        if doxygen_mapping:
            tagfiles = list()
            for (k, v) in doxygen_mapping.iteritems():
                tagfiles.append("%s=%s" % (k, v))
            opts["TAGFILES"] = " ".join(tagfiles)
        else:
            opts["TAGFILES"] = ""
        if name == "Doxyfile.in":
            append_file = os.path.join(src, "Doxyfile.in")
        else:
            append_file = None
        qidoc.templates.configure_file(in_file, out_file,
            append_file=append_file,
            opts=opts)

    # Also copy the css:
    qibuild.sh.install(
        os.path.join(templates, "doxygen", "doxygen.css"),
        os.path.join(src, "doxygen.css"),
        quiet=True)

def build(src, dest, opts):
    """ Build a doxygen project

    configure() should have been called first
    """
    ui.info(ui.green, "Building doxygen", src)
    cmd = ["doxygen", "Doxyfile.qidoc"]
    qibuild.command.call(cmd, cwd=src)
    build_html = os.path.join(src, "build-doc", "html")
    qibuild.sh.install(build_html, dest, quiet=True)
