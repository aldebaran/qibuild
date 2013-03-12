""" Manage the manifests used by the worktree

Examples:

  # remove a manifest from the list
  qisrc manifest --remove my_manifest

  # clone a new manifest
  qisrc manifest --add my_manifest git@example/manifest.git

  # change the groups used by this manifest
  qisrc manifest my_manifest --groups my_group

  # checkt that a manifest is correct before pushing it:
  qisrc manifest --check /path/to/manifest.xml

"""

from qisys import ui
import qisrc.parsers

import sys

def configure_parser(parser):
    qisrc.parsers.worktree_parser(parser)
    qisrc.parsers.groups_parser(parser)
    group = parser.add_argument_group("manifest options")
    group.add_argument("--add", action="store_true", dest="add",
                        help="add a new manifest: name url")
    group.add_argument("--rm", "--remove", action="store_true", dest="remove",
                        help="remove a manifest: name")
    group.add_argument("--check", action="store_true", dest="check",
                        help="check that a manifest is correct: path")
    group.add_argument("--list", action="store_true",
                        help="list the manifests")
    group.add_argument("name", metavar="NAME", nargs="?")
    group.add_argument("-b", "--branch",
                       help="the branch to use when fetching the manifest from a "
                            "git url")
    group.add_argument("url_or_path", metavar="URL", nargs="?")
    parser.set_defaults(branch="master")


def do(args):
    git_worktree = qisrc.parsers.get_git_worktree(args, sync_first=False)
    if args.list:
        list_manifests(git_worktree)
    elif args.remove:
        remove_manifest(git_worktree, args)
    elif args.add:
        add_manifest(git_worktree, args)
    elif args.check:
        check_manifest(git_worktree, args)
    else:
        configure_manifest(git_worktree, args)


def list_manifests(git_worktree):
    if not git_worktree.manifests:
        ui.info("No manifest yet. Use qisrc manifest --add to get one")
        return
    ui.info(ui.green, "Manifests configured in",
            ui.reset, ui.bold, git_worktree.root)
    for name, manifest in git_worktree.manifests.iteritems():
        ui.info(ui.green, " * ", ui.blue, name)
        ui.info(ui.tabs(2), "url:", manifest.url)
        if manifest.groups:
            ui.info(ui.tabs(2), "groups:", ", ".join(manifest.groups))


def remove_manifest(git_worktree, args):
    if not args.name:
        raise Exception("Please specify a name when using --remove")
    name = args.name
    check_exists(git_worktree, name)
    git_worktree.remove_manifest(name)

def add_manifest(git_worktree, args):
    if not args.name or not args.url_or_path:
        raise Exception("Please specify a name and a url when using --add")
    name = args.name
    url = args.url_or_path
    git_worktree.configure_manifest(name, url, groups=args.groups,
                                    branch=args.branch)

def configure_manifest(git_worktree, args):
    name = args.name
    check_exists(git_worktree, name)
    if args.url_or_path:
        url = args.url_or_path
    else:
        url = git_worktree.manifests[name].url
    git_worktree.configure_manifest(name, url, groups=args.groups,
                                    branch=args.branch)

def check_manifest(git_worktree, args):
    if not args.name:
        raise Exception("Please specify a name and a path when using --check")
    name = args.name
    check_exists(git_worktree, name)
    xml_path = args.url_or_path
    git_worktree.check_manifest(name, xml_path)

def check_exists(git_worktree, name):
    if not name in git_worktree.manifests:
        ui.error("No such manifest:", name)
        ui.info("""
Tips:
* Use `qisrc manifest --list` to see the list of the manifests
""")
        sys.exit(1)
