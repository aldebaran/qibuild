from setuptools import setup

setup(name="with_distutils",
      py_modules=["foo"],
      entry_points = {"console_scripts" : ["foo = foo:main"]}
)
