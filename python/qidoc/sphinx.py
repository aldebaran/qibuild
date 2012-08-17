## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

""" Set of tools to handle sphinx projects

"""

import os
import sys

from qibuild import ui
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
        ui.warning(mess)
        return

    opts["doxylink"] = str(rel_doxylink)
    opts["intersphinx_mapping"] = str(intersphinx_mapping)
    opts["themes_path"] = os.path.join(templates, "sphinx", "_themes")
    opts["themes_path"] = qibuild.sh.to_posix_path(opts["themes_path"])
    opts["ext_path"] = os.path.join(templates, "sphinx", "tools")
    opts["ext_path"] = qibuild.sh.to_posix_path(opts["ext_path"])

    conf_py_out = os.path.join(src, "qidoc", "conf.py")
    qidoc.templates.configure_file(conf_py_tmpl, conf_py_out,
        append_file=conf_py_in,
        opts=opts)


def gen_download_zips(src):
    """ Process sources of the documentation, looking for
    every directory containing a .zipme, and
    copying it do src/_zips/

    """
    zips_path = os.path.join(src, "_zips")
    qibuild.sh.mkdir(zips_path)
    for (root, directories, _files) in os.walk(src):
        for directory in directories:
            zipme = os.path.join(root, directory, ".zipme")
            if os.path.exists(zipme):
                qibuild.archive.zip_win(os.path.join(root, directory))


def build(src, dest, opts):
    """ Run sphinx-build on a sphinx repo

    configure() should have been called first

    """
    ui.info(ui.green, "Building sphinx", src)
    config_path = os.path.join(src, "qidoc")
    # Try with sphinx-build2 (for arch), then fall back on
    # sphinx-build
    sphinx_build2 = qibuild.command.find_program("sphinx-build2")
    if sphinx_build2:
        cmd = [sphinx_build2]
    else:
        sphinx_build = qibuild.command.find_program("sphinx-build")
        if not sphinx_build:
            raise Exception("sphinx-build not in path, please install it")
        cmd = [sphinx_build]

    if os.path.exists(os.path.join(config_path, "conf.py")):
        cmd.extend(["-c", config_path])
    if opts.get("werror"):
        cmd.append("-W")
    if opts.get("quiet"):
        cmd.append("-q")
    for flag in opts.get("flags", list()):
        cmd.extend(["-D", flag])
    cmd.extend([os.path.join(src, "source"), dest])

    env = os.environ.copy()
    release = opts.get("release", False)
    if release:
        env["build_type"] = "release"
    else:
        env["build_type"] = "internal"
    # by-pass sphinx-build bug on mac:
    if sys.platform == "darwin":
        env["LC_ALL"] = "en_US.UTF-8"
    qibuild.command.call(cmd, cwd=src, env=env)
