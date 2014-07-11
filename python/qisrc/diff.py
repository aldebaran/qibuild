"""" Computing diffs between manifest branches """

from qisys import ui
import qisrc.git

def diff_worktree(git_worktree, git_projects, branch, cmd=None):
    """ Run  `git <cmd> local_branch..remote_branch` for every project

    """
    if not cmd:
        cmd = ["log"]
    remote_projects = git_worktree.get_projects_on_branch(branch)
    for git_project in git_projects:
        remote_project = remote_projects.get(git_project.src)
        if not remote_project:
            continue
        git = qisrc.git.Git(git_project.path)
        local_branch = git.get_current_branch()
        remote_branch = remote_project.default_branch.name
        remote_ref = "%s/%s" % (remote_project.default_remote.name, remote_branch)
        full_cmd = cmd + ["%s..%s" % (local_branch, remote_ref)]
        rc, out = git.call(*full_cmd, raises=False)
        if rc != 0:
            continue
        if not out:
            continue
        ui.info(git_project.src)
        ui.info("-" * len(git_project.src))
        ui.info(out)
        ui.info()
