# Copyright (c) 2012-2018 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the COPYING file.

""" Tools to profile cmake execution

"""

import re
import os
import pickle

import qisys.sh

LOG_RE = re.compile(r"(.*?)\((\d+)\):")


def parse_cmake_log(input_file, qibuild_dir):
    """ Parse cmake logs

    Generate annotated source code for each cmake file in qibuild,
    """
    # cmake log is written like c:/path/to/qibuild/cmake/
    qibuild_dir = qisys.sh.to_posix_path(qibuild_dir)
    profile = dict()
    with open(input_file, "r") as fp:
        for line in fp:
            match = re.match(LOG_RE, line)
            if not match:
                continue
            (filename, line_no) = match.groups()
            if qibuild_dir not in filename:
                continue
            # 9 is len("/qibuild/")
            filename = filename[len(qibuild_dir) + 9:]
            filename = filename.replace("\\", "/")
            line_no = int(line_no)
            if filename not in profile:
                profile[filename] = dict()
            if line_no not in profile[filename]:
                profile[filename][line_no] = 0
            profile[filename][line_no] += 1
    dirname = os.path.dirname(input_file)
    profile_pickle = os.path.join(dirname, "profile.pickle")
    with open(profile_pickle, "w") as fp:
        pickle.dump(profile, fp)
    return profile


def gen_annotations(profile, out, qibuild_dir):  # pylint: disable=too-many-locals
    """ Write the files with the same layout , the same
    contents, and just a percentage of hits in the first
    column

    """
    partial_sums = [sum(profile[x].values()) for x in profile.keys()]
    grand_total = sum(partial_sums)
    pad = len(str(grand_total))
    for filename in profile.keys():
        orig_filename = os.path.join(qibuild_dir, "qibuild",
                                     filename)
        with open(orig_filename, "r") as fp:
            lines = fp.readlines()
        lines = [" " * (pad + 1) + x for x in lines]
        file_stats = profile[filename]

        for (line_no, hits) in file_stats.iteritems():
            orig_line = lines[line_no - 1]
            new_line = str(hits).rjust(pad) + orig_line[pad + 1:]
            lines[line_no - 1] = new_line
        new_filename = os.path.join(out, filename)
        new_dirname = os.path.dirname(new_filename)
        qisys.sh.mkdir(new_dirname, recursive=True)
        with open(new_filename, "w") as fp:
            fp.writelines(lines)
