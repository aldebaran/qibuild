## Copyright (c) 2012, 2013 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

"""Handling qilinguist config files."""

import os
import qisys.qixml
from qisys import ui

def parse_potfiles_in(prefix, file_path):
    """Parse POTFILES.in.
    Return [<parent/directory/path>], [<filename>]
    """
    with open(file_path, "r") as stream:
        filenames = list()
        parent_path = list()
        for line in stream:
            filepath = line.split("#")[0]
            pathclean = filepath.strip('\n ')
            path = pathclean.rsplit('/')
            if len(path) == 2:
                parent_path.append(os.path.join(prefix, path[0]))
                filenames.append(path[1])
            elif path[0]:
                filenames.append(path[0])
    stream.close()
    return parent_path, filenames

def get_relative_file_path_potfiles_in(prefix, file_path):
    """Get relative path for each file in the potfile.in.
    Return [<relatif/path/file>]
    """
    with open(file_path, "r") as stream:
        relativepath = list()
        for line in stream:
            filepath = line.split("#")[0]
            pathclean = filepath.strip('\n ')
            relativepath.append(pathclean)
    stream.close()
    return relativepath

def get_domain_from_qiproject(project):
    """Get the textdomain for gettext.
    If no project or translate tag is found return str().
    If no domain is found in translate tag, <project_name> is return."""
    xml_elem = qisys.qixml.read(project.qiproject_xml)
    root = xml_elem.getroot()
    if root.tag != "project":
        ui.error("No tag project in qiproject.xml for project", project.src)
        return str()

    translate = root.find("translate")
    if translate is None:
        ui.warning("No tag translate in qiproject.xml for project", project.src)
        return str()

    # get domain
    domain = translate.get("domain")
    if not domain:
        domain = xml_elem.find("project").get("name")
    return domain

def get_name_from_qiproject(project):
    """Get the application name for gettext.
    If no project or translate tag is found return str().
    If no domain is found in translate tag, <project_name> is return."""
    xml_elem = qisys.qixml.read(project.qiproject_xml)
    root = xml_elem.getroot()
    if root.tag != "project":
        ui.error("No tag project in qiproject.xml for project", project.src)
        return str()

    translate = root.find("translate")
    if translate is None:
        ui.warning("No tag translate in qiproject.xml for project", project.src)
        return str()

    # get domain
    name = translate.get("name")
    if not name:
        name = xml_elem.find("project").get("name")
    return name

def get_locale_from_qiproject(project):
    """Get a list of supported locale.
    If no project or translate tag is found return list().
    If no locale is found in translate tag, ["en_US"] is return."""
    xml_elem = qisys.qixml.read(project.qiproject_xml)
    root = xml_elem.getroot()
    if root.tag != "project":
        ui.error("No tag project in qiproject.xml for project", project.src)
        return list()

    translate = root.find("translate")
    if translate is None:
        ui.warning("No tag translate in qiproject.xml for project", project.src)
        return list()

    # get locale
    linguas = translate.get("linguas").split()
    if not linguas:
        linguas = ["en_US"]
    return linguas

def get_tr_framework(project):
    """Get tr framework.
    Return gettext if using gettext, qt if using qt, str() otherwise."""
    xml_elem = qisys.qixml.read(project.qiproject_xml)
    root = xml_elem.getroot()
    if root.tag != "project":
        ui.error("No tag project in qiproject.xml for project " + project.src)
        return str()

    translate = root.find("translate")
    if translate is None:
        ui.warning("No tag translate in qiproject.xml for project " + project.src)
        return str()

    # get locale
    tr = translate.get("tr").split()
    if tr and tr[0] == "gettext":
        return "gettext"
    elif tr and tr[0] == "qt":
        return "qt"
    return str()
