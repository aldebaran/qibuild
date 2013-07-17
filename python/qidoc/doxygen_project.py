import os

import qisys.command
import qidoc.doxygen
import qidoc.project

class DoxygenProject(qidoc.project.DocProject):
    """  A doc projet using doxygen """
    def __init__(self, doc_worktree, project, name,
                 depends=None, dest=None):
        self.doc_type = "doxygen"
        super(DoxygenProject, self).__init__(doc_worktree, project, name,
                                             depends=depends, dest=dest)

    @property
    def in_doxyfile(self):
        return os.path.join(self.path, "Doxyfile")

    @property
    def out_doxyfile(self):
        return os.path.join(self.build_dir, "Doxyfile")

    @property
    def tagfile(self):
        return os.path.join(self.build_dir, self.name + ".tag")

    def configure(self, **kwargs):
        """ Create a correct Doxyfile in self.build_dir.

        * Force OUTPUT_DIRECTORY
        * Rewrite INPUT and EXAMPLE_PATH
        * Add @INCLUDE_PATH and @INCLUDE statements if we
          have a template

        """
        version = kwargs.get("version")
        rel_paths = kwargs.get("rel_paths", False)
        in_conf = qidoc.doxygen.read_doxyfile(self.in_doxyfile)
        out_conf = in_conf.copy()
        out_conf["OUTPUT_DIRECTORY"] = self.build_dir
        out_conf["GENERATE_XML"] = "YES"  # required by qiapidoc and doxylink
        out_conf["GENERATE_HTML"] = "YES"
        out_conf["GENERATE_LATEX"] = "NO"
        out_conf["PROJECT_NAME"] = in_conf.get("PROJECT_NAME", self.name)
        out_conf["WARNINGS"] = "YES"
        out_conf["QUIET"] = "YES"
        out_conf["GENERATE_TAGFILE"] = self.tagfile
        doxydeps = list()
        # no need to recurse the dependencies here, doxygen does it for us
        for dep_name in self.depends:
            doc_project = self.doc_worktree.get_doc_project(dep_name, raises=False)
            if doc_project and doc_project.doc_type == "doxygen":
                doxydeps.append(doc_project)
        if doxydeps:
            out_conf["TAGFILES"] = ""
            for doxydep in doxydeps:
                if rel_paths:
                    dep_path = os.path.relpath(doxydep.dest, self.dest)
                else:
                    dep_path = doxydep.html_dir
                out_conf["TAGFILES"] += doxydep.tagfile + "=" + dep_path + " "

        if version:
            out_conf["PROJECT_NUMBER"] = version

        for path_key in ["INPUT", "EXAMPLE_PATH"]:
            in_value = in_conf.get(path_key)
            if not in_value:
                continue
            out_value = self.make_rel_paths(in_value)
            out_conf[path_key] = out_value

        qidoc.doxygen.write_doxyfile(out_conf, self.out_doxyfile)

    def build(self, **kwargs):
        """ Run doxygen from the build directory """
        cmd = ["doxygen", self.out_doxyfile]
        qisys.command.call(cmd, cwd=self.build_dir)

    def install(self, destdir):
        qisys.sh.install(self.html_dir, destdir)

    def make_rel_paths(self, value):
        """ Transform a relative path to the source into an
        absolute path (usable from a build directory)

        """
        res = list()
        for path in value.split():
            full_path = os.path.join(self.path, path)
            res.append(full_path)
        return " ".join(res)
