import pytest

import qixml
from xml.etree import ElementTree as etree

def test_qixml_parse_bool_attr():
    tree = etree.fromstring("<foo />")
    assert qixml.parse_bool_attr(tree, "bar", default=True) == True
    assert qixml.parse_bool_attr(tree, "bar", default=False) == False
    assert qixml.parse_bool_attr(tree, "bar") == False

    tree = etree.fromstring("<foo bar=\"true\" />")
    assert qixml.parse_bool_attr(tree, "bar", default=True) == True
    assert qixml.parse_bool_attr(tree, "bar", default=False) == True
    assert qixml.parse_bool_attr(tree, "bar") == True

    tree = etree.fromstring("<foo bar=\"false\" />")
    assert qixml.parse_bool_attr(tree, "bar", default=True) == False
    assert qixml.parse_bool_attr(tree, "bar", default=False) == False
    assert qixml.parse_bool_attr(tree, "bar") == False

    tree = etree.fromstring("<foo bar=\"1\" />")
    assert qixml.parse_bool_attr(tree, "bar", default=True) == True
    assert qixml.parse_bool_attr(tree, "bar", default=False) == True
    assert qixml.parse_bool_attr(tree, "bar") == True

    tree = etree.fromstring("<foo bar=\"0\" />")
    assert qixml.parse_bool_attr(tree, "bar", default=True) == False
    assert qixml.parse_bool_attr(tree, "bar", default=False) == False
    assert qixml.parse_bool_attr(tree, "bar") == False

    tree = etree.fromstring("<foo bar=\"blaaaah\" />")

    with pytest.raises(Exception):
        qixml.parse_bool_attr(tree, "bar")

def test_parse_int_attr():
    tree = etree.fromstring("<foo />")
    with pytest.raises(Exception):
        qixml.parse_int_attr(tree, "bar", default=None)

    assert qixml.parse_int_attr(tree, "bar", default=2) == 2

    with pytest.raises(Exception):
        qixml.parse_int_attr(tree, "bar")

    tree = etree.fromstring("<foo bar=\"2\" />")
    assert qixml.parse_int_attr(tree, "bar", default=2) == 2
    assert qixml.parse_int_attr(tree, "bar", default=1) == 2
    assert qixml.parse_int_attr(tree, "bar") == 2

    tree = etree.fromstring("<foo bar=\"false\" />")
    with pytest.raises(Exception):
        qixml.parse_int_attr(tree, "bar")

def test_parse_list_attr():
    tree = etree.fromstring("<foo />")
    assert qixml.parse_list_attr(tree, "bar") == list()

    tree = etree.fromstring("<foo bar=\"foo bar\" />")
    assert qixml.parse_list_attr(tree, "bar") == ["foo", "bar"]

def test_parse_required_attr():
    tree = etree.fromstring("<foo />")
    with pytest.raises(Exception):
        qixml.parse_required_attr(tree, "bar")

    tree = etree.fromstring("<foo bar=\"foo\" />")
    assert qixml.parse_required_attr(tree, "bar") == "foo"



