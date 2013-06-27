import os
import sys

from qisys import ui
import qisys.sh
import qidoc.project


class SphinxProject(qidoc.project.DocProject):
    """ A doc projet using Sphinx """
    def __init__(self, doc_worktree, project, name,
                 depends=None, dest=None):
        self.doc_type = "sphinx"
        super(SphinxProject, self).__init__(doc_worktree, project, name,
                                            depends=depends,
                                            dest=dest)

    @property
    def source_dir(self):
        return os.path.join(self.path, "source")

    @property
    def html_dir(self):
        html_dir = os.path.join(self.build_dir, "html")
        qisys.sh.mkdir(html_dir)
        return html_dir

    def configure(self):
        """ Create a correct conf.py in self.build_dir """
        in_conf_py = os.path.join(self.source_dir, "conf.py")
        if not os.path.exists(in_conf_py):
            return

        out_conf_py = os.path.join(self.build_dir, "conf.py")
        qisys.sh.safe_copy(in_conf_py, out_conf_py)

    def build(self):
        """ Run sphinx.main() with the correct arguments """
        try:
            import sphinx
        except ImportError, e:
            ui.error(e, "skipping build")
            return
        html_dir = os.path.join(self.build_dir, "html")
        sphinx.main(argv=[sys.executable,
                          "-c", self.build_dir,
                          "-b", "html",
                          self.source_dir, html_dir])

    def install(self, destdir):
        pass
