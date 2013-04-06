from qisys.test.conftest import *


import qitoolchain
import qitoolchain.toolchain

class Toolchains():
    """ A class to help qitoolchain testing """
    def __init__(self):
        tmpdir = tempfile.mkdtemp(prefix="test-qitoolchain")
        self.tmp = py.path.local(tmpdir)

    def clean(self):
        self.tmp.remove()

    def create(self, name):
        toolchain = qitoolchain.toolchain.Toolchain(name)
        return toolchain

    def add_package(self, name, package_name):
        toolchain = qitoolchain.get_toolchain(name)
        package_path = self.tmp.mkdir(package_name)
        package = qitoolchain.Package(package_name, package_path.strpath)
        toolchain.add_package(package)
        return package

@pytest.fixture
def toolchains(request):
    res = Toolchains()
    request.addfinalizer(res.clean)
    return res
