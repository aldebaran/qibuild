import os
import qitest.conf

class TestProject():
    def __init__(self, qitest_json):
        self.name = None
        self.tests = qitest.conf.parse_tests(qitest_json)
        self.sdk_directory = os.path.dirname(qitest_json)
