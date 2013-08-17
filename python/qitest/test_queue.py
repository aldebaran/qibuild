import contextlib
import collections
import time
import threading
from Queue import Queue

from qisys import ui

class TestQueue():
    """ A class able to run tests in parallel """
    def __init__(self, tests):
        self.tests = tests
        self.test_logger = TestLogger(tests)
        self.task_queue = Queue()
        self.launcher = None
        self.results = collections.OrderedDict()
        self.ok = False

    def run(self, num_jobs=1):
        """ Run all the tests """
        if not self.launcher:
            ui.error("test launcher not set, cannot run tests")
            return
        for i, test in enumerate(self.tests):
            self.task_queue.put((test, i))

        if num_jobs == 1:
            self.test_logger.single_job = True
        threads = list()

        for i in range(0, num_jobs):
            worker = TestWorker(self.task_queue, i)
            worker.launcher = self.launcher
            worker.test_logger = self.test_logger
            # No need for mutexes because of the GIL
            worker.results = self.results
            threads.append(worker)
            worker.start()

        self.task_queue.join()
        self._summary()

    def _summary(self):
        """ Display the tests results.

        Called at the end of self.run()
        Sets ``self.ok``

        """
        num_tests = len(self.tests)
        failed = [x for x in self.results.values() if not x[0]]
        num_failed = len(failed)
        self.ok = (num_failed == 0)
        if self.ok:
            ui.info("Ran %i tests" % num_tests)
            ui.info("All pass. Congrats!")
        else:
            ui.error("Ran %i tests, %i failures" % (num_tests, num_failed))

class TestWorker(threading.Thread):
    def __init__(self, queue, worker_index):
        super(TestWorker, self).__init__(name="TestWorker#%i" % worker_index)
        self.queue = queue
        self.launcher = None
        self.launcher = None
        self.test_logger = None
        self.results = dict()

    def run(self):
        while not self.queue.empty():
            test, index = self.queue.get()
            self.test_logger.on_start(test, index)
            result = None
            try:
                result = self.launcher.launch(test)
            except Exception, e:
                result = False, (ui.red, "Python exception during tests\n",
                                 str(e))
            self.test_logger.on_completed(test, index, result)
            self.results[test["name"]] = result
            self.queue.task_done()

class TestLogger:
    """ Small class used to print what is going on during
    tests, using a mutex so that outputs are not mixed up

    """
    def __init__(self, tests):
        self.mutex = Mutex()
        self.tests = tests
        self.max_len = max((len(x["name"]) for x in self.tests))
        self.single_job = False

    def on_start(self, test, index):
        """ Called when a test starts """
        if self.single_job:
            self._info(test, index, (), end="")
            return
        with self.mutex.acquire():
            self._info(test, index, ("starting ...",))

    def on_completed(self, test, index, result):
        """ Called when a test is over """
        ok, message = result
        if self.single_job:
            ui.info(*message)
            return
        with self.mutex.acquire():
            self._info(test, index, message)

    def _info(self, test, index, message, **kwargs):
        """ Helper method """
        ui.info_count(index, len(self.tests),
                      ui.blue, test["name"].ljust(self.max_len + 2),
                      ui.reset, *message, **kwargs)


class Mutex:
    """ A mutex usable as a with statement.

    """
    # Sure this is not in the stdlib ?
    def __init__(self):
        self._mutex = threading.Lock()

    @contextlib.contextmanager
    def acquire(self):
        self._mutex.acquire()
        yield
        self._mutex.release()
