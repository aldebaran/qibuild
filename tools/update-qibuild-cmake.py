## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

# Update all the qibuild.cmake files in a git repo
# (this will be done automatically by `qibuild configure`,
# but this tool can still be handy)

import os
import argparse
import subprocess
import shutil

def update_qibuild_cmake(template_path, git_repo):
    """ Update qibuild.cmake files in a git repo.

    - Check that repo is clean
    - Find all the qibuild.cmake files in the git repo,
      replace them by the template
    - Prepare a commit with a nice message

    """
    try:
        out = subprocess.check_output(["git", "status"], cwd=git_repo)
    except subprocess.CalledProcessError, e:
        mess  = "Could not run git status in %s\n" % git_repo
        mess += "Error was:\n"
        mess += str(e)
        raise Exception(mess)
    if not "clean" in out:
        mess  = "git repo not clean\n"
        mess += "Git status said:\n"
        mess += out
        raise Exception(mess)

    out = subprocess.check_output(["git", "ls-files"], cwd=git_repo)
    filenames = out.splitlines()
    for filename in filenames:
        basename = os.path.basename(filename)
        full_path = os.path.join(git_repo, filename)
        if basename == "qibuild.cmake":
            print "patching", filename
            shutil.copy(template_path, full_path)

    subprocess.check_call(["git", "commit", "-a", "-m", "update qibuild.cmake"],
        cwd=git_repo)



def main():
    """ Parse command line arguments """
    parser = argparse.ArgumentParser()
    parser.add_argument("template_path")
    parser.add_argument("git_repo")
    args = parser.parse_args()
    update_qibuild_cmake(args.template_path, args.git_repo)


if __name__ == "__main__":
    main()


