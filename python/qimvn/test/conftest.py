# Make all fixtures from qisys.test available to qibuild.test
from qisys.test.conftest import *
from qitoolchain.test.conftest import *

# Import usefull fixture from qibuild.test
from qibuild.test.conftest import qibuild_action
from qibuild.test.conftest import record_messages

from qibuild import run

# pylint: disable-msg=E1103
@pytest.fixture
def qimvn_action(request):
    res = QiMvnAction()
    return res

class QiMvnAction(TestAction):
    def __init__(self, worktree_root=None):
        pass

    def is_in_jar(self, jarpath, filename):
        """ Unpack file given jar
        """
        # Extract file from jar. If file is not in jar, command will fail.
        if qisys.command.call(["jar", "-xf", jarpath, filename]) != 0:
            return False
        return os.path.exists(os.path.join(os.path.dirname(jarpath), filename))
