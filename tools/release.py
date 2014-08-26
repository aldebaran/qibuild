"""" To be run for each qibuild release """

import argparse
import os

import qisys.sh
import qisrc.git

FILES_TO_PATCH = [
    "setup.py",
    "cmake/qibuild/version.cmake",
    "doc/source/conf.in.py",
    "python/qisys/main.py",
]

def fix_version_for_file(filename, old_version, new_version):
    with open(filename, "r") as fp:
        old_contents = fp.read()
    new_contents = old_contents.replace(old_version, new_version)
    with open(filename, "w") as fp:
        fp.write(new_contents)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("version")
    args = parser.parse_args()
    version = args.version
    this_dir = os.path.dirname(__file__)
    qibuild_root = os.path.join(this_dir, "..")
    git = qisrc.git.Git(qibuild_root)
    ok, message = git.require_clean_worktree()
    if not ok:
        raise Exception(message)
    for filename in FILES_TO_PATCH:
        full_path = os.path.join(qibuild_root, filename)
        fix_version_for_file(full_path, "next", version)
    git.commit("--all", "-m", "qibuild %s" % version)
    git.call("tag", "v" + version)
    for filename in FILES_TO_PATCH:
        full_path = os.path.join(qibuild_root, filename)
        fix_version_for_file(filename, version, "next")
    git.commit("--all", "-m", "start next development")
    print "All OK feel free to push"


if __name__ == "__main__":
    main()
