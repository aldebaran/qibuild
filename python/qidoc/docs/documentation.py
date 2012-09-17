
import abc
import qixml

from qibuild import ui

class MissingDependencyError(Exception):
    def __init__(self, doc, dep):
        self.doc, self.dep = doc, dep

    def __str__(self):
        return 'Couldn\'t find dependency {dep} for documentation {doc}.'.format(
            dep = self.dep, doc = self.doc,
        )


class ConfigureFailed(Exception):
    def __init__(self, project_name, reason):
        self.project_name, self.reason = project_name, reason

    def __str__(self):
        return '''Configuration of {project}'s documentation failed.
Reason: {reason}'''.format(
            project = self.project_name, reason = self.reason,
        )


class BuildFailed(Exception):
    def __init__(self, project_name, reason):
        self.project_name, self.reason = project_name, reason

    def __str__(self):
        return '''Build of {project}'s documentation failed.
Reason: {reason}'''.format(
            project = self.project_name, reason = self.reason
        )


class Documentation:
    __metaclass__ = abc.ABCMeta

    def __init__(self, element):
        self.name, self.src, self.dest, self.dependencies = None, None, None, []
        self._configured, self._built, self.docs = False, False, None
        self._parse(element)

    def _parse(self, element):
        self.name = qixml.parse_required_attr(element, "name")
        self.src = element.get("src", ".")
        self.dest = element.get("dest", self.name)
        depends_elements = element.findall("depends")
        for depends_element in depends_elements:
            self.dependencies.append(depends_element.get('name'))

    def configure(self, docs, opts, **kwargs):
        if self._configured:
            return
        if self._configured is None:
            # We have a cycle in the dependencies, user should check his
            # configuration. FIXME: Report better error.
            mess = 'Cycle in dependencies detected. '
            mess += 'Check your configuration.'
            raise Exception(mess)
        self._configured = None
        for dependency in self.dependencies:
            if dependency not in docs:
                raise MissingDependencyError(self, dependency)
            docs[dependency].configure(docs, opts, **kwargs)
        ui.debug('Configuring', self.type_name(), 'project', self.name)
        self._configure(docs, opts, **kwargs)
        self._configured = True

    def build(self, docs, opts, **kwargs):
        if self._built:
            return
        for dependency in self.dependencies:
            if dependency not in docs:
                raise MissingDependencyError(self, dependency)
            docs[dependency].build(docs, opts, **kwargs)
        ui.info('Building', self.type_name(), 'project', self.name)
        self._build(docs, opts, **kwargs)
        self._built = True

    def __cmp__(self, other):
        res = cmp(self.type_name(), other.type_name())
        if not res:
            res = cmp(self.name, other.name)
        return res

    @abc.abstractmethod
    def type_name(self):
        pass

    @abc.abstractmethod
    def get_mapping(self, docs, **kwargs):
        pass

    @abc.abstractmethod
    def _configure(self, docs, opts, **kwargs):
        pass

    @abc.abstractmethod
    def _build(self, docs, opts, **kwargs):
        pass
