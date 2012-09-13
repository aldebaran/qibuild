from qidoc.docs.documentation import Documentation, ConfigureFailed

class SphinxDoc(Documentation):
    def type_name(self): return 'sphinx'

    def get_mapping(self, docs, **kwargs):
        res = dict()
        for dep in self.dependencies:
            res[dep] = (self.docs[dep].dest, None)
        return res

    def _configure(self, opts, **kwargs):
        try:
            templates = kwargs['templates']
            doxylink = kwargs['doxylink'].copy()
        except KeyError as e:
            raise ConfigureFailed(self.name,
                'Keyword argument `{opt}` is missing.'.format(opt = e)
            )
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

    def _build(self, opts, **kwargs):
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
