## Copyright (c) 2011, Aldebaran Robotics
## All rights reserved.
##
## Redistribution and use in source and binary forms, with or without
## modification, are permitted provided that the following conditions are met:
##     * Redistributions of source code must retain the above copyright
##       notice, this list of conditions and the following disclaimer.
##     * Redistributions in binary form must reproduce the above copyright
##       notice, this list of conditions and the following disclaimer in the
##       documentation and/or other materials provided with the distribution.
##     * Neither the name of the Aldebaran Robotics nor the
##       names of its contributors may be used to endorse or promote products
##       derived from this software without specific prior written permission.
##
## THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
## ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
## WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
## DISCLAIMED. IN NO EVENT SHALL Aldebaran Robotics BE LIABLE FOR ANY
## DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
## (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
## LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
## ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
## (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
## SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

from distutils.core import setup
import sys
import os

def check_config():
    """ qibuild script can only be installed if
    qibuild/config.py has been configured by cmake

    """
    cur_dir = os.path.abspath(os.path.dirname(__file__))
    config_py = os.path.join(cur_dir, "qibuild", "config.py")
    if not os.path.exists(config_py):
        print "Error, could not find %s" % config_py
        print "Did you run cmake? "
        sys.exit(2)

check_config()

packages = [
    "qibuild",
    "qibuild.external",
    "qisrc",
    "qisrc.actions",
    "qibuild",
    "qibuild.actions",
    "qitoolchain",
    "qitoolchain.actions",
]

scripts = [
    "bin/qisrc",
    "bin/qibuild",
    "bin/qitoolchain",
]

package_data = {
 "qibuild" : ["templates/build.cfg",
              "templates/build-default.cfg",
              "templates/project/CMakeLists.txt",
              "templates/project/main.cpp",
              "templates/project/qibuild.manifest"
              ]
}


setup(name = 'qibuild',
      version = "0.1",
      description = "The qiBuild Framework",
      author = "Aldebaran Robotics",
      author_email = "qi-dev@aldebaran-robotics.com",
      packages = packages,
      package_data = package_data,
      license = "BSD",
      scripts = scripts
)


