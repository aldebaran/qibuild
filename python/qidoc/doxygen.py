## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

""" Set of tools to handle doxygen projects

"""

import os

import qidoc.command
import qidoc.templates

import qibuild

def configure(src, templates, opts, project_name=None):
    """ Configure a doxygen project

    Will we generate a Doxyfile.qidoc file
    (with header.html. footer.html and doxygen.css if necessary),
    so that you can keep a Doxyfile under version control
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
        qidoc.templates.configure_file(in_file, out_file, opts=opts)

    # Also copy the css:
    qibuild.sh.install(
        os.path.join(templates, "doxygen", "doxygen.css"),
        os.path.join(src, "doxygen.css"),
        quiet=True)



def build(src, dest):
    """ Build a doxygen project

    configure() should have been called first
    """
    print
    print "###"
    print "# Building doxygen ", src
    print
    cmd = ["doxygen", "Doxyfile.qidoc"]
    qidoc.command.call(cmd, cwd=src)
    build_html = os.path.join(src, "build-doc", "html")
    qibuild.sh.install(build_html, dest, quiet=True)


def gen_tag_file(src, project_name, tags_path):
    """ Generate doxygen tags for the given project
    inside tags_path

    build() should have been called first
    (doxytags needs to parse html files)

    Return path to the generated tag file

    """
    tag_file = os.path.join(tags_path, project_name + ".tag")
    build_html = os.path.join(src, "build-doc", "html")
    cmd = ["doxytag", "-t", tag_file]
    qidoc.command.call(cmd, cwd=build_html)
    return tag_file

