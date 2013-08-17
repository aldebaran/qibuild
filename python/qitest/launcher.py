import abc

class TestLauncher(object):
    """ Interface for a class able to launch a test. """
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def launch(self, test):
        pass


class ProcessTestLauncher(object):
    """ Implements TestLauncher using `qisys.command.Process```

    """
    def __init__(self, suite_runner):
        self.suite_runner = suite_runner

    def launch(self, test):
        process = qisys.command.Process(ncmd,
            cwd=cwd,
            env=env,
            verbose=self.verbose)
