import qisrc.templates


def test_process_templates(tmpdir):
    tmpl = tmpdir.mkdir("tmpl")
    tmpl_cmake_list = tmpl.ensure("CMakeLists.txt", file=True)
    tmpl_cmake_list.write("""\
cmake_minimum_required(VERSION 3.0)
project(@ProjectName@)

add_executable(@project_name@ "@project_name@/@project_name@.cpp")
""")
    tmpl_hpp = tmpl.ensure("@project_name@", "@project_name@.hpp", file=True)
    tmpl_hpp.write("""\
#ifndef @PROJECT_NAME@_HPP
#define @PROJECT_NAME@_HPP

class @ProjectName@ {
  public:
    void @projectName@Register() {
      // Your code goes here
    }
};

#endif
""")

    dest = tmpdir.mkdir("dest")
    qisrc.templates.process(tmpl.strpath, dest.strpath, project_name="monthyPython")

    dest_cmake = dest.join("CMakeLists.txt")
    assert dest_cmake.read() == """\
cmake_minimum_required(VERSION 3.0)
project(MonthyPython)

add_executable(monthy_python "monthy_python/monthy_python.cpp")
"""

    dest_hpp = dest.join("monthy_python", "monthy_python.hpp")
    assert dest_hpp.read() == """\
#ifndef MONTHY_PYTHON_HPP
#define MONTHY_PYTHON_HPP

class MonthyPython {
  public:
    void monthyPythonRegister() {
      // Your code goes here
    }
};

#endif
"""


def test_process_string():
    res = qisrc.templates.process_string("@project_name@.cpp",
                                         project_name="monthy_python")
    assert res == "monthy_python.cpp"

    res = qisrc.templates.process_string("#define @PROJECT_NAME@_HPP",
                                         project_name="Foo")

    assert res == "#define FOO_HPP"

    res = qisrc.templates.process_string("#define @PROJECT_NAME@_HPP",
                                         project_name="MonthyPython")

    assert res == "#define MONTHY_PYTHON_HPP"
