
import abc
import qixml

class MissingDependencyError(Exception):
    def __init__(self, doc, dep):
        self.doc, self.dep = doc, dep

    def __str__(self):
        return 'Couldn\'t find dependency {dep} for documentation {doc}.'.format(
            dep = self.dep, doc = self.doc,
        )


class Documentation:
    __metaclass__ = abc.ABCMeta

    def __init__(self, element):
        self.name, self.src, self.dest, self.dependencies = None, None, None, []
        self.configured, self.built = False, False
        self._parse(element)

    def _parse(self, element):
        self.name = qixml.parse_required_attr(element, "name")
        self.src = element.get("src", ".")
        self.dest = element.get("dest", self.name)
        depends_elements = element.findall("depends")
        for depends_element in depends_elements:
            self.dependencies.append(depends_element.get('name'))

    def configure(self, docs):
        if self.configured:
            return
        for dependency in self.dependencies:
            if dependency.name not in docs:
                raise MissingDependencyError(self, dependency)
            docs[dependency].configure(docs)
        self._configure()
        self.configured = True

    def build(self, docs):
        if self.built:
            return
        for dependency in self.dependencies:
            if dependency not in docs:
                raise MissingDependencyError(self, dependency)
            docs[dependency.name].build()
        self._build()

    def __cmp__(self, other):
        res = cmp(self.type_name(), other.type_name())
        if not res:
            res = cmp(self.name, other.name)
        return res

    @abc.abstractmethod
    def _configure(self):
        pass

    @abc.abstractmethod
    def _build(self):
        pass

    @abc.abstractmethod
    def type_name(self):
        pass
