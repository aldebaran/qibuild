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

