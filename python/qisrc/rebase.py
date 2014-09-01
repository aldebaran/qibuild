from qisys import ui
import qisys.interact

import qisrc.manifest

def rebase_worktree(git_worktree, git_projects, branch=None,
                    push=False, dry_run=False):
    if not git_projects:
        return
    upstream_projects = git_worktree.get_projects_on_branch(branch)
    rebased_projects, errors = rebase_projects(git_projects, upstream_projects, branch)
    if errors:
        raise Exception("Failed to rebase some projects")

    if push:
        push_projects(rebased_projects, dry_run=dry_run)


def push_projects(git_projects, dry_run=False):
    if not git_projects:
        return
    ui.info(ui.green, "Pushing ", len(git_projects), "projects")
    for i, git_project in enumerate(git_projects):
        default_branch = git_project.default_branch.name
        remote_branch = git_project.default_branch.remote_branch
        ui.info_count(i, len(git_projects), git_project.src)
        git = qisrc.git.Git(git_project.path)
        if git_project.review:
            push_remote = git_project.review_remote
        else:
            push_remote = git_project.default_remote
        remote_ref = "%s/%s" % (push_remote.name, remote_branch)
        display_changes(git, default_branch, remote_ref)
        answer = qisys.interact.ask_yes_no("OK to push?", default=False)
        if not answer:
            return
        to_push = "%s:%s" % (default_branch, remote_branch)
        push_args = [push_remote.name, to_push]
        push_args.append("--force")
        if dry_run:
            push_args.append("--dry-run")
        rc, out = git.push(*push_args, raises=False)
        if rc == 0:
            ui.info(out)
        else:
            ui.error(out)


def rebase_projects(git_projects, upstream_projects, branch):
    rebased_projects = list()
    errors = list()
    max_src = max(len(x.src) for x in git_projects)
    for i, git_project in enumerate(git_projects):
        ui.info_count(i, len(git_projects), git_project.src)
        git = qisrc.git.Git(git_project.path)
        git.fetch()
        local_branch = git_project.default_branch.name
        remote_branch = git_project.default_branch.remote_branch
        remote_name = git_project.default_remote.name
        remote_ref = "%s/%s" % (remote_name, remote_branch)
        if git.get_current_branch() != local_branch:
            ui.info(ui.brown, git_project.src, "[skipped]")
            ui.info("Not on %s branch" % local_branch)
            continue

        if not git_project.src in upstream_projects:
            ui.info(ui.brown, git_project.src, "[skipped]")
            ui.info("No match for %s on %s branch" % (git_project.src, branch))
            continue

        status = qisrc.git.get_status(git, local_branch, remote_ref)
        if status == "ahead":
            ui.info(ui.brown, git_project.src, "[skipped]")
            ui.info("You have local changes not pushed yet")
            continue
        if status == "behind":
            ui.info(ui.brown, git_project.src, "[skipped]")
            ui.info("Local branch is not up-to-date")
            continue

        upstream_project = upstream_projects[git_project.src]
        upstream_branch = upstream_project.default_branch.name
        upstream_ref = "%s/%s" % (upstream_project.default_remote.name, upstream_branch)

        status = qisrc.git.get_status(git, local_branch, upstream_ref)
        if status == "no-diff":
            ui.info("no changes")
            continue
        if status == "behind":
            git.merge(upstream_ref)
            rebased_projects.append(git_project)
        else:
            git.call("tag", "-f", "before-rebase")
            rc, out = git.call("rebase", upstream_ref, raises=False)
            if rc == 0:
                rebased_projects.append(git_project)
            else:
                ui.info(ui.red, git_project.src, "  [failed]")
                ui.info(out)
                git.call("rebase", "--abort", raises=False)
                errors.append(git_project)
                continue
    return rebased_projects, errors

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
