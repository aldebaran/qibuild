"""Helper to parse XML tree easily only defining methods."""

class RootXMLParser:
    """
    This class provides an easy interface to parse XML tags element by element.
    To work with it, you must inherit from this class and define methods on tags
    you want to parse.

    Example XML:
        <foo>
            <bar attr1="fooooooo">Some content!</bar>
            <easy><win>Yes!</win></easy>
            <win>Nooooooooooooooooooooooooooooooooo!</win>
        </foo>

    Root of the XML is foo. When :func:`RootXMLParser.parse` is called, it
    will try to call ``_parse_TAGNAME`` where tag name is the actual name of the
    tag you want to parse. It takes the element as a parameter.

    You can call parse recursively (from `_parse_TAGNAME` functions) to parse
    sub-trees. You always have :member:`backtrace` to know from where you came
    in ``_parse_TAGNAME``. Here is a complete example of a usage on XML above:

    class Foo(RootXMLParser):
        def _parse_bar(self, element):
            print 'Attribute attr1:', element.attrib['attr1']
            print 'Content:', element.text

        def _parse_easy(self, element):
            self.parse(element)

        def _parse_win(self, element):
            # We only want to parse win tag in easy tag.
            if 'easy' in self.backtrace:
                print 'Win text:', element.text

    A parser class should not have an attribute with the name of an xml
    attribute unless it wants to grab them.
    """

    def __init__(self, root):
        """Initialize the RootXMLParser with a root element.

        :param root: The root element.
        """
        self._root, self.backtrace = root, []

    def parse(self, root=None):
        """
        This function iterates on the childs of the element (or the root if an
        element is not given) and call ``_parse_TAGNAME`` functions.

        :param root: The root element that should be parsed.
        """
        if root is None:
            root = self._root
            self._parse_prologue()
            self._parse_attributes()
        self.backtrace.append(root.tag)
        for child in root:
            method_name = "_parse_{tagname}".format(tagname = child.tag)
            try:
                method = getattr(self.__class__, method_name)
            except AttributeError as err:
                self._parse_unknown_element(child, err)
                continue
            if method.func_code.co_argcount != 2:
                mess = "Handler for tag `%s' must take" % child.tag
                mess += " two arguments. (method: %s, takes " % method_name
                mess += "%d argument(s))" % method.func_code.co_argcount
                raise TypeError(mess)
            method(self, child)
        self.backtrace.pop()
        if root is self._root:
            self._parse_epilogue()

    def _parse_unknown_element(self, element, err):
        """
        This function will by default ignore unknown elements. You can overload
        it to change its behavior.

        :param element: The unknown element.
        :param err: The error message.
        """
        pass

    def _parse_prologue(self):
        """
        You can overload this function to do something before the beginning of
        parsing of the file.
        """
        pass

    def _parse_epilogue(self):
        """
        You can overload this function to do something after the end of the
        parsing of the file.
        """
        pass

    def _parse_attributes(self):
        """
        You can overload this function to get attribute of root before parsing
        his children. Attributes will be a dictionnary.
        """
        for attr in self._root.attrib:
            if hasattr(self, attr):
                default_value = getattr(self, attr)
                type_value = type(default_value)

                new_value = self._get_value_for_type(type_value,
                        self._root.attrib[attr])
                setattr(self, attr, new_value)

        self._post_parse_attributes()

    def _post_parse_attributes(self):
        """
        You can overload this function to add post treatment to parsing of
        attributes. Attributes will be a dictionnary.
        """
        pass

    def _get_value_for_type(self, type_value, value):
        if type_value == bool:
            if value.lower() in ["true", "1"]:
                return True
            if value.lower() in ["false", "0"]:
                return False
            mess = "Waiting for a boolean but value is '%s'." % value
            raise Exception(mess)

        return value

    def check_needed(self, attribute_name, node_name=None, value=None):
        if node_name is None:
            node_name = self.__class__.__name__.lower()

        if value is None:
            if hasattr(self, attribute_name):
                value = getattr(self, attribute_name)

        if value is None:
            mess = "Node '%s' must have a '%s' attribute." % (node_name,
                                                               attribute_name)
            raise Exception(mess)
