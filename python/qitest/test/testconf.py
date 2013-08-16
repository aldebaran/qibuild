
@pytest.fixture():
def test_factory():
    return Factory()

class Factory():

    test_gtest_one = {
        "name" : "gtest_one",
        "cmd" : ["/path/to/test_one", "--gtest_output", "foo.xml"],
        "timeout" : 2,
    }

    test_perf_one = {
        "name" : "perf_one",
        "cmd" : ["/path/to/perf_one"],
        "perf" : True
