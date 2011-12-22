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

""" Collection of parser fonctions for various actions
"""

import qibuild
from qibuild.cmdparse import default_parser

def toc_parser(parser):
    """ Parser settings for every action using a toc dir
    """
    qibuild.worktree.work_tree_parser(parser)
    parser.add_argument('-c', '--config',
        help='The configuration to use. '
             'If a toolchain exists with the same name '
             'exists it will be used. '
             'The settings from [config "<name>"] sections will '
             'also be used')

def build_parser(parser):
    """ Parser settings for every action doing builds
    """
    group = parser.add_argument_group("build configuration arguments")
    group.add_argument("--release", action="store_const", const="release",
        dest="build_type",
        help="Build in release (set CMAKE_BUILD_TYPE=RELEASE)")
    group.add_argument("--debug", action="store_const", const="debug",
        dest="build_type",
        help="Build in debug (set CMAKE_BUILD_TYPE=DEBUG)")
    group.add_argument("--build-type", action="store",
        dest="build_type",
        help="CMAKE_BUILD_TYPE usually DEBUG or RELEASE")
    group.add_argument("--cmake-generator", action="store",
        help="Specify the CMake generator")
    group.add_argument("-j", dest="num_jobs", type=int,
        help="Number of jobs to use")
    parser.set_defaults(debug=True)
    parser.set_defaults(num_jobs=1)
    parser.set_defaults(build_type="debug")

def project_parser(parser):
    """ Parser settings for every action using several toc projects
    """
    parser.add_argument("-a", "--all", action="store_true",
        help="Work on all projects")
    parser.add_argument("-s", "--single", action="store_true",
        help="Work on specified projects without taking dependencies into account.")
    parser.add_argument("projects", nargs="*", metavar="PROJECT", help="Project name(s)")
    parser.set_defaults(single=False, projects = list())
