import datetime
import multiprocessing
import os
import re
import sys

from qisys import ui
import qisys.command
import qitest.conf
import qitest.runner

class ProjectTestRunner(qitest.runner.TestSuiteRunner):
    """ Implements TestSuiteRunner for a qibuild/cmake project """

    def __init__(self, project):
        self.project = project
        self.perf = False
        self.nightly = False
        self.nightmare = False
        self._pattern = None
        self._coverage = False
        self._valgrind = False
        self._num_cpus = -1
        tests = qitest.conf.parse_tests(project.qitest_json)
        super(ProjectTestRunner, self).__init__(tests)
        for directory in (self.test_results_dir,
                          self.perf_results_dir):
            qisys.sh.rm(directory)
            qisys.sh.mkdir(directory)

    @property
    def launcher(self):
        """ Implements TestSuiteRunner.launcher """
        return ProcessTestLauncher(self)

    @property
    def test_results_dir(self):
        res = os.path.join(self.project.build_directory,
                           "test-results")
        return res

    @property
    def perf_results_dir(self):
        res = os.path.join(self.project.build_directory,
                           "perf-results")
        return res

    @property
    def tests(self):
        """ Override TestSuiteRunner.test to filter perf and nightly tests """
        res =  super(ProjectTestRunner, self).tests
        res = [x for x in res if x.get("perf", False) == self.perf]
        res = [x for x in res if x.get("nightly", False) == self.nightly]
        return res

    @property
    def num_cpus(self):
        return self._num_cpus

    @num_cpus.setter
    def num_cpus(self, value):
        if value == -1:
            return
        if not qisys.command.find_program("taskset"):
            mess = "taskset was not found on the system.\n"
            mess += "Cannot set number of CPUs used by the tests"
            raise Exception(mess)
        self._num_cpus = value

    @property
    def valgrind(self):
        return self._valgrind

    @valgrind.setter
    def valgrind(self, value):
        if not value:
            return
        if not qisys.command.find_program("valgrind"):
            raise Exception("valgrind was not found on the system")
        self._valgrind = value

    @property
    def coverage(self):
        return self._coverage

    @coverage.setter
    def coverage(self, value):
        if not value:
            return
        if not qisys.command.find_program("gcovr"):
            raise Exception("please install gcovr in order to measure coverage")


