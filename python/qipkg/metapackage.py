import os
import zipfile

import qisys.qixml

class MetaPackage(object):
    def __init__(self, worktree, mpml_path):
        self.worktree = worktree
        self.mpml = mpml_path
        self.pml_paths = list()
        self.name = None
        self.version = None
        self.load()

    def load(self):
        tree = qisys.qixml.read(self.mpml)
        root = tree.getroot()
        if root.tag != "metapackage":
            raise Exception("""
Invalid mpml %s
Root element must be <metapackage>
""" % self.mpml)
        self.name = qisys.qixml.parse_required_attr(root, "name",
                                                    xml_path=self.mpml)
        self.version = root.get("version")
        include_elems = root.findall("include")
        for include_elem in include_elems:
            src = qisys.qixml.parse_required_attr(include_elem, "src",
                                                  xml_path=self.mpml)
            src = os.path.join(self.worktree.root, src)
            if src.endswith(".pml"):
                self.pml_paths.append(src)
            if src.endswith(".mpml"):
                sub_meta = MetaPackage(self.worktree, src)
                self.pml_paths.extend(sub_meta.pml_paths)

    def make_meta_package(self, packages, output=None):
        if not output:
            if self.version:
                output = "%s-%s.mpkg" % (self.name, self.version)
            else:
                output = "%s.mpkg" % self.name
        archive = zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED)
        for package in packages:
            archive.write(package, arcname=os.path.basename(package))
        archive.close()
        return output
