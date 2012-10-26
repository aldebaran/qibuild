from types import ModuleType

def create_alias_module(name, target):
    """ Create an alias module.

    For instance, after:

      $ mv qibuild/archive.py -> qisys.archive.py

    You can patch qibuild/__init__.py like this:

      - from . import archive
      + from qisys.refact import create_alias_module
      + import qisys.archive
      + archive = qisy.refact.create_alias_module("archive", qisys.archive)

    """
    module = AliasModule(name, target)
    return module

class AliasModule(ModuleType):
    """ The class returned by create_alias_module

    name lookup will be delegated to the target, while printing
    a nice warning

    """
    def __init__(self, name, target):
        self.name = name
        self.target = target

    def __getattr__(self, name):
        thing = getattr(self.target, name)
        if thing:
            print "%s.%s is deprecated, use %s.%s instead" % \
                (self.name, name, self.target.__name__, name)
            return thing
        else:
            raise AttributeError("'module' object has no attribute '%s'" % name)
