import pytest

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
    with pytest.raises(Exception):
        qisys.qixml.parse_bool_attr(tree, "bar")

def test_parse_int_attr():
    tree = etree.fromstring("<foo />")
    # pylint: disable-msg=E1101
    with pytest.raises(Exception):
        qisys.qixml.parse_int_attr(tree, "bar", default=None)

    assert qisys.qixml.parse_int_attr(tree, "bar", default=2) == 2

    # pylint: disable-msg=E1101
    with pytest.raises(Exception):
        qisys.qixml.parse_int_attr(tree, "bar")

    tree = etree.fromstring("<foo bar=\"2\" />")
    assert qisys.qixml.parse_int_attr(tree, "bar", default=2) == 2
    assert qisys.qixml.parse_int_attr(tree, "bar", default=1) == 2
    assert qisys.qixml.parse_int_attr(tree, "bar") == 2

    tree = etree.fromstring("<foo bar=\"false\" />")
    # pylint: disable-msg=E1101
    with pytest.raises(Exception):
        qisys.qixml.parse_int_attr(tree, "bar")

def test_parse_list_attr():
    tree = etree.fromstring("<foo />")
    assert qisys.qixml.parse_list_attr(tree, "bar") == list()

    tree = etree.fromstring("<foo bar=\"foo bar\" />")
    assert qisys.qixml.parse_list_attr(tree, "bar") == ["foo", "bar"]

def test_parse_required_attr():
    tree = etree.fromstring("<foo />")
    # pylint: disable-msg=E1101
    with pytest.raises(Exception):
        qisys.qixml.parse_required_attr(tree, "bar")

    tree = etree.fromstring("<foo bar=\"foo\" />")
    assert qisys.qixml.parse_required_attr(tree, "bar") == "foo"



