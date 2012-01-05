## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

""" Set of tools to handle sphinx projects

"""

import os

import qidoc.command
import qidoc.templates
import qibuild.sh

def configure(src, dest, templates, intersphinx_mapping, doxylink, opts):
    """ Configure a sphinx repo

    The sphix repo MUST have a src/source/ directory
    (NOT the default of sphinx-quickstart)

    The conf.py will be put in src/qidoc/conf.py
    concatening the contents of the templates with the conf.py from
    src/qidoc/conf.in.py, so that you can put src/source/conf.py
    under version control

    """
    # Rebuild a doxylink dict with relative paths
    rel_doxylink = doxylink.copy()
    for (name, (tag_file, prefix)) in rel_doxylink.iteritems():
        full_prefix = os.path.join(dest, prefix)
        rel_prefix = os.path.relpath(full_prefix, dest)
        rel_doxylink[name] = (tag_file, rel_prefix)

    # Deal with conf.py
    conf_py_tmpl = os.path.join(templates, "sphinx", "conf.in.py")
    conf_py_in = os.path.join(src, "qidoc", "conf.in.py")
    if not os.path.exists(conf_py_in):
        mess = "Could not configure sphinx sources in:%s \n" % src
        mess += "qidoc/conf.in.py does not exists"
        raise Exception(mess)

    opts["doxylink"] = str(rel_doxylink)
    opts["intersphinx_mapping"] = str(intersphinx_mapping)

    conf_py_out = os.path.join(src, "qidoc", "conf.py")
    qidoc.templates.configure_file(conf_py_tmpl, conf_py_out,
        append_file=conf_py_in,
        opts=opts)

    # Copy _themes:
    themes_src = os.path.join(templates, "sphinx", "_themes")
    themes_dst = os.path.join(src, "qidoc", "_themes")
    qibuild.sh.install(themes_src, themes_dst, quiet=True)

    # Copy doxylink source code:
    doxylink_src = os.path.join(templates, "sphinx", "tools", "doxylink")
    doxylink_dst = os.path.join(src, "qidoc", "tools", "doxylink")
    qibuild.sh.install(doxylink_src, doxylink_dst, quiet=True)

def build(src, dest):
    """ Run sphinx-build on a sphinx repo

    configure() should have been called first

    """
    print
    print "###"
    print "# Building sphinx ", src, "->", dest
    print
    config_path = os.path.join(src, "qidoc")
    cmd = ["sphinx-build",
        "-c", config_path,
        os.path.join(src, "source"),
        dest]
    qidoc.command.call(cmd, cwd=src)
