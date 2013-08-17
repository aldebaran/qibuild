
class TestResult:
    """ Just a small class to store the results for a test

    """
    def __init__(self, test):
        self.test = test
        self.time = 0
        self.ok = False
        self.message = list()
