    def test_ctest(self):
        self._run_action("configure", "hello")
        self._run_action("make", "hello")
        self._run_action("test", "hello")


    def test_package(self):
        self._run_action("package", "world")
