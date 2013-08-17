from qisys import ui
import time
import qitest.test_queue
import qitest.launcher

class DummyLauncher(qitest.launcher.TestLauncher):
    def __init__(self):
        self.results = dict()

    def launch(self, test):
        default_time = 0.2
        default_result = True, (ui.green, "[OK]")
        sleep_time = default_time
        result = default_result
        fate = self.results.get(test["name"])
        if fate:
            sleep_time = fate.get("sleep_time", default_time)
            result = fate.get("result", default_result)
            if fate.get('raises'):
                raise Exception("Kaboom!")
        time.sleep(sleep_time)
        return result

def test_queue_happy():
    tests = [
     {"name" : "one"},
     {"name" : "two"},
     {"name" : "three"},
     {"name" : "four"},
     {"name" : "five"},
    ]
    test_queue = qitest.test_queue.TestQueue(tests)
    dummy_launcher = DummyLauncher()
    test_queue.launcher = dummy_launcher
    test_queue.run(num_jobs=3)
    assert test_queue.ok


def test_queue_sad():
    tests = [
     {"name" : "one"},
     {"name" : "two"},
     {"name" : "three"},
     {"name" : "four"},
     {"name" : "five"},
    ]
    test_queue = qitest.test_queue.TestQueue(tests)
    dummy_launcher = DummyLauncher()
    dummy_launcher.results = {
        "two" : {"result" : (False, (ui.red, "[FAIL]"))},
        "three" : {"raises" : True},
        "four" : {"sleep_time" : 0.4},
    }

    test_queue.launcher = dummy_launcher
    test_queue.run(num_jobs=3)
    assert not test_queue.ok


def test_one_job():
    tests = [
     {"name" : "one"},
     {"name" : "two"},
     {"name" : "three"},
    ]
    test_queue = qitest.test_queue.TestQueue(tests)
    dummy_launcher = DummyLauncher()
    test_queue.launcher = dummy_launcher
    test_queue.run(num_jobs=1)
    assert test_queue.ok

