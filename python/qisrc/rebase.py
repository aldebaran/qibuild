import copy

from qisys import ui
import qisrc.manifest

def rebase_worktree(git_worktree, git_projects, branch):
    if not git_projects:
        return

    manifest_repo = git_worktree._syncer.manifest_repo
    ref = "origin/" + branch
    manifest = qisrc.manifest.from_git_repo(manifest_repo, ref)
    groups = git_worktree._syncer.manifest.groups
    repos = manifest.get_repos(groups=groups)
    remote_projects = dict()
    for repo in repos:
        project = git_worktree.find_repo(repo)
        remote_project = copy.deepcopy(project)
        remote_project.read_remote_config(repo, quiet=True)
        remote_projects[remote_project.src] = remote_project

    max_src = max(len(x.src) for x in git_projects)
    for i, git_project in enumerate(git_projects):
        ui.info_count(i, len(git_projects),
                      git_project.src.ljust(max_src), end="\r")
        git = qisrc.git.Git(git_project.path)
        local_branch = git_project.default_branch
        if git.get_current_branch() != local_branch.name:
            ui.info(ui.brown, git_project.src, "  [skipped]")
            ui.info("Not on %s branch" % local_branch.name)
            continue

        if not git_project.src in remote_projects:
            ui.info(ui.brown, git_project.src, "  [skipped]")
            ui.info("No match for %s on %s branch" % (git_project.src, branch))
            continue

        remote_project = remote_projects[git_project.src]
        branch_name = remote_project.default_branch.name
        remote_name = remote_project.default_remote.name
        ref = "%s/%s" % (remote_name, branch_name)
        rc, out = git.call("rebase", ref, raises=False)
        if rc != 0:
            ui.info(ui.red, git_project.src, "  [failed]")
            git.call("rebase", "--abort")
