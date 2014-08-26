from qisys.test.conftest import *

class QiPyAction(TestAction):
    def __init__(self):
        super(QiPyAction, self).__init__("qipy.actions")

# pylint: disable-msg=E1101
@pytest.fixture
def qipy_action(cd_to_tmpdir):
    res = QiPyAction()
    return res
