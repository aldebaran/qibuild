from qidoc.docs.documentation import Documentation, ConfigureFailed

class DoxygenDoc(Documentation):
    def type_name(self): return 'doxygen'

    def get_mapping(self, docs, **kwargs):
        res = dict()
        for dep in self.dependencies:
            doxytag_file = os.path.join(kwargs['doxytags_path'],
                                        dep.name + ".tag")
            res[doxytag_file] = os.path.realpath(dep.dest, self.dest)
        return res

    def _configure(self, opts, **kwargs):
        try:
            templates = kwargs['templates']
        except KeyError as e:
            raise ConfigureFailed(self.name,
                'Keyword argument `{opt}` is missing'.format(opt = e)
            )
        for name in ['Doxyfile.in', 'header.in.html', 'footer.in.html']:
            if name == 'Doxyfile.in':
                out_name = 'Doxyfile.qidoc'
            else:
                out_name = name.replace('.in.', '.')
            out_file = os.path.join(self.src, out_name)
            in_file  = os.path.join(templates, 'doxygen', name)
            opts['PROJECT_NAME'] = self.name
            opts['PROJECT_NUMBER'] = opts['version']
            opts['OUTPUT_DIRECTORY'] = 'build-doc'
            opts['GENERATE_TAGFILE'] = ''
            if doxytags_path:
                tag_file = os.path.join(doxytags_path, project_name + '.tag')
                opts['GENERATE_TAGFILE'] = tag_file

            # tag files for dependencies.
            tagfiles = list()
            if doxygen_mapping:
                for (k, v) in doxygen_mapping.iteritems():
                    tagfiles.append("%s=%s" % (k, v))
            opts["TAGFILES"] = " ".join(tagfiles)

            append_file = None
            if name == "Doxyfile.in":
                append_file = os.path.join(src, "Doxyfile.in")
            qidoc.templates.configure_file(in_file, out_file,
                                           append_file=append_file,
                                           opts=opts)

        # Also copy the css:
        qibuild.sh.install(
            os.path.join(templates, "doxygen", "doxygen.css"),
            os.path.join(self.src, "doxygen.css"),
            quiet=True)

    def _build(self, opts, **kwargs):
        ui.info(ui.green, "Building doxygen", self.src)
        cmd = ["doxygen", "Doxyfile.qidoc"]
        qibuild.command.call(cmd, cwd=self.src)
        build_html = os.path.join(self.src, "build-doc", "html")
        qibuild.sh.install(build_html, self.dest, quiet=True)
