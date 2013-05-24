from qibuild.find import library_name
from qibuild.find import binary_name

def test_library_name():
    assert library_name("foo", debug=False, dynamic=True,  os_name="Windows") == "foo.dll"
    assert library_name("foo", debug=True,  dynamic=True,  os_name="Windows") == "foo_d.dll"
    assert library_name("foo", debug=False, dynamic=False, os_name="Windows") == "foo.lib"
    assert library_name("foo", debug=True,  dynamic=False, os_name="Windows") == "foo_d.lib"

    assert library_name("foo", dynamic=True,  os_name="Linux") == "libfoo.so"
    assert library_name("foo", dynamic=False, os_name="Linux") == "libfoo.a"

    assert library_name("foo", dynamic=True,  os_name="Mac") == "libfoo.dylib"
    assert library_name("foo", dynamic=False, os_name="Mac") == "libfoo.a"


def test_binary_name():
    assert binary_name("foo", debug=False, os_name="Windows") == "foo.exe"
    assert binary_name("foo", debug=True,  os_name="Windows") == "foo_d.exe"

    assert binary_name("foo", os_name="Mac") == "foo"
    assert binary_name("foo", os_name="Linux") == "foo"
