# Copyright (c) 2012-2018 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the COPYING file.
import os

import qisys.sh

from qitoolchain.binary_package import convert_to_qibuild, open_package
from qibuild.cmake.modules import add_cmake_module_to_archive


def convert_package(package_path, name, interactive=False):
    dest_dir = os.path.dirname(package_path)
    package = open_package(package_path)

    with qisys.sh.TempDir() as tmp:
        qibuild_package_path = convert_to_qibuild(package, output_dir=tmp)
        add_cmake_module_to_archive(qibuild_package_path, name, interactive=interactive)
        src = os.path.abspath(qibuild_package_path)
        dst = os.path.join(dest_dir, os.path.basename(qibuild_package_path))
        dst = os.path.abspath(dst)
        qisys.sh.mv(src, dst)
        qibuild_package_path = dst
    return qibuild_package_path