class ProcessTestLauncher(qitest.runner.TestLauncher):
    """ Implements TestLauncher using `qisys.command.Process```

    """
    def __init__(self, project_runner):
        self.suite_runner = project_runner
        self.project = self.suite_runner.project
        self.verbose = self.suite_runner.verbose
        self.valgrind_log = None
        self.perf_out = None
        self.test_out = None

    def launch(self, test):
        """ Implements TestLauncher.launch """
        self.perf_out = os.path.join(self.suite_runner.perf_results_dir,
                                     test["name"] + ".xml")
        self.test_out = os.path.join(self.suite_runner.test_results_dir,
                                     test["name"] + ".xml")
        res = qitest.result.TestResult(test)
        cmd = test["cmd"]
        if not os.path.exists(cmd[0]):
            res.ok = False
            res.message = (ui.red, cmd[0], "no such file or directory")
            return res
        self._update_test(test)

        cmd = test["cmd"]
        timeout = test["timeout"]
        env = test["env"]
        cwd = test["working_directory"]
        process = qisys.command.Process(cmd, cwd=cwd, env=env)
        start = datetime.datetime.now()
        process.run(timeout)
        end = datetime.datetime.now()
        delta = end - start

        res.time = float(delta.microseconds) / 10 ** 6 + delta.seconds
        res.out = process.out
        # Sometimes the process did not have any output,
        # but we still want to let the user know it ran
        if not process.out:
            res.out = "<no output>"

        message = self.get_message(process, timeout=timeout)
        if process.return_type == qisys.command.Process.OK:
            res.ok = True
            if self.verbose:
                ui.info("\n", process.out)
            message = (ui.green, message)
        elif process.return_type == qisys.command.Process.INTERRUPTED:
            res.ok = None
            message = (ui.brown, "interrupted")
        else:
            ui.info("\n", process.out)
            message = (ui.red, message)

        res.message = message
        self._post_run(res, test)
        return res

    def _update_test(self, test):
        """ Update the test given the settings on the test suite """
        self._update_test_cmd_for_project(test)
        self._update_test_env(test)
        self._update_test_cwd(test)
        valgrind = self.suite_runner.valgrind
        if valgrind:
            self._with_valgrind(test)
        num_cpus = self.suite_runner.num_cpus
        if num_cpus != -1:
            self._with_num_cpus(test, num_cpus)

    def _update_test_cmd_for_project(self, test):
        if not self.project:
            return
        perf_results = os.path.join(self.project.build_directory,
                                    "perf-results")
        if test.get("gtest"):
            cmd = test["cmd"]
            cmd.append("--gtest_output=xml:%s" % self.test_out)
        if test.get("perf"):
            qisys.sh.mkdir(perf_results)
            cmd = test["cmd"]
            cmd.extend(["--output", self.perf_out])

    def _update_test_env(self, test):
        env = os.environ.copy()
        if self.suite_runner.env:
            env = self.suite_runner.env.copy()
        test_env = test.get("environment")
        if test_env:
            env.update(test_env)
        if ui.CONFIG["color"] and test.get("gtest"):
            env["GTEST_COLOR"] = "yes"
        if os.name == 'nt':
            env["PATH"] = os.path.join(self.project.sdk_directory, "bin") + ";" + \
                          env["PATH"]
        if os.name == "darwin":
            env["DYLD_LIBRARY_PATH"] = os.path.join(self.project.sdk_directory, "lib") + ":" + \
                          env["DYLD_LIBRARY_PATH"]
        test["env"] = env
        # Quick hack:
        gtest_repeat = env.get("GTEST_REPEAT", "1")
        test["timeout"] = test["timeout"] * int(gtest_repeat)

    def _update_test_cwd(self, test):
        cwd = self.suite_runner.cwd
        test["working_directory"] = test.get("working_directory", cwd)

    def _with_valgrind(self, test):
        cwd = test["working_directory"]
        self.valgrind_log = os.path.join(cwd, test["name"] + "_valgrind.log")
        test["timeout"] = test["timeout"] * 10
        test["cmd"] = ["valgrind", "--track-fds=yes",
                       "--log-file=%s" % self.valgrind_log] + test["cmd"]

    def _with_num_cpus(self, test, num_cpus):
        cpu_list = get_cpu_list(multiprocessing.cpu_count(),
                                num_cpus, self.worker_index)
        taskset_opts = ["-c", ",".join(str(i) for i in cpu_list)]
        test["cmd"] = ["taskset"] + taskset_opts + test["cmd"]

    def _post_run(self, res, test):
        if not res.ok:
            # do not trust generated files:
            qisys.sh.rm(self.perf_out)
            qisys.sh.rm(self.test_out)

        if not res.ok or not os.path.exists(self.test_out):
            self._write_xml(res, test, self.test_out)

    def _write_xml(self, res, test, out_xml):
        """ Make sure a Junit XML compatible file is written """

        if sys.platform.startswith("win"):
            header = """<?xml version="1.0" encoding="ascii"?>"""
        else:
            header = """<?xml version="1.0" encoding="UTF-8"?>"""
        to_write = header + """
    <testsuites tests="1" failures="{num_failures}" disabled="0" errors="0" time="{time}" name="All">
        <testsuite name="{testsuite_name}" tests="1" failures="{num_failures}" disabled="0" errors="0" time="{time}">
        <testcase name="{testcase_name}" status="run">
        {failure}
        </testcase>
    </testsuite>
    </testsuites>
    """
        if res.ok:
            num_failures = "0"
            failure = ""
        else:
            num_failures = "1"
            failure = """
        <failure message="{message}">
            <![CDATA[ {out} ]]>
        </failure>
    """

        # Arbitrary limit output (~700 lines) to prevent from crashing on read
        res.out = res.out[-16384:]

        # Remove color before encoding
        if os.getenv("GTEST_COLOR") or sys.stdout.isatty():
            res.out = re.sub('\x1b[^m]*m', "", res.out)

        # Windows output is most likely code page 850
        if sys.platform.startswith("win"):
            encoding = "ascii"
        else:
            encoding = "utf-8"
        try:
            res.out = res.out.decode(encoding, "ignore").encode(encoding)
        except UnicodeDecodeError:
            pass

        failure = failure.format(out=res.out, message=res.message)
        to_write = to_write.format(num_failures=num_failures,
                                testsuite_name="test", # nothing clever to put here :/
                                testcase_name=test["name"],
                                failure=failure,
                                time=res.time)

        with open(out_xml, "w") as fp:
            fp.write(to_write)

    def get_message(self, process, timeout=None):
        """ Human readable string describing the state of the process """
        if process.return_type == qisys.command.Process.OK:
            return "[OK]"
        if process.return_type == qisys.command.Process.INTERRUPTED:
            return "Interrupted"
        if process.return_type == qisys.command.Process.NOT_RUN:
            mess = "Not run"
            if process.exception is not None:
                mess += ": " + str(process.exception)
            return mess
        if process.return_type == qisys.command.Process.TIME_OUT:
            return "Timed out (%is)" % timeout
        if process.return_type == qisys.command.Process.ZOMBIE:
            return "Zombie (Timeout = %is)" % timeout
        if process.return_type == qisys.command.Process.FAILED:
            retcode = process.returncode
            if retcode > 0:
                return "[FAIL] Return code: %i" % retcode
            else:
                return qisys.command.str_from_signal(-retcode)


def get_cpu_list(total_cpus, num_cpus_per_test, worker_index):
    cpu_list = list()
    i = worker_index * num_cpus_per_test
    cpu_list = range(i, i + num_cpus_per_test)
    cpu_list = [i % total_cpus for i in cpu_list]
    return cpu_list
