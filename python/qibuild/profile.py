## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

""" Tools to handle build profiles


"""

import qisys.qixml

class Profile:
    """ A profile is just a set of CMake flags for now.
    If has a name you can specify when building using -p

    """
    def __init__(self, name):
        self.name = name
        self.cmake_flags = list()

    def elem(self):
        elem = qisys.qixml.etree.Element("profile")
        elem.set("name",  self.name)
        if self.cmake_flags:
            cmake_elem = qisys.qixml.etree.Element("cmake")
            flags_elem = qisys.qixml.etree.Element("flags")
            cmake_elem.append(flags_elem)
            for flag in self.cmake_flags:
                (key, value) = flag.split("=")
                flag_elem = qisys.qixml.etree.Element("flag")
                flag_elem.set("name", key)
                flag_elem.text = value
                flags_elem.append(flag_elem)
            elem.append(cmake_elem)
        return elem

    def __eq__(self, other):
        return self.cmake_flags == other.cmake_flags

    def __ne__(self, other):
        return not self.__eq__(other)


def parse_profiles(xml_path):
    """ Parse .qi/qibuild.xml. Return a dict
    name -> Profile
    """
    res = dict()
    tree = qisys.qixml.read(xml_path)
    root = tree.getroot()
    profile_elems = root.findall("profiles/profile")
    for profile_elem in profile_elems:
        profile_name = qisys.qixml.parse_required_attr(profile_elem, "name")
        profile = Profile(profile_name)
        res[profile_name] = profile
        cmake_elem = profile_elem.find("cmake")
        if cmake_elem is None:
            continue
        flags_elem = cmake_elem.find("flags")
        if flags_elem is None:
            continue
        flag_elems = flags_elem.findall("flag")
        for flag_elem in flag_elems:
            key = qisys.qixml.parse_required_attr(flag_elem, "name")
            value = flag_elem.text.strip()
            to_add = "%s=%s" % (key, value)
            profile.cmake_flags.append(to_add)
    return res

def add_profile(xml_path, profile):
    """ Add a new profile to an XML file

    """
    tree = qisys.qixml.read(xml_path)
    root = tree.getroot()
    profiles = root.find("profiles")
    if profiles is None:
        profiles = qisys.qixml.etree.Element("profiles")
        root.append(profiles)
    profiles.append(profile.elem())
    qisys.qixml.write(tree, xml_path)
