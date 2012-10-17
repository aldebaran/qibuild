## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

""" Tools to handle build profiles


"""

import qixml

class Profile:
    """ A profile is just a set of CMake flags for now.
    If has a name you can specify when building using -p

    """
    def __init__(self, name):
        self.name = name
        self.cmake_flags = list()

    def elem(self):
        elem = qixml.etree.Element("profile")
        elem.set("name",  self.name)
        if self.cmake_flags:
            cmake = qixml.etree.Element("cmake")
            cmake.set("flags", "  ".join(self.cmake_flags))
            elem.append(cmake)
        return elem

    def __eq__(self, other):
        return set(self.cmake_flags) == set(other.cmake_flags)

    def __ne__(self, other):
        return not self.__eq__(other)


def parse_profiles(xml_path):
    """ Parse .qi/qibuild.xml. Return a dict
    name -> Profile
    """
    res = dict()
    tree = qixml.read(xml_path)
    root = tree.getroot()
    profile_elems = root.findall("profiles/profile")
    for profile_elem in profile_elems:
        profile_name = qixml.parse_required_attr(profile_elem, "name")
        profile = Profile(profile_name)
        res[profile_name] = profile
        cmake_elem = profile_elem.find("cmake")
        if cmake_elem is None:
            continue
        profile.cmake_flags = qixml.parse_list_attr(cmake_elem, "flags")
    return res

def add_profile(xml_path, profile):
    """ Add a new profile to an XML file

    """
    tree = qixml.read(xml_path)
    root = tree.getroot()
    profiles = root.find("profiles")
    if profiles is None:
        profiles = qixml.etree.Element("profiles")
        root.append(profiles)
    profiles.append(profile.elem())
    qixml.write(tree, xml_path)
