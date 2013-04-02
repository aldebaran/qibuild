import os
import qisys.sh

def test_worktree(worktree):
    assert len(worktree.projects) == 0
    assert os.path.exists(worktree.worktree_xml)

def test_tmp_conf(tmpfiles):
    qibuild_xml = qisys.sh.get_config_path("qi", "qibuild.xml")
    assert os.path.exists(os.path.dirname(qibuild_xml))
    assert not os.path.exists(qibuild_xml)
