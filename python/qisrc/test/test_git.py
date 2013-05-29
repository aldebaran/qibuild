import os
import qisrc.git

def test_name_from_url_common():
    examples = [
        ("git@git:foo/bar.git", "foo/bar.git"),
        ("/srv/git/foo/bar.git", "bar.git"),
        ("file:///srv/git/foo/bar.git", "bar.git"),
        ("ssh://git@review:29418/foo/bar.git", "foo/bar.git"),
        ("ssh://git@example.com/spam/eggs.git", "spam/eggs.git"),
        ("ssh://git@example.com/eggs.git", "eggs.git"),
        ("http://github.com/john/bar.git", "john/bar.git")

    ]
    for (url, expected) in  examples:
        actual = qisrc.git.name_from_url(url)
        assert actual == expected

def test_name_from_url_win():
    if not os.name == 'nt':
        return
    url = r"file://c:\path\to\bar.git"
    assert qisrc.git.name_from_url(url) == "bar.git"
