# Make all fixtures from qisys.test available to qibuild.test
from qisys.test.conftest import *
from qitoolchain.test.conftest import *
import qisys.qixml

# Import useful fixture from qibuild.test
from qibuild.test.conftest import qibuild_action
from qibuild.test.conftest import record_messages

from qibuild import run

# pylint: disable-msg=E1103
@pytest.fixture
def qimvn_action(request):
    res = QiMvnAction()
    return res

@pytest.fixture
# pylint: disable-msg=E1103
def local_repository(tmpdir):
    return "file://" + tmpdir.ensure("maven", dir=True).strpath

def add_repository(project, repository_url):
    """ Add a local repository in the tmpdir """
    import xml.etree
    xml.etree.ElementTree.register_namespace('', 'http://maven.apache.org/POM/4.0.0')
    pom_xml = os.path.join(project.path, "pom.xml")
    root = qisys.qixml.read(pom_xml).getroot()
    to_append = qisys.qixml.etree.fromstring(
"""
<repositories>
  <repository>
    <id>local-repository</id>
  <name>Native</name>
  <url>{url}</url>
  </repository>
</repositories>
        """.format(url=repository_url)
    )
    root.append(to_append)
    qisys.qixml.write(root, pom_xml)


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
