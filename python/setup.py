# Setup.py file

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
    "qitools",
    "qitools.external",
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


