## Copyright (c) 2012, 2013 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

"""This package contains the PackageWorkTree object.
"""
import os
import qisys.qixml
from qisys import ui
import qibuild.parsers
import qibuild.deploy
import qilinguist.builder
import zipfile

class Package(object):
    """ A class representing a .pkg object """

    def __init__(self, pml_path):
        """ pml_path: the pml file used to build the package
            builders: a list of builders (cmake, crg, qidoc, ...)
        """
        self.pml_path = pml_path
        self.root = os.path.dirname(self.pml_path)
        self.manifest_xml = os.path.join(self.root, "manifest.xml")
        if not os.path.exists(self.manifest_xml):
            raise Exception("%s does not exist" % self.manifest_xml)
        self.name = None
        self.version = None
        pkg_name(self.manifest_xml)
        self.output = "%s-%s.pkg" % (self.name, self.version)

    def make_package(self, pml_builder, output=None):
        stage_path = pml_builder.stage_path
        if not output:
            name = pkg_name(self.manifest_xml) + ".pkg"
            output = os.path.join(os.getcwd(), name)

        archive = zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED)
        #  Add the manifest
        manifest_xml = pml_builder.manifest_xml
        archive.write(manifest_xml, "manifest.xml")

        # Add everything from the staged path
        pml_builder.install(pml_builder.stage_path)
        stage_path = pml_builder.stage_path
        for root,_, filenames in os.walk(stage_path):
            for filename in filenames:
                full_path = os.path.join(root, filename)
                rel_path  = os.path.relpath(full_path, stage_path)
                ui.info(ui.green, "adding", ui.reset, ui.bold, rel_path)
                archive.write(full_path, rel_path)
        archive.close()

        ui.info(ui.green, "Package generated in",
                ui.reset, ui.bold, output)
        return output


def pkg_name(manifest_xml):
    "Return a string name-version"
    root = qisys.qixml.read(manifest_xml).getroot()
    uuid = root.get("uuid")
    version = root.get("version")
    output_name = "%s-%s" % (uuid, version)
    return output_name

