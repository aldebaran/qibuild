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
