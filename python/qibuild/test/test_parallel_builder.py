import qibuild.parallel_builder

class FakeProject(object):
    build_log = list()

    def __init__(self, name, deps=None):
        self.name = name
        self.build_type = "Debug"
        if deps:
            self.build_depends = deps
        else:
            self.build_depends = set()

    def build(self, *args, **kwargs):
        self.build_log.append(self.name)

def is_before(mylist, a, b):
    a_index = mylist.index(a)
    b_index = mylist.index(b)
    return a_index < b_index

def test_simple():
    a = FakeProject("a")
    b = FakeProject("b")
    c = FakeProject("c", deps=["a", "b"])
    builder = qibuild.parallel_builder.ParallelBuilder()
    builder.prepare_build_jobs([a, b, c])
    builder.build(num_workers=2)
    build_log = FakeProject.build_log
    assert is_before(build_log, "a", "c")
    assert is_before(build_log, "b", "c")
