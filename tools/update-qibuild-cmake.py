## Copyright (c) 2011, Aldebaran Robotics
## All rights reserved.
##
## Redistribution and use in source and binary forms, with or without
## modification, are permitted provided that the following conditions are met:
##     * Redistributions of source code must retain the above copyright
##       notice, this list of conditions and the following disclaimer.
##     * Redistributions in binary form must reproduce the above copyright
##       notice, this list of conditions and the following disclaimer in the
##       documentation and/or other materials provided with the distribution.
##     * Neither the name of the Aldebaran Robotics nor the
##       names of its contributors may be used to endorse or promote products
##       derived from this software without specific prior written permission.
##
## THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
## ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
## WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
## DISCLAIMED. IN NO EVENT SHALL Aldebaran Robotics BE LIABLE FOR ANY
## DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
## (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
## LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
## ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
## (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
## SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

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


