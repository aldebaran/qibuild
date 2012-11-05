import os
import sys

import qisys
import qisys.archive
import qidoc.templates

from qidoc.docs.documentation import Documentation, ConfigureFailedError
from qisys import ui

class SphinxDoc(Documentation):
    '''This class builds and configures sphinx projects.'''

    def type_name(self):
        return 'sphinx'

    def get_mapping(self, docs, **kwargs):
        res = dict()
        for dep in self.dependencies:
            res[dep] = (self.docs[dep].dest, None)
        return res

    def _configure(self, docs, opts, **kwargs):
        try:
            templates = kwargs['templates']
            doxylink = kwargs['doxylink'].copy()
        except KeyError as err:
            raise ConfigureFailedError(self.name,
                'Keyword argument `{opt}` is missing.'.format(opt = err)
            )
        rel_doxylink = dict()
        for (name, (tag_file, prefix)) in doxylink.iteritems():
            full_prefix = os.path.join(self.dest, prefix)
            rel_prefix = os.path.relpath(full_prefix, self.dest)
            rel_doxylink[name] = (tag_file, rel_prefix)

        # Deal with conf.py
        conf_py_tmpl = os.path.join(templates, "sphinx", "conf.in.py")
        conf_py_in = os.path.join(self.src, "qidoc", "conf.in.py")
        if not os.path.exists(conf_py_in):
            mess = "Could not configure sphinx sources in: %s\n" % self.src
            mess += "qidoc/conf.in.py does not exists"
            ui.warning(mess)
            return

        opts["doxylink"] = str(rel_doxylink)
        opts["intersphinx_mapping"] = str(self.get_mapping(docs))
        opts["themes_path"] = os.path.join(templates, "sphinx", "_themes")
        opts["themes_path"] = qisys.sh.to_posix_path(opts["themes_path"])
        opts["ext_path"] = os.path.join(templates, "sphinx", "tools")
        opts["ext_path"] = qisys.sh.to_posix_path(opts["ext_path"])

        conf_py_out = os.path.join(self.src, "qidoc", "conf.py")
        qidoc.templates.configure_file(conf_py_tmpl, conf_py_out,
            append_file=conf_py_in,
            opts=opts)

    def _build(self, docs, opts, **kwargs):
        config_path = os.path.join(self.src, "qidoc")
        # Generates a zip of the files.
        zips_path = os.path.join(self.src, "_zips")
        qisys.sh.mkdir(zips_path)
        for (root, directories, _files) in os.walk(self.src):
            for directory in directories:
                zipme = os.path.join(root, directory, ".zipme")
                if os.path.exists(zipme):
                    qisys.archive.compress(os.path.join(root, directory),
                                             algo="zip", quiet=True)
        # Try with sphinx-build2 (for arch), then fall back on
        # sphinx-build
        sphinx_build2 = qisys.command.find_program("sphinx-build2")
        if sphinx_build2:
            cmd = [sphinx_build2]
        else:
            sphinx_build = qisys.command.find_program("sphinx-build")
            if not sphinx_build:
                raise Exception("sphinx-build not in path, please install it")
            cmd = [sphinx_build]
        if opts.get('pdb'):
            cmd.append('-P')
        if os.path.exists(os.path.join(config_path, "conf.py")):
            cmd.extend(["-c", config_path])
        if opts.get("werror"):
            cmd.append("-W")
        for flag in opts.get("flags", list()):
            cmd.extend(["-D", flag])
        if not opts.get('verbose'):
            cmd.append('-q')
        cmd.extend([os.path.join(self.src, "source"), self.dest])
        env = os.environ.copy()
        release = opts.get("release", False)
        if release:
            env["build_type"] = "release"
        else:
            env["build_type"] = "internal"
        # by-pass sphinx-build bug on mac:
        if sys.platform == "darwin":
            env["LC_ALL"] = "en_US.UTF-8"
        qisys.command.call(cmd, cwd=self.src, env=env)

