from qisys import ui
import qisys.interact

import qisrc.manifest

def rebase_worktree(git_worktree, git_projects, branch,
                    push=False, undo=False):
    if not git_projects:
        return

    remote_projects = git_worktree.get_projects_on_branch(branch)
    if undo:
        undo_rebase(git_projects)
    else:
        rebased_projects = rebase_projects(git_projects, remote_projects, branch)
        if push:
            push_projects(rebased_projects)


def push_projects(git_projects):
    ui.info(ui.green, "Pushing projects")
    for i, git_project in enumerate(git_projects):
        ui.info_count(i, len(git_projects), git_project.src)
        git = qisrc.git.Git(git_project.path)
        branch_name = git_project.default_branch.name
        if git_project.review:
            remote = git_project.review_remote
        else:
            remote = git_project.default_remote
        remote_ref = "%s/%s" % (remote.name, branch_name)
        display_changes(git, branch_name, remote_ref)
        answer = qisys.interact.ask_yes_no("Continue?", default=False)
        if not answer:
            return
        to_push = "%s:%s" % (branch_name, branch_name)
        rc, out = git.push(remote.name, to_push, "--force",
                        raises=False)
        if rc != 0:
            ui.error(out)

def undo_rebase(git_projects):
    ui.info(ui.green, "Undoing push for", ui.red, len(git_projects),
            ui.green, "projects")
    for i, git_project in enumerate(git_projects):
        ui.info_count(i,  len(git_projects), git_project.src)
        if not git_project.default_branch:
            continue
        if git_project.review:
            remote = git_project.review_remote
        else:
            remote = git_project.default_remote
        remote_name = remote.name
        branch_name = git_project.default_branch.name
        git = qisrc.git.Git(git_project.path)
        git.reset("--hard", "before-rebase")
        to_push = "%s:%s" % (branch_name, branch_name)
        git.push("--force", remote_name, to_push)

def rebase_projects(git_projects, remote_projects, branch):
    rebased_projects = list()
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
        # tag where we were for later use:
        git.call("tag", "-f", "before-rebase")
        rc, out = git.call("rebase", ref, raises=False)
        if rc == 0:
            rebased_projects.append(git_project)
        else:
            ui.info(ui.red, git_project.src, "  [failed]")
            ui.info(out)
            git.call("rebase", "--abort", raises=False)
            continue
    return rebased_projects

def display_changes(git, remote_ref, branch_name):
    rc, out = git.call("shortlog", "%s..%s" % (remote_ref, branch_name),
                    raises=False)
    if out:
        ui.info(ui.bold, "Remote changes:")
    ui.info(out)
    rc, out = git.call("shortlog", "%s..%s" % (branch_name, remote_ref),
                        raises=False)
    if out:
        ui.info(ui.bold, "Local changes")
    ui.info(out)
