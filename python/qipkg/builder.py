""" Builder for pml files """
import os

import qibuild.worktree

import qisys.qixml
import qipkg.package

from qipy.worktree import PythonWorkTree
from qipy.python_builder import PythonBuilder
from qibuild.worktree import BuildWorkTree
from qibuild.cmake_builder import CMakeBuilder

class PMLBuilder(object):
    def __init__(self, pml_path,
                 cmake_builder,
                 python_builder,
                 linguist_builder):
        self.pml_path = pml_path
        self.base_dir = os.path.dirname(self.pml_path)
        self.manifest_xml = os.path.join(self.base_dir, "manifest.xml")
        if not os.path.exists(self.manifest_xml):
            raise Exception("%s does not exist" % self.manifest_xml)

        self.cmake_builder = cmake_builder
        self.python_builder = python_builder
        self.linguist_builder = linguist_builder

        self.build_worktree = self.cmake_builder.build_worktree
        self.python_worktree = self.python_builder.python_worktree
        self.linguist_worktree = linguist_builder.linguist_worktree
        self.builders = [self.cmake_builder, self.python_builder, self.linguist_builder]
        self.worktree = self.build_worktree.worktree

        self.file_list = list()

        self.load_pml(pml_path)

        # used to prepare deploying files and making packages,
        # so it must always exist but also always start empty
        dot_qi = self.worktree.dot_qi
        build_config = self.cmake_builder.build_config
        name = build_config.build_directory(prefix="qipkg")
        self.stage_path = os.path.join(dot_qi, name)
        qisys.sh.rm(self.stage_path)
        qisys.sh.mkdir(self.stage_path, recursive=True)

    def load_pml(self, pml_path):
        tree= qisys.qixml.read(pml_path)
        root = tree.getroot()
        qibuild_elems = root.findall("qibuild")
        for qibuild_elem in qibuild_elems:
            name = qisys.qixml.parse_required_attr(qibuild_elem, "name", pml_path)
            project = self.build_worktree.get_build_project(name, raises=True)
            self.cmake_builder.projects.append(project)

        qipython_elems = root.findall("qipython")
        for qipython_elem in qipython_elems:
            name = qisys.qixml.parse_required_attr(qipython_elem, "name", pml_path)
            project = self.python_worktree.get_python_project(name, raises=True)
            self.python_builder.projects.append(project)

        qilinguist_elems = root.findall("qilinguist")
        for qilinguist_elem in qilinguist_elems:
            name = qisys.qixml.parse_required_attr(qilinguist_elem, "name", pml_path)
            project = self.linguist_worktree.get_linguist_project(name, raises=True)
            self.linguist_builder.projects.append(project)

        # For top, ressource, dialog, behavior, add stuff to self.file_list
        behaviors = root.find("BehaviorDescriptions")
        if behaviors is not None:
            for child in behaviors.findall("BehaviorDescription"):
                src = child.get("src")
                full_src = os.path.join(src, "behavior.xar")
                self.file_list.append(full_src)

        # Dialog
        dialogs = root.find("Dialogs")
        if dialogs is not None:
            for child in dialogs.findall("Dialog"):
                src = child.get("src")
                self.file_list.append(src)

        # Resources
        resources = root.find("Resources")
        if resources is not None:
            for child in resources.findall("File"):
                src = child.get("src")
                self.file_list.append(src)

        # Topics
        topics = root.find("Topics")
        if topics is not None:
            for child in topics.findall("Topic"):
                src = child.get("src")
                self.file_list.append(src)

    def configure(self):
        for builder in self.builders:
            builder.configure()

    def build(self):
        for builder in self.builders:
            builder.build()

    def install(self, destination):
        # Use every available builder to install
        for builder in self.builders:
            if isinstance(builder, CMakeBuilder):
                builder.dep_types=["runtime"]
                builder.install(destination, components=["runtime"])
            else:
                builder.install(destination)
        # Also use file from file_list
        for src in self.file_list:
            full_src = os.path.join(self.base_dir, src)
            rel_src = os.path.relpath(full_src, self.base_dir)
            full_dest = os.path.join(destination, rel_src)
            qisys.sh.install(full_src, full_dest)

    def deploy(self, url):
        qisys.remote.deploy(self.stage_path, url)

    def deploy_package(self, url):
        package = self.make_package(output=None)
        # waiting for qiys.remote.deploy_file
        # qisys.remote.deploy_file(package)

    def make_package(self, output=None):
        package = qipkg.package.Package(self.pml_path)
        return package.make_package(self, output=output)

