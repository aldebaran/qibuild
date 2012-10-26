import abc
import qixml

from qisys import ui

class MissingDependencyError(Exception):
    '''The dependency of a documentation is missing.'''

    def __init__(self, doc, dep):
        Exception.__init__(self)
        self.doc, self.dep = doc, dep

    def __str__(self):
        return 'Couldn\'t find dependency {dep} for documentation {doc}.'.format(
            dep = self.dep, doc = self.doc.name,
        )


class ConfigureFailedError(Exception):
    '''Configuration of tje project failed.'''

    def __init__(self, project_name, reason):
        Exception.__init__(self)
        self.project_name, self.reason = project_name, reason

    def __str__(self):
        return '''Configuration of {project}'s documentation failed.
Reason: {reason}'''.format(
            project = self.project_name, reason = self.reason,
        )


class BuildFailedError(Exception):
    '''Build of the project failed.'''

    def __init__(self, project_name, reason):
        Exception.__init__(self)
        self.project_name, self.reason = project_name, reason

    def __str__(self):
        return '''Build of {project}'s documentation failed.
Reason: {reason}'''.format(
            project = self.project_name, reason = self.reason
        )


class DependencyCycleError(Exception):
    '''The is a cycle in dependency graph, example:
         * A depends on B
         * B depends on C
         * C depends on A
    '''

    def __str__(self):
        return 'Cycle in dependencies detected. Check your configuration.'


class Documentation:
    '''
    This class is the mother of all documentation projects. It manages all the
    dependencies and the target of the builds.

    It is an abstract class, you can't  instanciate it. Instead you should
    instanciate one of its subclasses (that must implement every abstract
    method bellow).
    '''

    __metaclass__ = abc.ABCMeta

    def __init__(self, element):
        self.name, self.src, self.dest, self.dependencies = None, None, None, []
        self._configured, self._built, self.docs = False, False, None
        self._parse(element)

    def _parse(self, element):
        '''
        This function parses XML configuration for the documentation project.
        '''
        self.name = qixml.parse_required_attr(element, "name")
        self.src = element.get("src", ".")
        self.dest = element.get("dest", self.name)
        depends_elements = element.findall("depends")
        for depends_element in depends_elements:
            self.dependencies.append(depends_element.get('name'))

    def configure(self, docs, opts, **kwargs):
        '''
        This is the main configure for the project, it will call configure of
        dependencies and then configure the project (subclass).
        '''
        if self._configured:
            return
        if self._configured is None:
            raise DependencyCycleError()
        self._configured = None
        for dependency in self.dependencies:
            if dependency not in docs:
                raise MissingDependencyError(self, dependency)
            docs[dependency].configure(docs, opts, **kwargs)
        ui.debug('Configuring', self.type_name(), 'project', self.name)
        self._configure(docs, opts, **kwargs)
        self._configured = True

    def build(self, docs, opts, **kwargs):
        '''
        Like configure, this calls the build method of dependencies before
        building itself.
        '''
        if self._built:
            return
        for dependency in self.dependencies:
            if dependency not in docs:
                raise MissingDependencyError(self, dependency)
            docs[dependency].build(docs, opts, **kwargs)
        ui.info(ui.green, 'Building', self.type_name(), 'project', ui.blue,
                self.name, ui.green, ' -> ', ui.purple, self.dest)
        self._build(docs, opts, **kwargs)
        self._built = True

    def __cmp__(self, other):
        '''Comapres type names (sphinx, doxygen).'''
        res = cmp(self.type_name(), other.type_name())
        if not res:
            res = cmp(self.name, other.name)
        return res

    @abc.abstractmethod
    def type_name(self):
        '''
        This function must return a string representing the type of the
        documentation, for example: sphinx or doxygen.
        '''
        pass

    @abc.abstractmethod
    def get_mapping(self, docs, **kwargs):
        pass

    @abc.abstractmethod
    def _configure(self, docs, opts, **kwargs):
        '''
        This is the self configuration. It is called when all the dependencies
        are configured.
        '''
        pass

    @abc.abstractmethod
    def _build(self, docs, opts, **kwargs):
        '''
        This function should build the project. All its dependencies are
        already built when this method is called.
        '''
        pass
