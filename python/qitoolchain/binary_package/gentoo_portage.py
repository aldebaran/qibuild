#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
"""
This module implements the Gentoo binary packages class,
which take benefit from portage's modules.

This module depends on portage:
http://www.gentoo.org/proj/en/portage/index.xml
"""
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import os
import re
import portage

import qisys
from qitoolchain.binary_package.gentoo import GentooPackage as GentooNoPortagePackage

_ARCH_VARIANT = r'-m(arch|cpu)=(\S+)\s'
_RE_ARCH_VARIANT = re.compile(_ARCH_VARIANT)

_DEPENDENCY = {
    'buildtime': 'DEPEND',
    'runtime': 'RDEPEND',
    'post-install': 'PDEPEND',
}


def _get_pkg_arch(metadata_dir):
    """
    Return the tuple architecture/variant for which the package has been built.
    :return: the tuple (architecture, variant)
    """
    def _parse_march(flags_file):
        value = None
        with open(flags_file, 'r') as fcflags:
            cflags = fcflags.read()
        match = _RE_ARCH_VARIANT.search(cflags)
        if match is not None:
            value = match.group(2)
        return value
    with open(os.path.join(metadata_dir, 'CHOST'), 'r') as fchost:
        arch = fchost.readline().strip().split('-', 1)[0]
    variant = None
    for flag_file in ['CFLAGS', 'CXXFLAGS']:
        variant = _parse_march(os.path.join(metadata_dir, flag_file))
        if variant is not None:
            break
    return arch, variant


class GentooPackage(GentooNoPortagePackage):
    """ Gentoo binary package endpoint using ``portage``. """

    def __init__(self, package_path):
        """ GentooPackage Init """
        GentooNoPortagePackage.__init__(self, package_path)

    def _load(self):
        """
        Read the metadata from the binary package and store them in the instance.
        :return: the metadata dictionary
        """
        with qisys.sh.TempDir() as work_dir:
            pkg = portage.xpak.tbz2(self.path)
            pkg.decompose(work_dir, cleanup=0)
            arch, arch_variant = _get_pkg_arch(work_dir)
            with open(os.path.join(work_dir, 'PF'), 'r') as fpf:
                pf = fpf.readline().strip()
            name, version, revision = portage.versions.pkgsplit(pf)
            dependency = dict()
            for dep, dep_filename in _DEPENDENCY.items():
                dep_path = os.path.join(work_dir, dep_filename)
                if not os.path.exists(dep_path):
                    dependency[dep] = list()
                    continue
                with open(dep_path, 'r') as fdep:
                    dependency[dep] = fdep.read().strip().split()
        dependency['all'] = list()
        for dep_list in _DEPENDENCY:
            dependency['all'].extend(dependency[dep_list])
        for dep, dep_list in dependency.items():
            dependency[dep] = list(set(dep_list))
        metadata = {
            'name': name,
            'version': version,
            'revision': revision,
            'arch': arch,
            'arch_variant': arch_variant,
            'dependencies': dependency,
        }
        self.metadata = metadata
