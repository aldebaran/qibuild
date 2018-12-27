#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" Test QiXml """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

from xml.etree import ElementTree as etree
import pytest

import qisys.qixml


def test_qixml_parse_bool_attr():
    """ Test QiXml Parse Bool Attr """
    tree = etree.fromstring("<foo />")
    assert qisys.qixml.parse_bool_attr(tree, "bar", default=True) is True
    assert qisys.qixml.parse_bool_attr(tree, "bar", default=False) is False
    assert qisys.qixml.parse_bool_attr(tree, "bar") is False
    tree = etree.fromstring("<foo bar=\"true\" />")
    assert qisys.qixml.parse_bool_attr(tree, "bar", default=True) is True
    assert qisys.qixml.parse_bool_attr(tree, "bar", default=False) is True
    assert qisys.qixml.parse_bool_attr(tree, "bar") is True
    tree = etree.fromstring("<foo bar=\"false\" />")
    assert qisys.qixml.parse_bool_attr(tree, "bar", default=True) is False
    assert qisys.qixml.parse_bool_attr(tree, "bar", default=False) is False
    assert qisys.qixml.parse_bool_attr(tree, "bar") is False
    tree = etree.fromstring("<foo bar=\"1\" />")
    assert qisys.qixml.parse_bool_attr(tree, "bar", default=True) is True
    assert qisys.qixml.parse_bool_attr(tree, "bar", default=False) is True
    assert qisys.qixml.parse_bool_attr(tree, "bar") is True
    tree = etree.fromstring("<foo bar=\"0\" />")
    assert qisys.qixml.parse_bool_attr(tree, "bar", default=True) is False
    assert qisys.qixml.parse_bool_attr(tree, "bar", default=False) is False
    assert qisys.qixml.parse_bool_attr(tree, "bar") is False
    tree = etree.fromstring("<foo bar=\"blaaaah\" />")
    with pytest.raises(Exception):
        qisys.qixml.parse_bool_attr(tree, "bar")


def test_parse_int_attr():
    """ Test Parse Int Attr """
    tree = etree.fromstring("<foo />")
    with pytest.raises(Exception):
        qisys.qixml.parse_int_attr(tree, "bar", default=None)
    assert qisys.qixml.parse_int_attr(tree, "bar", default=2) == 2
    with pytest.raises(Exception):
        qisys.qixml.parse_int_attr(tree, "bar")
    tree = etree.fromstring("<foo bar=\"2\" />")
    assert qisys.qixml.parse_int_attr(tree, "bar", default=2) == 2
    assert qisys.qixml.parse_int_attr(tree, "bar", default=1) == 2
    assert qisys.qixml.parse_int_attr(tree, "bar") == 2
    tree = etree.fromstring("<foo bar=\"false\" />")
    with pytest.raises(Exception):
        qisys.qixml.parse_int_attr(tree, "bar")


def test_parse_list_attr():
    """ Test Parse List Attr """
    tree = etree.fromstring("<foo />")
    assert qisys.qixml.parse_list_attr(tree, "bar") == list()
    tree = etree.fromstring("<foo bar=\"foo bar\" />")
    assert qisys.qixml.parse_list_attr(tree, "bar") == ["foo", "bar"]


def test_parse_required_attr():
    """ Test Parse Required Attribute """
    tree = etree.fromstring("<foo />")
    with pytest.raises(Exception):
        qisys.qixml.parse_required_attr(tree, "bar")
    tree = etree.fromstring("<foo bar=\"foo\" />")
    assert qisys.qixml.parse_required_attr(tree, "bar") == "foo"


def test_simple_xml_parser():
    """ Test Simple Xml Parser """
    tree = etree.fromstring("""\n<foo\n    bar="baz"\n    spam="eggs"\n/>\n""")

    class Foo(object):
        """ Foo Class """
        def __init__(self):
            """ Foo Init """
            self.bar = None
            self.spam = None
            self.quzz = 42

    class FooParser(qisys.qixml.XMLParser):
        """ FooParser Class """
        pass

    food = Foo()
    foo_parser = FooParser(food)
    foo_parser.parse(tree)
    assert food.quzz == 42
    assert food.bar == "baz"
    assert food.spam == "eggs"


