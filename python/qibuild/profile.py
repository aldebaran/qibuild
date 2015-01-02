## Copyright (c) 2012-2015 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

""" Tools to handle build profiles


"""

import os
import qisys.qixml

class Profile:
    """ A profile is just a set of CMake flags for now.
    If has a name you can specify when building using
    ``qibuild configure --profile <name>``

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
            for (key, value) in self.cmake_flags:
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
    if not os.path.exists(xml_path):
        with open(xml_path, "w") as fp:
            fp.write("<qibuild />")
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
            to_add = ((key, value))
            profile.cmake_flags.append(to_add)
    return res

def configure_build_profile(xml_path, name, flags):
    """ Add a new profile to an XML file """
    profile = Profile(name)
    profile.cmake_flags = flags
    tree = qisys.qixml.read(xml_path)
    root = tree.getroot()
    profiles_elem = root.find("profiles")
    if profiles_elem is None:
        profiles_elem = qisys.qixml.etree.Element("profiles")
        root.append(profiles_elem)
    for profile_elem in profiles_elem.findall("profile"):
        if profile_elem.get("name") == name:
            profiles_elem.remove(profile_elem)
    profiles_elem.append(profile.elem())
    qisys.qixml.write(tree, xml_path)

def remove_build_profile(xml_path, name):
    """ Remove a build profile from XML file """
    tree = qisys.qixml.read(xml_path)
    root = tree.getroot()
    profiles = root.find("profiles")
    if profiles is None:
        mess = "No profiled named '{name}' in {xml_path}"
        mess = mess.format(name=name, xml_path=xml_path)
        raise Exception(mess)
    match_elem = None
    for profile in profiles:
        if profile.get("name") == name:
            match_elem = profile
    if match_elem is None:
        raise Exception("No such profile: " + name)
    profiles.remove(match_elem)
    qisys.qixml.write(tree, xml_path)
