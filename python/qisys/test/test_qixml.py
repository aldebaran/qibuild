## Copyright (c) 2012-2016 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.
import pytest

import qisys.error
import qisys.qixml
from xml.etree import ElementTree as etree

def test_qixml_parse_bool_attr():
    tree = etree.fromstring("<foo />")
    assert qisys.qixml.parse_bool_attr(tree, "bar", default=True) == True
    assert qisys.qixml.parse_bool_attr(tree, "bar", default=False) == False
    assert qisys.qixml.parse_bool_attr(tree, "bar") == False

    tree = etree.fromstring("<foo bar=\"true\" />")
    assert qisys.qixml.parse_bool_attr(tree, "bar", default=True) == True
    assert qisys.qixml.parse_bool_attr(tree, "bar", default=False) == True
    assert qisys.qixml.parse_bool_attr(tree, "bar") == True

    tree = etree.fromstring("<foo bar=\"false\" />")
    assert qisys.qixml.parse_bool_attr(tree, "bar", default=True) == False
    assert qisys.qixml.parse_bool_attr(tree, "bar", default=False) == False
    assert qisys.qixml.parse_bool_attr(tree, "bar") == False

    tree = etree.fromstring("<foo bar=\"1\" />")
    assert qisys.qixml.parse_bool_attr(tree, "bar", default=True) == True
    assert qisys.qixml.parse_bool_attr(tree, "bar", default=False) == True
    assert qisys.qixml.parse_bool_attr(tree, "bar") == True

    tree = etree.fromstring("<foo bar=\"0\" />")
    assert qisys.qixml.parse_bool_attr(tree, "bar", default=True) == False
    assert qisys.qixml.parse_bool_attr(tree, "bar", default=False) == False
    assert qisys.qixml.parse_bool_attr(tree, "bar") == False

    tree = etree.fromstring("<foo bar=\"blaaaah\" />")

    # pylint: disable-msg=E1101
    with pytest.raises(qisys.error.Error):
        qisys.qixml.parse_bool_attr(tree, "bar")

def test_parse_int_attr():
    tree = etree.fromstring("<foo />")
    # pylint: disable-msg=E1101
    with pytest.raises(qisys.error.Error):
        qisys.qixml.parse_int_attr(tree, "bar", default=None)

    assert qisys.qixml.parse_int_attr(tree, "bar", default=2) == 2

    # pylint: disable-msg=E1101
    with pytest.raises(qisys.error.Error):
        qisys.qixml.parse_int_attr(tree, "bar")

    tree = etree.fromstring("<foo bar=\"2\" />")
    assert qisys.qixml.parse_int_attr(tree, "bar", default=2) == 2
    assert qisys.qixml.parse_int_attr(tree, "bar", default=1) == 2
    assert qisys.qixml.parse_int_attr(tree, "bar") == 2

    tree = etree.fromstring("<foo bar=\"false\" />")
    # pylint: disable-msg=E1101
    with pytest.raises(qisys.error.Error):
        qisys.qixml.parse_int_attr(tree, "bar")

def test_parse_list_attr():
    tree = etree.fromstring("<foo />")
    assert qisys.qixml.parse_list_attr(tree, "bar") == list()

    tree = etree.fromstring("<foo bar=\"foo bar\" />")
    assert qisys.qixml.parse_list_attr(tree, "bar") == ["foo", "bar"]

def test_parse_required_attr():
    tree = etree.fromstring("<foo />")
    # pylint: disable-msg=E1101
    with pytest.raises(qisys.error.Error):
        qisys.qixml.parse_required_attr(tree, "bar")

    tree = etree.fromstring("<foo bar=\"foo\" />")
    assert qisys.qixml.parse_required_attr(tree, "bar") == "foo"

def test_simple_xml_parser():
    tree = etree.fromstring("""
<foo
    bar="baz"
    spam="eggs"
/>
""")
    class Foo:
        def __init__(self):
            self.bar = None
            self.spam = None
            self.quzz = 42

    class FooParser(qisys.qixml.XMLParser):
        def __init__(self, target):
            super(FooParser, self).__init__(target)


    foo = Foo()
    foo_parser = FooParser(foo)
    foo_parser.parse(tree)

    assert foo.quzz == 42
    assert foo.bar == "baz"
    assert foo.spam == "eggs"