def test_required_attr():
    """ Test Required Attribute """
    tree = etree.fromstring("<foo />")

    class Foo(object):
        """ Foo Class """
        pass

    class FooParser(qisys.qixml.XMLParser):
        """ FooParser Class """
        def __init__(self, target):
            """ FooParser Init """
            super(FooParser, self).__init__(target)
            self._required = ["bar"]

    food = Foo()
    foo_parser = FooParser(food)
    with pytest.raises(Exception) as e:
        foo_parser.parse(tree)
    assert e.value.message == "Node 'foo' must have a 'bar' attribute"


def test_complex_xml_parser():
    """ Test Complex Xml Parser """

    class BarParser(qisys.qixml.XMLParser):
        """ BarParser Class """
        pass

    class FooParser(qisys.qixml.XMLParser):
        """ FooParser Class """

        def _write_bar(self, elem):
            """ Write Bar """
            parser = BarParser(self.target.bar)
            bar_elem = parser.xml_elem()
            elem.append(bar_elem)

        def _parse_bar(self, elem):
            """ ParseBar """
            parser = BarParser(self.target.bar)
            parser.parse(elem)

    class Bar(object):
        """ Bar Class """

        def __init__(self):
            """ Bar Init """
            self.baz = None

    class Foo(object):
        """ Foo Class """

        def __init__(self):
            """ Foo Init """
            self.bar = Bar()
            self.spam = None
            self.eggs = None

    foo1 = Foo()
    foo1.bar.baz = "Baz!"
    foo1.spam = 42
    foo1.eggs = True
    parser = FooParser(foo1)
    foo_xml = parser.xml_elem()
    foo2 = Foo()
    parser = FooParser(foo2)
    parser.parse(foo_xml)
    assert foo2.bar.baz == "Baz!"
    assert foo1.spam == 42
    assert foo1.eggs is True


def test_list_attr():
    """ Test List Attr """

    class Foo(object):
        """ Foo Class """

        def __init__(self):
            """ Foo Init """
            self.names = list()

    class FooParser(qisys.qixml.XMLParser):
        """ FooParser Class """
        pass

    foo1 = Foo()
    foo1.names = ["a", "b"]
    parser = FooParser(foo1)
    xml_elem = parser.xml_elem()
    foo1 = Foo()
    parser = FooParser(foo1)
    parser.parse(xml_elem)
    assert foo1.names == ["a", "b"]
    foo1.names = list()
    xml_elem = parser.xml_elem()
    foo1 = Foo()
    parser = FooParser(foo1)
    parser.parse(xml_elem)
    assert foo1.names == list()


def test_write_bool_attr():
    """ Test Write Bool Attr """

    class Foo(object):
        """ Foo Class """

        def __init__(self):
            """ Foo Init """
            self.bar = False

    class FooParser(qisys.qixml.XMLParser):
        """ FooParser Class """
        pass

    foo1 = Foo()
    foo1.bar = True
    parser = FooParser(foo1)
    xml_elem = parser.xml_elem()
    bar1 = qisys.qixml.parse_bool_attr(xml_elem, "bar")
    assert bar1 is True


def test_sanitize_xml():
    """ Test Sanitize Xml """
    invalid_xml = u'<failure message="\u001a\r\nflag\r\n" />'
    valid_xml = qisys.qixml.sanitize_xml(invalid_xml)
    assert "\r\nflag\r\n" in valid_xml
    etree.fromstring(valid_xml)  # Doesn't raise


def test_ignore_attributes():
    """ Test Ignore Attributes """

    class Foo(object):
        """ Foo Class """

        def __init__(self):
            """ Foo Init """
            self.bar = "bar"
            self.baz = "baz"

    class FooParser(qisys.qixml.XMLParser):
        """ FooParser Class """

        def __init__(self, target):
            """ FooParser Init """
            super(FooParser, self).__init__(target)
            self._ignore = ["bar"]

    foo1 = Foo()
    parser = FooParser(foo1)
    xml_elem = etree.fromstring('<foo bar="spam" baz="eggs" />')
    parser.parse(xml_elem)
    assert foo1.bar == "bar"  # should not have changed
    assert foo1.baz == "eggs"  # should have changed
