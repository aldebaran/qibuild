## Copyright (c) 2012, 2013 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

""" Run performance tests.
"""

import os
import re
import signal
import sys
import csv
from collections import OrderedDict

from qisys import ui
import qisys


def sigint_handler(signum, frame):
    def double_sigint(signum, frame):
        ui.warning('Exiting main program without caring (may leave ' +
                   'zombies and the like).')
        sys.exit(1)
    ui.warning('Received keyboard interrupt. Killing all processes ' +
               '. This may take few seconds.')
    qisys.command.SIGINT_EVENT.set()
    signal.signal(signal.SIGINT, double_sigint)


def run_perfs(project, pattern=None, dry_run=False):
    """ Called by qibuild test --perf

    :param project: name of the project to run
    :param pattern: run only perf tests which name matches this pattern
    :param dry_run: only print out which perfs tests would be run

    """
    build_dir = project.build_directory
    signal.signal(signal.SIGINT, sigint_handler)
    all_tests = parse_perflist_files(build_dir)

    tests = list()

    if pattern:
        try:
            tests = [x for x in all_tests if re.search(pattern, x[0])]
        except Exception as e:
            mess = "Invalid pattern \"{}\": {}".format(pattern, e)
            raise Exception(mess)
        if not tests:
            mess = "No performance tests matching %s\n" % pattern
            mess += "Known performance tests are:\n"
            for x in all_tests:
                mess += "  * " + x[0] + "\n"
            raise Exception(mess)
    else:
        tests = all_tests

    if not tests:
        ui.warning("No performance tests found for project", project.name)
        return

    if dry_run:
        ui.info(ui.green, "List of performance tests for", project.name)
        for x in tests:
            ui.info(ui.green, " * ", ui.reset, x[0])
        return

    ui.info(ui.green, "Running perfomance test for", project.name, "...")
    results = OrderedDict()
    for test in tests:
        name = test[0]
        cmd = [test[1]]
        try:
            timeout = int(test[2])
        except:
            timeout = None
        ui.info(ui.green, " * ", ui.reset, name)
        test_result = os.path.join(project.build_directory, "perf-results")
        qisys.sh.mkdir(test_result)
        output_xml = os.path.join(test_result, name + ".xml")
        cmd.extend(["--output", output_xml])
        process = qisys.command.Process(cmd, verbose=True)
        process.run(timeout)
        print(process.out)
        if timeout and process.return_type == qisys.command.Process.TIME_OUT:
            print("Timed out (%is)" % timeout)
        success = process.return_type == qisys.command.Process.OK
        if not success:
            qisys.sh.rm(output_xml)
            ui.info(ui.red, "Process exited unexpectedly, removed XML output")
        results[name] = success

    # Recap results
    failed = [x for x in results.values() if not x]
    total = len(tests)
    if not failed:
        ui.info("Ran %i tests" % total)
        ui.info("All pass. Congrats!")
        return True
    else:
        ui.error("Ran %i tests, %i failures" % (total, len(failed)))
        padding = max(len(x) for x in results.keys())
        for test, success in results.items():
            if not success:
                ui.info(ui.bold, " -", ui.red, test.ljust(padding + 5))
        return False


def parse_perflist_files(build_dir):
    """ Looks for perflist.txt in build_dir.
        And parse it.
    """
    perflist_file = os.path.join(build_dir, "perflist.txt")
    if not os.path.exists(perflist_file):
        return list()

    perf_tests = list()

    with open(perflist_file, "r") as csvfile:
        content = csv.reader(csvfile, delimiter=';')
        for row in content:
            perf_tests.append(row)

    return perf_tests