def test_required_attr():
    tree = etree.fromstring("<foo />")
    class Foo:
        pass

    class FooParser(qisys.qixml.XMLParser):
        def __init__(self, target):
            super(FooParser, self).__init__(target)
            self._required = ["bar"]

    foo = Foo()
    foo_parser = FooParser(foo)
    # pylint: disable-msg=E1101
    with pytest.raises(qisys.error.Error) as e:
        foo_parser.parse(tree)
    assert e.value.message == "Node 'foo' must have a 'bar' attribute"


def test_complex_xml_parser():

    class BarParser(qisys.qixml.XMLParser):
        def __init__(self, target):
            super(BarParser, self).__init__(target)

    class FooParser(qisys.qixml.XMLParser):
        def __init__(self, target):
            super(FooParser, self).__init__(target)

        def _write_bar(self, elem):
            parser = BarParser(self.target.bar)
            bar_elem = parser.xml_elem()
            elem.append(bar_elem)

        def _parse_bar(self, elem):
            parser = BarParser(self.target.bar)
            parser.parse(elem)

    class Bar:
        def __init__(self):
            self.baz = None

    class Foo:
        def __init__(self):
            self.bar = Bar()
            self.spam = None
            self.eggs = None

    foo = Foo()
    foo.bar.baz = "Baz!"
    foo.spam = 42
    foo.eggs = True
    parser = FooParser(foo)
    foo_xml = parser.xml_elem()

    foo2 = Foo()
    parser = FooParser(foo2)
    parser.parse(foo_xml)
    assert foo2.bar.baz == "Baz!"
    foo.spam == 42
    foo.eggs == True

def test_list_attr():
    class Foo:
        def __init__(self):
            self.names = list()

    class FooParser(qisys.qixml.XMLParser):
        def __init__(self, target):
            super(FooParser, self).__init__(target)

    foo = Foo()
    foo.names = ["a", "b"]
    parser = FooParser(foo)
    xml_elem = parser.xml_elem()
    foo = Foo()
    parser = FooParser(foo)
    parser.parse(xml_elem)
    assert foo.names == ["a", "b"]
    foo.names = list()
    xml_elem = parser.xml_elem()
    foo = Foo()
    parser = FooParser(foo)
    parser.parse(xml_elem)
    assert foo.names == list()


def test_write_bool_attr():
    class Foo:
        def __init__(self):
            self.bar = False

    class FooParser(qisys.qixml.XMLParser):
        def __init__(self, target):
            super(FooParser, self).__init__(target)

    foo = Foo()
    foo.bar = True
    parser = FooParser(foo)
    xml_elem = parser.xml_elem()
    bar = qisys.qixml.parse_bool_attr(xml_elem, "bar")
    assert bar is True


def test_sanitize_xml():
    invalid_xml = u'<failure message="\u001a\r\nflag\r\n" />'
    valid_xml = qisys.qixml.sanitize_xml(invalid_xml)
    assert "\r\nflag\r\n" in valid_xml
    etree.fromstring(valid_xml)  # Doesn't raise


def test_ignore_attributes():
    class Foo:
        def __init__(self):
            self.bar = "bar"
            self.baz = "baz"

    class FooParser(qisys.qixml.XMLParser):
        def __init__(self, target):
            super(FooParser, self).__init__(target)
            self._ignore = ["bar"]

    foo = Foo()
    parser = FooParser(foo)
    xml_elem = etree.fromstring('<foo bar="spam" baz="eggs" />')
    parser.parse(xml_elem)

    assert foo.bar == "bar" # should not have changed
    assert foo.baz == "eggs" # should have changed

def test_indent(tmpdir):
    root = etree.Element("root")
    sub = etree.SubElement(root, "sub")
    sub.text = "some text"
    out = tmpdir.join("out.xml")
    qisys.qixml.write(root, out.strpath)
    assert out.read() == """\
<root>
  <sub>some text</sub>
</root>
"""
